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

from gnuradio import analog
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio.filter import firdes
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
        self.preamble_detector = lora2.lora_preamble_detect(self.SF, 8)
        self.payload_extractor = lora2.lora_implicit_get_payload(self.SF, self.n_syms*self.SF/8, 0, False)
        self.add_reversed_chirps = lora2.lora_add_reversed_chirps(self.SF, self.interp, "packet_len", "payload", "rev_chirps")
        self.add_preamble = lora2.lora_add_preamble(8, 0x12, "packet_len", "sync_word", "payload")
        self.freq_xlating = lora2.freq_xlating(0.0, 'freq_offset')
        self.css_mod = lora2.css_mod(self.M, self.interp, 'packet_len')
        self.css_demod = grc_css_demod(self.M)
        self.vector_source = blocks.vector_source_s(self.syms_vec.tolist(), False, 1, [])
        self.vector_sink = blocks.vector_sink_s(1, self.n_syms)
        self.to_tagged = blocks.stream_to_tagged_stream(gr.sizeof_short, 1, self.n_syms, 'packet_len')
        self.multiplicator = blocks.multiply_vcc(1)
        self.delayer = blocks.delay(gr.sizeof_gr_complex*1, self.delay)
        self.adder = blocks.add_vcc(1)
        self.cfo_source = analog.sig_source_c(1.0, analog.GR_COS_WAVE, self.cfo, 1, 0)
        self.noise_source = analog.noise_source_c(analog.GR_GAUSSIAN, self.noise_var, 0)

        self.debug_sink = blocks.vector_sink_s(1, 1024)

        ##################################################
        # Connections
        ##################################################
        #Modulator
        self.connect((self.vector_source, 0), (self.to_tagged, 0))
        self.connect((self.to_tagged, 0), (self.add_preamble, 0))
        self.connect((self.add_preamble, 0), (self.css_mod, 0))
        self.connect((self.css_mod, 0), (self.add_reversed_chirps, 0))
        self.connect((self.add_reversed_chirps, 0), (self.adder, 1))

        self.connect((self.add_preamble, 0), (self.debug_sink, 0))

        #Channel
        self.connect((self.noise_source, 0), (self.adder, 0))
        self.connect((self.adder, 0), (self.multiplicator, 1))
        self.connect((self.cfo_source, 0), (self.multiplicator, 0))
        self.connect((self.multiplicator, 0), (self.delayer, 0))
        self.connect((self.delayer, 0), (self.preamble_detector, 0))

        #Demodulator
        self.connect((self.preamble_detector, 0), (self.freq_xlating, 0))
        self.connect((self.freq_xlating, 0), (self.css_demod, 0))
        self.connect((self.css_demod, 0), (self.payload_extractor, 0))
        self.connect((self.payload_extractor, 0), (self.vector_sink, 0))

if __name__ == "__main__":
    #Parameters
    n_syms = 1024
    SF = 9
    syms_vec = numpy.random.randint(0, 2**SF, n_syms, dtype=numpy.uint16)

    #Setup block
    tb = lora_sync_test(SF, syms_vec, 0, 0, 0)

    #Simulate
    tb.start()
    tb.stop()
    tb.wait()

    #Retrieve data
    syms_vec_demod = numpy.array(tb.vector_sink.data(), dtype=numpy.uint16)
    print(tb.debug_sink.data())
    print(syms_vec_demod)

    #Compute BER
    n_bits = SF*n_syms
    n_error = 0

    bits_vec = numpy.unpackbits(syms_vec.view(numpy.uint8))
    bits_vec_demod = numpy.unpackbits(syms_vec_demod.view(numpy.uint8))
    n_error = numpy.sum(numpy.abs(bits_vec - bits_vec_demod))

    BER = float(n_error)/n_bits
    print('BER: ' + str(BER))
