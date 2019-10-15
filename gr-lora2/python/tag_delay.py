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

class tag_delay(gr.sync_block):
    """
    docstring for block tag_delay
    """
    def __init__(self, delay):
        gr.sync_block.__init__(self,
            name="tag_delay",
            in_sig=[numpy.complex64],
            out_sig=[numpy.complex64])

        self.delay = delay
        self.set_tag_propagation_policy(gr.TPP_CUSTOM)


    def work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]

        tags = self.get_tags_in_window(0, 0, len(in0))
        for tag in tags:
            tag.offset += self.delay
            self.add_item_tag(0, tag.offset, tag.key, tag.value)

        out[:] = in0
        return len(output_items[0])

