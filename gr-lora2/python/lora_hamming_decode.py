#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019 Alexandre Marquet.
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

import pmt
import numpy
from gnuradio import gr

class lora_hamming_decode(gr.basic_block):
    """
    docstring for block lora_hamming_decode
    """
    def __init__(self, CR, len_tag_key):
        gr.basic_block.__init__(self,
            name="lora_hamming_decode",
            in_sig=[numpy.uint8],
            out_sig=[numpy.uint8])

        #A block of data is 4 bits long.
        #Total length for a codeword is (4 + CR) bits long.
        self.CR = CR
        self.cw_len = CR + 4

        self.syndrome_table_CR4 = numpy.array([[0, 0, 0, 0, 0, 0, 0, 0],
                                            [0, 0, 0, 1, 0, 0, 0, 0],
                                            [0, 0, 1, 0, 0, 0, 0, 0],
                                            [0, 0, 0, 0, 1, 0, 0, 1],
                                            [0, 1, 0, 0, 0, 0, 0, 0],
                                            [0, 0, 0, 0, 1, 1, 0, 0],
                                            [0, 0, 0, 0, 0, 1, 0, 1],
                                            [0, 0, 0, 0, 0, 0, 1, 0],
                                            [1, 0, 0, 0, 0, 0, 0, 0],
                                            [0, 0, 0, 0, 1, 0, 1, 0],
                                            [0, 0, 0, 0, 0, 0, 1, 1],
                                            [0, 0, 0, 0, 0, 1, 0, 0],
                                            [0, 0, 0, 0, 0, 1, 1, 0],
                                            [0, 0, 0, 0, 0, 0, 0, 1],
                                            [0, 0, 0, 0, 1, 0, 0, 0],
                                            [0, 0, 0, 1, 1, 0, 0, 0]],
                                            dtype=numpy.uint8)

        self.syndrome_table_CR3 = numpy.array([[0, 0, 0, 0, 0, 0, 0],
                                           [0, 0, 1, 0, 0, 0, 0],
                                           [0, 1, 0, 0, 0, 0, 0],
                                           [0, 0, 0, 0, 0, 1, 0],
                                           [1, 0, 0, 0, 0, 0, 0],
                                           [0, 0, 0, 0, 0, 0, 1],
                                           [0, 0, 0, 1, 0, 0, 0],
                                           [0, 0, 0, 0, 1, 0, 0]],
                                           dtype=numpy.uint8)

        self.syndrome_table_CR2 = numpy.array([[0, 0, 0, 0, 0, 0],
                                            [0, 0, 0, 0, 0, 1],
                                            [0, 0, 1, 0, 0, 0],
                                            [0, 0, 0, 0, 1, 0]],
                                            dtype=numpy.uint8)
        self.syndrome_table_CR1 = numpy.array([[0, 0, 0, 0, 0],
                                            [0, 0, 0, 0, 1]],
                                            dtype=numpy.uint8)

        self.len_tag_key = None
        if len(len_tag_key) != 0:
            self.len_tag_key = len_tag_key

        #self.set_relative_rate(0.5)
        self.set_output_multiple(4)
        self.set_tag_propagation_policy(gr.TPP_CUSTOM)

    def forecast(self, noutput_items, ninput_items_required):
        #How many block of data shall we produce?
        n_blocks = noutput_items // 4

        ninput_items_required[0] = n_blocks * self.cw_len

    #Syndrome decoder
    def decode_one_block(self, data_block):
        if self.CR == 4:
            syndrome = (data_block[0]^data_block[4]^data_block[5]^data_block[7])<<3
            syndrome |= (data_block[1]^data_block[4]^data_block[6]^data_block[7])<<2
            syndrome |= (data_block[2]^data_block[4]^data_block[5]^data_block[6])<<1
            syndrome |= (data_block[3]^data_block[5]^data_block[6]^data_block[7])

            data_block = (data_block + self.syndrome_table_CR4[syndrome])%2
        elif self.CR == 3:
            syndrome = (data_block[0]^data_block[3]^data_block[4]^data_block[6])<<2
            syndrome |= (data_block[1]^data_block[3]^data_block[4]^data_block[5])<<1
            syndrome |= (data_block[2]^data_block[4]^data_block[5]^data_block[6])

            data_block = (data_block + self.syndrome_table_CR3[syndrome])%2
        elif self.CR == 2:
            syndrome = (data_block[0]^data_block[2]^data_block[3]^data_block[4])<<1
            syndrome |= (data_block[1]^data_block[3]^data_block[4]^data_block[5])

            data_block = (data_block + self.syndrome_table_CR2[syndrome])%2
        elif self.CR == 2:
            syndrome = (data_block[0]^data_block[1]^data_block[2]^data_block[3]^data_block[4])<<1

            data_block = (data_block + self.syndrome_table_CR1[syndrome])%2

        return data_block[-4:]

    def propagate_tags(self, tags, out_idx):
        out_tag_offset = out_idx + self.nitems_written(0)

        for tag in tags:
            #Handle len_tag_key, if any
            if (self.len_tag_key is not None ) and (pmt.to_python(tag.key) == self.len_tag_key):
                new_len = pmt.to_python(tag.value) * 4.0/self.cw_len
                tag.value = pmt.to_pmt(int(new_len))

            self.add_item_tag(0, out_tag_offset, tag.key, tag.value)

    def general_work(self, input_items, output_items):
        in0 = input_items[0]

        #How many blocks have we got in the input buffer / can we fit in the output buffer?
        n_blocks = min(len(in0)//self.cw_len, len(output_items[0])//4)

        #With this information, we can directly compute how many items will be
        #consumed and produced.
        ninput_items_consumed = n_blocks * self.cw_len
        noutput_items_produced = n_blocks * 4

        for i in range(0, n_blocks):
            in_idx_start = i*self.cw_len
            in_idx_stop = in_idx_start + self.cw_len - 1

            out_idx_start = i*4
            out_idx_stop = out_idx_start + 4 - 1

            #Handle tag propagation
            tags = self.get_tags_in_window(0, in_idx_start, in_idx_stop)
            self.propagate_tags(tags, out_idx_start)

            output_items[0][out_idx_start:out_idx_stop+1] = self.decode_one_block(\
                    in0[in_idx_start:in_idx_stop+1])

        self.consume(0, ninput_items_consumed)
        return noutput_items_produced
