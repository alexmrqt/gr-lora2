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

class css_phase_corr(gr.sync_block):
    """
    docstring for block css_phase_corr
    """
    def __init__(self, M, len_reg):
        gr.sync_block.__init__(self,
            name="css_phase_corr",
            in_sig=[(numpy.complex64, M)],
            out_sig=[(numpy.complex64, M), numpy.float32])

        self.M = M
        self.reg = len_reg*[0.0 + 1j*0.0]

    def work(self, input_items, output_items):
        inp = input_items[0]
        outp_sig = output_items[0]
        outp_phase = output_items[1]

        for i in range(0, len(outp_sig)):
            #Correct phase of incoming signal
            phase = numpy.angle(numpy.sum(self.reg))
            outp_sig[i] = inp[i] * numpy.exp(-1j*phase)
            outp_phase[i] = phase

            #Find extremum of the real part of the signal
            rsig = numpy.real(outp_sig[i])
            dec = 0
            if(numpy.max(rsig) > numpy.max(-1.0 * rsig)):
                dec = numpy.argmax(rsig)
            else:
                dec = numpy.argmin(rsig)

            #Shift reg and add input symbol corresponding to decision
            self.reg.pop(0)
            self.reg.append(inp[i][dec])

        return len(output_items[0])
