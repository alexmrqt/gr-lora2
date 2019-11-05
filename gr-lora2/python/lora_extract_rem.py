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

class lora_extract_rem(gr.sync_block):
    """
    docstring for block lora_extract_rem
    """
    def __init__(self, SF, CR, soft=False):
        gr.sync_block.__init__(self,
            name="lora_extract_rem",
            in_sig=[numpy.float32 if soft else numpy.uint8],
            out_sig=[numpy.float32 if soft else numpy.uint8])

        # The header fills an interleaving matrix, that is SF*(CR+4) bits before
        # decoding and deinterleaving.
        # The header is sent in reduced rate mode, thus there are only
        # (SF-2)*(CR+4) bits after deinterleaving.
        self.len_block = (SF-2) * (CR+4)
        self.CR = CR
        self.soft = soft

        self.set_output_multiple(self.len_block)

    def work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]

        n_blocks = len(in0)//self.len_block

        for i in range(0, n_blocks):
            vect = in0[i*self.len_block:(i+1)*self.len_block]
            rem_bits = vect[(5*(self.CR+4)):].tolist()

            if self.soft:
                self.add_item_tag(0, i+self.nitems_written(0),
                        pmt.intern('rem_bits'),
                        pmt.init_f32vector(len(rem_bits), rem_bits))
            else:
                self.add_item_tag(0, i+self.nitems_written(0),
                        pmt.intern('rem_bits'),
                        pmt.init_u8vector(len(rem_bits), rem_bits))

        #Copy input to output
        out[:] = in0

        return len(output_items[0])

