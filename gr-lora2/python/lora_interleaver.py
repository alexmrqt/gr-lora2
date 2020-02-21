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

class lora_interleaver(gr.basic_block):
    """
    docstring for block lora_interleaver
    """
    def __init__(self, SF, CR, reduced_rate = False):
        gr.basic_block.__init__(self,
            name="lora_interleaver",
            in_sig=[numpy.uint8],
            out_sig=[numpy.uint16])

        #Storing arguments as attributes
        self.SF = SF
        self.CR = CR
        self.reduced_rate = reduced_rate

        #For binary to short conversion
        self.base2 = [2**i  for i in range(SF-1, -1, -1)]

        #Length of one block of data
        self.len_block_in = self.SF * (self.CR+4)
        #In reduced rate mode, we need two codeword less
        if self.reduced_rate:
            self.len_block_in = (self.SF-2) * (self.CR+4)

        self.len_block_out = self.CR+4

        self.set_output_multiple(self.len_block_out)
        self.set_tag_propagation_policy(gr.TPP_CUSTOM)

    def forecast(self, noutput_items, ninput_items_required):
        #setup size of input_items[i] for work call
        for i in range(len(ninput_items_required)):
            n_blocks = noutput_items // self.len_block_out

            ninput_items_required[i] = n_blocks * self.len_block_in

    def propagate_tags(self, tags, out_idx):
        out_tag_offset = out_idx + self.nitems_written(0)

        for tag in tags:
            self.add_item_tag(0, out_tag_offset, tag.key, tag.value)

    def general_work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]

        # signal processing starts here -----

        # How many blocks should we produce?
        n_blocks = min(len(in0) // self.len_block_in, len(out) // self.len_block_out)

        for j in range(0, n_blocks):
            in_idx_start = j*self.len_block_in
            in_idx_stop = in_idx_start + self.len_block_in - 1

            out_idx_start = j*self.len_block_out

            vect_bin = in0[in_idx_start:in_idx_stop+1]

            #Handle tag propagation
            tags = self.get_tags_in_window(0, in_idx_start, in_idx_stop+1)
            self.propagate_tags(tags, out_idx_start)

            #Process items
            for i in range(0, self.CR+4):
                tmp = numpy.zeros(self.SF, dtype=numpy.uint16)

                #Shuffle
                for j in range(0, self.SF if not self.reduced_rate else self.SF-2):
                    idx = (self.SF-1 - ((j-i)%self.SF))*(self.CR+4) \
                            + self.CR+4-1 - i
                    tmp[j] = vect_bin[idx]

                #Convert bit vector (of SF bits) to integer
                out[out_idx_start+i] = numpy.dot(self.base2, tmp)

        #Tell GNURadio how many items were produced
        self.consume(0, n_blocks * self.len_block_in)
        return len(output_items[0])
