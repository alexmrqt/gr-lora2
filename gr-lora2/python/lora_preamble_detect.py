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
    def __init__(self, SF, preamble_len, debug=False, thres=1e-4):
        gr.sync_block.__init__(self,
            name="lora_preamble_detect",
            in_sig=[numpy.complex64],
            out_sig=[numpy.complex64])

        self.debug = debug

        self.M=2**SF
        self.preamble_len = preamble_len
        self.thres = thres

        self.demod = css_demod_algo.css_demod_algo(self.M)
        self.demod_conj = css_demod_algo.css_demod_algo(self.M, True)
        self.preamble_value = 0
        self.sync_value = [0, 0]
        self.sof_value = 0

        #Buffers are initially set to -1
        self.conj_buffer = numpy.zeros(2, dtype=numpy.int) - 1
        self.buffer = numpy.zeros(preamble_len + 2, dtype=numpy.int) - 1

        self.detect_downchirp0 = False
        self.detect_downchirp1 = False

        self.set_output_multiple(self.M)

    def detect_preamble(self):
        #Buffer not full yet
        if self.buffer[0] == -1:
            return False

        mean = numpy.mean(self.buffer[0:self.preamble_len])
        mean_err_sq = numpy.sum(numpy.abs(self.buffer[0:self.preamble_len]-mean)**2)
        max_err_sq = self.M**2

        if(mean_err_sq/max_err_sq < self.thres):
            self.preamble_value = numpy.uint16(numpy.round(mean))

            if self.debug == True:
                print('Preamble detected: ' + str(self.preamble_value))

            self.detect_sync()
            self.detect_downchirp0 = True


    def detect_sync(self):
        self.sync_value[0] = numpy.mod(numpy.int16(self.buffer[-2]) - self.preamble_value, self.M)
        self.sync_value[1] = numpy.mod(numpy.int16(self.buffer[-1]) - self.preamble_value, self.M)

        #First sync value must be different from preamble value
        if self.sync_value[0] < 8:
            return False

        if self.debug == True:
            print('Sync word detected: ' + str(self.sync_value))

        return True

    def check_downchirps(self):
        if self.conj_buffer[0] == self.conj_buffer[1]:
            self.sof_value = self.conj_buffer[0]

            if self.debug == True:
                print('SOF detected: ' + str(self.sof_value))

            return True

        return False

    def find_first_symbol(self):
        pass

    def tag_end_preamble(self, sym_idx):
        #Compute time and frequency shift
        time_shift = (self.preamble_value - self.sof_value)/2
        freq_shift = (self.preamble_value + self.sof_value)/2

        freq_shift = freq_shift%(self.M/2)
        #We cannot correct frequency shifts higher than M/4 and lower than -M/4
        if freq_shift >= self.M/4:
            freq_shift -= self.M/2

        time_shift = -time_shift
        if time_shift > numpy.abs(freq_shift):
            time_shift -= self.M/2
        elif time_shift < -numpy.abs(freq_shift):
            time_shift += self.M/2

        #Prepare tag
        tag_offset = self.nitems_written(0) + time_shift + (sym_idx+1)*self.M + self.M/4

        tag1_key = pmt.intern('pkt_start')
        tag1_value = pmt.PMT_NIL
        tag2_key = pmt.intern('freq_offset')
        tag2_value = pmt.to_pmt(freq_shift/float(self.M))
        tag3_key = pmt.intern('sync_word')
        tag3_value = pmt.to_pmt(self.sync_value)
        tag4_key = pmt.intern('time_offset')
        tag4_value = pmt.to_pmt(time_shift)

        #Append tags
        self.add_item_tag(0, tag_offset, tag1_key, tag1_value)
        self.add_item_tag(0, tag_offset, tag2_key, tag2_value)
        self.add_item_tag(0, tag_offset, tag3_key, tag3_value)
        self.add_item_tag(0, tag_offset, tag4_key, tag4_value)

    def work(self, input_items, output_items):
        in0 = input_items[0]
        out0 = output_items[0]

        #Copy input to output
        out0[:] = in0[:]

        n_syms = len(in0)//self.M
        #Preamble detection
        for i in range(0, n_syms):
            if self.detect_downchirp1 or self.detect_downchirp0:
                #Conjugate demod
                self.conj_buffer = numpy.roll(self.conj_buffer, -1)
                self.conj_buffer[-1] = self.demod_conj.demodulate(in0[i*self.M:(i+1)*self.M])

            if self.detect_downchirp1:
                #SOF detection
                if self.check_downchirps():
                    self.find_first_symbol()
                    self.tag_end_preamble(i)

                self.detect_downchirp1 = False

            if self.detect_downchirp0:
                self.detect_downchirp0 = False
                self.detect_downchirp1 = True

            #Demod
            self.buffer = numpy.roll(self.buffer, -1)
            self.buffer[-1] = self.demod.demodulate(in0[i*self.M:(i+1)*self.M])
            #Preamble detection
            self.detect_preamble()

        return len(output_items[0])
