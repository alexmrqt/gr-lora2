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
import numpy
from matplotlib import pyplot as plt

from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr
from grc_css_demod import grc_css_demod  # grc-generated hier_block
import lora2


class lora_sync_test(gr.top_block):

    def __init__(self, SF, syms_vec, noise_var, cfo, delay):
        gr.top_block.__init__(self, "Lora Sync Test")

        ##################################################
        # Variables
        ##################################################
        self.SF = SF
        self.syms_vec = syms_vec
        self.n_syms = len(self.syms_vec)
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
        self.css_mod = lora2.css_mod(self.M, self.interp, 'packet_len')
        self.css_demod = grc_css_demod(self.M)
        self.vector_source = blocks.vector_source_s(self.syms_vec.tolist(), False)
        self.vector_sink = blocks.vector_sink_s(1, self.n_syms)
        self.adder = blocks.add_vcc(1)
        self.noise_source = analog.noise_source_c(analog.GR_GAUSSIAN, numpy.sqrt(self.noise_var), 0)
        self.tag_gate = blocks.tag_gate(gr.sizeof_gr_complex)
        self.head = blocks.head(gr.sizeof_short, self.n_syms)

        ##################################################
        # Connections
        ##################################################
        #Modulator
        self.connect((self.vector_source, 0), (self.css_mod, 0))
        self.connect((self.css_mod, 0), (self.tag_gate, 0))

        #Channel
        self.connect((self.tag_gate, 0), (self.adder, 1))
        self.connect((self.noise_source, 0), (self.adder, 0))
        self.connect((self.adder, 0), (self.css_demod, 0))

        #Demodulator
        self.connect((self.css_demod, 0), (self.head, 0))
        self.connect((self.head, 0), (self.vector_sink, 0))

if __name__ == "__main__":
    #Parameters
    SF = 9
    n_bytes = 300*SF
    n_syms = 8*n_bytes/SF
    M = 2**SF

    EbN0dB = numpy.linspace(0, 10, 11)
    Eb = 1.0/M
    N0=Eb * 10**(-EbN0dB/10.0)
    noise_var=(M**2 * N0)/numpy.log2(M)

    print('N_syms: ' + str(n_syms))

    BER = numpy.zeros(len(EbN0dB))
    for i in range(0, len(EbN0dB)):
        syms_vec = numpy.random.randint(0, 2**SF, n_syms, dtype=numpy.uint16)

        #Setup block
        tb = lora_sync_test(SF, syms_vec, noise_var[i], 0, 0)

        #Simulate
        tb.start()
        tb.wait()

        #Retrieve data
        syms_vec_demod = numpy.array(tb.vector_sink.data(), dtype=numpy.uint16)

        #Compute BER
        n_bits = SF*n_syms
        n_error = 0

        bits_vec = numpy.unpackbits(syms_vec.view(numpy.uint8))
        bits_vec_demod = numpy.unpackbits(syms_vec_demod.view(numpy.uint8))
        n_error = numpy.sum(bits_vec ^ bits_vec_demod)

        BER[i] = float(n_error)/n_bits
        print('BER @ EbN0 (dB)=' +str(EbN0dB[i]) + ' -> '+ str(BER[i]))

    plt.semilogy(EbN0dB, BER)
    plt.grid(which='both')
    plt.ylabel('BER')
    plt.xlabel('Eb/N0 (dB)')

    axes = plt.gca()
    axes.set_ylim([1e-5, 0.5])
    plt.legend()
    plt.show()
