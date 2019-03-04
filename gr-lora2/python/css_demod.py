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

class css_demod(gr.sync_block):
    """
    docstring for block css_demod
    """
    def __init__(self, M, freq_loop_gain):
        gr.sync_block.__init__(self,
            name="css_demod",
            in_sig=[(numpy.complex64,M)],
            out_sig=[numpy.uint16, (numpy.complex64, M), numpy.float32])

        self.M = M
        self.freq_loop_gain = freq_loop_gain
        self.k = numpy.arange(0, self.M)

        self.demodulator = css_demod_algo(self.M)

        self.cfo_est = 0.0
        self.init_phase = 0.0
        #Keep track of the last two phases
        self.phase_buff = numpy.zeros(2, dtype=numpy.float32)

    def work(self, input_items, output_items):
        in0 = input_items[0]
        out0 = output_items[0]
        out1 = output_items[1]
        out2 = output_items[2]

        if self.freq_loop_gain > 0.0:
            for i in range(0, len(in0)):
                #Set initial offset, if tag detected
                tags = self.get_tags_in_window(0, i, i+1,
                        pmt.intern('fine_freq_offset'))

                if len(tags) > 0:
                    #If there are multiple tag, only interpret the first one
                    self.cfo_est = pmt.to_float(tags[0].value)

                #Update frequency
                phase_gain = -2 * numpy.pi * self.cfo_est
                phasor = numpy.exp(1j * phase_gain * self.k + self.init_phase)
                self.init_phase = (1j * phase_gain * self.M + self.init_phase)%(2*numpy.pi)

                #Correct frequency and demodulate
                (hard_sym, spectrum) = \
                        self.demodulator.demodulate_with_spectrum(in0[i]*phasor)

                #Set outputs
                out0[i] = hard_sym[0]
                out1[i] = spectrum[0]
                out2[i] = self.cfo_est

                #Frequency discriminator
                self.phase_buff = numpy.roll(self.phase_buff, -1)
                self.phase_buff[-1] = numpy.angle(out1[i][hard_sym][0])

                phase_diff = numpy.mod(numpy.diff(self.phase_buff), 2*numpy.pi)
                phase_diff[phase_diff>numpy.pi] -= 2*numpy.pi

                #Compute error
                error = numpy.mean(phase_diff)
                error *= 0.5/(self.M*numpy.pi)

                #Update frequency
                self.cfo_est += self.freq_loop_gain*error
        else:
            for i in range(0, len(in0)):
                (hard_sym, spectrum) = \
                        self.demodulator.demodulate_with_spectrum(in0[i])
                out0[i] = hard_sym[0]
                out1[i] = spectrum[0]

        return len(output_items[0])
