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
        self.set_tag_propagation_policy(gr.TPP_CUSTOM)

    def forecast(self, noutput_items, ninput_items_required):
        #Most of the time, this block simply decimates by M
        ninput_items_required[0] = self.M * noutput_items

    def propagate_tags(self, in_rel_start, in_rel_end):
        tags = self.get_tags_in_window(0, in_rel_start, in_rel_end)

        for tag in tags:
            rel_offset = tag.offset - self.nitems_read(0)
            tag.offset = rel_offset // self.M + self.nitems_written(0)

            self.add_item_tag(0, tag.offset, tag.key, tag.value)

    def general_work(self, input_items, output_items):
        in0 = input_items[0]
        tags = self.get_tags_in_window(0, 0, len(in0), pmt.intern('pkt_start'))

        ##Stream already synced with packet start
        if len(tags) == 0 or (tags[0].offset - self.nitems_read(0)) == 0:
            #Make sure we only sync for one packet
            if len(tags) > 1:
                len_pkt = tags[1].offset - self.nitems_read(0)
            else:
                len_pkt = len(in0)

            #Compute number of complete symbols in input stream
            #Check that output buffer is large enough to handle n_syms
            n_syms = min(len_pkt // self.M, output_items[0].shape[0])

            output_items[0][0:n_syms] = numpy.array(numpy.split(in0[0:n_syms*self.M], n_syms))

            self.propagate_tags(0, n_syms*self.M)

            self.consume(0, n_syms*self.M)
            return n_syms

        ##Stream needs sync
        #Vectorize items preceding the tag
        n_items = tags[0].offset - self.nitems_read(0)
        n_syms = min(n_items // self.M, output_items[0].shape[0])

        if n_syms > 0:
            output_items[0][0:n_syms] = numpy.split(in0[0:n_syms*self.M], n_syms)

            self.propagate_tags(0, n_syms*self.M)

        #Drop remaining items
        ninput_consumed = n_items

        #Put any tag in dropped items on the last output item
        tags = self.get_tags_in_window(0, n_syms*self.M, n_items)
        for tag in tags:
            tag.offset += self.nitems_written(0) - self.nitems_read(0) + n_syms - 1

            self.add_item_tag(0, tag.offset, tag.key, tag.value)

        self.consume(0, ninput_consumed)
        return n_syms
