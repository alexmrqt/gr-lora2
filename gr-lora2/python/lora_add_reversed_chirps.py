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

class lora_add_reversed_chirps(gr.basic_block):
    """
    docstring for block lora_add_reversed_chirps
    """
    def __init__(self, SF, interp, len_tag_key, payload_tag_key, rev_chirps_tag_key):
        gr.basic_block.__init__(self,
            name="lora_add_reversed_chirps",
            in_sig=[numpy.complex64],
            out_sig=[numpy.complex64])

        self.set_tag_propagation_policy(gr.TPP_DONT)

        self.M = int(2**SF)
        self.interp = interp
        modulator = css_mod_algo.css_mod_algo(self.M, self.interp)

        self.copied_prev_pass = 0

        self.len_tag_key = pmt.intern(len_tag_key)
        self.payload_tag_key = pmt.intern(payload_tag_key)
        self.rev_chirps_tag_key = pmt.intern(rev_chirps_tag_key)

        #Generate rev chirps
        self.rev_chirps = numpy.conjugate(modulator.modulate([0,0,0]))
        self.rev_chirps = self.rev_chirps[0:(2*self.M + self.M//4 - 1)*interp]

    def forecast(self, noutput_items, ninput_items_required):
        #When no chirps is to be appened, this block is a sync block
        ninput_items_required[0] = noutput_items

    def handle_tag_propagation(self, length):
        tags_orig = self.get_tags_in_window(0, 0, length)

        for tag in tags_orig:
            tag_offset = tag.offset - self.nitems_read(0)
            tag_offset += self.nitems_written(0)

            tag_value = pmt.to_python(tag.value)

            if pmt.to_python(tag.key) == pmt.to_python(self.len_tag_key):
                tag_value += len(self.rev_chirps)

            self.add_item_tag(0, tag_offset, tag.key, pmt.to_pmt(tag_value))

    def append_downchirps(self, input_items, output_items):
        in0 = input_items[0]
        len_out0 = len(output_items[0][:])

        nitems = min(len(self.rev_chirps) + 1 - self.copied_prev_pass, len_out0)

        #Add a tag to denote begining of reversed chirps sequence
        if self.copied_prev_pass == 0:
            self.add_item_tag(0, self.nitems_written(0),
                    self.rev_chirps_tag_key, pmt.PMT_NIL)

        #If there is enough room for everything
        if len_out0 >= (len(self.rev_chirps) + 1 - self.copied_prev_pass):
            if nitems-1 > 0:
                output_items[0][:nitems-1] = \
                        self.rev_chirps[self.copied_prev_pass:self.copied_prev_pass+nitems-1]

            #Add payload tag on first payload item
            output_items[0][nitems-1] = in0[0]
            self.add_item_tag(0, self.nitems_written(0) + len(self.rev_chirps),
                    self.payload_tag_key, pmt.PMT_NIL)

            self.copied_prev_pass = 0
            self.consume(0, 1)
        else:
            #Copy chunk of downchirps
            output_items[0][:nitems] = \
                    self.rev_chirps[self.copied_prev_pass:self.copied_prev_pass+nitems]

            self.copied_prev_pass += len_out0
            self.consume(0, 0)

        return nitems

    def general_work(self, input_items, output_items):
        in0 = input_items[0]

        len_out0 = len(output_items[0][:])

        if self.copied_prev_pass > 0:
            return self.append_downchirps(input_items, output_items)

        #Retrieve tags with payload_tag_key
        tags = self.get_tags_in_window(0, 0, len(in0), self.payload_tag_key)

        #If no tags is present, copy input to output and return.
        if len(tags) == 0:
            nitems = min(len(in0), len_out0)
            output_items[0][:nitems] = in0[:nitems]

            #Handle tags associated with this data
            self.handle_tag_propagation(nitems)

            self.consume(0, nitems)
            return nitems
        else:
            #Make sure tag is on the first item
            nitems = tags[0].offset - self.nitems_read(0)
            if nitems > 0:
                nitems = min(nitems, len_out0)
                output_items[0][:nitems] = in0[:nitems]

                #Handle tags associated with this data
                self.handle_tag_propagation(nitems)

                self.consume(0, nitems)
                return nitems

            #Append reversed chirps and first payload item
            return self.append_downchirps(input_items, output_items)
