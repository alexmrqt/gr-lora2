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

class css_timing_err_detector(gr.sync_block):
    """
    docstring for block css_timing_err_detector
    """
    def __init__(self, M, algo=1):
        gr.sync_block.__init__(self,
            name="css_timing_err_detector",
            in_sig=[numpy.complex64],
            out_sig=[])

        self.M = M
        self.algo = algo
        self.demodulator = css_demod_algo(self.M)
        self.sym_count = 1

        self.sym_buff = numpy.zeros(3, dtype=numpy.int16)
        self.prev_spectrum = numpy.zeros(M, dtype=numpy.complex64)

        self.message_port_register_out(pmt.intern("time"))

        self.set_output_multiple(self.M)

    def work(self, input_items, output_items):
        in0 = input_items[0]
        est_delay = 0.0

        n_syms = len(in0) // self.M
        for i in range(0, n_syms):
            sig = in0[i*self.M:(i+1)*self.M]

            (sym, spectrum) = \
                    self.demodulator.demodulate_with_spectrum(sig)

            self.sym_buff = numpy.roll(self.sym_buff, -1)
            self.sym_buff[2] = sym

            if self.sym_count > 2:
                if (self.sym_buff[1] != self.sym_buff[0]) and (self.sym_buff[1] != self.sym_buff[2]):
                    est_delay = numpy.abs(self.prev_spectrum[self.sym_buff[0]]) \
                            - numpy.abs(self.prev_spectrum[self.sym_buff[2]])
                    if self.algo == 2:
                        est_delay = numpy.sign(est_delay)*(self.M-numpy.abs(spectrum[0][sym]))
                    if self.algo == 3:
                        est_delay += numpy.sign(est_delay)*(self.M-numpy.abs(spectrum[0][sym]))
                        est_delay *= 0.5

                    self.message_port_pub(pmt.intern("time"),
                            pmt.from_float(numpy.float64(est_delay)))
            else:
                self.sym_count += 1

            self.prev_spectrum = spectrum[0]

        return len(input_items[0])

