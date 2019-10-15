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

class gray_deindexer(gr.sync_block):
    """
    docstring for block gray_deindexer
    """
    def __init__(self, M):
        gr.sync_block.__init__(self,
            name="gray_deindexer",
            in_sig=[(numpy.float32, M)],
            out_sig=[(numpy.float32, M)])

        self.M = M

    def work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]

        for i in range(0, self.M):
            #out[:,gray[i]] = in0[:,i]
            out[:,i^(i>>1)] = in0[:,i]

        return len(output_items[0])

