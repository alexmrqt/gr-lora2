#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019 Alexandre Marquet..
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

class css_demod_algo():
    def __init__(self, M, conjugate=False):
        self.M = M

        k = numpy.linspace(0.0, self.M-1.0, self.M)

        if conjugate:
            self.conj_chirp = numpy.exp(1j*numpy.pi*k/self.M*k)
        else:
            self.conj_chirp = numpy.exp(-1j*numpy.pi*k/self.M*k)

    def demodulate(self, input_items):
        ninput_items = len(input_items)
        noutput_items = ninput_items // self.M
        output_items = numpy.zeros(noutput_items, dtype=numpy.uint16)

        #Process block by block
        for i in range(0, noutput_items):
            #Dechirp
            dechirped_sig = input_items[self.M*i:self.M*(i+1)] * self.conj_chirp

            #Do FFT and shift it
            fft_sig = numpy.fft.fftshift(numpy.fft.fft(dechirped_sig))

            #Symbol is the FFT bin with maximum power
            output_items[i] = numpy.argmax(numpy.abs(fft_sig))

        return output_items

    def soft_demodulate(self, input_items):
        ninput_items = len(input_items)
        noutput_items = ninput_items // self.M
        hard_output = numpy.zeros(noutput_items, dtype=numpy.uint16)
        confidence = numpy.zeros(noutput_items, dtype=numpy.float32)

        #Process block by block
        for i in range(0, noutput_items):
            #Dechirp
            dechirped_sig = input_items[self.M*i:self.M*(i+1)] * self.conj_chirp

            #Do FFT and shift it
            fft_sig = numpy.fft.fftshift(numpy.fft.fft(dechirped_sig))

            #Symbol is the FFT bin with maximum power
            hard_output[i] = numpy.argmax(numpy.abs(fft_sig))
            confidence[i] = numpy.max(numpy.abs(fft_sig))

        return (hard_output, confidence)

    def complex_demodulate(self, input_items):
        ninput_items = len(input_items)
        noutput_items = ninput_items // self.M
        hard_output = numpy.zeros(noutput_items, dtype=numpy.uint16)
        complex_value = numpy.zeros(noutput_items, dtype=numpy.complex64)

        #Process block by block
        for i in range(0, noutput_items):
            #Dechirp
            dechirped_sig = input_items[self.M*i:self.M*(i+1)] * self.conj_chirp

            #Do FFT and shift it
            fft_sig = numpy.fft.fftshift(numpy.fft.fft(dechirped_sig))

            #Symbol is the FFT bin with maximum power
            hard_output[i] = numpy.argmax(numpy.abs(fft_sig))
            complex_value[i] = fft_sig[hard_output[i]]

        return (hard_output, complex_value)

    def demodulate_with_spectrum(self, input_items):
        ninput_items = len(input_items)
        noutput_items = ninput_items // self.M
        symbols = numpy.zeros(noutput_items, dtype=numpy.uint16)
        spectrums = numpy.zeros((noutput_items, self.M), dtype=numpy.complex64)

        #Process block by block
        for i in range(0, noutput_items):
            #Dechirp
            dechirped_sig = input_items[self.M*i:self.M*(i+1)] * self.conj_chirp

            #Do FFT and shift it
            spectrums[i,:] = numpy.fft.fftshift(numpy.fft.fft(dechirped_sig))

            #Symbol is the FFT bin with maximum power
            symbols[i] = numpy.argmax(numpy.abs(spectrums[i,:]))

        return (symbols, spectrums)
