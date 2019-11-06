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

from lora2 import css_demod_algo, css_mod_algo

class css_fine_delay_detector(gr.decim_block):
    """
    docstring for block css_fine_delay_detector
    """
    def __init__(self, M, interp=1):
        gr.decim_block.__init__(self,
            name="css_fine_delay_detector",
            in_sig=[numpy.complex64],
            out_sig=[numpy.float32], decim=M*interp)

        self.M = M
        self.Q = interp

        self.demodulator = css_demod_algo(self.M)
        self.modulator = css_mod_algo(self.M, self.Q)

    def work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]

        n_syms = len(in0) // (self.M*self.Q)
        for i in range(0, n_syms):
            sig = in0[i*(self.M*self.Q):(i+1)*(self.M*self.Q)]

            hard_sym = self.demodulator.demodulate(sig[::self.Q])

            reconst_sig = numpy.zeros(self.M*self.Q + 2*self.Q, dtype=numpy.complex64)
            reconst_sig[self.Q:-self.Q] = self.modulator.modulate(hard_sym)

            out[i] = numpy.argmax(numpy.correlate(sig, reconst_sig)) - self.Q

        return len(output_items[0])

