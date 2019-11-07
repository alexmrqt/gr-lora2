import json
from gnuradio import channels as gr_chan
from gnuradio import blocks
from gnuradio import gr

import numpy
import matplotlib.pyplot as plt

import os
import sys
sys.path.append(os.environ.get('GRC_HIER_PATH', os.path.expanduser('~/.grc_gnuradio')))

from lora2 import css_mod
from lora2 import css_demod
import channels

class ber_vs_ebn0_awgn(gr.top_block):

    def __init__(self, M, max_cfo, sigma2_cfo, EbN0dB, B_cfo, n_syms):
        gr.top_block.__init__(self, "BER vs Eb/N0 AWGN")

        ##################################################
        # Variables
        ##################################################
        self.n_syms= n_syms

        noisevar = numpy.sqrt(float(M)/numpy.log2(M) * 10**(-EbN0dB/10.0))

        self.syms_vec = numpy.random.randint(0, M, n_syms)

        ##################################################
        # Blocks
        ##################################################
        self.syms_src = blocks.vector_source_s(self.syms_vec, False)

        self.css_mod = css_mod(M)

        #Channel (1: noise)
        self.awgn_chan = channels.awgn(noisevar)

        #Channel (2: cfo)
        self.cfo = gr_chan.cfo_model(1.0, sigma2_cfo, max_cfo, numpy.random.randint(0, 255))

        self.css_demod = css_demod(M, 0.0, 0.0, 1)
        #self.css_demod = grc_css_demod(M)
        self.css_demod_cfo = css_demod(M, B_cfo, 0.0, 1)
        self.css_demod_nocfo = css_demod(M, 0.0, 0.0, 1)

        self.est_syms_sink = blocks.vector_sink_s()
        self.spectrum_sink1 = blocks.null_sink(gr.sizeof_gr_complex*M)
        self.cfo_err_sink1= blocks.null_sink(4)
        self.delay_err_sink1= blocks.null_sink(4)

        self.est_syms_cfo_sink = blocks.vector_sink_s()
        self.spectrum_sink2 = blocks.null_sink(gr.sizeof_gr_complex*M)
        self.cfo_err_sink2= blocks.null_sink(4)
        self.delay_err_sink2= blocks.null_sink(4)

        self.est_syms_nocfo_sink = blocks.vector_sink_s()
        self.spectrum_sink3 = blocks.null_sink(gr.sizeof_gr_complex*M)
        self.cfo_err_sink3= blocks.null_sink(4)
        self.delay_err_sink3= blocks.null_sink(4)

        ##################################################
        # Connections
        ##################################################

        self.connect((self.syms_src, 0), (self.css_mod, 0))

        self.connect((self.css_mod, 0), (self.awgn_chan, 0))
        self.connect((self.awgn_chan, 0), (self.cfo, 0))

        self.connect((self.awgn_chan, 0), (self.css_demod_nocfo, 0))

        self.connect((self.cfo, 0), (self.css_demod, 0))
        self.connect((self.cfo, 0), (self.css_demod_cfo, 0))

        self.connect((self.css_demod, 0), (self.est_syms_sink, 0))
        self.connect((self.css_demod, 1), (self.spectrum_sink1, 0))
        self.connect((self.css_demod, 2), (self.cfo_err_sink1, 0))
        self.connect((self.css_demod, 3), (self.delay_err_sink1, 0))

        self.connect((self.css_demod_cfo, 0), (self.est_syms_cfo_sink, 0))
        self.connect((self.css_demod_cfo, 1), (self.spectrum_sink2, 0))
        self.connect((self.css_demod_cfo, 2), (self.cfo_err_sink2, 0))
        self.connect((self.css_demod_cfo, 3), (self.delay_err_sink2, 0))

        self.connect((self.css_demod_nocfo, 0), (self.est_syms_nocfo_sink, 0))
        self.connect((self.css_demod_nocfo, 1), (self.spectrum_sink3, 0))
        self.connect((self.css_demod_nocfo, 2), (self.cfo_err_sink3, 0))
        self.connect((self.css_demod_nocfo, 3), (self.delay_err_sink3, 0))

