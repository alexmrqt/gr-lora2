#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2019 Alexandre Marquet.
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

import pmt
import numpy
from gnuradio import gr

from lora2 import css_demod_algo
from lora2 import mmse_fir_fractional_delayer

class css_demod(gr.basic_block):
    """
    docstring for block css_demod
    """
    def __init__(self, M, freq_loop_gain, time_loop_gain):
        gr.basic_block.__init__(self,
            name="css_demod",
            in_sig=[numpy.complex64],
            out_sig=[numpy.uint16, (numpy.complex64, M), numpy.float32, numpy.float32])

        self.M = M
        self.freq_loop_gain = freq_loop_gain
        self.time_loop_gain = time_loop_gain
        self.k = numpy.arange(0, self.M)

        self.demodulator = css_demod_algo(self.M)
        self.delayer = mmse_fir_fractional_delayer.mmse_fir_fractional_delayer()

        self.delay_est = 0.0
        self.cfo_est = 0.0
        self.init_phase = 0.0
        #Keep track of the last two phases
        self.phase_buff = numpy.zeros(2, dtype=numpy.float32)

        #Block tag propagation
        self.set_tag_propagation_policy(gr.TPP_CUSTOM)

    def forecast(self, noutput_items, ninput_items_required):
        #Most of the time, this block simply decimates by M
        ninput_items_required[0] = self.M * noutput_items

    def general_work(self, input_items, output_items):
        in0 = input_items[0]
        out0 = output_items[0]
        out1 = output_items[1]
        out2 = output_items[2]
        out3 = output_items[3]

        sym_count = 0

        n_syms = min(len(in0) // self.M, len(out0))
        for i in range(0, n_syms):
            #Set initial offset, if tag detected
            tags = self.get_tags_in_window(0, i*self.M, (i+1)*self.M,
                    pmt.intern('fine_freq_offset'))

            if len(tags) > 0:
                #If there are multiple tag, only interpret the first one
                self.cfo_est = pmt.to_float(tags[0].value)
                #Also reset delay estimator and initial phase
                self.init_phase = 0.0
                self.delay_est = 0.0
                sym_count = 0

            #Update frequency
            phase_gain = -2 * numpy.pi * self.cfo_est
            phasor = numpy.exp(1j * (phase_gain * self.k + self.init_phase))
            self.init_phase = (phase_gain * self.M + self.init_phase)%(2*numpy.pi)

            #Correct time, frequency and demodulate
            sig = in0[i*self.M:(i+1)*self.M]
            correct_sig = self.delayer.delay(sig*phasor, self.delay_est)
            (hard_sym, spectrum) = \
                    self.demodulator.demodulate_with_spectrum(correct_sig)

            #Add 1 to demodulated symbols counter
            sym_count += 1

            #Set outputs
            out0[i] = hard_sym[0]
            out1[i] = spectrum[0]
            out2[i] = self.cfo_est
            out3[i] = self.delay_est

            ##CFO estimation if at least 2 symbols were demodulated
            if sym_count > 1:
                #Frequency discriminator
                self.phase_buff = numpy.roll(self.phase_buff, -1)
                self.phase_buff[-1] = numpy.angle(out1[i][hard_sym][0])

                phase_diff = numpy.mod(numpy.diff(self.phase_buff), 2*numpy.pi)
                phase_diff[phase_diff>numpy.pi] -= 2*numpy.pi

                #Compute error
                freq_error = numpy.mean(phase_diff)
                freq_error *= 0.5/(self.M*numpy.pi)

                #Update frequency
                self.cfo_est += self.freq_loop_gain*freq_error

            ##Delay estimation
            spectrum[0] /= numpy.sum(numpy.abs(spectrum[0])**2)
            prev_sym_complex_val = spectrum[0][(hard_sym[0]-1)%self.M]
            sym_complex_val = spectrum[0][hard_sym[0]]
            next_sym_complex_val = spectrum[0][(hard_sym[0]+1)%self.M]

            delay_error = numpy.abs(prev_sym_complex_val) \
                    - numpy.abs(next_sym_complex_val)
            delay_error *= (1.0 - numpy.abs(sym_complex_val)) * self.M

            #Update delay
            self.delay_est += self.time_loop_gain*delay_error
            self.delay_est = self.delay_est%1.0

        self.consume(0, n_syms*self.M)
        return n_syms
