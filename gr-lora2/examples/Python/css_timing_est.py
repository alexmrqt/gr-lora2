import pmt
import numpy
import json
from matplotlib import pyplot as plt

from gnuradio import analog
from gnuradio import filter
from gnuradio import blocks
from gnuradio import gr
from lora2 import css_mod
from lora2 import css_timing_err_detector
import channels

class css_delay_est(gr.top_block):
    def __init__(self, SF, delay, EbN0dB, n_syms, algo):
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
                -self.delay/self.M, 1, 0)
        self.multiplicator = blocks.multiply_vcc(1)

        #Delay Estimator
        self.delay_est = css_timing_err_detector(self.M, algo)
        self.msg_debug = blocks.message_debug()

        ##################################################
        # Connections
        ##################################################
        self.connect((self.syms_src, 0), (self.css_mod, 0))
        self.connect((self.css_mod, 0), (self.tag_gate, 0))

        self.connect((self.tag_gate, 0), (self.int_delayer, 0))
        self.connect((self.int_delayer, 0), (self.frac_delayer, 0))
        self.connect((self.frac_delayer, 0), (self.awgn_chan, 0))

        self.connect((self.awgn_chan, 0), (self.multiplicator, 0))
        self.connect((self.cfo_comp, 0), (self.multiplicator, 1))
        self.connect((self.multiplicator, 0), (self.delay_est, 0))
        self.msg_connect((self.delay_est, pmt.intern('time')),
                (self.msg_debug, pmt.intern('store')))

if __name__ == "__main__":
    params = {
        'SF': 9,
        'n_syms': 5,
        'EbN0dB': 100,
        'algo': 4,
    }
    M =  2**params['SF']
    #delays = numpy.linspace(-0.5, 0.5, 20)
    delays = numpy.linspace(-M/2, M/2, 50)

    save = False
    filename = 'CSS_DELAY_EST.json'

    est_delays = numpy.zeros(len(delays))
    for i in range(0, len(delays)):
        print('CFO: ' + str(delays[i]))

        #if delays[i] < 0:
        #    delay = delays[i] + 1.0
        #else:
        #    delay = delays[i]
        tb = css_delay_est(params['SF'], delays[i], params['EbN0dB'], params['n_syms'], params['algo'])
        tb.run()

        est_delays[i] = pmt.to_python(tb.msg_debug.get_message(0))

    if save:
        results = {}
        results['params'] = params
        results['delays'] = delays.tolist()
        results['est_delays'] = est_delays.tolist()

        fid = open(filename, 'w')
        json.dump(results, fid)
        fid.close()
        print('Results written in ' + filename + '.')

    plt.plot(delays, est_delays, '-x')

    plt.grid(which='both')
    plt.xlabel('Normalized Delay')
    plt.ylabel('Estimated Delay')

    plt.show()

