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
    def __init__(self, M):
        self.M = M

        self.k = numpy.linspace(0, self.M-1, self.M)
        self.base_chirp_freq = (self.k + self.M) / 2.0

    def modulate(self, input_items):
        ninput_items = len(input_items)
        output_items = numpy.zeros(self.M * ninput_items, dtype=numpy.complex64)

        for i in range(0, ninput_items):
            out_phase = 2 * numpy.pi * (self.base_chirp_freq + input_items[i])/float(self.M) * self.k

            output_items[i*self.M:(i+1)*self.M] = numpy.exp(1j * out_phase)

        return output_items
