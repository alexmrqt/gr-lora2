from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr

import numpy
import matplotlib.pyplot as plt

import os
import sys
sys.path.append(os.environ.get('GRC_HIER_PATH', os.path.expanduser('~/.grc_gnuradio')))
from css_demod_coh import css_demod_coh  # grc-generated hier_block
from css_demod import css_demod  # grc-generated hier_block
from css_mod import css_mod  # grc-generated hier_block


class ber_vs_ebn0_awgn(gr.top_block):

    def __init__(self, M, n_syms, len_int, EbN0dB):
        gr.top_block.__init__(self, "BER vs Eb/N0 AWGN")

        ##################################################
        # Variables
        ##################################################
        self.n_syms= n_syms

        Eb=1.0/M
        N0=Eb * 10**(-EbN0dB/10.0)
        noisevar=(M**2 * N0)/numpy.log2(M)

        self.syms_vec = numpy.random.randint(0, M, n_syms)

        ##################################################
        # Blocks
        ##################################################
        self.syms_src = blocks.vector_source_s(self.syms_vec, False)

        self.css_mod = css_mod(M)

        self.noise_src = analog.noise_source_c(analog.GR_GAUSSIAN, numpy.sqrt(noisevar), 0)
        self.noise_adder = blocks.add_vcc(1)

        self.css_demod = css_demod(M)
        self.css_demod_coh = css_demod_coh(M, len_int)

        self.est_syms_sink = blocks.vector_sink_s()
        self.est_syms_coh_sink = blocks.vector_sink_s()

        ##################################################
        # Connections
        ##################################################

        self.connect((self.syms_src, 0), (self.css_mod, 0))

        self.connect((self.noise_src, 0), (self.noise_adder, 0))
        self.connect((self.css_mod, 0), (self.noise_adder, 1))

        self.connect((self.noise_adder, 0), (self.css_demod, 0))
        self.connect((self.noise_adder, 0), (self.css_demod_coh, 0))

        self.connect((self.css_demod, 0), (self.est_syms_sink, 0))
        self.connect((self.css_demod_coh, 0), (self.est_syms_coh_sink, 0))

def main():
    SF = 7
    M = 2**SF
    n_syms = 16384
    n_simus = 2
    #EbN0dB = [0]
    EbN0dB = numpy.linspace(0, 10, 11)

    len_int=256

    BER = numpy.zeros(len(EbN0dB))
    BER_coh = numpy.zeros(len(EbN0dB))

    #Simu
    for i in range(0, len(EbN0dB)):
        print("Eb/N0=" + str(EbN0dB[i]))

        n_err = 0
        n_err_coh = 0
        for j in range(0, n_simus):
            tb = ber_vs_ebn0_awgn(M, n_syms, len_int, EbN0dB[i])
            tb.run()

            syms = tb.syms_vec
            est_syms = tb.est_syms_sink.data()
            est_syms_coh = tb.est_syms_coh_sink.data()

            for k in range(0, len(syms)):
                bits = [int(ele) for ele in list(numpy.binary_repr(syms[k], SF))]

                est_bits = [int(ele) for ele in list(numpy.binary_repr(est_syms[k], SF))]
                est_bits_coh = [int(ele) for ele in list(numpy.binary_repr(est_syms_coh[k], SF))]

                n_err += numpy.sum(numpy.abs(numpy.array(bits)-numpy.array(est_bits)))
                n_err_coh += numpy.sum(numpy.abs(numpy.array(bits)-numpy.array(est_bits_coh)))

            tb.est_syms_sink.reset()
            tb.est_syms_coh_sink.reset()

        BER[i] = float(n_err)/(n_simus*n_syms*SF)
        BER_coh[i] = float(n_err_coh)/(n_simus*n_syms*SF)

        print("Error count:" + str(n_err) + " (non coherent), " + str(n_err_coh) + " (coherent)")
        print("BER:" + str(BER[i]) + " (non coherent), " + str(BER_coh[i]) + " (coherent)")
        print("\n")

    #Union bound of Pe
    EbN0 = 10**(EbN0dB/10.0)
    Pe = numpy.exp(-SF*(numpy.sqrt(EbN0) - numpy.sqrt(numpy.log(2)))**2)
    Pb = float(2**(SF-1))/(2**SF - 1) * Pe

    #Plot results
    plt.semilogy(EbN0dB, BER, '-x', label="BER non-coherent")
    plt.semilogy(EbN0dB, BER_coh, '-+', label="BER coherent")
    #plt.semilogy(EbN0dB, Pb, '-', label="UB on Pb (coherent)")

    plt.grid(which='both')
    plt.ylabel('BER')
    plt.xlabel('Eb/N0 (dB)')

    axes = plt.gca()
    axes.set_ylim([1e-5, 0.5])
    plt.legend()
    plt.show()

if __name__ == '__main__':
    main()
