import pmt
import numpy
import json
from matplotlib import pyplot as plt

from gnuradio import filter
from gnuradio import blocks
from gnuradio import gr
from lora2 import css_mod
from lora2 import css_fine_sfo_detector
import channels

class css_sfo_est(gr.top_block):
    def __init__(self, SF, sfo, EbN0dB, n_syms):
        gr.top_block.__init__(self, "CSS SFO Estimator")

        ##################################################
        # Variables
        ##################################################
        self.SF = SF
        self.sfo = sfo

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

        #Channel (2: sfo)
        self.sfo = filter.fractional_interpolator_cc(1.0, 1.0 + sfo)

        #SFO Estimator
        self.sfo_est = css_fine_sfo_detector(self.M, 3)
        self.msg_debug = blocks.message_debug()

        ##################################################
        # Connections
        ##################################################
        self.connect((self.syms_src, 0), (self.css_mod, 0))
        self.connect((self.css_mod, 0), (self.tag_gate, 0))

        self.connect((self.tag_gate, 0), (self.sfo, 0))
        self.connect((self.sfo, 0), (self.awgn_chan, 0))

        self.connect((self.awgn_chan, 0), (self.sfo_est, 0))
        self.msg_connect((self.sfo_est, pmt.intern('sfo')),
                (self.msg_debug, pmt.intern('store')))

if __name__ == "__main__":
    params = {
        'SF': 9,
        'n_syms': 3,
        'EbN0dB': 20,
    }
    M =  2**params['SF']
    sfos = numpy.linspace(-0.1/M, 0.1/M, 100)

    save = False
    filename = 'CSS_SFO_EST.json'

    est_sfos = numpy.zeros(len(sfos))
    for i in range(0, len(sfos)):
        print('SFO: ' + str(sfos[i]))

        tb = css_sfo_est(params['SF'], sfos[i], params['EbN0dB'], params['n_syms'])
        tb.run()

        est_sfos[i] = pmt.to_python(tb.msg_debug.get_message(0))

    if save:
        results = {}
        results['params'] = params
        results['sfos'] = sfos.tolist()
        results['est_sfos'] = est_sfos.tolist()

        fid = open(filename, 'w')
        json.dump(results, fid)
        fid.close()
        print('Results written in ' + filename + '.')

    plt.plot(sfos, est_sfos, '-x')

    plt.grid(which='both')
    plt.xlabel('Normalized SFO')
    plt.ylabel('Estimated SFO')

    plt.show()

