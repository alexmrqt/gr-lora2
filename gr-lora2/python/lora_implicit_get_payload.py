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
from gnuradio import gr
import pmt

class lora_implicit_get_payload(gr.basic_block):
    """
    docstring for block lora_implicit_get_payload
    """
    def __init__(self, payload_len):
        gr.basic_block.__init__(self,
            name="lora_implicit_get_payload",
            in_sig=[numpy.int16],
            out_sig=[numpy.int16])

        self.payload_len = payload_len
        self.set_output_multiple(payload_len)


    def forecast(self, noutput_items, ninput_items_required):
        #setup size of input_items[i] for work call
        for i in range(len(ninput_items_required)):
            ninput_items_required[i] = noutput_items

    def general_work(self, input_items, output_items):
        #output_items[0][:] = input_items[0]
        in0 = input_items[0]
        tags = self.get_tags_in_window(0, 0, len(in0), pmt.intern('pkt_start'))

        len_in0 = len(in0)
        len_out0 = len(output_items[0][:])

        out0_ptr = 0
        ninput_consumed = 0
        noutput_produced = 0

        for i in range(0, len(tags)):
            in0_start_idx = tags[i].offset - self.nitems_read(0)
            in0_stop_idx = in0_start_idx + self.payload_len - 1
            out0_stop_idx = out0_ptr + self.payload_len - 1

            #If we have a full payload, that fits into the output buffer
            if out0_stop_idx < len_out0 and in0_stop_idx < len_in0:
                output_items[0][out0_ptr:(out0_stop_idx+1)] = \
                        in0[in0_start_idx:(in0_stop_idx+1)]

                out0_ptr += self.payload_len
                noutput_produced += self.payload_len
                ninput_consumed = in0_stop_idx
            #Else, drop every input symbols up to the payload start
            else:
                ninput_consumed = in0_start_idx - 2

                break

        self.consume(0, ninput_consumed)
        return noutput_produced
