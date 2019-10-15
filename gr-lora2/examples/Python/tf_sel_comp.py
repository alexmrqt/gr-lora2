from gnuradio import blocks
from gnuradio import gr

import numpy
import matplotlib.pyplot as plt

import os
import sys
sys.path.append(os.environ.get('GRC_HIER_PATH', os.path.expanduser('~/.grc_gnuradio')))
from grc_css_demod import grc_css_demod # grc-generated hier_block
from grc_css_demod_coh import grc_css_demod_coh  # grc-generated hier_block
from lora2 import css_mod

import channels

class ber_vs_ebn0_awgn(gr.top_block):
    """
    A class to simulate performance of a CSS transceiver over AWGN.
    """

    def __init__(self, M, n_syms, len_int, EbN0dB, channel):
        gr.top_block.__init__(self, "BER vs Eb/N0 AWGN")

        ##################################################
        # Variables
        ##################################################
        self.n_syms= n_syms

        noisevar=numpy.sqrt(float(M)/numpy.log2(M) * 10**(-EbN0dB/10.0))

        self.syms_vec = numpy.random.randint(0, M, n_syms)
        #self.syms_vec = numpy.random.randint(M/4, M-M/4, n_syms)

        ##################################################
        # Blocks
        ##################################################
        self.syms_src = blocks.vector_source_s(self.syms_vec, False)

        self.css_mod = css_mod(M, 1)

        self.awgn_chan = channels.awgn(noisevar)
        self.selective_chan = None
        if channel == 'proakis-b':
            self.selective_chan = channels.proakis_b()
        elif channel == 'basic-t-sel':
            self.selective_chan = channels.basic_t_sel(M)

        self.css_demod = grc_css_demod(M)
        self.css_demod_coh = grc_css_demod_coh(M, len_int)

        self.est_syms_sink = blocks.vector_sink_s()
        self.est_syms_coh_sink = blocks.vector_sink_s()

        ##################################################
        # Connections
        ##################################################

        self.connect((self.syms_src, 0), (self.css_mod, 0))

        if self.selective_chan is None:
            self.connect((self.css_mod, 0), (self.awgn_chan, 0))
        else:
            self.connect((self.css_mod, 0), (self.selective_chan, 0))
            self.connect((self.selective_chan, 0), (self.awgn_chan, 0))

        self.connect((self.awgn_chan, 0), (self.css_demod_coh, 0))
        self.connect((self.awgn_chan, 0), (self.css_demod, 0))

        self.connect((self.css_demod, 0), (self.est_syms_sink, 0))
        self.connect((self.css_demod_coh, 0), (self.est_syms_coh_sink, 0))

def do_simu(EbN0dB, n_simus, SF, n_syms, n_min_err, channel):
    M = 2**SF

    BER = numpy.zeros(len(EbN0dB))
    BER_coh = numpy.zeros(len(EbN0dB))

    for i in range(0, len(EbN0dB)):
        print("Eb/N0=" + str(EbN0dB[i]))

        n_err = 0
        n_err_coh = 0
        n_bits = 0
        for j in range(0, n_simus):
            tb = ber_vs_ebn0_awgn(M, n_syms, -1, EbN0dB[i], channel)
            tb.run()

            est_syms = tb.est_syms_sink.data()
            est_syms_coh = tb.est_syms_coh_sink.data()

            syms = tb.syms_vec[:len(est_syms)]

            for k in range(0, len(syms)):
                bits = [int(ele) for ele in list(numpy.binary_repr(syms[k], SF))]

                est_bits = [int(ele) for ele in list(numpy.binary_repr(est_syms[k], SF))]
                est_bits_coh = [int(ele) for ele in list(numpy.binary_repr(est_syms_coh[k], SF))]

                n_err += numpy.sum(numpy.abs(numpy.array(bits)-numpy.array(est_bits)))
                n_err_coh += numpy.sum(numpy.abs(numpy.array(bits)-numpy.array(est_bits_coh)))
                n_bits += len(bits)

            tb.est_syms_sink.reset()
            tb.est_syms_coh_sink.reset()

            if n_err_coh > n_min_err:
                break

        BER[i] = float(n_err)/n_bits
        BER_coh[i] = float(n_err_coh)/n_bits

    return {'uncoh': BER, 'coh': BER_coh}

def main():
    SF = 9                  #Spreading factor
    n_syms = 16384          #Number of symbols to be transmitted in a simulation
    n_simus = 10            #Max. number of simulations to perform
    n_min_err = 1000        #Minimum number of errors to be observed to stop the simulation
    EbN0dB = numpy.linspace(0, 10, 11) #Eb/N0 points to simulate
    #n_syms = 16
    #n_simus = 1
    #EbN0dB = numpy.array([100])

    print('Simulations over AWGN.')
    BER_awgn = do_simu(EbN0dB, n_simus, SF, n_syms, n_min_err, 'awgn')
    print('Simulations over Proakis B.')
    BER_proakis_b = do_simu(EbN0dB, n_simus, SF, n_syms, n_min_err, 'proakis-b')
    print('Simulations over basic time-selective channel.')
    BER_basic_t_sel = do_simu(EbN0dB, n_simus, SF, n_syms, n_min_err, 'basic-t-sel')

    #save data
    fid = open("EbN0dB.raw", "wb")
    EbN0dB.tofile(fid)
    fid.close()
    fid = open("BER.raw", "wb")
    BER_awgn['uncoh'].tofile(fid)
    fid = open("BER_coh.raw", "wb")
    BER_awgn['coh'].tofile(fid)
    fid = open("BER_f_chan.raw", "wb")
    BER_proakis_b['uncoh'].tofile(fid)
    fid = open("BER_coh_f_chan.raw", "wb")
    BER_proakis_b['coh'].tofile(fid)
    fid = open("BER_t_chan.raw", "wb")
    BER_basic_t_sel['uncoh'].tofile(fid)
    fid = open("BER_coh_t_chan.raw", "wb")
    BER_basic_t_sel['coh'].tofile(fid)
    fid.close()

    #Plot results
    plt.semilogy(EbN0dB, BER_awgn['uncoh'], '-+', label='Non coherent AWGN')
    plt.semilogy(EbN0dB, BER_awgn['coh'], '-x', label='Coherent AWGN')
    plt.semilogy(EbN0dB, BER_proakis_b['uncoh'], '--+', label='Non coherent Proakis B')
    plt.semilogy(EbN0dB, BER_proakis_b['coh'], '--x', label='Coherent Proakis B')
    plt.semilogy(EbN0dB, BER_basic_t_sel['uncoh'], '-.+', label='Non coherent t selective')
    plt.semilogy(EbN0dB, BER_basic_t_sel['coh'], '-.x', label='Coherent t selective')

    plt.grid(which='both')
    plt.ylabel('BER')
    plt.xlabel('Eb/N0 (dB)')

    axes = plt.gca()
    axes.set_ylim([1e-5, 0.5])
    plt.legend()
    plt.show()

if __name__ == '__main__':
    main()
