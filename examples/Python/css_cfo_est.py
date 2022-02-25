import pmt
import numpy
import json
from matplotlib import pyplot as plt

from gnuradio import analog
from gnuradio import filter
from gnuradio import blocks
from gnuradio import gr
from lora2 import css_mod
from lora2 import css_fine_cfo_detector
import channels

class css_cfo_est(gr.top_block):
    def __init__(self, SF, cfo, delay, interp, EbN0dB, n_syms):
        gr.top_block.__init__(self, "CSS CFO Estimator")

        ##################################################
        # Variables
        ##################################################
        self.SF = SF
        self.cfo = cfo

        self.interp = interp
        delay = delay*interp
        self.M = M = 2**self.SF

        self.syms_vec = numpy.random.randint(0, M, n_syms)
        noisevar = float(M)/numpy.log2(M) * 10**(-EbN0dB/10.0)

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

        #Channel (3: cfo)
        self.cfo_source = analog.sig_source_c(1.0, analog.GR_COS_WAVE, self.cfo,
                1, 0)
        self.multiplicator = blocks.multiply_vcc(1)

        #CFO Estimator
        self.decim = filter.fir_filter_ccf(interp, [1.0])
        self.cfo_est = css_fine_cfo_detector(self.M)
        self.msg_debug = blocks.message_debug()

        ##################################################
        # Connections
        ##################################################
        self.connect((self.syms_src, 0), (self.css_mod, 0))
        self.connect((self.css_mod, 0), (self.tag_gate, 0))

        self.connect((self.tag_gate, 0), (self.int_delayer, 0))
        self.connect((self.int_delayer, 0), (self.frac_delayer, 0))
        self.connect((self.frac_delayer, 0), (self.frac_delayer_fix, 0))
        self.connect((self.frac_delayer_fix, 0), (self.decim, 0))
        self.connect((self.decim, 0), (self.multiplicator, 0))
        self.connect((self.cfo_source, 0), (self.multiplicator, 1))
        self.connect((self.multiplicator, 0), (self.awgn_chan, 0))

        self.connect((self.awgn_chan, 0), (self.cfo_est, 0))
        self.msg_connect((self.cfo_est, pmt.intern('cfo')),
                (self.msg_debug, pmt.intern('store')))

if __name__ == "__main__":
    params = {
        'SF': 9,
        'interp': 4,
        'delay': 2.0/4,
        'n_syms': 10,
        'EbN0dB': 100,
    }
    M =  2**params['SF']
    cfos = numpy.linspace(-0.5/M, 0.5/M, 100)

    save = True
    filename = 'CSS_CFO_EST_W_DELAY2.json'

    est_cfos = numpy.zeros(len(cfos))
    for i in range(0, len(cfos)):
        print('CFO: ' + str(cfos[i]))

        tb = css_cfo_est(params['SF'], cfos[i], params['delay'], params['interp'], params['EbN0dB'], params['n_syms'])
        tb.run()

        est_cfos[i] = 0.0
        for j in range(0, tb.msg_debug.num_messages()):
            est_cfos[i] += pmt.to_python(tb.msg_debug.get_message(j))
        est_cfos[i] /= tb.msg_debug.num_messages()

    if save:
        results = {}
        results['params'] = params
        results['cfos'] = cfos.tolist()
        results['est_cfos'] = est_cfos.tolist()

        fid = open(filename, 'w')
        json.dump(results, fid)
        fid.close()
        print('Results written in ' + filename + '.')

    plt.plot(cfos, est_cfos, '-x')
    plt.plot(cfos, cfos, '--')

    plt.grid(which='both')
    plt.xlabel('Normalized CFO')
    plt.ylabel('Estimated CFO')

    plt.show()
