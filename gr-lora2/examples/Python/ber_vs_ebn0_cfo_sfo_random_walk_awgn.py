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

    def __init__(self, M, max_cfo, sigma2_cfo, max_sfo, sigma2_sfo, EbN0dB,\
            B_cfo, B_delay, interp, n_syms, seed_cfo, seed_sfo):
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
        self.cfo = gr_chan.cfo_model(1.0, sigma2_cfo, max_cfo, seed_cfo)

        #Channel (3: sfo)
        self.sfo = gr_chan.sro_model(1.0, sigma2_sfo, max_sfo, seed_sfo)
        self.frac_delayer_fix = blocks.delay(gr.sizeof_gr_complex, 3)

        self.css_demod = css_demod(M, 0.0, 0.0, interp)
        #self.css_demod = grc_css_demod(M)
        self.css_demod_sfo = css_demod(M, B_cfo, B_delay, interp)
        self.css_demod_nosfocfo = css_demod(M, 0.0, 0.0, interp)
        self.css_demod_nosfo = css_demod(M, B_cfo, 0.0, interp)
        self.css_demod_nocfo = css_demod(M, 0.0, B_delay, interp)

        self.est_syms_sink = blocks.vector_sink_s()
        self.spectrum_sink1 = blocks.null_sink(gr.sizeof_gr_complex*M)
        self.cfo_err_sink1= blocks.null_sink(4)
        self.delay_err_sink1= blocks.null_sink(4)

        self.est_syms_sfo_sink = blocks.vector_sink_s()
        self.spectrum_sink2 = blocks.null_sink(gr.sizeof_gr_complex*M)
        self.cfo_err_sink2= blocks.null_sink(4)
        self.delay_err_sink2= blocks.null_sink(4)

        self.est_syms_nosfocfo_sink = blocks.vector_sink_s()
        self.spectrum_sink3 = blocks.null_sink(gr.sizeof_gr_complex*M)
        self.cfo_err_sink3= blocks.null_sink(4)
        self.delay_err_sink3= blocks.null_sink(4)

        self.est_syms_nosfo_sink = blocks.vector_sink_s()
        self.spectrum_sink4 = blocks.null_sink(gr.sizeof_gr_complex*M)
        self.cfo_err_sink4= blocks.null_sink(4)
        self.delay_err_sink4= blocks.null_sink(4)

        self.est_syms_nocfo_sink = blocks.vector_sink_s()
        self.spectrum_sink5 = blocks.null_sink(gr.sizeof_gr_complex*M)
        self.cfo_err_sink5= blocks.null_sink(4)
        self.delay_err_sink5= blocks.null_sink(4)

        ##################################################
        # Connections
        ##################################################

        self.connect((self.syms_src, 0), (self.css_mod, 0))

        self.connect((self.css_mod, 0), (self.awgn_chan, 0))
        self.connect((self.awgn_chan, 0), (self.cfo, 0))
        self.connect((self.cfo, 0), (self.sfo, 0))
        self.connect((self.sfo, 0), (self.frac_delayer_fix, 0))

        self.connect((self.awgn_chan, 0), (self.css_demod_nosfocfo, 0))

        self.connect((self.frac_delayer_fix, 0), (self.css_demod, 0))
        self.connect((self.frac_delayer_fix, 0), (self.css_demod_sfo, 0))
        self.connect((self.frac_delayer_fix, 0), (self.css_demod_nosfo, 0))
        self.connect((self.frac_delayer_fix, 0), (self.css_demod_nocfo, 0))

        self.connect((self.css_demod, 0), (self.est_syms_sink, 0))
        self.connect((self.css_demod, 1), (self.spectrum_sink1, 0))
        self.connect((self.css_demod, 2), (self.cfo_err_sink1, 0))
        self.connect((self.css_demod, 3), (self.delay_err_sink1, 0))

        self.connect((self.css_demod_sfo, 0), (self.est_syms_sfo_sink, 0))
        self.connect((self.css_demod_sfo, 1), (self.spectrum_sink2, 0))
        self.connect((self.css_demod_sfo, 2), (self.cfo_err_sink2, 0))
        self.connect((self.css_demod_sfo, 3), (self.delay_err_sink2, 0))

        self.connect((self.css_demod_nosfocfo, 0), (self.est_syms_nosfocfo_sink, 0))
        self.connect((self.css_demod_nosfocfo, 1), (self.spectrum_sink3, 0))
        self.connect((self.css_demod_nosfocfo, 2), (self.cfo_err_sink3, 0))
        self.connect((self.css_demod_nosfocfo, 3), (self.delay_err_sink3, 0))

        self.connect((self.css_demod_nosfo, 0), (self.est_syms_nosfo_sink, 0))
        self.connect((self.css_demod_nosfo, 1), (self.spectrum_sink4, 0))
        self.connect((self.css_demod_nosfo, 2), (self.cfo_err_sink4, 0))
        self.connect((self.css_demod_nosfo, 3), (self.delay_err_sink4, 0))

        self.connect((self.css_demod_nocfo, 0), (self.est_syms_nocfo_sink, 0))
        self.connect((self.css_demod_nocfo, 1), (self.spectrum_sink5, 0))
        self.connect((self.css_demod_nocfo, 2), (self.cfo_err_sink5, 0))
        self.connect((self.css_demod_nocfo, 3), (self.delay_err_sink5, 0))

