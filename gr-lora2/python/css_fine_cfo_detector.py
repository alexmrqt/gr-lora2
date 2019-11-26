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
from lora2 import css_demod_algo

class css_fine_cfo_detector(gr.sync_block):
    """
    docstring for block css_fine_cfo_detector
    """
    def __init__(self, M, timing=0):
        gr.sync_block.__init__(self,
            name="css_fine_cfo_detector",
            in_sig=[numpy.complex64],
            out_sig=[])

        self.M = M
        self.timing = timing
        self.first_sym = True

        #Keep track of the last two phases
        #self.phase_buff = numpy.zeros(2, dtype=numpy.float32)
        self.cmplx_sym_buff = numpy.zeros(2, dtype=numpy.complex64)
        self.sym_buff = numpy.zeros(2, dtype=numpy.uint16)
        self.demodulator = css_demod_algo(self.M)

        self.message_port_register_out(pmt.intern("cfo"))

        self.set_output_multiple(self.M)

    def work(self, input_items, output_items):
        in0 = input_items[0]

        n_syms = len(in0) // self.M
        for i in range(0, n_syms):
            sig = in0[i*self.M:(i+1)*self.M]
            (hard_sym, spectrum) = \
                    self.demodulator.demodulate_with_spectrum(sig)

            #self.phase_buff = numpy.roll(self.phase_buff, -1)
            #self.phase_buff[-1] = numpy.angle(spectrum[0][hard_sym])

            ###CFO estimation if at least 2 symbols were demodulated
            #if not self.first_sym:
            #    #Frequency discriminator
            #    phase_diff = numpy.mod(numpy.diff(self.phase_buff), 2*numpy.pi)
            #    phase_diff[phase_diff>numpy.pi] -= 2*numpy.pi

            #    #Compute error
            #    freq_error = phase_diff*0.5/(self.M*numpy.pi)

            #    self.message_port_pub(pmt.intern("cfo"),
            #            pmt.from_float(numpy.float64(freq_error)))
            #else:
            #    self.first_sym = False

            self.cmplx_sym_buff = numpy.roll(self.cmplx_sym_buff, -1)
            self.cmplx_sym_buff[-1] = spectrum[0][hard_sym]

            self.sym_buff = numpy.roll(self.sym_buff, -1)
            self.sym_buff[-1] = hard_sym

            ##CFO estimation if at least 2 symbols were demodulated
            if not self.first_sym:
                #Frequency discriminator
                phase_diff = self.cmplx_sym_buff[-1]*numpy.conj(self.cmplx_sym_buff[0])
                phase_diff *= numpy.exp(-1j*2*numpy.pi*self.timing*(self.sym_buff[-1]-self.sym_buff[0])/self.M)
                phase_diff = numpy.angle(phase_diff)

                #Compute error
                freq_error = phase_diff*0.5/(self.M*numpy.pi)


                self.message_port_pub(pmt.intern("cfo"),
                        pmt.from_float(numpy.float64(freq_error)))
            else:
                self.first_sym = False

        return len(input_items[0])
