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
            B_cfo, B_delay, interp, n_syms):
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

        self.css_mod = css_mod(M, interp)

        #Channel (1: noise)
        self.awgn_chan = channels.awgn(noisevar)

        #Channel (2: cfo)
        self.cfo = gr_chan.cfo_model(interp, sigma2_cfo, max_cfo, numpy.random.randint(0, 255))

        #Channel (3: sfo)
        self.sfo = gr_chan.sro_model(1.0, sigma2_sfo, max_sfo, numpy.random.randint(0, 255))
        self.frac_delayer_fix = blocks.delay(gr.sizeof_gr_complex, 3)

        self.css_demod_sfo = css_demod(M, B_cfo, B_delay, interp)

        self.est_syms_sfo_sink = blocks.null_sink(2)
        self.spectrum_sink = blocks.null_sink(gr.sizeof_gr_complex*M)
        self.cfo_err_sink= blocks.vector_sink_f()
        self.delay_err_sink= blocks.vector_sink_f()
        

        ##################################################
        # Connections
        ##################################################

        self.connect((self.syms_src, 0), (self.css_mod, 0))

        self.connect((self.css_mod, 0), (self.awgn_chan, 0))
        self.connect((self.awgn_chan, 0), (self.cfo, 0))
        self.connect((self.cfo, 0), (self.sfo, 0))
        self.connect((self.sfo, 0), (self.frac_delayer_fix, 0))

        self.connect((self.frac_delayer_fix, 0), (self.css_demod_sfo, 0))

        self.connect((self.css_demod_sfo, 0), (self.est_syms_sfo_sink, 0))
        self.connect((self.css_demod_sfo, 1), (self.spectrum_sink, 0))
        self.connect((self.css_demod_sfo, 2), (self.cfo_err_sink, 0))
        self.connect((self.css_demod_sfo, 3), (self.delay_err_sink, 0))

def main():
    params = {
        'SF': 9,
        'B_cfo': 0.4,
        'B_delay': 0.3,
        'interp': 8,
        'n_syms': 1024,
        'max_sfo': 50e-6,
        'sigma2_sfo': 1e-6,
        #'max_sfo': 0.0,
        #'sigma2_sfo': 0.0,
        'max_cfo': 1.0,
        'sigma2_cfo': 1e-6,
        #'max_cfo': 0.0,
        #'sigma2_cfo': 0.0,
        'EbN0dB': 100,
    }
    M = 2**params['SF']

    save = False
    filename = 'CSS_CFO_SFO_TRACK_RANDOM_WALK.json'

    #Simu
    tb = ber_vs_ebn0_awgn(M, params['max_cfo'], params['sigma2_cfo'],
            params['max_sfo'], params['sigma2_sfo'],
            params['EbN0dB'], params['B_cfo'], params['B_delay'],
            params['interp'], params['n_syms'])
    tb.run()

    est_cfos = tb.cfo_err_sink.data()
    est_sfos = tb.delay_err_sink.data()

    #save data
    if save:
        results = {}
        results['params'] = params
        results['est_cfos'] = est_cfos

        fid = open(filename, 'w')
        json.dump(results, fid)
        fid.close()
        print('Results written in ' + filename + '.')

    plt.figure()
    plt.subplot(2,1,1)
    plt.plot(est_cfos[0:params['n_syms']], '-')
    plt.grid(which='both')
    plt.xlabel('Symbol index')
    plt.ylabel('CFO Error')

    plt.subplot(2,1,2)
    plt.plot(est_sfos[0:params['n_syms']], '-')
    plt.grid(which='both')
    plt.xlabel('Symbol index')
    plt.ylabel('Delay Error')

    plt.show()

if __name__ == '__main__':
    main()



