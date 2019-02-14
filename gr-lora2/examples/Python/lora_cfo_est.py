#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: GPL-3.0
#
##################################################
# GNU Radio Python Flow Graph
# Title: Lora Sync Test
# Generated: Wed Feb 13 16:52:37 2019
# GNU Radio version: 3.7.12.0
##################################################

import os
import sys
sys.path.append(os.environ.get('GRC_HIER_PATH', os.path.expanduser('~/.grc_gnuradio')))
import pmt
import numpy
from matplotlib import pyplot as plt

from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr
import lora2


class lora_sync_test(gr.top_block):

    def __init__(self, SF, n_pkts, n_syms_pkt, noise_var, cfo, delay):
        gr.top_block.__init__(self, "Lora Sync Test")

        ##################################################
        # Variables
        ##################################################
        self.SF = SF
        self.n_syms_pkt = n_syms_pkt
        self.noise_var = noise_var
        self.cfo = cfo
        self.delay = delay

        self.interp = 1
        self.chan_margin = 75000
        self.chan_bw = 125000
        self.M = 2**self.SF

        ##################################################
        # Blocks
        ##################################################
        #Modulator
        syms_vec = numpy.random.randint(0, 2**SF, n_syms_pkt*n_pkts,
                dtype=numpy.uint16)
        self.vector_source = blocks.vector_source_s(syms_vec.tolist(), False)
        self.to_tagged = blocks.stream_to_tagged_stream(gr.sizeof_short, 1,
                self.n_syms_pkt, 'packet_len')
        self.add_preamble = lora2.lora_add_preamble(8, 0x12, "packet_len",
                "sync_word", "payload")
        self.css_mod = lora2.css_mod(self.M, self.interp, 'packet_len')
        self.add_reversed_chirps = lora2.lora_add_reversed_chirps(self.SF,
                self.interp, "packet_len", "payload", "rev_chirps")

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

        self.preamble_detector = lora2.lora_preamble_detect(self.SF, 8, debug=False)
        self.store_tags = lora2.store_tags(numpy.complex64, "freq_offset")

        ##################################################
        # Connections
        ##################################################
        #Modulator
        self.connect((self.vector_source, 0), (self.to_tagged, 0))
        self.connect((self.to_tagged, 0), (self.add_preamble, 0))
        self.connect((self.add_preamble, 0), (self.css_mod, 0))
        self.connect((self.css_mod, 0), (self.add_reversed_chirps, 0))
        self.connect((self.add_reversed_chirps, 0), (self.tag_gate, 0))

        #Channel
        self.connect((self.tag_gate, 0), (self.adder, 1))
        self.connect((self.noise_source, 0), (self.adder, 0))
        self.connect((self.adder, 0), (self.multiplicator, 1))
        self.connect((self.cfo_source, 0), (self.multiplicator, 0))
        self.connect((self.multiplicator, 0), (self.delayer, 0))
        self.connect((self.delayer, 0), (self.preamble_detector, 0))

        #Demodulator
        self.connect((self.preamble_detector, 0), (self.store_tags, 0))


if __name__ == "__main__":
    #Parameters
    SF = 9
    n_pkts = 10
    n_bytes = 10*SF
    n_syms = 8*n_bytes/SF
    M = 2**SF

    #EbN0dB = numpy.linspace(0, 10, 11)
    EbN0dB = numpy.array([50])
    Eb = 1.0/M
    N0=Eb * 10**(-EbN0dB/10.0)
    noise_var=(M**2 * N0)/numpy.log2(M)

    cfo_min = -0.25
    cfo_max = 0.25
    cfos = numpy.linspace(cfo_min, cfo_max, 100)

    #CFO impact
    cfo_est = numpy.zeros((len(cfos), len(EbN0dB)))
    for j in range(0, len(cfos)):
        print('CFO = ' + str(cfos[j]))
        for i in range(0, len(EbN0dB)):
            #Setup block
            tb = lora_sync_test(SF, n_pkts, n_syms, noise_var[i], cfos[j], 0)

            #Simulate
            tb.start()
            tb.wait()

            #Retrieve
            tags = tb.store_tags.get_tags()

            #Compute error
            mean_est_cfo = 0.0
            if len(tags) > 0:
                for tag in tags:
                    mean_est_cfo -= pmt.to_float(tag.value)
                mean_est_cfo /= len(tags)
            else:
                mean_est_cfo = 10.0

            #Detected / total ratio
            cfo_est[j,i] = mean_est_cfo

            print('Estimated CFO Eb/N0 (dB)=' + str(EbN0dB[i]) + ' -> '
                    + str(mean_est_cfo))

    plt.figure()
    for j in range(0, len(EbN0dB)):
        plt.plot(cfos, cfo_est[:,j], label=str(EbN0dB[j]))

    plt.title('Impact of CFO on detection')
    plt.grid(which='both')
    plt.ylabel('Dectected / Total')
    plt.xlabel('CFO')

    axes = plt.gca()
    axes.set_ylim([cfo_min, cfo_max])
    plt.legend()
    plt.show()

