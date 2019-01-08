#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019 Lies Temzi, Juan Pablo Hagata, Alexandre Marquet.
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

class lora_deinterleaver(gr.sync_block):
    """
    docstring for block lora_deinterleaver
    """
    def __init__(self, SF, CR):
        gr.sync_block.__init__(self,
            name="lora_deinterleaver",
            in_sig=[numpy.int8],
            out_sig=[numpy.int8])

        #Storing arguments as attributes
        self.SF = SF
        self.CR = CR

        #We want len(input_items) = len(output_items) = N*SF*CR
        self.set_output_multiple(self.SF*self.CR)

    def work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]

        # <+signal processing here+>
        # For the moment, this block only copy input to output
        out[:] = in0

        #Tell GNURadio how many items were produced
        return len(output_items[0])
