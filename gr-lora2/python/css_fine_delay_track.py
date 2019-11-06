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
from lora2 import css_mod_algo
from lora2 import css_demod_algo

class css_fine_delay_track(gr.decim_block):
    """
    docstring for block css_fine_delay_track
    """
    def __init__(self, M, interp, B):
        gr.basic_block.__init__(self,
            name="css_fine_delay_track",
            in_sig=[numpy.complex64],
            out_sig=[numpy.float32])

        self.M = M
        self.Q = interp
        self.b1 = B

        self.demodulator = css_demod_algo(self.M)
        self.modulator = css_mod_algo(self.M, self.Q)

        #Delay estimate
        self.delay = 0.0
        self.cum_delay = 0.0

    def forecast(self, noutput_items, ninput_items_required):
        #Most of the time, this block simply decimates by M*Q
        ninput_items_required[0] = self.M * self.Q * noutput_items

    def delay_detect(self, sig, hard_sym):
        reconst_sig = numpy.zeros(self.M*self.Q + 2*self.Q, dtype=numpy.complex64)
        reconst_sig[self.Q:-self.Q] = self.modulator.modulate(hard_sym)

        return numpy.argmax(numpy.correlate(sig, reconst_sig)) - self.Q

    def general_work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]

        start_idx = 0
        stop_idx = start_idx + self.M*self.Q
        sym_count = 0
        while (stop_idx < len(in0)) and (sym_count < len(out)):
            sig = in0[start_idx:stop_idx]

            hard_sym = self.demodulator.demodulate(sig[::self.Q])

            self.delay += self.b1 * self.delay_detect(sig, hard_sym)

            self.cum_delay += int(numpy.round(self.delay))
            out[sym_count] = self.cum_delay

            start_idx += self.M*self.Q + int(numpy.round(self.delay))
            stop_idx = start_idx + self.M*self.Q

            self.delay -= int(numpy.round(self.delay))

            sym_count += 1

        #Tell GNURadio how many items were produced
        self.consume(0, start_idx)
        return sym_count
