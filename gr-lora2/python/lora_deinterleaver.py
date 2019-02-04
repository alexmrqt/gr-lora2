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

    def forecast(self, noutput_items, ninput_items_required):
        #setup size of input_items[i] for work call
        for i in range(len(ninput_items_required)):
            n_blocks = noutput_items // self.len_block_out

            ninput_items_required[i] = n_blocks * self.len_block_in

    def general_work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]

        # signal processing starts here -----

        # How many blocks should we produce?
        n_blocks = min(len(in0) // self.len_block_in, len(out) // self.len_block_out)

        for j in range(0, n_blocks):
            vect_short = in0[j*self.len_block_in:(j+1)*self.len_block_in]
            vect_bin = [numpy.binary_repr(ele, self.SF) for ele in vect_short]
            vect_bin = [numpy.frombuffer(ele.encode(), dtype='S1') for ele in vect_bin]
            vect_bin = numpy.array(vect_bin).flatten()

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
            out[j*self.len_block_out:(j+1)*self.len_block_out] = mtx.flatten()

        self.consume(0, n_blocks * self.len_block_in)
        return n_blocks * self.len_block_out
