from gnuradio import blocks
from gnuradio import gr

import numpy
import matplotlib.pyplot as plt

import os
import sys
import json
sys.path.append(os.environ.get('GRC_HIER_PATH', os.path.expanduser('~/.grc_gnuradio')))
from grc_mfsk_demod import grc_mfsk_demod # grc-generated hier_block
from grc_mfsk_demod_coh import grc_mfsk_demod_coh  # grc-generated hier_block
from grc_mfsk_mod import grc_mfsk_mod
from lora2 import mfsk_genie_phase_est

import channels

class ber_vs_ebn0_awgn(gr.top_block):
    """
    A class to simulate performance of a M-FSK transceiver over AWGN.
    """

    def __init__(self, M, n_syms, len_int, EbN0dB, channel):
        gr.top_block.__init__(self, "BER vs Eb/N0")

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

        self.mfsk_mod = grc_mfsk_mod(M)

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
            self.genie_phase_est = mfsk_genie_phase_est(M)

        self.mfsk_demod = grc_mfsk_demod(M)
        self.mfsk_demod_coh = grc_mfsk_demod_coh(M)

        self.est_syms_sink = blocks.vector_sink_s()
        self.est_syms_coh_sink = blocks.vector_sink_s()

        ##################################################
        # Connections
        ##################################################

        self.connect((self.syms_src, 0), (self.mfsk_mod, 0))

        if self.selective_chan is None:
            self.connect((self.mfsk_mod, 0), (self.awgn_chan, 0))
        else:
            self.connect((self.mfsk_mod, 0), (self.selective_chan, 0))
            if channel == 'itu-in-out-ped-A':
                self.connect((self.selective_chan, 0), (self.genie_phase_est, 0))
                self.connect((self.genie_phase_est, 0), (self.awgn_chan, 0))
            else:
                self.connect((self.selective_chan, 0), (self.awgn_chan, 0))

        self.connect((self.awgn_chan, 0), (self.mfsk_demod_coh, 0))
        self.connect((self.awgn_chan, 0), (self.mfsk_demod, 0))

        self.connect((self.mfsk_demod, 0), (self.est_syms_sink, 0))
        self.connect((self.mfsk_demod_coh, 0), (self.est_syms_coh_sink, 0))

def do_simu(EbN0dB, n_simus, SF, n_syms, n_min_err, channel):
    M = 2**SF

    BER = numpy.zeros(len(EbN0dB))
    BER_coh = numpy.zeros(len(EbN0dB))

    try:
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
    except Exception as e:
        print('An error occured.')
        print(e)

    return {'uncoh': BER, 'coh': BER_coh}

def main():
    params = {
        'comp_type': 'proakis-b',    #Type of simulation: awgn, basic-t-sel,
                                # proakis-b or itu-in-out-ped-A
        'SF': 9,                #Spreading factor
        'n_syms': 16384,        #Number of symbols to be transmitted in a simulation
        'n_simus': 100,         #Max. number of simulations to perform
        'n_min_err': 1000,      #Minimum number of errors to be observed to stop the simulation
    }
    EbN0dB = numpy.linspace(0, 10, 11) #Eb/N0 points to simulate

    save = True

    #Simu
    BER = do_simu(EbN0dB, params['n_simus'], params['SF'],
            params['n_syms'], params['n_min_err'], params['comp_type'])

    if params['comp_type'] == 'awgn':
        file_title = 'MFSK_BER.json'
        label = 'AWGN'
    if params['comp_type'] == 'proakis-b':
        file_title = 'MFSK_BER_proakis_b.json'
        label = 'Proakis B'
    if params['comp_type'] == 'basic-t-sel':
        file_title = 'MFSK_BER_basic_t_sel.json'
        label = 'Basic time-selective'
    if params['comp_type'] == 'itu-in-out-ped-A':
        file_title = 'MFSK_BER_itu-in-out-ped-A.json'
        label = 'Rayleigh fading'

    #save data
    if save:
        results = {}
        results['params'] = params
        results['EbN0dB'] = EbN0dB.tolist()

        fid = open('UNCOH_' + file_title, 'w')
        results['BER'] = BER['uncoh'].tolist()
        json.dump(results, fid)
        fid.close()

        fid = open(file_title, 'w')
        results['BER'] = BER['coh'].tolist()
        json.dump(results, fid)
        fid.close()

    #Plot results
    plt.semilogy(EbN0dB, BER['uncoh'], '-+', label=label)
    plt.semilogy(EbN0dB, BER['coh'], '-x', label='Coherent ' + label)

    plt.grid(which='both')
    plt.ylabel('BER')
    plt.xlabel('Eb/N0 (dB)')

    axes = plt.gca()
    axes.set_ylim([1e-5, 0.5])
    plt.legend()
    plt.show()

if __name__ == '__main__':
    main()
