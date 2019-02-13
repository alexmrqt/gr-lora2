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

class flip_half_bytes(gr.sync_block):
    """
    docstring for block flip_half_bytes
    """
    def __init__(self):
        gr.sync_block.__init__(self,
            name="flip_half_bytes",
            in_sig=[numpy.uint8],
            out_sig=[numpy.uint8])

    def work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]

        for i in range(0,len(in0)):
            low_nibble = in0[i]&0x0F
            high_nibble = (in0[i]>>4)&0x0F
            out[i] = (low_nibble<<4)|high_nibble

        return len(output_items[0])