def plot(EbN0dB, BER, BER_sfo, BER_nosfocfo, BER_nosfo, BER_nocfo):
    plt.clf()

    #Plot results
    plt.semilogy(EbN0dB, BER, '-x', label="Without CFO + Delay tracking")
    plt.semilogy(EbN0dB, BER_sfo, '-x', label="With CFO + Delay tracking")
    plt.semilogy(EbN0dB, BER_nosfo, '-x', label="With CFO tracking")
    plt.semilogy(EbN0dB, BER_nocfo, '-x', label="With Delay tracking")
    plt.semilogy(EbN0dB, BER_nosfocfo, '-+', label="No SFO, No CFO")

    plt.grid(which='both')
    plt.ylabel('BER')
    plt.xlabel('Eb/N0 (dB)')

    axes = plt.gca()
    axes.set_ylim([1e-5, 0.5])
    plt.legend()
    plt.pause(0.1)

def main():
    params = {
        'SF': 9,
        'B_cfo': 0.35,
        'B_delay': 0.3,
        'interp': 8,
        #'n_syms': 16384,
        #'n_simus': 100,
        'n_syms': 227,
        'n_simus': 10,
        #'n_min_err': 1000,
        'max_sfo': 0.01,
        'sigma2_sfo': 1.0e-7,
        #'max_sfo': 0.0,
        #'sigma2_sfo': 0.0,
        'max_cfo': 1.0,
        'sigma2_cfo': 5.0e-6,
        #'max_cfo': 0.0,
        #'sigma2_cfo': 0.0,
        'seed_cfo': numpy.random.randint(0, 255),
        'seed_sfo': numpy.random.randint(0, 255),
    }
    EbN0dB = numpy.arange(0, 8)
    M = 2**params['SF']

    save = False
    filename = 'BER_CFO_SFO_RANDOM_WALK.json'

    BER = numpy.zeros(len(EbN0dB))          #No tracking
    BER_sfo = numpy.zeros(len(EbN0dB))      #Tracking
    BER_nosfocfo = numpy.zeros(len(EbN0dB))    #No SFO
    BER_nocfo = numpy.zeros(len(EbN0dB))
    BER_nosfo = numpy.zeros(len(EbN0dB))

    #Simu
    for i in range(0, len(EbN0dB)):
        print("Eb/N0=" + str(EbN0dB[i]))

        n_err = 0
        n_err_sfo = 0
        n_err_nosfocfo = 0
        n_err_nosfo = 0
        n_err_nocfo = 0
        n_tot_bits = 0

        for j in range(0, params['n_simus']):
            print(j)
            tb = ber_vs_ebn0_awgn(M, params['max_cfo'], params['sigma2_cfo'],
                    params['max_sfo'], params['sigma2_sfo'],
                    EbN0dB[i], params['B_cfo'], params['B_delay'],
                    params['interp'], params['n_syms'], params['seed_cfo'],
                    params['seed_cfo'])
            tb.run()

            syms = tb.syms_vec
            est_syms = tb.est_syms_sink.data()
            est_syms_sfo = tb.est_syms_sfo_sink.data()
            est_syms_nosfocfo = tb.est_syms_nosfocfo_sink.data()
            est_syms_nocfo = tb.est_syms_nocfo_sink.data()
            est_syms_nosfo = tb.est_syms_nosfo_sink.data()

            n_syms = min(len(est_syms), len(est_syms_sfo), len(est_syms_nosfocfo))
            for k in range(0, n_syms):
                bits = [int(ele) for ele in list(numpy.binary_repr(syms[k], params['SF']))]

                est_bits = [int(ele) for ele in list(numpy.binary_repr(est_syms[k], params['SF']))]
                est_bits_sfo = [int(ele) for ele in list(numpy.binary_repr(est_syms_sfo[k], params['SF']))]
                est_bits_nosfocfo = [int(ele) for ele in list(numpy.binary_repr(est_syms_nosfocfo[k], params['SF']))]
                est_bits_nocfo = [int(ele) for ele in list(numpy.binary_repr(est_syms_nocfo[k], params['SF']))]
                est_bits_nosfo = [int(ele) for ele in list(numpy.binary_repr(est_syms_nosfo[k], params['SF']))]

                n_tot_bits += len(est_bits)
                n_err += numpy.sum(numpy.abs(numpy.array(bits)-numpy.array(est_bits)))
                n_err_sfo += numpy.sum(numpy.abs(numpy.array(bits)-numpy.array(est_bits_sfo)))
                n_err_nosfocfo += numpy.sum(numpy.abs(numpy.array(bits)-numpy.array(est_bits_nosfocfo)))
                n_err_nocfo += numpy.sum(numpy.abs(numpy.array(bits)-numpy.array(est_bits_nocfo)))
                n_err_nosfo += numpy.sum(numpy.abs(numpy.array(bits)-numpy.array(est_bits_nosfo)))

            BER[i] = float(n_err)/n_tot_bits
            BER_sfo[i] = float(n_err_sfo)/n_tot_bits
            BER_nosfocfo[i] = float(n_err_nosfocfo)/n_tot_bits
            BER_nocfo[i] = float(n_err_nocfo)/n_tot_bits
            BER_nosfo[i] = float(n_err_nosfo)/n_tot_bits

            plot(EbN0dB, BER, BER_sfo, BER_nosfocfo, BER_nosfo, BER_nocfo)

            #if (n_err_sfo > params['n_min_err']) \
            #        and (n_err_nocfo > params['n_min_err']) \
            #        and (n_err_nosfo > params['n_min_err']) \
            #        and (n_err_nosfocfo > params['n_min_err']):
            #    break

            if j == (params['n_simus']-1):
                #print('Maximum number of simulations reached with ' + str(min(n_err, n_err_cfo)) + ' errors!')
                print('Maximum number of simulations reached!')

            tb.est_syms_sink.reset()
            tb.est_syms_sfo_sink.reset()
            tb.est_syms_nosfocfo_sink.reset()
            tb.est_syms_nocfo_sink.reset()
            tb.est_syms_nosfo_sink.reset()

    #save data
    if save:
        results = {}
        results['params'] = params
        results['EbN0dB'] = EbN0dB.tolist()

        results['BER'] = BER.tolist()
        results['BER_sfo'] = BER_sfo.tolist()
        results['BER_nosfocfo'] = BER_nosfocfo.tolist()
        results['BER_nocfo'] = BER_nosfocfo.tolist()
        results['BER_nosfo'] = BER_nosfocfo.tolist()

        fid = open(filename, 'w')
        json.dump(results, fid)
        fid.close()
        print('Results written in ' + filename + '.')

    print('Appuyez sur une touche pour fermer.')
    input()

if __name__ == '__main__':
    main()


