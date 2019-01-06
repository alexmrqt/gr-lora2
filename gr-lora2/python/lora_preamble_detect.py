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
    def __init__(self, SF, preamble_len, sync_word):
        gr.sync_block.__init__(self,
            name="lora_preamble_detect",
            in_sig=[numpy.complex64],
            out_sig=[numpy.complex64])

        self.M=2**SF
        self.preamble_len = preamble_len
        self.sync_word = sync_word

        self.demodulator = css_demod_algo.css_demod_algo(self.M)
        self.preamble_value = 0
        self.sof_value = 0

        self.count = 0
        self.state = 0 #0: DETECT_PRE, 1: DETECT_SYNC, 2: DETECT_SOF

        #Buffers are initially set to -1
        self.conj_buffer = numpy.zeros(2, dtype=numpy.int16) - 1
        self.buffer = None
        if(preamble_len == 1):
            self.buffer = numpy.zeros(2, dtype=numpy.int16) - 1
        else:
            self.buffer = numpy.zeros(preamble_len, dtype=numpy.int16) - 1

        self.set_output_multiple(self.M)

    def detect_preamble(self):
        pattern = numpy.repeat(self.buffer[0], self.preamble_len)

        if (self.buffer == pattern).all():
            self.preamble_value = self.buffer[0]
            self.state = 1 #Go to DETECT_SYNC

    def detect_sync(self):
        self.count += 1

        if self.count == 2:
            self.count = 0

            expected_val = self.preamble_value + self.sync_word
            if (self.buffer[-1] == expected_val) and (self.buffer[-2] == expected_val):
                self.state = 2 #Go to DETECT_SOF
            else:
                #Check for preamble presence
                self.detect_preamble()

    def detect_sof(self, input_items, sym_idx):
        self.count += 1

        #Shift buffer
        self.conj_buffer = numpy.roll(self.conj_buffer, -1)

        #Demodulate with up-chirp
        #(equivalent to non-coherently demodulate conjugate of signal)
        self.conj_buffer[-1] = self.demodulator.demodulate(numpy.conjugate(input_items))[0]

        if self.count == 2:
            self.count = 0

            if self.conj_buffer[0] == self.conj_buffer[1]:
                self.sof_value = self.conj_buffer[0]

                self.tag_end_preamble(sym_idx)
            else:
                #Reset conjugate buffer
                self.conj_buffer = numpy.zeros(2, dtype=numpy.int16) - 1

                #Check for preamble presence
                self.detect_preamble()

            #Go to DETECT_PREAMBLE in all case
            self.state = 0

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

        #Append tags
        self.add_item_tag(0, tag_offset, tag1_key, tag1_value)
        self.add_item_tag(0, tag_offset, tag2_key, tag2_value)


    def work(self, input_items, output_items):
        in0 = input_items[0]
        out0 = output_items[0]

        #Copy input to output
        out0[:] = in0[:]

        #Demodulate received items
        syms = self.demodulator.demodulate(in0)

        #Preamble detection
        for i in range(0, len(syms)):
            #Shift buffer
            self.buffer = numpy.roll(self.buffer, -1)
            self.buffer[-1] = syms[i]

            if self.state == 0: #DETECT_PRE
                self.detect_preamble()
                continue
            elif self.state == 1: #DETECT_SYNC
                self.detect_sync()
                continue
            else: #DETECT_SOF
                self.detect_sof(in0[i*self.M:(i+1)*self.M], i)
                continue

        return len(output_items[0])
