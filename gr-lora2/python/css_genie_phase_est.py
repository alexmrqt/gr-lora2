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
import pmt
from gnuradio import gr
import css_demod_algo

class css_genie_phase_est(gr.sync_block):
    """
    docstring for block css_genie_phase_est
    """
    def __init__(self, M):
        gr.sync_block.__init__(self,
            name="css_genie_phase_est",
            in_sig=[numpy.complex64],
            out_sig=[numpy.complex64])

        self.M = M
        self.demod = css_demod_algo.css_demod_algo(self.M)

        self.set_output_multiple(self.M)

    def work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]

        #Phase estimation for each symbol
        demod = self.demod.complex_demodulate(in0)
        sym_phase = numpy.angle(demod[1])

        #Tagging
        for i in range(0, len(sym_phase)):
            self.add_item_tag(0, self.M*i + self.nitems_written(0),
                    pmt.intern('phase'),
                    pmt.to_pmt(numpy.exp(-1j*sym_phase[i])))

        #Pass input to output
        out[:] = in0

        return len(output_items[0])

