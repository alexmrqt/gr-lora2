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

class css_timing_err_track(gr.basic_block):
    """
    docstring for block css_timing_err_track
    """
    def __init__(self, M, B, res):
        gr.basic_block.__init__(self,
            name="css_timing_err_track",
            in_sig=[numpy.complex64],
            out_sig=[numpy.float32])

        self.M = M
        self.b1 = B
        self.res = res
        self.global_sym_count = 0

        self.demodulator = css_demod_algo(self.M)

        self.sym_buff = numpy.zeros(3, dtype=numpy.int16)
        self.delay_buff = numpy.zeros(2, dtype=numpy.int16)
        self.prev_spectrum = numpy.zeros(M, dtype=numpy.complex64)

        self.est_delay = 0.0
        self.est_cum_delay = 0

        #self.set_history(self.M)
        self.set_relative_rate(1.0/self.M)

    def forecast(self, noutput_items, ninput_items_required):
        #setup size of input_items[i] for work call
        for i in range(len(ninput_items_required)):
            ninput_items_required[i] = noutput_items * self.M

    def timing_detect(self):
        if (self.sym_buff[1] != self.sym_buff[0]) and (self.sym_buff[1] != self.sym_buff[2]):
            prev_sym = numpy.mod(self.sym_buff[0] + self.delay_buff[0], self.M)
            next_sym = numpy.mod(self.sym_buff[2] - self.delay_buff[1], self.M)

            return numpy.abs(self.prev_spectrum[prev_sym]) \
                    - numpy.abs(self.prev_spectrum[next_sym])
        else:
            return 0.0

    def general_work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]


        sym_count = 0
        start_idx = 0
        stop_idx = self.M - 1
        while (stop_idx < len(in0)) and (sym_count < len(out)):
            (sym, spectrum) = self.demodulator.demodulate_with_spectrum(\
                    in0[start_idx:(stop_idx+1)])

            self.sym_buff = numpy.roll(self.sym_buff, -1)
            self.sym_buff[2] = sym

            #Correct symbol frequency shift due to delaying
            sym = (sym-self.est_cum_delay)%self.M

            if self.global_sym_count > 2:
                #Loop Filter
                err = self.timing_detect()
                self.est_delay -= self.b1 * err
                
                #Keep delay contained in +/- M/2 to prevent symbol loss
                if self.est_delay > self.M/2:
                    self.est_delay = self.M/2
                elif self.est_delay < -self.M/2:
                    self.est_delay = -self.M/2

                #Compute estimated integer delay
                int_delay = int(numpy.round(-self.est_delay))
                if (numpy.abs(int_delay) < self.res):
                    int_delay = 0

                #Update cumulative delay
                self.est_cum_delay += int_delay

                #Update delay buffer
                self.delay_buff = numpy.roll(self.delay_buff, -1)
                self.delay_buff[1] = int_delay
            else:
                self.global_sym_count += 1

            #Save this spectrum for next timing error estimation
            self.prev_spectrum = spectrum[0]

            #Output
            out[sym_count] = self.est_cum_delay

            #Takes integer delay into account
            start_idx += self.M + self.delay_buff[1]
            stop_idx = start_idx + self.M - 1

            #Update state variables
            self.est_delay += self.delay_buff[1]

            sym_count += 1

        #Tell GNURadio how many items were produced
        self.consume(0, start_idx)
        return sym_count
