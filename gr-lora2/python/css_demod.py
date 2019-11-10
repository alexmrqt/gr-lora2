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

from lora2 import css_mod_algo
from lora2 import css_demod_algo

class css_demod(gr.basic_block):
    """
    docstring for block css_demod
    """
    def __init__(self, M, B_cfo, B_delay, interp):
        gr.basic_block.__init__(self,
            name="css_demod",
            in_sig=[numpy.complex64],
            out_sig=[numpy.uint16, (numpy.complex64, M), numpy.float32, numpy.float32])

        self.M = M
        self.Q = interp
        self.demodulator = css_demod_algo.css_demod_algo(self.M)
        self.modulator = css_mod_algo.css_mod_algo(self.M, self.Q)
        self.global_sym_count = 0

        ##CFO-related attributes
        self.b1_cfo = B_cfo
        self.est_cfo = 0.0
        self.init_phase = 0.0
        #Keep track of the last two phases
        self.phase_buff = numpy.zeros(2, dtype=numpy.float32)

        ##Delay-related attributes
        self.b1_delay = B_delay
        self.delay = 0.0

        ##GNURadio
        self.set_tag_propagation_policy(gr.TPP_CUSTOM)
        self.set_relative_rate(1.0/self.M)

    def forecast(self, noutput_items, ninput_items_required):
        #Most of the time, this block simply decimates by M
        ninput_items_required[0] = self.M * self.Q * noutput_items

    def delay_detect(self, sig, hard_sym):
        reconst_sig = numpy.zeros(self.M*self.Q + 2*self.Q, dtype=numpy.complex64)
        reconst_sig[self.Q:-self.Q] = self.modulator.modulate(hard_sym)

        return numpy.argmax(numpy.abs(numpy.correlate(sig, reconst_sig))) - self.Q

    def cfo_detect(self):
        #Frequency discriminator
        phase_diff = numpy.mod(numpy.diff(self.phase_buff)+numpy.pi, 2*numpy.pi)-numpy.pi

        #Compute error
        return phase_diff*0.5/(self.M*numpy.pi)

    def vco_advance(self, freq, step):
        #self.init_phase *= numpy.exp(1j*2*numpy.pi*freq*step)
        self.init_phase = numpy.mod(self.init_phase + 2*numpy.pi*freq*step, 2*numpy.pi)

        return numpy.exp(self.init_phase)

    def vco_advance_vec(self, freq, n_samples):
        k = numpy.arange(0, n_samples)

        phasor = numpy.exp(1j*2*numpy.pi*freq*k + 1j*self.init_phase)

        #Update initial phase
        self.init_phase = numpy.mod(self.init_phase \
                + 2*numpy.pi*freq*(n_samples-1), 2*numpy.pi)

        return phasor

    def cfo_correct(self, in_sig):
        return in_sig*self.vco_advance_vec(-self.est_cfo/self.Q, self.M*self.Q)

    def init_est_cfo_with_tag(self, start, stop):
        tags_fine_cfo = self.get_tags_in_window(0, start, stop, \
                pmt.intern('fine_freq_offset'))
        tags_coarse_cfo = self.get_tags_in_window(0, start, stop, \
                pmt.intern('coarse_freq_offset'))

        if (len(tags_fine_cfo) == 0) and (len(tags_coarse_cfo) == 0):
            return

        if (len(tags_fine_cfo) > 0) and (len(tags_coarse_cfo) > 0):
            self.est_cfo = pmt.to_python(tags_fine_cfo[0].value) \
                    + pmt.to_python(tags_coarse_cfo[0].value)
        elif (len(tags_coarse_cfo) > 0):
            self.est_cfo = pmt.to_python(tags_coarse_cfo[0])
        else:
            self.est_cfo = pmt.to_python(tags_fine_cfo[0])

        #Reset VCO phase
        self.init_phase = 0.0

    def handle_tag_prop(self, in_start_idx, in_stop_idx, out_idx):
        tags = self.get_tags_in_window(0, in_start_idx, in_stop_idx+1)

        for tag in tags:
            tag.offset = out_idx + self.nitems_written(0)
            self.add_item_tag(0, tag)

            tag.offset = out_idx + self.nitems_written(1)
            self.add_item_tag(1, tag)

            tag.offset = out_idx + self.nitems_written(2)
            self.add_item_tag(2, tag)

            tag.offset = out_idx + self.nitems_written(3)
            self.add_item_tag(3, tag)


    def general_work(self, input_items, output_items):
        in0 = input_items[0]
        out0 = output_items[0]
        out1 = output_items[1]
        out2 = output_items[2]
        out3 = output_items[3]

        sym_count = 0

        start_idx = 0
        stop_idx = self.M*self.Q - 1
        while (stop_idx < len(in0)) and (sym_count < len(out0)):
            ##Check for pkt_start
            tags_pkt_start = self.get_tags_in_window(0, start_idx, stop_idx+1, \
                    pmt.intern('pkt_start'))
            if len(tags_pkt_start) > 0:
                #Initialize CFO estimate
                self.init_est_cfo_with_tag(start_idx, stop_idx+1)
                #Reset delay estimate
                self.delay = 0.0

                can_start_idx = tags_pkt_start[0].offset - self.nitems_read(0)

                if can_start_idx != start_idx:
                    #Shift tags by the number of items to be deleted
                    self.handle_tag_prop(start_idx, can_start_idx-1, sym_count)

                    #Skip items to align to can_start_idx
                    start_idx = can_start_idx
                    stop_idx = start_idx + self.M*self.Q - 1

                    #Reset global symbol counter
                    self.global_sym_count = 0

                    continue

            ##Handle tag propagation
            self.handle_tag_prop(start_idx, stop_idx, sym_count)

            ##Demodulate
            sig = self.cfo_correct(in0[start_idx:(stop_idx+1)])
            (sym, spectrum) = self.demodulator.demodulate_with_spectrum(sig[::self.Q])

            self.phase_buff = numpy.roll(self.phase_buff, -1)
            self.phase_buff[-1] = numpy.angle(spectrum[0][sym])

            ##CFO estimation if at least 2 symbols were demodulated
            cfo_err = 0.0
            old_cfo = self.est_cfo
            if self.global_sym_count > 0:
                cfo_err = self.cfo_detect()
                #Loop Filter
                self.est_cfo += self.b1_cfo * cfo_err
            else:
                self.global_sym_count += 1
            out2[sym_count] = self.est_cfo
            #out2[sym_count] = cfo_err

            ##Delay estimation is sensitive to CFO. Thus, it is estimated only
            ##once an estimate of the CFO is produced
            delay_err = self.delay_detect(sig, sym)
            self.delay += self.b1_delay * delay_err
            out3[sym_count] = self.delay
            #out3[sym_count] = delay_err

            #Next symbol
            int_delay = int(numpy.round(self.delay))

            start_idx += self.M*self.Q + int_delay
            stop_idx = start_idx + self.M*self.Q-1

            #Acount for delay compensation in start_idx
            self.delay -= int_delay
            #Acount for delay compensation in the VCO
            if int_delay > 0:
                self.vco_advance(self.est_cfo/self.Q, int_delay);
            else:
                self.vco_advance(old_cfo/self.Q, int_delay);

            ##TODO: Handle tag propagation of deleted items (?)

            ##Outputs
            out0[sym_count] = sym
            out1[sym_count] = spectrum[0]

            #Increment number of processed symbols in this call of work
            sym_count += 1

        #Tell GNURadio how many items were produced
        self.consume(0, start_idx)
        return sym_count
