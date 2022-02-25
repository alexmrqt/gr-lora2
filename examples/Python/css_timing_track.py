import numpy
import json
from matplotlib import pyplot as plt

from gnuradio import filter
from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr
from lora2 import css_mod
from lora2 import css_timing_err_track
import channels

class css_delay_est(gr.top_block):
    def __init__(self, SF, delay, EbN0dB, B, quant, n_syms):
        gr.top_block.__init__(self, "CSS Timing Estimator")

        ##################################################
        # Variables
        ##################################################
        self.SF = SF
        self.delay = delay

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
        delay_int = int(numpy.floor(self.delay))
        delay_float = self.delay - delay_int

        self.frac_delayer = filter.fractional_interpolator_cc(delay_float, 1.0)
        if delay_int > 0:
            self.int_delayer = blocks.delay(gr.sizeof_gr_complex, delay_int)
        else:
            self.int_delayer = blocks.skiphead(gr.sizeof_gr_complex, -delay_int)

        #Channel (2: cfo compensator)
        self.cfo_comp = analog.sig_source_c(1.0, analog.GR_COS_WAVE,
                self.delay/self.M, 1, 0)
        self.multiplicator = blocks.multiply_vcc(1)

        #Delay Estimator
        self.delay_track = css_timing_err_track(self.M, B, quant)
        self.delay_sink = blocks.vector_sink_f()

        ##################################################
        # Connections
        ##################################################
        self.connect((self.syms_src, 0), (self.css_mod, 0))
        self.connect((self.css_mod, 0), (self.tag_gate, 0))

        self.connect((self.tag_gate, 0), (self.int_delayer, 0))
        if numpy.abs(delay_float) > 1e-2:
            self.connect((self.int_delayer, 0), (self.frac_delayer, 0))
            self.connect((self.frac_delayer, 0), (self.multiplicator, 0))
        else:
            self.connect((self.int_delayer, 0), (self.multiplicator, 0))
        self.connect((self.cfo_comp, 0), (self.multiplicator, 1))
        self.connect((self.multiplicator, 0), (self.awgn_chan, 0))

        self.connect((self.awgn_chan, 0), (self.delay_track, 0))
        self.connect((self.delay_track, 0), (self.delay_sink, 0))

if __name__ == "__main__":
    params = {
        'SF': 9,
        'n_syms': 10,
        'delay': -2**9/8,
        'frac_delay': 0.0,
        'EbN0dB': 100,
        'B': 0.3,
        'quant': 1,
    }
    M =  2**params['SF']

    save = False
    filename = 'CSS_TIMING_ERR_TRACK.json'

    tb = css_delay_est(params['SF'], params['delay'] + params['frac_delay'],
            params['EbN0dB'], params['B'], params['quant'], params['n_syms'])
    print(tb.syms_vec)
    print('')
    tb.run()

    est_delays = tb.delay_sink.data()

    if save:
        results = {}
        results['params'] = params
        results['est_delays'] = est_delays

        fid = open(filename, 'w')
        json.dump(results, fid)
        fid.close()
        print('Results written in ' + filename + '.')

    plt.plot(numpy.arange(0, params['n_syms']),
            numpy.round((params['delay'] + params['frac_delay']))*numpy.ones(params['n_syms']),
            '--')
    plt.plot(est_delays, '-')

    plt.grid(which='both')
    plt.xlabel('Symbol index')
    plt.ylabel('Estimated delay')
    plt.xlim([0, params['n_syms']])
    plt.ylim([-M/2, M/2])

    plt.show()
