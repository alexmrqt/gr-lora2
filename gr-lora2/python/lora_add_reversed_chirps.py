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
    def __init__(self, SF, interp, len_tag_key, pre_end_tag_key, rev_chirps_end_tag_key):
        gr.basic_block.__init__(self,
            name="lora_add_reversed_chirps",
            in_sig=[numpy.complex64],
            out_sig=[numpy.complex64])

        self.M = 2**SF
        self.interp = interp
        modulator = css_mod_algo.css_mod_algo(self.M, self.interp)

        self.len_tag_key = pmt.intern(len_tag_key)
        self.pre_end_tag_key = pmt.intern(pre_end_tag_key)
        self.rev_chirps_end_tag_key = pmt.intern(rev_chirps_end_tag_key)

        #Generate rev chirps
        self.rev_chirps = numpy.conjugate(modulator.modulate([0,0,0]))
        self.rev_chirps = self.rev_chirps[0:(2*self.M + self.M/4)*interp]

        #Set to True in order to add rev_chirps at the begining of next call
        self.flag_add_rev_chirps = False

    def forecast(self, noutput_items, ninput_items_required):
        #When no chirps is to be appened, this block is a sync block
        if self.flag_add_rev_chirps == False:
            ninput_items_required[0] = noutput_items
        else:
            ninput_items_required[0] = noutput_items + len(self.rev_chirps)

    def copy_and_shift_tags_in_window(self, which_input, in_ptr, out_ptr, length):
        tags_orig = self.get_tags_in_window(which_input, in_ptr, length)

        for tag in tags_orig:
            tag_offset = tag.offset - self.nitems_read(0) - in_ptr
            tag_offset += self.nitems_written(0) + out_ptr

            tag_value = pmt.to_python(tag.value)

            if pmt.to_python(tag.key) == pmt.to_python(self.len_tag_key):
                tag_value += len(self.rev_chirps)

            self.add_item_tag(which_input, tag_offset, tag.key,
                    pmt.to_pmt(tag_value))

        return

    def general_work(self, input_items, output_items):
        in0 = input_items[0]

        len_out0 = len(output_items[0][:])

        in0_ptr = 0
        out0_ptr = 0
        ninput_consumed = 0
        noutput_produced = 0

        #Add rev_chirps at the begining of output buffer if needed
        if self.flag_add_rev_chirps == True:
            if len_out0 >= len(self.rev_chirps):
                output_items[0][0:len(self.rev_chirps)] = self.rev_chirps

                #Append rev_chirps_end_tag
                self.add_item_tag(0,
                        self.nitems_written(0) + len(self.rev_chirps)-1,
                        self.rev_chirps_end_tag_key, pmt.PMT_NIL)

                self.flag_add_rev_chirps = False

                out0_ptr = len(self.rev_chirps)
                noutput_produced += len(self.rev_chirps)
            else:
                self.consume(0, ninput_consumed)
                return noutput_produced

        #Retrieve tags with pre_end_tag_key
        tags = self.get_tags_in_window(0, 0, len(in0), self.pre_end_tag_key)

        #If no tags is present, copy input to output and return.
        if len(tags) == 0:
            output_items[0][out0_ptr:] = in0[:(len_out0-out0_ptr)]

            #Handle tags associated with this data
            self.copy_and_shift_tags_in_window(0, 0, out0_ptr, len_out0-out0_ptr)

            self.consume(0, len_out0)
            return len_out0

        #Add reversed chirps for each preamble (if output buffer large enough)
        for i in range(0, len(tags)):
            in0_stop_idx = in0_ptr + tags[i].offset - self.nitems_read(0)
            out0_stop_idx = out0_ptr + tags[i].offset - self.nitems_read(0)
            #Go to the end of the symbol marked by pre_end_tag_key
            in0_stop_idx += self.M*self.interp - 1
            out0_stop_idx += self.M*self.interp - 1

            #Copy data preceding the tag
            #Case 1: data fits in output buffer
            if out0_stop_idx < len_out0:
                output_items[0][out0_ptr:(out0_stop_idx+1)] = \
                        in0[in0_ptr:(in0_stop_idx+1)]

                #Handle tags associated with this data
                self.copy_and_shift_tags_in_window(0, in0_ptr, out0_ptr,
                        in0_stop_idx-in0_ptr+1)

                #Update counters and pointers
                ninput_consumed += in0_stop_idx - in0_ptr+1
                noutput_produced+= out0_stop_idx - out0_ptr+1
                in0_ptr = in0_stop_idx+1
                out0_ptr = out0_stop_idx+1
            #Case 2: data does not fit in output buffer
            else:
                out0_stop_idx = len_out0-1
                in0_stop_idx = in0_ptr + (out0_stop_idx - out0_ptr)

                output_items[0][out0_ptr:(out0_stop_idx+1)] = \
                        in0[in0_ptr:(in0_stop_idx+1)]

                #Handle tags associated with this data
                self.copy_and_shift_tags_in_window(0, in0_ptr, out0_ptr,
                        in0_stop_idx-in0_ptr+1)

                #Update counters and break
                ninput_consumed += in0_stop_idx - in0_ptr + 1
                noutput_produced += out0_stop_idx - out0_ptr + 1

                break

            #Append reversed chirps
            out0_stop_idx = out0_ptr + len(self.rev_chirps) - 1
            #Case 1: If data fits in output buffer, then append reversed chirps
            if out0_stop_idx < len_out0:
                output_items[0][out0_ptr:(out0_stop_idx+1)] = self.rev_chirps

                #Append rev_chirps_end_tag
                self.add_item_tag(0, self.nitems_written(0) + out0_stop_idx,
                        self.rev_chirps_end_tag_key, pmt.PMT_NIL)

                #Update counters and pointers
                noutput_produced+= len(self.rev_chirps)
                out0_ptr = out0_stop_idx+1
            #Case 2: If data does not fit in output buffer, exit
            else:
                self.flag_add_rev_chirps = True
                break

        self.consume(0, ninput_consumed)
        return noutput_produced
