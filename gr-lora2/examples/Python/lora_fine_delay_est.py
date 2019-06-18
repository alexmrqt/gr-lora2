import os
import sys
sys.path.append(os.environ.get('GRC_HIER_PATH', os.path.expanduser('~/.grc_gnuradio')))
import pmt
import numpy
from matplotlib import pyplot as plt

from gnuradio import analog
from gnuradio import blocks
from gnuradio import filter
from gnuradio import gr
import lora2


class lora_sync_test(gr.top_block):

    def __init__(self, SF, n_pkts, n_syms_pkt, noise_var, cfo, delay, fine_delay):
        gr.top_block.__init__(self, "Lora Sync Test")

        ##################################################
        # Variables
        ##################################################
        self.SF = SF
        self.n_syms_pkt = n_syms_pkt
        self.noise_var = noise_var
        self.cfo = cfo
        self.delay = delay
        self.fine_delay = fine_delay

        self.interp = 1
        self.M = 2**self.SF

        ##################################################
        # Blocks
        ##################################################
        #Modulator
        syms_vec = numpy.random.randint(0, 2**SF, n_syms_pkt*n_pkts,
                dtype=numpy.uint16)
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

        #Channel (3: delay)
        self.delayer = blocks.delay(gr.sizeof_gr_complex, self.delay)
        self.fine_delayer = filter.fractional_interpolator_cc(self.fine_delay, 1.0)

        #Demod
        self.to_vect = lora2.css_sync_and_vectorize(self.M)
        self.demod = lora2.css_demod(self.M, 0.0,0.0)
        self.null_sink_f1 = blocks.null_sink(gr.sizeof_float)
        self.null_sink_f2 = blocks.null_sink(gr.sizeof_float)
        self.null_sink_s = blocks.null_sink(gr.sizeof_short)
        self.fine_time_err_est = lora2.css_fine_freq_error_detector(self.M)
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
        self.connect((self.multiplicator, 0), (self.delayer, 0))
        self.connect((self.delayer, 0), (self.fine_delayer, 0))

        #Demodulator
        self.connect((self.fine_delayer, 0), (self.to_vect, 0))
        self.connect((self.to_vect, 0), (self.demod, 0))
        self.connect((self.demod, 1), (self.fine_time_err_est, 0))
        self.msg_connect((self.fine_time_err_est, 'time'),
                (self.msg_sink, 'store'))

        self.connect((self.demod, 0), (self.null_sink_s, 0))
        self.connect((self.demod, 2), (self.null_sink_f1, 0))
        self.connect((self.demod, 3), (self.null_sink_f2, 0))
 
if __name__ == "__main__":
    #Parameters
    SF = 9
    n_pkts = 1
    n_syms = 2
    M = 2**SF

    EbN0dB = numpy.linspace(0, 50, 11)
    #EbN0dB = numpy.array([100])
    Eb = 1.0/M
    N0=Eb * 10**(-EbN0dB/10.0)
    noise_var=(M**2 * N0)/numpy.log2(M)
    time_offset = 0
    cfo = 0.0

    fine_delay_min = 0.0
    fine_delay_max = 0.99
    fine_delays = numpy.linspace(fine_delay_min, fine_delay_max, 20)

    #Fine delay impact
    fine_delay_est = numpy.zeros((len(fine_delays), len(EbN0dB)))
    for j in range(0, len(fine_delays)):
        print('Fine delay = ' + str(fine_delays[j]))
        for i in range(0, len(EbN0dB)):
            if fine_delays[j] < 1.0:
                #Setup block
                tb = lora_sync_test(SF, n_pkts, n_syms, noise_var[i], cfo,
                        time_offset, fine_delays[j])
            else:
                tb = lora_sync_test(SF, n_pkts, n_syms, noise_var[i], cfo,
                        time_offset+1, fine_delays[j]-1)

            #Simulate
            tb.start()
            tb.wait()

            n_msg = tb.msg_sink.num_messages()

            if n_msg > 0:
                est_delay = 0.0
                for k in range(0, n_msg):
                    est_delay -= pmt.to_float(tb.msg_sink.get_message(k))

                #Detected / total ratio
                fine_delay_est[j,i] = est_delay/n_msg

                print('Estimated fine delay Eb/N0 (dB)=' + str(EbN0dB[i]) + ' -> '
                        + str(fine_delay_est[j,i]))
            else:
                print('No message detected.')

            del tb

    plt.figure()
    plt.plot(fine_delays, fine_delays, label='Ref')
    for j in range(0, len(EbN0dB)):
        plt.plot(fine_delays, fine_delay_est[:,j], label=str(EbN0dB[j]), marker='+')


    plt.title('Fine delay estimator')
    plt.grid(which='both')
    plt.ylabel('Estimated delay')
    plt.xlabel('delay')

    axes = plt.gca()
    axes.set_xlim([fine_delay_min, fine_delay_max])
    #axes.set_ylim([fine_delay_min, fine_delay_max])
    extremum = numpy.max((numpy.max(fine_delay_est.flatten()), -numpy.min(fine_delay_est.flatten())))
    axes.set_ylim([-extremum, extremum])
    plt.legend()
    plt.show()


