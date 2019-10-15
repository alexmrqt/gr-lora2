from gnuradio import blocks
from gnuradio import gr

import numpy
import matplotlib.pyplot as plt

import os
import sys
import pmt
sys.path.append(os.environ.get('GRC_HIER_PATH', os.path.expanduser('~/.grc_gnuradio')))
from lora2 import lora_hamming_encode
from lora2 import lora_whiten
from lora2 import lora_interleaver
from lora2 import gray_decode
from lora2 import css_mod
from grc_css_demod_coh import grc_css_demod_coh  # grc-generated hier_block
from lora2 import gray_encode
from lora2 import lora_deinterleaver
from lora2 import lora_hamming_decode

import channels


class ber_vs_ebn0_awgn(gr.top_block):
    """
    A class to simulate performance of a LoRa transceiver (with CR=4) over AWGN.
    """

    def __init__(self, M, n_bits, len_int, EbN0dB, channel):
        gr.top_block.__init__(self, "BER vs Eb/N0")

        ##################################################
        # Variables
        ##################################################
        self.n_bits= n_bits

        self.M = M
        self.SF = SF = int(numpy.log2(M))
        self.CR = CR = 4
        self.code_eff = code_eff = CR / (CR+4.0)
        noisevar=numpy.sqrt(1.0/code_eff * float(M)/SF * 10**(-EbN0dB/10.0))

        self.bits_vec = numpy.random.randint(0, 2, n_bits)

        self.pkt_len_tag = pkt_len_tag = gr.tag_t()
        pkt_len_tag_key = 'pkt_len'
        pkt_len_tag.key = pmt.to_pmt(pkt_len_tag_key)
        pkt_len_tag.value = pmt.to_pmt(n_bits)

        ##################################################
        # Blocks
        ##################################################
        self.bits_src = blocks.vector_source_b(self.bits_vec, False, 1, [pkt_len_tag])

        self.encoder = lora_hamming_encode(CR, pkt_len_tag_key)
        self.whiten = lora_whiten(CR, pkt_len_tag_key)
        self.interleaver = lora_interleaver(SF, CR)
        self.ungray = gray_decode()
        self.css_mod = css_mod(M, 1)

        self.awgn_chan = channels.awgn(noisevar)
        self.selective_chan = None
        if channel == 'proakis-b':
            self.selective_chan = channels.proakis_b()
            #Packet_len tag is removed by the channel
            self.sts = blocks.stream_to_tagged_stream(gr.sizeof_char, 1,
                    int(n_bits/code_eff)-(CR+4)*SF, pkt_len_tag_key)
        elif channel == 'basic-t-sel':
            self.selective_chan = channels.basic_t_sel(M)

        self.css_demod_coh = grc_css_demod_coh(M, len_int)
        self.gray = gray_encode()
        self.deinterleaver = lora_deinterleaver(SF, CR)
        self.dewhiten = lora_whiten(CR, pkt_len_tag_key)
        self.decoder = lora_hamming_decode(CR, pkt_len_tag_key)

        self.est_bits_sink = blocks.vector_sink_b()

        ##################################################
        # Connections
        ##################################################

        self.connect((self.bits_src, 0), (self.encoder, 0))
        self.connect((self.encoder, 0), (self.whiten, 0))
        self.connect((self.whiten, 0), (self.interleaver, 0))
        self.connect((self.interleaver, 0), (self.ungray, 0))
        self.connect((self.ungray, 0), (self.css_mod, 0))

        if self.selective_chan is None:
            self.connect((self.css_mod, 0), (self.awgn_chan, 0))
        else:
            self.connect((self.css_mod, 0), (self.selective_chan, 0))
            self.connect((self.selective_chan, 0), (self.awgn_chan, 0))

        self.connect((self.awgn_chan, 0), (self.css_demod_coh, 0))
        self.connect((self.css_demod_coh, 0), (self.gray, 0))
        self.connect((self.gray, 0), (self.deinterleaver, 0))
        if channel == 'proakis-b':
            self.connect((self.deinterleaver, 0), (self.sts, 0))
            self.connect((self.sts, 0), (self.dewhiten, 0))
        else:
            self.connect((self.deinterleaver, 0), (self.dewhiten, 0))
        self.connect((self.dewhiten, 0), (self.decoder, 0))
        self.connect((self.decoder, 0), (self.est_bits_sink, 0))

def main():
    comp_type = 'basic-t-chan'      #Type of simulation: awgn, basic-t-chan or proakis-b
    SF = 9                  #Spreading factor
    M = numpy.power(2,SF)   #Number of symbols in the modulation alphabet
    n_bits = 1008           #Number of bits to be transmitted in a simulation
    n_simus = 200           #Max. number of simulations to perform
    n_min_err = 1000        #Minimum number of errors to be observed to stop the simulation
    EbN0dB = numpy.linspace(0, 10, 11) #Eb/N0 points to simulate

    #n_bits = 1008
    #n_simus = 1
    #EbN0dB = numpy.array([100])

    len_int=-1              #Deactivate phase correction for the coherent demodulator.


    BER = numpy.zeros(len(EbN0dB))

    #Simu
    for i in range(0, len(EbN0dB)):
        print("Eb/N0=" + str(EbN0dB[i]))

        n_err_coh = 0
        n_tot_bits = 0

        for j in range(0, n_simus):
            tb = ber_vs_ebn0_awgn(M, n_bits, len_int, EbN0dB[i], comp_type)
            tb.run()

            est_bits = tb.est_bits_sink.data()
            bits = tb.bits_vec[:len(est_bits)]

            n_tot_bits += len(est_bits)
            n_err_coh += numpy.sum(numpy.abs(numpy.array(bits)-numpy.array(est_bits)))

            del tb

            if n_err_coh > n_min_err:
                break

        BER[i] = float(n_err_coh)/n_tot_bits

        if BER[i] == 0.0:
            break

    #save data
    fid = open("EbN0dB.raw", "wb")
    EbN0dB.tofile(fid)
    fid.close()
    if comp_type == 'awgn':
        file_title = 'LORA_BER.raw'
        label = 'AWGN'
    if comp_type == 'proakis-b':
        file_title = 'LORA_BER_proakis_b.raw'
        label = 'Proakis B'
    if comp_type == 'basic-t-chan':
        file_title = 'LORA_BER_basic_t_chan.raw'
        label = 'Basic time-selective'

    fid = open(file_title, "wb")
    BER.tofile(fid)
    fid.close()

    plt.semilogy(EbN0dB, BER, '-x', label=label)

    plt.grid(which='both')
    plt.ylabel('BER')
    plt.xlabel('Eb/N0 (dB)')

    axes = plt.gca()
    axes.set_ylim([1e-5, 0.5])
    plt.legend()
    plt.show()

if __name__ == '__main__':
    main()
