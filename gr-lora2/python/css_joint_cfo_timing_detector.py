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
from lora2 import css_demod_algo

class css_joint_cfo_timing_detector(gr.decim_block):
    """
    docstring for block css_joint_cfo_timing_detector
    """
    def __init__(self, M, step):
        gr.decim_block.__init__(self,
            name="css_joint_cfo_timing_detector",
            in_sig=[numpy.complex64],
            out_sig=[numpy.float32, numpy.float32], decim=M)

        self.M = M
        self.step = step
        self.first_sym = True

        self.h = numpy.array([0.0, 0.0]) #delta_t, M*delta_f

        #Keep track of the last two phases
        self.phase_buff = numpy.zeros(2, dtype=numpy.float32)
        self.sym_buff = numpy.zeros(2, dtype=numpy.float32)
        self.demodulator = css_demod_algo(self.M)

        #self.set_output_multiple(10)

    def cfo_timing_lms_step(self):
        if (not self.first_sym):
            #Frequency discriminator
            phase_diff = numpy.mod(numpy.diff(self.phase_buff), 2*numpy.pi)
            phase_diff[phase_diff>numpy.pi] -= 2*numpy.pi

            #Compute error
            freq_est = phase_diff/(2*numpy.pi)

            x = numpy.array([1.0 + numpy.diff(self.sym_buff)[0]/self.M, 1.0])
            self.h += self.step * x * (freq_est - numpy.dot(self.h, x))
        else:
            self.first_sym = False

    def cfo_timing_grad(self, phases, syms):
        h = numpy.array([0.0, 0.0]).reshape([2,1])

        #Frequency discriminator
        phase_diff = numpy.mod(numpy.diff(phases), 2*numpy.pi)
        phase_diff[phase_diff>numpy.pi] -= 2*numpy.pi

        #Compute error
        freq_est = phase_diff.reshape([len(phase_diff), 1])/(2*numpy.pi)
        a = 1.0 + numpy.diff(syms)/self.M
        X = numpy.array([a, numpy.ones(len(a))]).transpose()

        for i in range(0, 10):
            h += self.step * numpy.matmul(numpy.transpose(X), freq_est - numpy.matmul(X, h))

        return h[:,0]
    
    def check_hyp(self):
        delta_t = 0.4
        delta_f = 0.0/self.M
        if (not self.first_sym):
            #Frequency discriminator
            phase_diff = numpy.mod(numpy.diff(self.phase_buff), 2*numpy.pi)
            phase_diff[phase_diff>numpy.pi] -= 2*numpy.pi

            #Compute error
            freq_est = phase_diff/(2*numpy.pi)
            #eps = delta_f*self.M + delta_t * numpy.diff(self.sym_buff)[0]/self.M
            #eps = delta_f*self.M + delta_t * numpy.diff(self.sym_buff)[0]/(self.M**2)
            eps = delta_f*self.M

            print(freq_est - eps)

            return freq_est - eps

        else:
            self.first_sym = False

        return 0.0

    def work(self, input_items, output_items):
        in0 = input_items[0]
        out0 = output_items[0]
        out1 = output_items[1]

        n_syms = len(out0)
        for i in range(0, n_syms):
            sig = in0[i*self.M:(i+1)*self.M]
            (hard_sym, spectrum) = \
                    self.demodulator.demodulate_with_spectrum(sig)

            self.phase_buff = numpy.roll(self.phase_buff, -1)
            self.phase_buff[-1] = numpy.angle(spectrum[0][hard_sym])

            self.sym_buff = numpy.roll(self.sym_buff, -1)
            self.sym_buff[-1] = hard_sym

            ###CFO estimation if at least 2 symbols were demodulated
            #self.cfo_timing_lms_step()
            #out0[i] = self.h[1]/self.M
            #out1[i] = self.h[0]

            hyp = self.check_hyp()
            out0[i] = hyp
            out1[i] = hyp

        (hard_sym, spectrum) = \
                self.demodulator.complex_demodulate(in0)

        ##CFO estimation if at least 2 symbols were demodulated
        #self.cfo_timing_lms_step()
        #h = self.cfo_timing_grad(numpy.angle(spectrum), hard_sym)
        #out0[0] = h[1]/self.M
        #out1[0] = h[0]

        return len(output_items[0])
