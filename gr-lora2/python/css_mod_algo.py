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

class css_mod_algo():
    def __init__(self, M, interp = 1):
        self.M = float(M)
        self.Q = float(interp)
        self.MQ = float(self.M * self.Q)
        self.MQ_int = self.M * self.Q

        self.k = numpy.linspace(0.0, self.MQ-1.0, self.MQ)

    def modulate(self, input_items):
        ninput_items = len(input_items)
        output_items = numpy.zeros(self.MQ * ninput_items, dtype=numpy.complex64)

        for i in range(0, ninput_items):
            out_freq = self.k/(2.0*self.Q) - self.M/2.0 + input_items[i] \
                    - self.M * numpy.round(self.k/(self.MQ) - 0.5 + input_items[i]/self.M)
            out_phase = 2.0 * numpy.pi * out_freq / self.MQ * self.k

            output_items[i*self.MQ_int:(i+1)*self.MQ_int] = numpy.exp(1j * out_phase)

        return output_items
