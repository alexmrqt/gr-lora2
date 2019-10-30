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

        self.M=int(2**SF)
        self.preamble_len = preamble_len
        self.thres = thres

        self.demod = css_demod_algo(self.M)
        self.demod_conj = css_demod_algo(self.M, True)

        #Buffers are initially set to -1
        self.conj_buffer = numpy.zeros(2, dtype=numpy.int) - 1
        self.conj_complex_buffer = numpy.zeros(2, dtype=numpy.complex64)

        if preamble_len > 2:
            self.buffer = numpy.zeros(preamble_len + 2, dtype=numpy.int) - 1
            self.complex_buffer = numpy.zeros(preamble_len + 2, dtype=numpy.complex64)
            self.buffer_meta = [dict() for i in range(0, preamble_len + 2)]
        else:
            self.buffer = numpy.zeros(5, dtype=numpy.int) - 1
            self.complex_buffer = numpy.zeros(5, dtype=numpy.complex64)
            self.buffer_meta = [dict() for i in range(0, 5)]

        self.set_output_multiple(self.M)

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

        #Save sync value
        self.buffer_meta[-1]['sync_value'] = numpy.int16(sync_val)

        tmp1 = self.complex_buffer[2:-1] * numpy.conj(self.complex_buffer[1:-2])
        tmp2 = numpy.angle(tmp1[1:] * numpy.conj(tmp1[:-1]))
        tmp2 *= 1.0/(2*self.M*numpy.pi)

        #Compute and save fine frequency offset, corresponding to
        #fine_cfo + fine_delay
        #Compute phases of complex samples corresponding to detected symbols
        #Ignore first and last symbol as they are subject to time misalignment
        phase_diff = numpy.angle(self.complex_buffer[2:-1] \
                    * numpy.conj(self.complex_buffer[1:-2]))
        fine_offset = numpy.mean(phase_diff)

        self.buffer_meta[-1]['fine_offset'] = fine_offset

        return True

    def check_downchirps(self):
        #Allow an error of +/- 1 on the two symbols
        if numpy.abs(self.conj_buffer[0] - self.conj_buffer[1]) <= 1:
            #Return symbol with the most confidence
            idx = numpy.argmax(numpy.abs(self.conj_complex_buffer))

            #Compute and save fine frequency offset, corresponding to
            #fine_cfo - fine_delay
            conj_fine_offset = numpy.angle(self.conj_complex_buffer[1] \
                        * numpy.conj(self.conj_complex_buffer[0]))

            return (self.conj_buffer[idx], conj_fine_offset)

        return None

    def compute_tf_shifts(self, preamble_value, sof_value):
        #Compute time and frequency shift
        time_shift = (preamble_value - sof_value)//2
        freq_shift = (preamble_value + sof_value)//2

        if self.M >= 512:
            freq_shift = freq_shift%(self.M//2)
            #We cannot correct frequency shifts higher than M/4 and lower than -M/4
            if freq_shift >= self.M//4:
                freq_shift -= self.M//2
        else:
            #This strangeness is likely due to the modulo M nature of the computation
            freq_shift -= self.M//2 + 5

        time_shift = -time_shift
        if time_shift > numpy.abs(freq_shift):
            time_shift -= self.M//2
        elif time_shift < -numpy.abs(freq_shift):
            time_shift += self.M//2

        return (freq_shift, time_shift)

    def compute_fine_tf_shifts(self, fine_offset, conj_fine_offset):
        #Compute time and frequency shift
        fine_time_shift = (fine_offset - conj_fine_offset)/(2*2*numpy.pi)
        fine_freq_shift = (fine_offset + conj_fine_offset)/(2*self.M*2*numpy.pi)

        return (fine_freq_shift, fine_time_shift)

    def tag_end_preamble(self, freq_shift, fine_freq_shift, time_shift, fine_time_shift, sync_value, sof_idx):
        #Prepare tag
        #This delay estimator has an uncertainty of +/-M (by steps of M/2).
        #So we put the tag M items before the estimated SOF item, to allow
        #A successive block to remove this uncertainty.
        tag_offset = self.nitems_written(0) + time_shift + sof_idx*self.M \
                + self.M//4

        tag1_key = pmt.intern('fine_freq_offset')
        tag1_value = pmt.to_pmt(fine_freq_shift)
        tag2_key = pmt.intern('coarse_freq_offset')
        tag2_value = pmt.to_pmt(freq_shift/self.M)
        tag3_key = pmt.intern('sync_word')
        tag3_value = pmt.to_pmt(sync_value)
        tag4_key = pmt.intern('time_offset')
        tag4_value = pmt.to_pmt(int(time_shift))
        #tag5_key = pmt.intern('fine_time_offset')
        #tag5_value = pmt.to_pmt(fine_time_shift)

        #Append tags
        self.add_item_tag(0, tag_offset, tag1_key, tag1_value)
        self.add_item_tag(0, tag_offset, tag2_key, tag2_value)
        self.add_item_tag(0, tag_offset, tag3_key, tag3_value)
        self.add_item_tag(0, tag_offset, tag4_key, tag4_value)
        #self.add_item_tag(0, tag_offset, tag5_key, tag5_value)

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
            self.buffer[-1] = hard_sym[0]
            self.complex_buffer[-1] = complex_sym[0]

            #Conjugate demod and shift conjugate buffer, if needed
            #AABBC or ABBCC
            #   ^       ^
            if ('sync_value' in self.buffer_meta[-2]) or ('sync_value' in self.buffer_meta[-3]):
                self.conj_buffer = numpy.roll(self.conj_buffer, -1)
                self.conj_complex_buffer = numpy.roll(self.conj_complex_buffer, -1)

                (hard_sym, complex_sym) = self.demod_conj.complex_demodulate(
                                                in0[i*self.M:(i+1)*self.M])
                self.conj_buffer[-1] = hard_sym[0]
                self.conj_complex_buffer[-1] = complex_sym[0]

            #Check for preamble
            self.detect_preamble()

            #Retrieve sync word value and compute fine frequency shift
            #AAABB
            #  ^
            if 'preamble_value' in self.buffer_meta[-3]:
                preamble_value = self.buffer_meta[-3]['preamble_value']
                self.detect_sync(preamble_value)

            #Compute time-frequency shift if downchirps has same value
            #ABBCC
            #  ^
            if 'sync_value' in self.buffer_meta[-3]:
                chk_down = self.check_downchirps()
                if not chk_down is None:
                    (sof_value, conj_fine_offset) = chk_down

                    ##Compute shifts
                    if sof_value >= 0:
                        preamble_value = self.buffer_meta[-5]['preamble_value']
                        (freq_shift, time_shift) = self.compute_tf_shifts(preamble_value, sof_value)

                        fine_offset = self.buffer_meta[-3]['fine_offset']
                        (fine_freq_shift, fine_time_shift) = self.compute_fine_tf_shifts(fine_offset, conj_fine_offset)

                        #Tag
                        sync_value = self.buffer_meta[-3]['sync_value']
                        self.tag_end_preamble(freq_shift, fine_freq_shift, time_shift, fine_time_shift, sync_value, i)

        #Copy input to output
        out0[:] = in0[:]

        return len(output_items[0])
