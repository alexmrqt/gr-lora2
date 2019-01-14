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

class lora_interleaver(gr.sync_block):
    """
    docstring for block lora_interleaver
    """
    def __init__(self, SF, CR):
        gr.sync_block.__init__(self,
            name="lora_interleaver",
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

        # signal processing starts here -----

        # convert the vector into a matrix
        input_mat= in0

        # print the input matrix
        print input_mat

        # flipping horizontally the input matrix
        flipped_horiz= numpy.fliplr( input_mat )

        # placeholder for the concatenation
        out_mat= numpy.array([], dtype=numpy.int).reshape(0,self.CR+4)

        # non-square matrix offset
        offset= self.SF-(self.CR+4)

        # diagonal concatenation
        for x in range( 0, self.SF ):

            # auxiliar variable for the first iteration
            # aux= numpy.flip( flipped_horiz.diagonal( -x+offset ), 0 )
            aux= numpy.flipud( flipped_horiz.diagonal( -x+offset ) )


            # multiple iterations for the size of the matrix:
            # ex: 18x8
            # |   ||   ||   ||   |
            # |   ||   ||   ||   |
            # |   ||   ||   ||   |
            #     8   16   24   32 
            #
            # 18+x / 8 = #of iterations
            # (CR+4+x) / SF

            for y in range( 1, (self.CR+4+x) / self.SF +1 ):

                # concatenate the first iteration with each new iteration
                aux= numpy.concatenate( ( aux, numpy.flipud( flipped_horiz.diagonal( y*self.SF-x+offset ) ) ), axis=0)

            # concatenate vertically the auxilliar vectors
            out_mat= numpy.vstack( (out_mat, aux) )

        # print the output
        print out_mat

        # convert the output matrix into a vector
        out_vect= out_mat.reshape(-1)

        # <+signal processing here+>
        # For the moment, this block only copy input to output
        out[:] = out_vect

        #Tell GNURadio how many items were produced
        return len(output_items[0])
