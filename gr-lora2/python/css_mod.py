#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018 Alexandre Marquet.
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

from lora2 import css_mod_algo

class css_mod(gr.interp_block):
    """
    docstring for block css_mod
    """
    def __init__(self, M, interp, len_tag_key):
        gr.interp_block.__init__(self,
            name="css_mod",
            in_sig=[numpy.uint16],
            out_sig=[numpy.complex64],
            interp=M*interp)

        self.tot_interp = M*interp
        self.len_tag_key = len_tag_key
        self.modulator = css_mod_algo.css_mod_algo(M,interp)

    def work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]

        #Modulate
        out[:] = self.modulator.modulate(in0[:])

        #Propagate tags
        tags = self.get_tags_in_window(0, 0, len(in0))

        for tag in tags:
            tag_in_idx = tag.offset - self.nitems_read(0)
            tag_out_idx = tag_in_idx * self.tot_interp
            tag_out_offset = tag_out_idx + self.nitems_written(0)

            if str(tag.key) == self.len_tag_key:
                tag_val = pmt.to_python(tag.value) * self.tot_interp
                self.add_item_tag(0, tag_out_offset, tag.key, pmt.to_pmt(tag_val))
            else:
                self.add_item_tag(0, tag_out_offset, tag.key, tag.value)

        return len(output_items[0])

