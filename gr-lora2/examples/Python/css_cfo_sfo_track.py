import json
from gnuradio import analog
from gnuradio import blocks
from gnuradio import filter
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

    def __init__(self, M, cfo, delay, EbN0dB, B_cfo, B_delay, Q_res, Q_det, n_syms):
        gr.top_block.__init__(self, "BER vs Eb/N0 AWGN")

        ##################################################
        # Variables
        ##################################################
        self.n_syms= n_syms

        self.intern_interp= 32
        delay = delay*self.intern_interp
        self.Q_res = Q_res
        self.M = M

        noisevar = numpy.sqrt(float(M)/numpy.log2(M) * 10**(-EbN0dB/10.0))

        self.syms_vec = numpy.random.randint(0, M, n_syms)

        ##################################################
        # Blocks
        ##################################################
        self.syms_src = blocks.vector_source_s(self.syms_vec, False)

        self.css_mod = css_mod(M, self.intern_interp)

        #Channel (1: noise)
        self.awgn_chan = channels.awgn(noisevar)

        #Channel (2: cfo)
        self.cfo_source = analog.sig_source_c(1.0, analog.GR_COS_WAVE, cfo,
                1, 0)
        self.multiplicator = blocks.multiply_vcc(1)

        #Channel (3: delay)
        int_delay = 0
        frac_delay = 0.0
        self.int_delayer = None
        if delay > 0:
            int_delay = int(delay)
            frac_delay = delay-int_delay
            self.int_delayer = blocks.delay(gr.sizeof_gr_complex, int_delay)
        else:
            int_delay = int(-delay)
            frac_delay = -delay-int_delay
            self.int_delayer = blocks.skiphead(gr.sizeof_gr_complex, int_delay)
        self.frac_delayer = filter.mmse_resampler_cc(frac_delay, 1.0)
        #Frac delayer introduces a delay of 3
        self.frac_delayer_fix = blocks.delay(gr.sizeof_gr_complex, 3)
        self.decim = filter.fir_filter_ccf(self.intern_interp, [1.0])

        self.css_demod_sfo = css_demod(M, B_cfo, B_delay, Q_res, Q_det)

        self.est_syms_sfo_sink = blocks.null_sink(2)
        self.spectrum_sink = blocks.null_sink(gr.sizeof_gr_complex*M)
        self.cfo_err_sink= blocks.vector_sink_f()
        self.delay_err_sink= blocks.vector_sink_f()
        

        ##################################################
        # Connections
        ##################################################

        self.connect((self.syms_src, 0), (self.css_mod, 0))

        self.connect((self.css_mod, 0), (self.awgn_chan, 0))
        self.connect((self.awgn_chan, 0), (self.int_delayer, 0))
        self.connect((self.int_delayer, 0), (self.frac_delayer, 0))
        self.connect((self.frac_delayer, 0), (self.frac_delayer_fix, 0))
        self.connect((self.frac_delayer_fix, 0), (self.decim, 0))
        self.connect((self.decim, 0), (self.multiplicator, 0))
        self.connect((self.cfo_source, 0), (self.multiplicator, 1))

        self.connect((self.multiplicator, 0), (self.css_demod_sfo, 0))

        self.connect((self.css_demod_sfo, 0), (self.est_syms_sfo_sink, 0))
        self.connect((self.css_demod_sfo, 1), (self.spectrum_sink, 0))
        self.connect((self.css_demod_sfo, 2), (self.cfo_err_sink, 0))
        self.connect((self.css_demod_sfo, 3), (self.delay_err_sink, 0))

def main():
    params = {
        'SF': 9,
        'B_cfo': 0.8,
        'B_delay': 0.8,
        'Q_res': 8,
        'Q_det': 4,
        'n_syms': 40,
        'cfo': 0.4/(2**9),
        'delay': 0.4,
        'EbN0dB': 40,
    }
    M = 2**params['SF']

    save = True
    filename = 'CSS_CFO_SFO_TRACK.json'

    #Simu
    tb = ber_vs_ebn0_awgn(M, params['cfo'], params['delay'],
            params['EbN0dB'], params['B_cfo'], params['B_delay'],
            params['Q_res'], params['Q_det'], params['n_syms'])
    tb.run()

    est_cfos = tb.cfo_err_sink.data()
    est_sfos = tb.delay_err_sink.data()

    #save data
    if save:
        results = {}
        results['params'] = params
        results['est_cfos'] = est_cfos
        results['est_sfos'] = est_sfos

        fid = open(filename, 'w')
        json.dump(results, fid)
        fid.close()
        print('Results written in ' + filename + '.')

    plt.figure()
    plt.subplot(2,1,1)
    plt.plot(numpy.array(est_cfos[0:params['n_syms']])*M, '-')
    plt.plot(params['cfo']*numpy.ones(params['n_syms'])*M, '--')
    plt.grid(which='both')
    plt.xlabel('Symbol index')
    plt.ylabel('CFO Error')

    plt.subplot(2,1,2)
    plt.plot(est_sfos[0:params['n_syms']], '-')
    plt.plot(params['delay']*numpy.ones(params['n_syms']), '--')
    plt.grid(which='both')
    plt.xlabel('Symbol index')
    plt.ylabel('Delay Error')

    plt.show()

if __name__ == '__main__':
    main()



