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

import numpy
from gnuradio import gr
from lora2 import css_demod_algo

class css_fine_cfo_track(gr.decim_block):
    """
    docstring for block css_fine_cfo_track
    """
    def __init__(self, M, B):
        gr.decim_block.__init__(self,
            name="css_fine_cfo_track",
            in_sig=[numpy.complex64],
            out_sig=[numpy.float32], decim=M)

        self.M = M
        self.b1 = B
        self.first_sym = True

        self.demodulator = css_demod_algo(self.M)

        #CFO estimate
        self.cfo = 0.0

        #Keep track of the phases of the two last symbols
        self.phase_buff = numpy.zeros(2, dtype=numpy.float32)
        #Keep track of the phase for the VCO
        self.phase = 0.0

    def cfo_detect(self):
        #Frequency discriminator
        #phase_diff = numpy.mod(numpy.diff(self.phase_buff), 2*numpy.pi)
        #phase_diff[phase_diff>numpy.pi] -= 2*numpy.pi
        phase_diff = numpy.mod(numpy.diff(self.phase_buff)+numpy.pi, 2*numpy.pi)-numpy.pi
        #phase_diff[phase_diff>numpy.pi] -= 2*numpy.pi

        #Compute error
        return phase_diff*0.5/(self.M*numpy.pi)

    def cfo_correct(self, in_sig):
        #VCO output
        phasor = numpy.exp(-1j*2*numpy.pi*self.cfo*numpy.arange(0, self.M) + 1j*self.phase)

        #Update initial phase
        self.phase = numpy.mod(self.phase -2*numpy.pi*self.cfo*(self.M-1), 2*numpy.pi)

        #Return input signal mixed with VCO output
        return in_sig*phasor

    def work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]

        n_syms = len(in0) // self.M
        for i in range(0, n_syms):
            (hard_sym, spectrum) = self.demodulator.demodulate_with_spectrum(
                    self.cfo_correct(in0[i*self.M:(i+1)*self.M]))

            self.phase_buff = numpy.roll(self.phase_buff, -1)
            self.phase_buff[-1] = numpy.angle(spectrum[0][hard_sym])

            ##CFO estimation if at least 2 symbols were demodulated
            if not self.first_sym:
                #Loop Filter
                self.cfo += self.b1 * self.cfo_detect()
            else:
                self.first_sym = False

            out[i] = self.cfo

        return len(output_items[0])

