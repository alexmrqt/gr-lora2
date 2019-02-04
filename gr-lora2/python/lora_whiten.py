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

class lora_whiten(gr.sync_block):
    """
    docstring for block lora_whiten
    """
    def __init__(self, CR):
        gr.sync_block.__init__(self,
            name="lora_whiten",
            in_sig=[numpy.uint8],
            out_sig=[numpy.uint8])

        self.poly = 0
        self.seed = 0
        if CR == 4:
            self.poly = 0x560C8279C8D93DFB18965335298EDBE3
            self.seed = 0x32665B15521BFDD6C41E4B1B4C1A32EA

        self.sr = self.seed

    def reset_lfsr(self):
        self.sr = self.seed

    def shift_lfsr(self):
        #Output is the last element of the LFSR
        out = self.sr&0x01

        #To calculate next input:
        # 1) - Bitwise AND LFSR content and polyniomial
        # 2) - XOR each bits of the result of 1).
        next_input = 0
        xor = self.sr&self.poly
        while xor != 0:
            next_input ^= xor&0x01
            xor >>= 1

        #Update LFSR by shifting is content and adding nex_input as first element
        self.sr = (self.sr>>1)|(next_input<<127)

        return out

    def work(self, input_items, output_items):
        in0 = input_items[0]
        out0 = output_items[0]

        tags = self.get_tags_in_window(0, 0, len(in0), pmt.intern('packet_len'))
        tags = list(tags)

        for i in range(0, len(in0)):
            #Reset LFSR if this is the beginning of a new packet
            if len(tags) != 0:
                if tags[0].offset == (i + self.nitems_read(0)):
                    self.reset_lfsr()

                    tags.pop(0)

            #XOR input and LFSR
            out0[i] = in0[i] ^ self.shift_lfsr()

        return len(output_items[0])

