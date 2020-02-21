from gnuradio import blocks
from gnuradio import gr

import numpy
import matplotlib.pyplot as plt

import os
import sys
import pmt
import json
sys.path.append(os.environ.get('GRC_HIER_PATH', os.path.expanduser('~/.grc_gnuradio')))
from lora2 import lora_hamming_encode
from lora2 import lora_whiten
from lora2 import lora_interleaver
from lora2 import gray_decode
from lora2 import css_mod
from grc_css_demod_coh import grc_css_demod_coh  # grc-generated hier_block
from grc_css_demod import grc_css_demod # grc-generated hier_block
from grc_mfsk_demod import grc_mfsk_demod # grc-generated hier_block
from grc_mfsk_demod_coh import grc_mfsk_demod_coh  # grc-generated hier_block
from grc_mfsk_mod import grc_mfsk_mod
from lora2 import gray_encode
from lora2 import lora_deinterleaver
from lora2 import lora_hamming_decode
from lora2 import css_genie_phase_est
from lora2 import mfsk_genie_phase_est

from lora2 import lora_soft_dewhiten
from lora2 import lora_soft_deinterleaver
from lora2 import gray_deindexer
from grc_css_soft_demod_coh import grc_css_soft_demod_coh # grc-generated hier_block
from grc_css_soft_demod import grc_css_soft_demod # grc-generated hier_block
from grc_mfsk_soft_demod import grc_mfsk_soft_demod # grc-generated hier_block
from grc_mfsk_soft_demod_coh import grc_mfsk_soft_demod_coh  # grc-generated hier_block
from lora2 import css_llr_converter
from lora2 import lora_soft_hamming_decode

import channels


class ber_vs_ebn0_awgn(gr.top_block):
    """
    A class to simulate performance of a LoRa transceiver (with CR=4) over AWGN.
    """

    def __init__(self, M, n_bits, n_pkts, len_int, EbN0dB, channel, coherent=True, fsk_lora=False):
        gr.top_block.__init__(self, "BER vs Eb/N0")

        ##################################################
        # Variables
        ##################################################
        self.n_bits= n_bits

        self.M = M
        self.SF = SF = int(numpy.log2(M))
        self.CR = CR = 4
        self.code_eff = code_eff = 4.0 / (CR+4.0)
        noisevar=numpy.sqrt(1.0/code_eff * float(M)/SF * 10**(-EbN0dB/10.0))

        n_pad = numpy.ceil(n_bits/(code_eff * SF * (CR+4))) \
                    * (self.code_eff * SF * (CR+4)) - n_bits
        n_bits += n_pad
        n_bits = int(n_bits)
        self.bits_vec = numpy.random.randint(0, 2, n_bits*n_pkts)

        pkt_len_tag_key = 'pkt_len'
        self.pkt_len_tags = pkt_len_tags = []
        offset = 0

        for i in range(n_pkts):
            tag = gr.tag_t()
            tag.key = pmt.to_pmt(pkt_len_tag_key)
            tag.value = pmt.to_pmt(n_bits)
            tag.offset = offset

            pkt_len_tags.append(tag)

            offset += n_bits

        ##################################################
        # Blocks
        ##################################################
        self.bits_src = blocks.vector_source_b(self.bits_vec, False, 1, pkt_len_tags)

        self.encoder = lora_hamming_encode(CR, pkt_len_tag_key)
        self.whiten = lora_whiten(CR, pkt_len_tag_key)
        self.interleaver = lora_interleaver(SF, CR)
        self.ungray = gray_decode()
        if fsk_lora:
            self.mod = grc_mfsk_mod(M)
        else:
            self.mod = css_mod(M, 1)

        self.awgn_chan = channels.awgn(noisevar)
        self.selective_chan = None
        if channel == 'proakis-b':
            self.selective_chan = channels.proakis_b()
        elif channel == 'basic-t-sel':
            self.selective_chan = channels.basic_t_sel(M)
        elif channel == 'itu-in-out-ped-A':
            delta_v = 0.83 #m/s = 3km/h
            f0 = 868.1e6
            c = 3e8
            max_doppler = delta_v/c*f0
            bw = 125e3
            self.selective_chan = channels.itu_outdoor_indoor_ped(max_doppler, bw, True)
            if coherent:
                if fsk_lora:
                    self.genie_phase_est = mfsk_genie_phase_est(M)
                else:
                    self.genie_phase_est = css_genie_phase_est(M)

        if coherent:
            if fsk_lora:
                self.soft_demod = grc_mfsk_soft_demod_coh(M)
            else:
                self.soft_demod = grc_css_soft_demod_coh(M)
        else:
            if fsk_lora:
                self.soft_demod = grc_mfsk_soft_demod(M)
            else:
                self.soft_demod = grc_css_soft_demod(M)
        self.gray_deidx = gray_deindexer(M)
        self.llr_converter = css_llr_converter(M, True, noisevar)
        self.soft_deinterleaver = lora_soft_deinterleaver(SF, CR)
        self.soft_dewhiten = lora_soft_dewhiten(CR, pkt_len_tag_key)
        self.soft_decoder = lora_soft_hamming_decode(CR, pkt_len_tag_key)

        self.est_bits_soft_sink = blocks.vector_sink_b()

        ##################################################
        # Connections
        ##################################################

        #Modulator
        self.connect((self.bits_src, 0), (self.encoder, 0))
        self.connect((self.encoder, 0), (self.whiten, 0))
        self.connect((self.whiten, 0), (self.interleaver, 0))
        self.connect((self.interleaver, 0), (self.ungray, 0))
        self.connect((self.ungray, 0), (self.mod, 0))

        #Channel
        if self.selective_chan is None:
            self.connect((self.mod, 0), (self.awgn_chan, 0))
        else:
            self.connect((self.mod, 0), (self.selective_chan, 0))
            if coherent and (channel == 'itu-in-out-ped-A'):
                self.connect((self.selective_chan, 0), (self.genie_phase_est, 0))
                self.connect((self.genie_phase_est, 0), (self.awgn_chan, 0))
            else:
                self.connect((self.selective_chan, 0), (self.awgn_chan, 0))

        #Soft demodulator
        self.connect((self.awgn_chan, 0), (self.soft_demod, 0))
        self.connect((self.soft_demod, 0), (self.gray_deidx, 0))
        self.connect((self.gray_deidx, 0), (self.llr_converter, 0))
        self.connect((self.llr_converter, 0), (self.soft_deinterleaver, 0))
        self.connect((self.soft_deinterleaver, 0), (self.soft_dewhiten, 0))
        self.connect((self.soft_dewhiten, 0), (self.soft_decoder, 0))
        self.connect((self.soft_decoder, 0), (self.est_bits_soft_sink, 0))

