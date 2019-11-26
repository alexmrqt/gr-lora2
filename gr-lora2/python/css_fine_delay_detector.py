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
from gnuradio import gr

from lora2 import css_demod_algo, css_mod_algo

class css_fine_delay_detector(gr.decim_block):
    """
    docstring for block css_fine_delay_detector
    """
    def __init__(self, M, interp=1, algo=0):
        gr.decim_block.__init__(self,
            name="css_fine_delay_detector",
            in_sig=[numpy.complex64],
            out_sig=[numpy.float32], decim=M*(interp if algo == 0 else 1))

        self.M = M
        self.Q = interp
        self.algo = algo

        self.demodulator = css_demod_algo(self.M)
        if algo == 2:
            self.modulator = css_mod_algo(self.M, 3)
        else:
            self.modulator = css_mod_algo(self.M, self.Q)

    def work_algo0(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]

        n_syms = len(in0) // (self.M*self.Q)
        for i in range(0, n_syms):
            sig = in0[i*(self.M*self.Q):(i+1)*(self.M*self.Q)]

            hard_sym = self.demodulator.demodulate(sig[::self.Q])

            reconst_sig = numpy.zeros(self.M*self.Q + 2*self.Q, dtype=numpy.complex64)
            reconst_sig[self.Q:-self.Q] = self.modulator.modulate(hard_sym)

            out[i] = numpy.argmax(numpy.abs(numpy.correlate(sig, reconst_sig))) - self.Q
            out[i] *= 1.0/self.Q

        return len(output_items[0])

    def work_algo1(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]

        n_syms = len(in0) // (self.M)
        for i in range(0, n_syms):
            sig = in0[i*self.M:(i+1)*self.M]

            hard_sym = self.demodulator.demodulate(sig)

            reconst_sig = self.modulator.modulate(hard_sym).reshape((self.Q, self.M), order='F')
            reconst_sig[self.Q//2:,:] = numpy.roll(reconst_sig[self.Q//2:,:], 1)

            out[i] = numpy.argmax(numpy.abs(numpy.dot(reconst_sig, numpy.conj(sig))))
            if out[i] >= self.Q//2:
                out[i] -= self.Q
            out[i] *= -1.0/self.Q

        return len(output_items[0])

    def work_algo2(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]

        n_syms = len(in0) // (self.M)
        for i in range(0, n_syms):
            sig = in0[i*self.M:(i+1)*self.M]

            hard_sym = self.demodulator.demodulate(sig)

            reconst_sig = self.modulator.modulate(hard_sym)
            early = reconst_sig[3+1:-3:3]
            center = reconst_sig[3:-3:3]
            late = reconst_sig[3-1:-4:3]

            tmp_early = numpy.abs(numpy.dot(early, numpy.conj(sig[1:-1])))
            tmp_center = numpy.abs(numpy.dot(center, numpy.conj(sig[1:-1])))
            tmp_late = numpy.abs(numpy.dot(late, numpy.conj(sig[1:-1])))
            out[i] = -(tmp_early - tmp_late)/1000.0
            #out[i] *= -8.0/(self.M)
            #out[i] *= -8.0*tmp_center/(self.M**2)

        return len(output_items[0])

    def work_algo3(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]

        n_syms = len(in0) // (self.M*self.Q)
        for i in range(0, n_syms):
            sig = in0[i*(self.M*self.Q):(i+1)*(self.M*self.Q)]

            hard_sym = self.demodulator.demodulate(sig[::self.Q])

            reconst_sig = numpy.zeros(self.M*self.Q + 2*self.Q, dtype=numpy.complex64)
            reconst_sig[self.Q:-self.Q] = self.modulator.modulate(hard_sym)

            #out[i] = numpy.argmax(numpy.abs(numpy.correlate(sig, reconst_sig))) - self.Q
            out[i] = numpy.abs(numpy.diff(numpy.correlate(sig, reconst_sig))[self.Q-1])
            print(out[i])
            #out[i] *= 1.0/self.Q

        return len(output_items[0])

    def work(self, input_items, output_items):
        if self.algo == 0:
            return self.work_algo0(input_items, output_items)
        elif self.algo == 1:
            return self.work_algo1(input_items, output_items)
        elif self.algo == 2:
            return self.work_algo2(input_items, output_items)
        elif self.algo == 3:
            return self.work_algo3(input_items, output_items)
        else:
            return 0
