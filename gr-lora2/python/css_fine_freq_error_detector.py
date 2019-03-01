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

class css_fine_freq_error_detector(gr.sync_block):
    """
    docstring for block css_fine_freq_error_detector
    """
    def __init__(self, M, len_reg):
        gr.sync_block.__init__(self,
            name="css_fine_freq_error_detector",
            in_sig=[(numpy.complex64, M)],
            out_sig=[])

        self.M = M

        self.message_port_register_out(pmt.intern("freq"))

        self.set_output_multiple(len_reg)

    def work(self, input_items, output_items):
        phase = numpy.float64(0.0)
        est_cfo = numpy.float64(0.0)

        for item in input_items[0]:
            sym_idx = numpy.argmax(numpy.abs(item))
            new_phase = numpy.angle(item[sym_idx])

            phase_diff = (phase - new_phase)%(2*numpy.pi)
            if phase_diff > numpy.pi:
                phase_diff -= 2*numpy.pi
            est_cfo += phase_diff

            phase = new_phase

        est_cfo /= len(input_items[0])
        est_cfo *= 0.5/((self.M-self.M/16)*numpy.pi)


        self.message_port_pub(pmt.intern("freq"), pmt.from_float(numpy.float64(est_cfo)))

        return len(input_items[0])

