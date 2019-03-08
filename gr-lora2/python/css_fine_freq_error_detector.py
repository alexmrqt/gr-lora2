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

class css_fine_freq_error_detector(gr.sync_block):
    """
    docstring for block css_fine_freq_error_detector
    """
    def __init__(self, M):
        gr.sync_block.__init__(self,
            name="css_fine_freq_error_detector",
            in_sig=[(numpy.complex64, M)],
            out_sig=[])

        self.M = M

        self.reg_syms = numpy.zeros(2, dtype=numpy.int)
        self.reg_complex = numpy.zeros(2, dtype=numpy.complex64)

        self.message_port_register_out(pmt.intern("time"))

    def work(self, input_items, output_items):
        in0 = input_items[0]
        est_delay = 0.0

        for i in range(0, len(in0)):
            self.reg_syms = numpy.roll(self.reg_syms, -1)
            self.reg_complex = numpy.roll(self.reg_complex, -1)

            in0[i] /= numpy.sum(numpy.abs(in0[i])**2)
            self.reg_syms[-1] = numpy.argmax(numpy.abs(in0[i]))
            self.reg_complex[-1] = in0[i][self.reg_syms[-1]]

            est_delay = numpy.abs(in0[i][(self.reg_syms[-1]-1)%self.M]) \
                    - numpy.abs(in0[i][(self.reg_syms[-1]+1)%self.M])
            est_delay *= (1.0 - numpy.abs(self.reg_complex[-1])) * self.M

            self.message_port_pub(pmt.intern("time"), pmt.from_float(numpy.float64(est_delay)))

        return len(input_items[0])

