import numpy
import json
from matplotlib import pyplot as plt

from gnuradio import filter
from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr
from lora2 import css_mod
from lora2 import css_fine_cfo_track
import channels

class css_cfo_est(gr.top_block):
    def __init__(self, SF, cfo, delay, interp, EbN0dB, B, n_syms):
        gr.top_block.__init__(self, "CSS CFO Estimator")

        ##################################################
        # Variables
        ##################################################
        self.SF = SF
        self.cfo = cfo

        self.interp = 1
        self.M = M = 2**self.SF

        self.syms_vec = numpy.random.randint(0, M, n_syms)
        noisevar = float(M)/numpy.log2(M) * 10**(-EbN0dB/10.0)

        ##################################################
        # Blocks
        ##################################################
        #Modulator
        self.syms_src = blocks.vector_source_s(self.syms_vec, False)
        self.css_mod = css_mod(M, 1)

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

        #Channel (3: cfo)
        self.cfo_source = analog.sig_source_c(1.0, analog.GR_COS_WAVE, self.cfo,
                1, 0)
        self.multiplicator = blocks.multiply_vcc(1)

        #CFO Estimator
        self.cfo_track = css_fine_cfo_track(self.M, B)
        self.cfo_sink = blocks.vector_sink_f()

        ##################################################
        # Connections
        ##################################################
        self.connect((self.syms_src, 0), (self.css_mod, 0))
        self.connect((self.css_mod, 0), (self.tag_gate, 0))

        self.connect((self.tag_gate, 0), (self.int_delayer, 0))
        self.connect((self.int_delayer, 0), (self.frac_delayer, 0))
        self.connect((self.frac_delayer, 0), (self.frac_delayer_fix, 0))
        self.connect((self.frac_delayer_fix, 0), (self.multiplicator, 0))
        self.connect((self.cfo_source, 0), (self.multiplicator, 1))
        self.connect((self.multiplicator, 0), (self.awgn_chan, 0))

        self.connect((self.awgn_chan, 0), (self.cfo_track, 0))
        self.connect((self.cfo_track, 0), (self.cfo_sink, 0))

if __name__ == "__main__":
    params = {
        'SF': 9,
        'interp': 4,
        'delay': 1.0/4,
        'cfo': 0.4/2**9,
        'n_syms': 100,
        'EbN0dB': 10,
        'B': 0.40,
    }
    M =  2**params['SF']

    save = False
    filename = 'CSS_CFO_TRACK_B_'+ str(params['B'])[2:] +'.json'

    tb = css_cfo_est(params['SF'], params['cfo'], params['delay'],
            params['interp'], params['EbN0dB'], params['B'], params['n_syms'])
    tb.run()

    est_cfos = tb.cfo_sink.data()

    if save:
        results = {}
        results['params'] = params
        results['est_cfos'] = est_cfos

        fid = open(filename, 'w')
        json.dump(results, fid)
        fid.close()
        print('Results written in ' + filename + '.')

    plt.plot(numpy.arange(0, params['n_syms']), params['cfo']*numpy.ones(params['n_syms']), '--')
    plt.plot(est_cfos, '-')

    plt.grid(which='both')
    plt.xlabel('Symbol index')
    plt.ylabel('Estimated CFO')
    plt.xlim([0, params['n_syms']])
    #plt.ylim([-0.5/M, 0.5/M])

    plt.show()
