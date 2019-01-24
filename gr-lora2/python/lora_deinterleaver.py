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

        # signal processing starts here -----

        # input vector
        input_vect= in0
        print input_vect

        # convert the vector into a matrix
        input_mat= input_vect.reshape((self.CR+4,self.SF))

        # print the input matrix
        print input_mat

        # transpose input matrix
        transposed= numpy.transpose( input_mat )

        # split matrix into row vectors
        array= numpy.split( transposed, self.SF )

        # placeholder for the concatenation
        out_mat= numpy.array([], dtype=numpy.int).reshape(0,self.CR+4)

        # shift index
        i=0

        # vector loop
        for v in array:

            # circular shift each vector by i
            v= numpy.roll( v, i )

            # store the vector in the new matrix
            out_mat= numpy.vstack( (out_mat, v) )

            # increse de shift index
            i=i+1

        # flip vertially the result matrix
        out_mat= numpy.flipud( out_mat )

        # print output
        print out_mat

        # vector version of the output
        output_vect= out_mat.reshape(-1)
        print output_vect

        # <+signal processing here+>
        # For the moment, this block only copy input to output
        out[:] = output_vect

        #Tell GNURadio how many items were produced
        return len(output_items[0])
