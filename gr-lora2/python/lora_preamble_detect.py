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

        self.M=2**SF
        self.preamble_len = preamble_len
        self.thres = thres

        self.demod = css_demod_algo.css_demod_algo(self.M)
        self.demod_conj = css_demod_algo.css_demod_algo(self.M, True)

        #Buffers are initially set to -1
        self.conj_buffer = numpy.zeros(2, dtype=numpy.int) - 1
        self.conj_buffer_soft = numpy.zeros(2)

        if preamble_len > 2:
            self.buffer = numpy.zeros(preamble_len + 2, dtype=numpy.int) - 1
            self.complex_buffer = numpy.zeros(preamble_len + 2, dtype=numpy.complex64)
            self.buffer_meta = [dict() for i in range(0, preamble_len + 2)]
        else:
            self.buffer = numpy.zeros(5, dtype=numpy.int) - 1
            self.complex_buffer = numpy.zeros(5, dtype=numpy.complex64)
            self.buffer_meta = [dict() for i in range(0, 5)]

        self.set_output_multiple(self.M)

    def fine_freq_estimate(self):
        #Compute phases of complex samples corresponding to detected symbols
        phases = numpy.angle(self.complex_buffer)

        #Defferentiate phase, modulo 2pi, to get frequency
        phase_diff = numpy.mod(numpy.diff(phases), 2*numpy.pi)
        phase_diff[phase_diff>numpy.pi] -= 2*numpy.pi

        fine_freq_estimate = numpy.mean(phase_diff)

        #Correct estimate with the slope of the estimator
        fine_freq_estimate *= 0.5/((self.M-self.M/16)*numpy.pi)

        self.buffer_meta[-1]['fine_freq_shift'] = fine_freq_estimate

    def detect_preamble(self):
        #Buffer not full yet
        if self.buffer[0] == -1:
            return False

        mean = numpy.mean(self.buffer[-(self.preamble_len+2):-2])
        mean_err_sq = numpy.sum(numpy.abs(self.buffer[-(self.preamble_len+2):-2] - mean)**2)
        max_err_sq = self.M**2

        if(mean_err_sq/max_err_sq < self.thres):
            self.buffer_meta[self.preamble_len-1]['preamble_value'] = numpy.uint16(numpy.round(mean))

            return True

        return False


    def detect_sync(self, preamble_value):
        sync_val = [numpy.mod(numpy.int16(self.buffer[-2]) - preamble_value, self.M),
                    numpy.mod(numpy.int16(self.buffer[-1]) - preamble_value, self.M)]

        #First sync value must be different from preamble value
        if sync_val[0] < 8:
            return False

        self.buffer_meta[-1]['sync_value'] = sync_val

        return True

    def check_downchirps(self):
        #Allow an error of +/- 1 on the two symbols
        if numpy.abs(self.conj_buffer[0] - self.conj_buffer[1]) <= 1:
            #Return symbol with the most confidence
            idx = numpy.argmax(self.conj_buffer_soft)

            return self.conj_buffer[idx]

        return -1

    def compute_tf_shifts(self, preamble_value, sof_value):
        #Compute time and frequency shift
        time_shift = (preamble_value - sof_value)/2
        freq_shift = (preamble_value + sof_value)/2

        if self.M >= 512:
            freq_shift = freq_shift%(self.M/2)
            #We cannot correct frequency shifts higher than M/4 and lower than -M/4
            if freq_shift >= self.M/4:
                freq_shift -= self.M/2
        else:
            freq_shift -= self.M/2 + 5

        time_shift = -time_shift
        if time_shift > numpy.abs(freq_shift):
            time_shift -= self.M/2
        elif time_shift < -numpy.abs(freq_shift):
            time_shift += self.M/2

        return (freq_shift, time_shift)


    def tag_end_preamble(self, freq_shift, fine_freq_shift, time_shift, sync_value, sof_idx):
        #Prepare tag
        #This delay estimator has an uncertainty of +/-M (by steps of M/2).
        #So we put the tag M items before the estimated SOF item, to allow
        #A successive block to remove this uncertainty.
        tag_offset = self.nitems_written(0) + time_shift + sof_idx*self.M \
                + self.M/4

        tag1_key = pmt.intern('fine_freq_offset')
        tag1_value = pmt.to_pmt(float(fine_freq_shift))
        tag2_key = pmt.intern('freq_offset')
        tag2_value = pmt.to_pmt(freq_shift/float(self.M))
        tag3_key = pmt.intern('sync_word')
        tag3_value = pmt.to_pmt(sync_value)
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

        n_syms = len(in0)//self.M

        for i in range(0, n_syms):
            #Demod and shift buffer
            self.buffer = numpy.roll(self.buffer, -1)
            self.complex_buffer = numpy.roll(self.complex_buffer, -1)
            self.buffer_meta.pop(0)
            self.buffer_meta.append(dict())

            (hard_sym, complex_sym) = \
                    self.demod.complex_demodulate(in0[i*self.M:(i+1)*self.M])
            (self.buffer[-1], self.complex_buffer[-1]) = (hard_sym[0], complex_sym[0])

            #Conjugate demod and shift conjugate buffer, if needed
            #AABBC or ABBCC
            #   ^       ^
            if ('sync_value' in self.buffer_meta[-2]) or ('sync_value' in self.buffer_meta[-3]):
                self.conj_buffer = numpy.roll(self.conj_buffer, -1)
                self.conj_buffer_soft = numpy.roll(self.conj_buffer_soft, -1)

                (hard, soft) = self.demod_conj.soft_demodulate(
                                                in0[i*self.M:(i+1)*self.M])
                self.conj_buffer[-1] = hard[0]
                self.conj_buffer_soft[-1] = soft[0]

            #Check for preamble
            self.detect_preamble()

            #Retrieve sync word value and compute fine frequency shift
            #AAABB
            #  ^
            if 'preamble_value' in self.buffer_meta[-3]:
                preamble_value = self.buffer_meta[-3]['preamble_value']
                self.detect_sync(preamble_value)

                self.fine_freq_estimate()

            #Compute time-frequency shift if downchirps has same value
            #ABBCC
            #  ^
            if 'sync_value' in self.buffer_meta[-3]:
                sof_value = self.check_downchirps()

                ##Compute shifts
                if sof_value >= 0:
                    preamble_value = self.buffer_meta[-5]['preamble_value']
                    (freq_shift, time_shift) = self.compute_tf_shifts(preamble_value, sof_value)

                    #Tag
                    fine_freq_shift = self.buffer_meta[-3]['fine_freq_shift']
                    sync_value = self.buffer_meta[-3]['sync_value']
                    self.tag_end_preamble(freq_shift, fine_freq_shift, time_shift, sync_value, i)

        #Copy input to output
        out0[:] = in0[:]

        return len(output_items[0])
