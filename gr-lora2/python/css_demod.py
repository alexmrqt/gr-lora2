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

class css_demod(gr.basic_block):
    """
    docstring for block css_demod
    """
    def __init__(self, M, B_cfo):
        gr.basic_block.__init__(self,
            name="css_demod",
            in_sig=[numpy.complex64],
            out_sig=[numpy.uint16, (numpy.complex64, M), numpy.float32])

        self.M = M
        self.demodulator = css_demod_algo(self.M)
        self.global_sym_count = 0

        ##CFO-related attributes
        self.b1_cfo = B_cfo
        self.est_cfo = 0.0
        self.init_phase = 0.0
        #Keep track of the last two phases
        self.phase_buff = numpy.zeros(2, dtype=numpy.float32)

        ##GNURadio
        self.set_tag_propagation_policy(gr.TPP_CUSTOM)
        self.set_relative_rate(1.0/self.M)

    def forecast(self, noutput_items, ninput_items_required):
        #Most of the time, this block simply decimates by M
        ninput_items_required[0] = self.M * noutput_items

    def cfo_detect(self):
        #Frequency discriminator
        phase_diff = numpy.mod(numpy.diff(self.phase_buff), 2*numpy.pi)
        phase_diff[phase_diff>numpy.pi] -= 2*numpy.pi

        #Compute error
        return phase_diff*0.5/(self.M*numpy.pi)

    def vco_advance(self, freq, step):
        #self.init_phase *= numpy.exp(1j*2*numpy.pi*freq*step)
        self.init_phase = numpy.mod(self.init_phase + 2*numpy.pi*freq*step, 2*numpy.pi)

        return numpy.exp(self.init_phase)

    def vco_advance_vec(self, freq, n_samples):
        k = numpy.arange(0, n_samples)

        phasor = numpy.exp(1j*2*numpy.pi*freq*k + 1j*self.init_phase)

        #Update initial phase
        self.init_phase = numpy.mod(self.init_phase \
                + 2*numpy.pi*freq*(n_samples-1), 2*numpy.pi)

        return phasor

    def cfo_correct(self, in_sig):
        return in_sig*self.vco_advance_vec(-self.est_cfo, self.M)

    def general_work(self, input_items, output_items):
        in0 = input_items[0]
        out0 = output_items[0]
        out1 = output_items[1]
        out2 = output_items[2]

        sym_count = 0

        start_idx = 0
        stop_idx = self.M - 1
        while (stop_idx < len(in0)) and (sym_count < len(out0)):
            (sym, spectrum) = self.demodulator.demodulate_with_spectrum(\
                    self.cfo_correct(in0[start_idx:(stop_idx+1)]))

            self.phase_buff = numpy.roll(self.phase_buff, -1)
            self.phase_buff[-1] = numpy.angle(spectrum[0][sym])

            ##CFO estimation if at least 2 symbols were demodulated
            cfo_err = 0.0
            if self.global_sym_count > 1:
                cfo_err = self.cfo_detect()
                #Loop Filter
                self.est_cfo += self.b1_cfo * cfo_err
            else:
                self.global_sym_count += 1

            #Save this spectrum for next timing error estimation
            self.prev_spectrum = spectrum[0]

            #Next symbol
            start_idx += self.M
            stop_idx = start_idx + self.M - 1

            #Outputs
            out0[sym_count] = sym
            out1[sym_count] = spectrum[0]
            out2[sym_count] = self.est_cfo

            #Increment number of processed symbols in this call of work
            sym_count += 1

        #Tell GNURadio how many items were produced
        self.consume(0, start_idx)
        return sym_count
