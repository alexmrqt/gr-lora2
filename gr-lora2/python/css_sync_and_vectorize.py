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

class css_sync_and_vectorize(gr.basic_block):
    """
    docstring for block css_sync_and_vectorize
    """
    def __init__(self, M):
        gr.basic_block.__init__(self,
            name="css_sync_and_vectorize",
            in_sig=[(numpy.complex64)],
            out_sig=[(numpy.complex64, M)])

        self.M = M

        #Block tag propagation
        #self.tag_propagation_policy(gr.TPP_DONT)

    def forecast(self, noutput_items, ninput_items_required):
        #Most of the time, this block simply decimates by M
        ninput_items_required[0] = self.M * noutput_items

    def general_work(self, input_items, output_items):
        in0 = input_items[0]
        tags = self.get_tags_in_window(0, 0, len(in0), pmt.intern('pkt_start'))

        ##Stream already synced with packet start
        if len(tags) == 0 :
            #Compute number of complete symbols in input stream
            n_syms = int(len(in0)/float(self.M))

            #Check that output buffer is large enough to handle n_syms
            if(output_items[0].shape[0] < n_syms):
                n_syms = output_items[0].shape[0]

            output_items[0][0:n_syms] = numpy.array(numpy.split(in0[0:n_syms*self.M], n_syms))

            self.consume(0, n_syms*self.M)
            return n_syms

        ##Stream needs sync
        out_ptr = 0
        ninput_consumed = 0
        noutput_produced = 0
        for i in range(0, len(tags)):
            start_idx = tags[i].offset - self.nitems_read(0)

            #If this is the last tag
            next_tag_idx = len(in0)
            #If there is another tag to come
            if i != (len(tags)-1):
                next_tag_idx = tags[i+1].offset - self.nitems_read(0)

            nitems = next_tag_idx - start_idx
            if nitems >= self.M:
                #Compute number of complete symbols in range
                # [start_idx ; next_tag_idx [
                n_syms = int(nitems/float(self.M))
                #Check that output buffer is large enough to handle n_syms
                if(output_items[0].shape[0] < n_syms):
                    n_syms = output_items[0].shape[0]

                end_idx = start_idx + n_syms * self.M

                #Create vector output
                output_items[0][out_ptr:(out_ptr+n_syms)] = numpy.split(in0[start_idx:end_idx], n_syms)

                #Add tag on output
                self.add_item_tag(0, self.nitems_written(0) + out_ptr, pmt.intern('pkt_start'), pmt.PMT_NIL)

                #Update pointers and counters
                out_ptr += n_syms
                noutput_produced += n_syms
                ninput_consumed = end_idx

        self.consume(0, ninput_consumed)
        return noutput_produced
