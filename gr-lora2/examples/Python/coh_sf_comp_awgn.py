from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr

import numpy
import matplotlib.pyplot as plt

import os
import sys
sys.path.append(os.environ.get('GRC_HIER_PATH', os.path.expanduser('~/.grc_gnuradio')))
from grc_css_demod_coh import grc_css_demod_coh  # grc-generated hier_block
from lora2 import css_mod


class ber_vs_ebn0_awgn(gr.top_block):

    def __init__(self, M, n_syms, len_int, EbN0dB):
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

        self.noise_src = analog.noise_source_c(analog.GR_GAUSSIAN, noisevar, 0)
        self.noise_adder = blocks.add_vcc(1)

        self.css_demod_coh = grc_css_demod_coh(M, len_int)

        self.est_syms_sink = blocks.vector_sink_s()
        self.est_syms_coh_sink = blocks.vector_sink_s()
        self.est_syms_quad_sink = blocks.vector_sink_s()

        ##################################################
        # Connections
        ##################################################

        self.connect((self.syms_src, 0), (self.css_mod, 0))

        self.connect((self.noise_src, 0), (self.noise_adder, 0))
        self.connect((self.css_mod, 0), (self.noise_adder, 1))

        self.connect((self.noise_adder, 0), (self.css_demod_coh, 0))

        self.connect((self.css_demod_coh, 0), (self.est_syms_coh_sink, 0))

def main():
    SF = numpy.arange(7,13)
    M = numpy.power(2,SF)
    n_syms = 16384
    n_simus = 4
    EbN0dB = numpy.linspace(0, 6, 13)
    #n_syms = 16
    #n_simus = 1
    #EbN0dB = numpy.array([100])

    len_int=256

    BER_coh = numpy.zeros((len(SF), len(EbN0dB)))

    #Simu
    for l in range(0, len(SF)):
        print("SF=" + str(SF[l]))
        for i in range(0, len(EbN0dB)):
            print("Eb/N0=" + str(EbN0dB[i]))

            n_err_coh = 0
            for j in range(0, n_simus):
                tb = ber_vs_ebn0_awgn(M[l], n_syms, len_int, EbN0dB[i])
                tb.run()

                syms = tb.syms_vec
                est_syms_coh = tb.est_syms_coh_sink.data()

                for k in range(0, len(syms)):
                    bits = [int(ele) for ele in list(numpy.binary_repr(syms[k], SF[l]))]

                    est_bits_coh = [int(ele) for ele in list(numpy.binary_repr(est_syms_coh[k], SF[l]))]

                    n_err_coh += numpy.sum(numpy.abs(numpy.array(bits)-numpy.array(est_bits_coh)))

                tb.est_syms_coh_sink.reset()

            BER_coh[l,i] = float(n_err_coh)/(n_simus*n_syms*SF[l])

            print("Error count:" + str(n_err_coh) + " (coherent).")
            print("BER:" + str(BER_coh[l,i]) + " (coherent).")
            print("\n")

    #save data
    fid = open("EbN0dB.raw", "wb")
    EbN0dB.tofile(fid)
    fid.close()
    fid = open("BER_coh.raw", "wb")
    BER_coh.tofile(fid)
    fid.close()
    fid = open("SF.raw", "wb")
    SF.tofile(fid)
    fid.close()

    #Plot results
    for l in range(0, len(SF)):
        plt.semilogy(EbN0dB, BER_coh[l,:], label=str(SF[l]))

    plt.grid(which='both')
    plt.ylabel('BER')
    plt.xlabel('Eb/N0 (dB)')

    axes = plt.gca()
    axes.set_ylim([1e-5, 0.5])
    plt.legend()
    plt.show()

if __name__ == '__main__':
    main()
