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

from lora2 import css_mod_algo

class lora_preamble_detect(gr.sync_block):
    """
    docstring for block lora_preamble_detect
    """
    def __init__(self, SF, preamble_len, sync_word, threshold):
        gr.sync_block.__init__(self,
            name="lora_preamble_detect",
            in_sig=[numpy.complex64],
            out_sig=[numpy.complex64, numpy.complex64])

        #Generate ideal preamble samples
        modulator = css_mod_algo.css_mod_algo(2**SF)

        preamble_start = modulator.modulate(numpy.zeros(preamble_len))
        preamble_sync_word = modulator.modulate([sync_word, sync_word])
        preamble_downchirps = numpy.conjugate(modulator.modulate([0,0]))

        self.preamble = numpy.concatenate((preamble_start, preamble_sync_word,
            preamble_downchirps))

        #Set history to the number of taps (here, the size of the preamble)
        self.set_history(len(self.preamble))


    def work(self, input_items, output_items):
        in0 = input_items[0]
        out0 = output_items[0]
        out1 = output_items[0]

        out0[:] = in0
        out1[:] = numpy.correlate(self.preamble, in0, 'valid')

        return len(output_items[0])

