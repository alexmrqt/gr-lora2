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

class lora_deinterleaver(gr.basic_block):
    """
    docstring for block lora_deinterleaver
    """
    def __init__(self, SF, CR, reduced_rate = False):
        gr.basic_block.__init__(self,
            name="lora_deinterleaver",
            in_sig=[numpy.uint16],
            out_sig=[numpy.uint8])

        #Storing arguments as attributes
        self.SF = SF
        self.CR = CR
        self.reduced_rate = reduced_rate

        #Length of one block of data
        self.len_block_in = self.CR+4
        self.len_block_out = self.SF * (self.CR+4)

        #In reduced rate mode, two codewords are discarded from the output
        #block.
        if self.reduced_rate:
            self.len_block_out = (self.SF-2) * (self.CR+4)

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
            out_idx_stop = out_idx_start + self.len_block_out - 1

            #Handle tag propagation
            tags = self.get_tags_in_window(0, in_idx_start, in_idx_stop+1)
            self.propagate_tags(tags, out_idx_start)

            #Process items
            vect_short = in0[in_idx_start:in_idx_stop+1]
            vect_bin = [[(ele>>k)&0x01 for k in reversed(range(0,self.SF))] \
                    for ele in vect_short]
            vect_bin = numpy.array(vect_bin, dtype=numpy.uint8).flatten()

            mtx = numpy.flipud(vect_bin.reshape((self.CR+4, self.SF)).transpose())

            # In reduced rate mode, the last two line of the interleaving matrix
            # are removed.
            if self.reduced_rate:
                mtx = mtx[:-2,:]

            #Cyclic shift each column of mtx by its column index
            for i in range(0, mtx.shape[1]):
                mtx[:,i] = numpy.roll(mtx[:,i], i)

            #Reverse column order
            mtx = numpy.fliplr(mtx)

            # Put output vector into the output buffer
            out[out_idx_start:out_idx_stop+1] = mtx.flatten()

        self.consume(0, n_blocks * self.len_block_in)
        return n_blocks * self.len_block_out
