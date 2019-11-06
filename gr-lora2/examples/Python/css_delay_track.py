import pmt
import numpy
import json
from matplotlib import pyplot as plt

from gnuradio import filter
from gnuradio import blocks
from gnuradio import gr
from lora2 import css_mod
from lora2 import css_fine_delay_track
import channels

class css_delay_track(gr.top_block):
    def __init__(self, SF, delay, interp, B, EbN0dB, n_syms):
        gr.top_block.__init__(self, "CSS Delay Track")

        ##################################################
        # Variables
        ##################################################
        self.SF = SF

        delay = delay*interp
        self.interp = interp
        self.M = M = 2**self.SF

        self.syms_vec = numpy.random.randint(0, M, n_syms)
        noisevar = float(M)/numpy.log2(M) * 10**(-EbN0dB/10.0) * interp

        ##################################################
        # Blocks
        ##################################################
        #Modulator
        self.syms_src = blocks.vector_source_s(self.syms_vec, False)
        self.css_mod = css_mod(M, interp)

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

        #Delay Estimator
        self.delay_track = css_fine_delay_track(self.M, interp, B)
        self.delay_sink = blocks.vector_sink_f()

        ##################################################
        # Connections
        ##################################################
        self.connect((self.syms_src, 0), (self.css_mod, 0))
        self.connect((self.css_mod, 0), (self.tag_gate, 0))

        self.connect((self.tag_gate, 0), (self.int_delayer, 0))
        self.connect((self.int_delayer, 0), (self.frac_delayer, 0))
        self.connect((self.frac_delayer, 0), (self.frac_delayer_fix, 0))
        self.connect((self.frac_delayer_fix, 0), (self.awgn_chan, 0))

        self.connect((self.awgn_chan, 0), (self.delay_track, 0))
        self.connect((self.delay_track, 0), (self.delay_sink, 0))

if __name__ == "__main__":
    params = {
        'SF': 9,
        'interp': 4,
        'n_syms': 100,
        'delay': 2.0/4,
        'B': 0.4,
        'EbN0dB': 100,
    }
    M =  2**params['SF']

    save = False
    filename = 'CSS_DELAY_TRACK.json'

    est_delays = numpy.zeros(params['n_syms'])
    tb = css_delay_track(params['SF'], params['delay'], params['interp'],
            params['B'], params['EbN0dB'], params['n_syms'])
    tb.run()

    est_delays = tb.delay_sink.data()

    if save:
        results = {}
        results['params'] = params
        results['est_delays'] = est_delays.tolist()

        fid = open(filename, 'w')
        json.dump(results, fid)
        fid.close()
        print('Results written in ' + filename + '.')

    plt.plot(numpy.array(est_delays)/params['interp'], '-x')
    plt.plot(params['delay']*numpy.ones(params['n_syms']), '--')

    plt.grid(which='both')
    plt.ylim([-1.0, 1.0])
    plt.xlabel('Normalized Delay')
    plt.ylabel('Symbol Index')

    plt.show()
