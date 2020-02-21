import numpy
import json
from matplotlib import pyplot as plt

from gnuradio import filter
from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr
import lora2
#from lora2 import css_mod
import channels

class css_delay_track(gr.top_block):
    def __init__(self, SF, cfo, delay, interp, EbN0dB, n_syms_pkt, n_pkt):
        gr.top_block.__init__(self, "CSS CFO and Delay Track")

        ##################################################
        # Variables
        ##################################################
        self.SF = SF
        self.cfo = cfo

        self.intern_interp= 1
        delay = delay*self.intern_interp*interp
        self.interp = interp
        self.M = M = 2**self.SF

        self.syms_vec = numpy.random.randint(0, M, n_syms_pkt*n_pkt)
        noisevar = float(M)/numpy.log2(M) * 10**(-EbN0dB/10.0)

        ##################################################
        # Blocks
        ##################################################
        #Modulator
        self.syms_src = blocks.vector_source_s(self.syms_vec, False)
        self.css_mod = lora2.css_mod(M, self.intern_interp*self.interp)

        #LoRa
        self.to_tagged = blocks.stream_to_tagged_stream(gr.sizeof_short, 1,
                n_syms_pkt, 'packet_len')
        self.add_preamble = lora2.lora_add_preamble(8, 0x12, "packet_len",
                "sync_word", "payload")
        self.add_reversed_chirps = lora2.lora_add_reversed_chirps(self.SF,
                self.interp*self.intern_interp, "packet_len", "payload", "rev_chirps")

        #Channel (1: noise)
        self.tag_gate = blocks.tag_gate(gr.sizeof_gr_complex)
        self.awgn_chan = channels.awgn(noisevar)

        #Channel (2: delay)
        int_delay = 0
        frac_delay = 0.0
        self.int_delayer = None
        if delay > 0:
            int_delay = int(delay)
            frac_delay = delay-int_delay
            self.int_delayer = blocks.delay(gr.sizeof_gr_complex, int_delay)
        else:
            int_delay = int(-delay)
            frac_delay = -delay-int_delay
            self.int_delayer = blocks.skiphead(gr.sizeof_gr_complex, int_delay)
        self.frac_delayer = filter.mmse_resampler_cc(frac_delay, 1.0)
        #Frac delayer introduces a delay of 3
        self.frac_delayer_fix = blocks.delay(gr.sizeof_gr_complex, 3)
        self.tmp = filter.fir_filter_ccf(self.interp, [1.0])

        #Channel (3: cfo)
        self.cfo_source = analog.sig_source_c(1.0, analog.GR_COS_WAVE, self.cfo,
                1, 0)
        self.multiplicator = blocks.multiply_vcc(1)

        #Estimator
        self.preamble_detector = lora2.lora_preamble_detect(self.SF, 8)
        self.sof_detector = lora2.lora_detect_sof(self.SF)
        self.tags = lora2.store_tags()

        ##################################################
        # Connections
        ##################################################
        self.connect((self.syms_src, 0), (self.to_tagged, 0))
        self.connect((self.to_tagged, 0), (self.add_preamble, 0))
        self.connect((self.add_preamble, 0), (self.css_mod, 0))
        self.connect((self.css_mod, 0), (self.add_reversed_chirps, 0))
        self.connect((self.add_reversed_chirps, 0), (self.tag_gate, 0))

        self.connect((self.tag_gate, 0), (self.int_delayer, 0))
        self.connect((self.int_delayer, 0), (self.frac_delayer, 0))
        self.connect((self.frac_delayer, 0), (self.frac_delayer_fix, 0))
        self.connect((self.frac_delayer_fix, 0), (self.tmp, 0))
        self.connect((self.tmp, 0), (self.multiplicator, 0))
        self.connect((self.cfo_source, 0), (self.multiplicator, 1))
        self.connect((self.multiplicator, 0), (self.awgn_chan, 0))

        self.connect((self.awgn_chan, 0), (self.preamble_detector, 0))
        self.connect((self.preamble_detector, 0), (self.sof_detector, 0))
        self.connect((self.sof_detector, 0), (self.tags, 0))

if __name__ == "__main__":
    params = {
        'SF': 9,
        'interp': 2,
        'delay': 20.0,
        'cfo': 0.2/(2*2**9), #cfo/(interp*M)
        'n_syms_pkt': 89,
        'n_pkts': 1,
        'EbN0dB': 100,
    }
    M =  2**params['SF']

    save = False
    filename = 'LORA_CFO_DELAY_DETECT.json'

    tb = css_delay_track(params['SF'], params['cfo'], params['delay'], params['interp'],
            params['EbN0dB'], params['n_syms_pkt'], params['n_pkts'])
    tb.run()

    tags = tb.tags.get_tags()

    for ele in tags:
        print(str(ele.key) + ': ' + str(ele.value))

    if save:
        pass
        #results = {}
        #results['params'] = params
        #results['est_delays'] = est_delays.tolist()
        #results['est_cfos'] = est_cfos.tolist()

        #fid = open(filename, 'w')
        #json.dump(results, fid)
        #fid.close()
        #print('Results written in ' + filename + '.')