def plot(EbN0dB, SF, BER, label):
    plt.clf()

    for i in range(0, len(SF)):
        plt.semilogy(EbN0dB, BER[i,:], '-x', label=label + ' SF=' + str(SF[i]))

    plt.grid(which='both')
    plt.ylabel('BER')
    plt.xlabel('Eb/N0 (dB)')

    axes = plt.gca()
    axes.set_ylim([1e-5, 0.5])
    plt.legend()
    plt.pause(0.1)

def save_to_json(filename, EbN0dB, SF, BER, params):
    results = {}
    results['params'] = params
    results['SF'] = SF
    results['EbN0dB'] = EbN0dB.tolist()

    fid = open(filename, 'w')
    results['BER'] = BER.tolist()
    json.dump(results, fid)
    fid.close()

def main():
    params = {
        'comp_type': 'itu-in-out-ped-A',      #Type of simulation: awgn, basic-t-sel, proakis-b or itu-in-out-ped-A
        'coherent': False,         #Coherent demodulation?
        'fsk_lora': False,         #Use FSK instead of CSS?
        'n_bits': 1008,            #Number of bits to be transmitted in a simulation
        'n_pkts': 40,              #Number of packets in a simulation run
        'n_simus': 100,            #Max. number of simulations to perform
        'len_int': -1              #Deactivate phase correction for the coherent demodulator.
    }
    #SF = [7, 8, 9, 10, 11, 12]
    SF = [10]
    #EbN0dB = numpy.linspace(0, 30, 11) #Eb/N0 points to simulate
    EbN0dB = numpy.arange(30, 36, 3) #Eb/N0 points to simulate

    save = True

    BER = numpy.zeros((len(SF), len(EbN0dB)))

    if params['comp_type'] == 'awgn':
        file_title = 'LORA_BER.json'
        label = 'AWGN'
    if params['comp_type'] == 'proakis-b':
        file_title = 'LORA_BER_proakis_b.json'
        label = 'Proakis B'
    if params['comp_type'] == 'basic-t-sel':
        file_title = 'LORA_BER_basic_t_sel.json'
        label = 'Basic time-selective'
    if params['comp_type'] == 'itu-in-out-ped-A':
        file_title = 'LORA_BER_itu-in-out-ped-A.json'
        label = 'Rayleigh fading'

    if params['fsk_lora']:
        file_title = 'FSK_' + file_title

    if not params['coherent']:
        file_title = 'UNCOH_' + file_title

    #Simu
    for i in range(0, len(SF)):
        print('SF=' + str(SF[i]))
        M = 2**SF[i]

        n_err = numpy.zeros(len(EbN0dB))
        n_tot_bits = numpy.zeros(len(EbN0dB))

        for j in range(0, params['n_simus']):
            print(j)

            tbs = [ber_vs_ebn0_awgn(M, params['n_bits'], params['n_pkts'],
                    params['len_int'], EbN0dB_i, params['comp_type'],
                    params['coherent'], params['fsk_lora']) for EbN0dB_i in EbN0dB]

            for tb in tbs:
                tb.start()

            for tb in tbs:
                tb.wait()

            for k in range(0, len(EbN0dB)):
                est_bits = tbs[k].est_bits_soft_sink.data()
                bits = tbs[k].bits_vec[:len(est_bits)]

                n_tot_bits[k] += len(est_bits)
                n_err[k] += numpy.sum(numpy.abs(numpy.array(bits)-numpy.array(est_bits)))

                BER[i,k] = float(n_err[k])/n_tot_bits[k]

            #save data
            if save:
                save_to_json('SF_' + str(SF[i]) + '_' + file_title, EbN0dB,
                        SF[i], BER[i,:], params)

            plot(EbN0dB, SF, BER, label)

            del tbs

if __name__ == '__main__':
    main()
