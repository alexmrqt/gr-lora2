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

class lora_crc(gr.sync_block):
    """
    docstring for block lora_crc
    """
    def __init__(self, mode=True):
        gr.sync_block.__init__(self,
                name="lora_crc", in_sig=[], out_sig=[])

        self.message_port_register_in(pmt.intern('pdus'))
        self.message_port_register_out(pmt.intern('pdus'))

        if mode:
            self.set_msg_handler(pmt.intern("pdus"), self.handle_check)
        else:
            self.set_msg_handler(pmt.intern("pdus"), self.handle_generate)

    def crc16(self, crc, data, poly):
        for i in range(0,8):
            if crc&0x8000:
                crc <<= 1
                crc &= 0xFFFF
                crc ^= poly
            else:
                crc <<= 1
                crc &= 0xFFFF

        return crc ^ data

    def lora_payload_crc(self, data):
        crc = 0

        for ele in data:
            crc = self.crc16(crc, ele, 0x1021)

        return crc

    def handle_check(self, msg):
        hdr = pmt.car(msg)
        payload = pmt.to_python(pmt.cdr(msg))

        if pmt.equal(pmt.dict_ref(hdr, pmt.intern('has_crc'), pmt.PMT_F), pmt.PMT_T):
            crc = (payload[-1]<<8)|payload[-2]
            data = payload[:-2]

            comp_crc = self.lora_payload_crc(data)

            if comp_crc == crc:
                self.message_port_pub(pmt.intern('pdus'), pmt.cons(hdr, pmt.to_pmt(data)))
                print('CRC OK: ' + hex(crc) + ' == ' + hex(comp_crc))
            else:
                print('CRC NOK: ' + hex(crc) + ' != ' + hex(comp_crc))
        else:
            self.message_port_pub(pmt.intern('pdus'), msg)

    def handle_generate(self, msg):
        hdr = pmt.car(msg)
        payload = pmt.to_python(pmt.cdr(msg))

        if pmt.equal(pmt.dict_ref(hdr, pmt.intern('has_crc'), pmt.PMT_F), pmt.PMT_T):
            crc = self.lora_payload_crc(payload)
            payload = numpy.concatenate((payload, numpy.array([crc&0xFF, crc>>8], dtype=numpy.uint8)))

            self.message_port_pub(pmt.intern('pdus'), pmt.cons(hdr, pmt.to_pmt(payload)))
        else:
            self.message_port_pub(pmt.intern('pdus'), msg)

    def work(self, input_items, output_items):
        return len(output_items[0])

