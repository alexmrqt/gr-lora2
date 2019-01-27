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

import numpy
import pmt
from gnuradio import gr

class lora_header_decode(gr.sync_block):
    """
    docstring for block lora_header_decode
    """
    def __init__(self, SF, check_crc):
        gr.sync_block.__init__(self,
            name="lora_header_decode",
            in_sig=[numpy.uint8],
            out_sig=[])

        # The header fills an interleaving matrix, that is SF*(CR+4) bits before
        # decoding and deinterleaving.
        # The header is sent in reduced rate mode, thus there are only
        # (SF-2)*(CR+4) bits after deinterleaving.
        # Finally, the header is coded with CR = 4, which gives (SF-2)*4 bits
        # after decoding.
        self.len_block = (SF-2) * 4
        self.check_crc = check_crc

        self.message_port_register_out(pmt.intern("hdr"))

        self.set_output_multiple(self.len_block)

    def compute_hdr_crc(self, vect):
        res = numpy.zeros(8, dtype=numpy.uint8)

        res[3] = numpy.sum(vect[[0,1,2,3]])%2
        res[4] = numpy.sum(vect[[0,4,5,6,11]])%2
        res[5] = numpy.sum(vect[[1,4,7,8,10]])%2
        res[6] = numpy.sum(vect[[1,5,6,9,10,11]])%2
        res[7] = numpy.sum(vect[[3,6,8,9,10,11]])%2

        return res

    def work(self, input_items, output_items):
        in0 = input_items[0]

        n_blocks = len(in0)//self.len_block

        for i in range(0, n_blocks):
            vect = in0[i*self.len_block:(i+1)*self.len_block]

            #Check CRC if needed
            if self.check_crc:
                chk = vect[12:20]
                computed_chk = self.compute_hdr_crc(vect[0:12])

                if (chk != computed_chk).any():
                    print('CRC check failed : ' + str(chk) + ' != ' + str(computed_chk))

                    continue

            #Retrieve fields
            length = numpy.packbits(vect[0:8])[0] #To be converted in symbols...
            CR = (numpy.packbits(vect[8:11])>>5)[0]
            has_crc = (numpy.packbits(vect[11])>>7)[0]
            rem_bits = vect[20:].tolist()

            #Construct message
            out_msg = pmt.make_dict()
            out_msg = pmt.dict_add(out_msg, pmt.intern('packet_len'),
                    pmt.from_long(long(length)))
            out_msg = pmt.dict_add(out_msg, pmt.intern('CR'),
                    pmt.from_long(long(CR)))
            if has_crc:
                out_msg = pmt.dict_add(out_msg, pmt.intern('has_crc'), pmt.PMT_T)
            else:
                out_msg = pmt.dict_add(out_msg, pmt.intern('has_crc'), pmt.PMT_F)
            if len(rem_bits) != 0:
                out_msg = pmt.dict_add(out_msg, pmt.intern('rem_bits'),
                        pmt.init_u8vector(len(rem_bits), rem_bits))

            #Fire message!
            self.message_port_pub(pmt.intern("hdr"), out_msg)

        return len(in0)

