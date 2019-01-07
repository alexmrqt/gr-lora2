#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018 Alexandre Marquet.
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#

import numpy
import pmt
from gnuradio import gr

#from lora2 import css_mod_algo
from lora2 import css_demod_algo

class lora_preamble_detect(gr.sync_block):
    """
    docstring for block lora_preamble_detect
    """
    def __init__(self, SF, preamble_len):
        gr.sync_block.__init__(self,
            name="lora_preamble_detect",
            in_sig=[numpy.complex64],
            out_sig=[numpy.complex64])

        self.debug = True

        self.M=2**SF
        self.preamble_len = preamble_len

        self.demodulator = css_demod_algo.css_demod_algo(self.M)
        self.preamble_value = 0
        self.sync_value = [0, 0]
        self.sof_value = 0

        #Buffers are initially set to -1
        self.conj_buffer = numpy.zeros(2, dtype=numpy.int16) - 1
        self.buffer = numpy.zeros(preamble_len + 4, dtype=numpy.int16) - 1

        self.set_output_multiple(self.M)

    def detect_preamble(self):
        #Buffer not full yet
        if self.buffer[0] == -1:
            return False

        pattern = numpy.repeat(self.buffer[0], self.preamble_len)
        if (self.buffer[0:self.preamble_len] == pattern).all():
            self.preamble_value = self.buffer[0]

            if self.debug == True:
                print('Preamble detected!')

            return True

        return False

    def detect_sync(self):
        self.sync_value[0] = numpy.mod(self.buffer[-4] - self.preamble_value, self.M)
        self.sync_value[1] = numpy.mod(self.buffer[-3] - self.preamble_value, self.M)

        if self.debug == True:
            print('Sync word detected: ' + str(self.sync_value))

        return True

    def detect_sof(self):
        if self.conj_buffer[0] == self.conj_buffer[1]:
            self.sof_value = self.conj_buffer[0]

            if self.debug == True:
                print('SOF detected!')

            return True

        return False

    def tag_end_preamble(self, sym_idx):
        #Compute time and frequency shift
        time_shift = (self.preamble_value + self.sof_value)/2
        freq_shift = (self.preamble_value - self.sof_value)/2

        #Prepare tag
        tag_offset = self.nitems_written(0) + self.M*(sym_idx+1) + self.M/4 - time_shift
        if time_shift > self.M/2:
            tag_offset += self.M
        tag1_key = pmt.intern('pkt_start')
        tag1_value = pmt.PMT_NIL
        tag2_key = pmt.intern('freq_offset')
        tag2_value = pmt.to_pmt(-freq_shift/float(self.M))
        tag3_key = pmt.intern('sync_word')
        tag3_value = pmt.to_pmt(self.sync_value)

        #Append tags
        self.add_item_tag(0, tag_offset, tag1_key, tag1_value)
        self.add_item_tag(0, tag_offset, tag2_key, tag2_value)
        self.add_item_tag(0, tag_offset, tag3_key, tag3_value)


    def work(self, input_items, output_items):
        in0 = input_items[0]
        out0 = output_items[0]

        #Copy input to output
        out0[:] = in0[:]

        #Demodulate received items
        syms = self.demodulator.demodulate(in0)

        #Demodulate with up-chirp
        #(equivalent to non-coherently demodulate conjugate of signal)
        conj_syms = self.demodulator.demodulate(numpy.conjugate(in0))

        #Preamble detection
        for i in range(0, len(syms)):
            #Shift buffer
            self.buffer = numpy.roll(self.buffer, -1)
            self.buffer[-1] = syms[i]

            #Shift buffer
            self.conj_buffer = numpy.roll(self.conj_buffer, -1)
            self.conj_buffer[-1] = conj_syms[i]

            if self.detect_preamble() and self.detect_sync() and self.detect_sof():
                self.tag_end_preamble(i)

            #if self.state == 0: #DETECT_PRE
            #    self.detect_preamble()

            #    continue
            #elif self.state == 1: #DETECT_SYNC
            #    self.detect_sync()
            #    continue
            #else: #DETECT_SOF
            #    self.detect_sof(i)
            #    continue

        return len(output_items[0])
