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
        self.SF = SF

        self.message_port_register_out(pmt.intern("hdr"))

        self.set_output_multiple(self.len_block)

    def compute_hdr_crc(self, vect):
        res = numpy.zeros(8, dtype=numpy.uint8)

        res[3] = numpy.sum(vect[[0,1,2,3]])%2
        res[4] = numpy.sum(vect[[0,4,5,6,11]])%2
        res[5] = numpy.sum(vect[[1,4,7,8,10]])%2
        res[6] = numpy.sum(vect[[2,5,7,9,10,11]])%2
        res[7] = numpy.sum(vect[[3,6,8,9,10,11]])%2

        return res

    def compute_fields(self, vect):
        out = {}

        #Retrieve fields
        out['payload_len'] = numpy.packbits(vect[0:8])[0]
        out['CR'] = (numpy.packbits(vect[8:11])>>5)[0]
        out['has_crc'] = (numpy.packbits(vect[11])>>7)[0]
        out['rem_bits'] = vect[20:].tolist()

        out['packet_len'] = out['payload_len'] + 2*out['has_crc']

        #Compute length as number of LoRa symbols
        n_bits = out['packet_len'] * 8 #Before hamming coding
        n_bits *= (4+out['CR'])/4.0 #After hamming coding

        #To be interleaved, the number of bits in the packet must be a multiple
        #of (CR+4)*SF. If not, the payload is padded with zeros
        bits_multiple = (out['CR'] + 4) * self.SF
        out['packet_len_bits'] = int(numpy.ceil(float(n_bits)/bits_multiple) * bits_multiple)

        #There is SF bits per symbol
        out['packet_len_syms'] = out['packet_len_bits']/self.SF

        #Number of bits used to pad the payload
        out['pad_len'] = out['packet_len_bits'] - n_bits

        return out

    def construct_msg(self, parsed_header):
        #Construct message
        out_msg = pmt.make_dict()
        #out_msg = pmt.dict_add(out_msg, pmt.intern('packet_len'),
        #        pmt.from_long(long(parsed_header['packet_len'])))

        #out_msg = pmt.dict_add(out_msg, pmt.intern('payload_len'),
        #        pmt.from_long(long(parsed_header['payload_len'])))

        out_msg = pmt.dict_add(out_msg, pmt.intern('packet_len_syms'),
                pmt.from_long(long(parsed_header['packet_len_syms'])))

        out_msg = pmt.dict_add(out_msg, pmt.intern('packet_len_bits'),
                pmt.from_long(long(parsed_header['packet_len_bits'])))

        out_msg = pmt.dict_add(out_msg, pmt.intern('CR'),
                pmt.from_long(long(parsed_header['CR'])))

        out_msg = pmt.dict_add(out_msg, pmt.intern('pad_len'),
                pmt.from_long(long(parsed_header['pad_len'])))

        if parsed_header['has_crc']:
            out_msg = pmt.dict_add(out_msg, pmt.intern('has_crc'), pmt.PMT_T)
        else:
            out_msg = pmt.dict_add(out_msg, pmt.intern('has_crc'), pmt.PMT_F)

        if len(parsed_header['rem_bits']) != 0:
            out_msg = pmt.dict_add(out_msg, pmt.intern('rem_bits'),
                    pmt.init_u8vector(len(parsed_header['rem_bits']),
                        parsed_header['rem_bits']))

        return out_msg

    def work(self, input_items, output_items):
        in0 = input_items[0]

        n_blocks = len(in0)//self.len_block

        for i in range(0, n_blocks):
            vect = in0[i*self.len_block:(i+1)*self.len_block]

            #Check CRC if needed
            if self.check_crc:
                chk = vect[12:20]
                computed_chk = self.compute_hdr_crc(vect[0:12].copy())

                if (chk == computed_chk).all():
                    parsed_header = self.compute_fields(vect)

                    out_msg = self.construct_msg(parsed_header)

                    #Fire message!
                    self.message_port_pub(pmt.intern("hdr"), out_msg)
                else:
                    #Signal that HDR demodulation fail with a PMT_F
                    self.message_port_pub(pmt.intern("hdr"), pmt.PMT_F)
            else:
                parsed_header = self.compute_fields(vect)

                out_msg = self.construct_msg(parsed_header)

                #Fire message!
                self.message_port_pub(pmt.intern("hdr"), out_msg)

        return len(in0)

