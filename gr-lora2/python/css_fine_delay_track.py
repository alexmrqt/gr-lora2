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
import math
import scipy.signal
from gnuradio import gr
from lora2 import css_mod_algo
from lora2 import css_demod_algo

class css_fine_delay_track(gr.decim_block):
    """
    docstring for block css_fine_delay_track
    """
    def __init__(self, M, Q_det, Q_res, B):
        gr.basic_block.__init__(self,
            name="css_fine_delay_track",
            in_sig=[numpy.complex64],
            out_sig=[numpy.float32])

        self.M = M
        self.Q_det = Q_det
        self.Q_res = Q_res
        self.b1 = B

        #zeta = 1 #Damping factor
        #bw = 0.1 #Loop bandwidth
        #Kp = 1.0 #Detector gain

        #theta = bw / (zeta + 1/(4*zeta))
        #self.K1 = -4*zeta*theta / ((1 + 2*zeta*theta + theta**2)*Kp)
        #self.K2 = -4*theta**2 / ((1 + 2*zeta*theta + theta**2)*Kp)
        #self.X2 = 0.0

        self.demodulator = css_demod_algo(self.M)
        self.modulator = css_mod_algo(self.M, self.Q_det)

        #Delay estimate
        self.delay = 0.0
        self.cum_delay = 0.0

        #History : we want interp/2 items before and after the symbol
        #self.set_history(self.Q//2+1)

    #def forecast(self, noutput_items, ninput_items_required):
    #    #Most of the time, this block simply decimates by M*Q
    #    #ninput_items_required[0] = (self.M * self.Q + self.Q//2) * noutput_items
    #    ninput_items_required[0] = (self.M * self.Q) * noutput_items

    #def delay_detect(self, sig, hard_sym):
    #    reconst_sig = numpy.zeros(self.M*self.Q + 2*self.Q, dtype=numpy.complex64)
    #    reconst_sig[self.Q:-self.Q] = self.modulator.modulate(hard_sym)

    #    return numpy.argmax(numpy.abs(numpy.correlate(sig, reconst_sig))) - self.Q

    def forecast(self, noutput_items, ninput_items_required):
        #Most of the time, this block simply decimates by M
        ninput_items_required[0] = self.M * noutput_items

    def delay_detect(self, sig):
        hard_sym = self.demodulator.demodulate(sig)

        reconst_sig = self.modulator.modulate(hard_sym).reshape((self.Q_det, self.M), order='F')
        reconst_sig[self.Q_det//2:,:] = numpy.roll(reconst_sig[self.Q_det//2:,:], 1)

        delay = numpy.argmax(numpy.abs(numpy.dot(reconst_sig, numpy.conj(sig))))
        if delay >= self.Q_det//2:
            delay -= self.Q_det
        return -delay/self.Q_det

    def frac_delay(self, sig, delay, interp):
        int_delay = int(delay*interp)
        gcd = math.gcd(int_delay, interp)
        new_delay = int_delay//gcd
        new_interp = interp//gcd

        return scipy.signal.resample_poly(sig, new_interp, 1)[new_delay::new_interp]

    def general_work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]

        start_idx = 0
        stop_idx = start_idx + self.M
        sym_count = 0
        while (stop_idx < len(in0)) and (sym_count < len(out)):
            #Fractional delay
            sig = self.frac_delay(in0[start_idx:stop_idx], self.delay, self.Q_res)

            #Detect
            err = self.delay_detect(sig)
            self.delay += self.b1 * err
            self.cum_delay += self.b1 * err
            out[sym_count] = self.cum_delay
            #out[sym_count] = err

            #Correct integer delay
            start_idx += self.M + int(self.delay)
            self.delay -= int(self.delay)
            if self.delay < -1e-6:
                start_idx -= 1
                self.delay += 1
            stop_idx = start_idx + self.M

            sym_count += 1

        #Tell GNURadio how many items were produced
        self.consume(0, start_idx)
        return sym_count
