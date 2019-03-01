import os
import sys
sys.path.append(os.environ.get('GRC_HIER_PATH', os.path.expanduser('~/.grc_gnuradio')))
import pmt
import numpy
from matplotlib import pyplot as plt

from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr
from grc_css_demod import grc_css_demod  # grc-generated hier_block
import lora2


class lora_sync_test(gr.top_block):

    def __init__(self, SF, n_syms, noise_var, cfo):
        gr.top_block.__init__(self, "Lora Sync Test")

        ##################################################
        # Variables
        ##################################################
        self.SF = SF
        self.n_syms = n_syms
        self.noise_var = noise_var
        self.cfo = cfo

        self.interp = 1
        self.M = 2**self.SF

        ##################################################
        # Blocks
        ##################################################
        #Modulator
        syms_vec = numpy.random.randint(0, 2**SF, n_syms, dtype=numpy.uint16)
        self.vector_source = blocks.vector_source_s(syms_vec.tolist(), False)
        self.css_mod = lora2.css_mod(self.M, self.interp, 'packet_len')

        #Channel (1: noise)
        self.tag_gate = blocks.tag_gate(gr.sizeof_gr_complex)
        self.noise_source = analog.noise_source_c(analog.GR_GAUSSIAN,
                numpy.sqrt(self.noise_var), 0)
        self.adder = blocks.add_vcc(1)

        #Channel (2: cfo)
        self.cfo_source = analog.sig_source_c(1.0, analog.GR_COS_WAVE, self.cfo,
                1, 0)
        self.multiplicator = blocks.multiply_vcc(1)

        #Demodulator
        self.css_demod = grc_css_demod(self.M)
        self.null_sink = blocks.null_sink(gr.sizeof_short)
        self.cfo_det = lora2.css_fine_freq_error_detector(self.M, 8)
        self.msg_sink = blocks.message_debug()

        ##################################################
        # Connections
        ##################################################
        #Modulator
        self.connect((self.vector_source, 0), (self.css_mod, 0))
        self.connect((self.css_mod, 0), (self.tag_gate, 0))

        #Channel
        self.connect((self.tag_gate, 0), (self.adder, 1))
        self.connect((self.noise_source, 0), (self.adder, 0))
        self.connect((self.adder, 0), (self.multiplicator, 1))
        self.connect((self.cfo_source, 0), (self.multiplicator, 0))
        self.connect((self.multiplicator, 0), (self.css_demod, 0))

        #Demodulator
        self.connect((self.css_demod, 0), (self.null_sink, 0))
        self.connect((self.css_demod, 1), (self.cfo_det, 0))
        self.msg_connect((self.cfo_det, "freq"), (self.msg_sink, "store"))

if __name__ == "__main__":
    #Parameters
    SF = 9
    n_syms = 8
    M = 2**SF

    #EbN0dB = numpy.linspace(0, 10, 11)
    EbN0dB = numpy.array([100])
    Eb = 1.0/M
    N0=Eb * 10**(-EbN0dB/10.0)
    noise_var=(M**2 * N0)/numpy.log2(M)

    cfo_min = -0.5/M
    cfo_max = 0.5/M
    cfos = numpy.linspace(cfo_min, cfo_max, 50)

    #CFO impact
    est_cfo = numpy.zeros((len(cfos), len(EbN0dB)))
    for j in range(0, len(cfos)):
        print('CFO = ' + str(cfos[j]))
        for i in range(0, len(EbN0dB)):
            #Setup block
            tb = lora_sync_test(SF, n_syms, noise_var[i], cfos[j])

            #Simulate
            tb.start()
            tb.wait()

            if tb.msg_sink.num_messages() == 0:
                print('No message received')
            else:
                for k in range(0, tb.msg_sink.num_messages()):
                    msg = tb.msg_sink.get_message(k)
                    est_cfo[j,i] -= pmt.to_float(msg)

                est_cfo[j,i] /= tb.msg_sink.num_messages()

            print('Estimated cfo at EbN0dB = ' + str(EbN0dB[i]) + ': '
                    + str(est_cfo[j,i]))

            del tb

    plt.figure()
    plt.plot(cfos, cfos, label='Ref')
    for j in range(0, len(EbN0dB)):
        plt.plot(cfos, est_cfo[:,j], label=str(EbN0dB[j]), marker='+')


    plt.title('Fine CFO estimator')
    plt.grid(which='both')
    plt.ylabel('Estimated CFO')
    plt.xlabel('CFO')

    axes = plt.gca()
    #axes.set_xlim([-1.0, 1.0])
    #axes.set_ylim([-1.0, 1.0])
    axes.set_xlim([cfo_min, cfo_max])
    axes.set_ylim([cfo_min, cfo_max])
    #extremum = numpy.max((numpy.max(error.flatten()), -numpy.min(error.flatten())))
    #axes.set_ylim([-extremum, extremum])
    plt.legend()
    plt.show()