def main():
    params = {
        'SF': 9,
        'B_cfo': 0.4,
        #'n_syms': 16384,
        #'n_simus': 100,
        'n_syms': 1024,
        'n_simus': 10,
        'n_min_err': 1000,
        'max_cfo': 1.0,
        'sigma2_cfo': 0.4/2**18,
    }
    EbN0dB = numpy.linspace(0, 10, 11)
    M = 2**params['SF']

    save = False
    filename = 'BER_CFO_RANDOM_WALK.json'

    BER = numpy.zeros(len(EbN0dB))          #No tracking
    BER_cfo = numpy.zeros(len(EbN0dB))      #Tracking
    BER_nocfo = numpy.zeros(len(EbN0dB))    #No CFO

    #Simu
    for i in range(0, len(EbN0dB)):
        print("Eb/N0=" + str(EbN0dB[i]))

        n_err = 0
        n_err_cfo = 0
        n_err_nocfo = 0
        n_tot_bits = 0

        for j in range(0, params['n_simus']):
            tb = ber_vs_ebn0_awgn(M, params['max_cfo'], params['sigma2_cfo'],
                    EbN0dB[i], params['B_cfo'], params['n_syms'])
            tb.run()

            syms = tb.syms_vec
            est_syms = tb.est_syms_sink.data()
            est_syms_cfo = tb.est_syms_cfo_sink.data()
            est_syms_nocfo = tb.est_syms_nocfo_sink.data()

            for k in range(0, len(syms)):
                bits = [int(ele) for ele in list(numpy.binary_repr(syms[k], params['SF']))]

                est_bits = [int(ele) for ele in list(numpy.binary_repr(est_syms[k], params['SF']))]
                est_bits_cfo = [int(ele) for ele in list(numpy.binary_repr(est_syms_cfo[k], params['SF']))]
                est_bits_nocfo = [int(ele) for ele in list(numpy.binary_repr(est_syms_nocfo[k], params['SF']))]

                n_tot_bits += len(est_bits)
                n_err += numpy.sum(numpy.abs(numpy.array(bits)-numpy.array(est_bits)))
                n_err_cfo += numpy.sum(numpy.abs(numpy.array(bits)-numpy.array(est_bits_cfo)))
                n_err_nocfo += numpy.sum(numpy.abs(numpy.array(bits)-numpy.array(est_bits_nocfo)))

            if (n_err > params['n_min_err']) \
                    and (n_err_cfo > params['n_min_err']) \
                    and (n_err_nocfo > params['n_min_err']):
                break

            if j == (params['n_simus']-1):
                #print('Maximum number of simulations reached with ' + str(min(n_err, n_err_cfo)) + ' errors!')
                print('Maximum number of simulations reached!')

            tb.est_syms_sink.reset()
            tb.est_syms_cfo_sink.reset()
            tb.est_syms_nocfo_sink.reset()

        BER[i] = float(n_err)/n_tot_bits
        BER_cfo[i] = float(n_err_cfo)/n_tot_bits
        BER_nocfo[i] = float(n_err_nocfo)/n_tot_bits

    #save data
    if save:
        results = {}
        results['params'] = params
        results['EbN0dB'] = EbN0dB.tolist()

        fid = open(filename, 'w')
        results['BER'] = BER.tolist()
        results['BER_cfo'] = BER_cfo.tolist()
        results['BER_nocfo'] = BER_nocfo.tolist()
        json.dump(results, fid)
        fid.close()
        print('Results written in ' + filename + '.')

    #Plot results
    plt.semilogy(EbN0dB, BER, '-x', label="Without CFO tracking")
    plt.semilogy(EbN0dB, BER_cfo, '-x', label="With CFO tracking")
    plt.semilogy(EbN0dB, BER_nocfo, '-+', label="No CFO")

    plt.grid(which='both')
    plt.ylabel('BER')
    plt.xlabel('Eb/N0 (dB)')

    axes = plt.gca()
    axes.set_ylim([1e-5, 0.5])
    plt.legend()
    plt.show()

if __name__ == '__main__':
    main()

