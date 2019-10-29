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

class css_fine_sfo_detector(gr.sync_block):
    """
    docstring for block css_fine_sfo_detector
    """
    def __init__(self, M, algo=1):
        gr.sync_block.__init__(self,
            name="css_fine_sfo_detector",
            in_sig=[numpy.complex64],
            out_sig=[])

        self.M = M
        self.algo = algo
        self.demodulator = css_demod_algo(self.M)

        #Keep track of the last two delays
        self.delay_buff = numpy.zeros(2, dtype=numpy.float32)
        self.first_sym = True

        self.message_port_register_out(pmt.intern("sfo"))

        self.set_output_multiple(self.M)

    def work(self, input_items, output_items):
        in0 = input_items[0]

        n_syms = len(in0) // self.M
        for i in range(0, n_syms):
            sig = in0[i*self.M:(i+1)*self.M]

            (sym, spectrum) = \
                    self.demodulator.demodulate_with_spectrum(sig)

            prev_sym_complex_val = spectrum[0][(sym-1)%self.M]
            sym_complex_val = spectrum[0][sym]
            next_sym_complex_val = spectrum[0][(sym+1)%self.M]

            est_delay = numpy.abs(prev_sym_complex_val) \
                    - numpy.abs(next_sym_complex_val)
            if self.algo == 1:
                est_delay /= numpy.abs(sym_complex_val) #1
            elif self.algo == 2:
                est_delay *= (1.0 - numpy.abs(sym_complex_val)/self.M)*numpy.pi/self.M #2
            else:
                est_delay = (1.0 - numpy.abs(sym_complex_val)/self.M)*numpy.sign(est_delay) #3

            self.delay_buff = numpy.roll(self.delay_buff, -1)
            self.delay_buff[-1] = est_delay

            ##SFO estimation if at least 2 symbols were demodulated
            if not self.first_sym:
                self.message_port_pub(pmt.intern("sfo"),
                        pmt.from_float(numpy.float64(numpy.diff(self.delay_buff))))
            else:
                self.first_sym = False

        return len(input_items[0])

