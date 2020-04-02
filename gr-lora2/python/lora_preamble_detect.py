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
import pmt
from gnuradio import gr

from lora2 import css_demod_algo

_STATE_WAIT = 0
_STATE_UP = 1
_STATE_SYNC = 2
_STATE_DOWN = 3

class state_wait:
    def __init__(self, M, N_up, thres):
        self.M = M
        self.N_up = N_up
        self.thres = thres

        self.demod = css_demod_algo(self.M)

        self.buffer = numpy.zeros(self.N_up//2, dtype=numpy.int) - 1
        self.buffer_phi = numpy.zeros(self.N_up//2-1)

        self.samples_pre = numpy.zeros(self.M, dtype=numpy.complex64)

        self.phi = 0.0 #Fine frequency shift estimate

    def init_buffers(self):
        self.buffer = numpy.zeros(self.N_up//2, dtype=numpy.int) - 1
        self.buffer_phi = numpy.zeros(self.N_up//2-1)

    def dechirp(self, samples):
        return samples * numpy.exp(-1j*numpy.pi*(numpy.arange(0, self.M)**2)/self.M)

    def compute_phi(self, samples):
        return numpy.angle(numpy.sum(self.dechirp(self.samples_pre) * numpy.conjugate(self.dechirp(samples)))) / (2*numpy.pi)

    #samples are samples of current symbol
    #samples_pre are samples of previous symbol
    def work(self, samples):
        self.buffer = numpy.roll(self.buffer, -1)
        self.buffer[-1] = self.demod.demodulate(samples)[0]

        self.buffer_phi = numpy.roll(self.buffer_phi, -1)
        self.buffer_phi[-1] = self.compute_phi(samples)

        if self.buffer[-2] != -1:
            pre_detected = True
            for i in range(1, self.N_up//2):
                if abs((self.buffer[0] - self.buffer[i])%self.M) > 1:
                    pre_detected = False
                    break

            if pre_detected:
                self.phi = numpy.mean(self.buffer_phi) / self.M

                self.init_buffers()
                return _STATE_UP

        self.samples_pre = samples

        return _STATE_WAIT

    def get_fine_freq_shift(self):
        return self.phi

class state_up:
    def __init__(self, M, N_up):
        self.M = M
        self.N_up = N_up

        self.demod = css_demod_algo(self.M)

        self.buffer = numpy.zeros((self.N_up//2, M), dtype=numpy.complex64)

        self.up_cnt = 0

        self.up = 0
        self.neigh_up_val = numpy.zeros(3, dtype=numpy.complex64)

    def init_buffer(self):
        self.buffer = numpy.zeros((self.N_up//2, self.M), dtype=numpy.complex64)

    def work(self, samples):
        if self.up_cnt < (self.N_up//2-1):
            self.buffer[self.up_cnt][:] = samples

            self.up_cnt += 1

            return _STATE_UP
        else:
            self.buffer[self.up_cnt][:] = samples
            mean_samples = numpy.mean(self.buffer, axis=0)

            (sym, spectrum) = self.demod.demodulate_with_spectrum(mean_samples)

            self.up = sym[0]
            self.neigh_up_val[0] = spectrum[0][(self.up-1)%self.M]
            self.neigh_up_val[1] = spectrum[0][self.up]
            self.neigh_up_val[2] = spectrum[0][(self.up+1)%self.M]

            self.init_buffer()
            self.up_cnt = 0
            return _STATE_SYNC

    def get_up(self):
        return self.up

    def get_neigh_up_val(self):
        return self.neigh_up_val

class state_sync:
    def __init__(self, M):
        self.M = M

        self.demod = css_demod_algo(self.M)

        self.sync_cnt = 0

        self.sync_val = 0
        self.sync_idx = numpy.zeros(2, dtype=numpy.int)
        self.sync_conf = numpy.zeros(2, dtype=numpy.float32)

    def work(self, samples, sym_up):
        if self.sync_cnt == 0:
            self.sync_cnt += 1

            (self.sync_idx[0], self.sync_conf[0]) = self.demod.soft_demodulate(samples)

            return _STATE_SYNC
        else:
            (self.sync_idx[1], self.sync_conf[1]) = self.demod.soft_demodulate(samples)

            if self.sync_conf[0] > self.sync_conf[1]:
                self.sync_val = numpy.uint16( 3*numpy.round(((self.sync_idx[0]-sym_up)%self.M)/3) )
            else:
                self.sync_val = numpy.uint16( 3*numpy.round(((self.sync_idx[1]-sym_up)%self.M)/3) )

            self.sync_cnt = 0
            return _STATE_DOWN

    def get_sync_val(self):
        return self.sync_val

class state_down:
    def __init__(self, M):
        self.M = M

        self.demod = css_demod_algo(self.M, conjugate=True)

        self.down_cnt = 0

        self.down_val = numpy.zeros(2, dtype=numpy.uint16)
        self.neigh_down_val = numpy.zeros((2, 3), dtype=numpy.complex64)

        self.freq_shift = 0
        self.fine_time_shift = 0
        self.time_shift = 0

    def compute_freq_shift(self, up, down, neigh_up_val, neigh_down_val):
        eps = 1e-6
        up_diff = numpy.abs(neigh_up_val[2]) - numpy.abs(neigh_up_val[0])
        down_diff = numpy.abs(neigh_down_val[2]) - numpy.abs(neigh_down_val[0])
        nu = 0
        nu_star = 0

        if up_diff > eps:
            nu = 1
        elif up_diff < -eps:
            nu = -1

        if down_diff > eps:
            nu_star = 1
        elif down_diff < -eps:
            nu_star = -1
        gamma = nu if nu == nu_star else 0

        Gamma = lambda N,k: k if (k < N/2) else (k-N)

        tmp = int(up) + int(down) + gamma
        #print(str(0.5*Gamma(self.M, tmp%self.M)) + ", " + str(gamma))
        self.freq_shift = int(0.5*Gamma(self.M, tmp%self.M))

    def compute_time_shift(self, up):
        tmp = int(up) - int(self.freq_shift)
        self.time_shift = numpy.uint16(tmp%self.M)

    def compute_fine_time_shift(self, neigh_up_val):
        w = 1j*2*numpy.pi*self.time_shift/self.M
        tmp = numpy.exp(-w) * neigh_up_val[2] - numpy.exp(w) * neigh_up_val[0]
        tmp /= 2*neigh_up_val[1] \
                - numpy.exp(-w) * neigh_up_val[2] - numpy.exp(w) * neigh_up_val[0]

        if numpy.isnan(tmp):
            self.fine_time_shift = 0.0
        elif numpy.abs(numpy.real(tmp)) < 1.0:
            self.fine_time_shift = - numpy.real(tmp)
        else:
            self.fine_time_shift = 0.0

    def work(self, samples, up, neigh_up_val):
        if self.down_cnt == 0:
            self.down_cnt += 1

            (sym, spectrum) = self.demod.demodulate_with_spectrum(samples)
            self.down_val[0] = sym[0]
            self.neigh_down_val[0][0] = spectrum[0][(sym[0]-1)%self.M]
            self.neigh_down_val[0][1] = spectrum[0][sym[0]]
            self.neigh_down_val[0][2] = spectrum[0][(sym[0]+1)%self.M]

            return _STATE_DOWN
        else:
            (sym, spectrum) = self.demod.demodulate_with_spectrum(samples)
            self.down_val[1] = sym[0]
            self.neigh_down_val[1][0] = spectrum[0][(sym[0]-1)%self.M]
            self.neigh_down_val[1][1] = spectrum[0][sym[0]]
            self.neigh_down_val[1][2] = spectrum[0][(sym[0]+1)%self.M]

            if numpy.abs(self.neigh_down_val[0][1]) > numpy.abs(self.neigh_down_val[1][1]):
                self.compute_freq_shift(up, self.down_val[0], neigh_up_val, self.neigh_down_val[0])
            else:
                self.compute_freq_shift(up, self.down_val[1], neigh_up_val, self.neigh_down_val[1])

            self.compute_time_shift(up)
            self.compute_fine_time_shift(neigh_up_val)

            self.down_cnt = 0
            return _STATE_WAIT

    def get_freq_shift(self):
        return self.freq_shift / self.M

    def get_fine_time_shift(self):
        return self.fine_time_shift

    def get_time_shift(self):
        return self.time_shift

class lora_preamble_detect(gr.sync_block):
    """
    docstring for block lora_preamble_detect
    """
    def __init__(self, SF, preamble_len, thres=1e-4):
        gr.sync_block.__init__(self,
            name="lora_preamble_detect",
            in_sig=[numpy.complex64],
            out_sig=[numpy.complex64])

        self.M=int(2**SF)
        self.N_up = preamble_len
        self.thres = thres

        self.wait = state_wait(self.M, self.N_up, self.thres)
        self.up = state_up(self.M, self.N_up)
        self.sync = state_sync(self.M)
        self.down = state_down(self.M)

        self.state = _STATE_WAIT

        self.sym_up = 0
        self.neigh_up_val = numpy.zeros(3, dtype=numpy.complex64)
        self.sync_val = 0

        self.vco_phase = 0.0
        self.fine_freq_shift = 0.0
        self.freq_shift = 0
        self.fine_time_shift = 0
        self.time_shift = 0

        self.set_output_multiple(self.M)

    def tag_end_preamble(self, sof_idx):

        time_shift = (self.M - self.time_shift) if self.time_shift != 0 else 0

        #Prepare tag
        tag_offset = self.nitems_written(0) + time_shift + sof_idx*self.M \
                + self.M//4

        tag1_key = pmt.intern('fine_freq_offset')
        tag1_value = pmt.to_pmt(-self.fine_freq_shift)
        tag2_key = pmt.intern('coarse_freq_offset')
        tag2_value = pmt.to_pmt(self.freq_shift)
        tag3_key = pmt.intern('sync_word')
        tag3_value = pmt.to_pmt(int(self.sync_val))
        tag4_key = pmt.intern('time_offset')
        tag4_value = pmt.to_pmt(int(time_shift))
        tag5_key = pmt.intern('fine_time_offset')
        tag5_value = pmt.to_pmt(float(self.fine_time_shift))

        #Append tags
        self.add_item_tag(0, tag_offset, tag1_key, tag1_value)
        self.add_item_tag(0, tag_offset, tag2_key, tag2_value)
        self.add_item_tag(0, tag_offset, tag3_key, tag3_value)
        self.add_item_tag(0, tag_offset, tag4_key, tag4_value)
        self.add_item_tag(0, tag_offset, tag5_key, tag5_value)
        self.add_item_tag(0, tag_offset, pmt.intern('pkt_start'), pmt.PMT_NIL)

    def vco_advance_vec(self, freq, n_samples):
        k = numpy.arange(0, n_samples)

        phasor = numpy.exp(1j*2*numpy.pi*freq*k + 1j*self.vco_phase)

        #Update initial phase
        self.vco_phase = numpy.mod(self.vco_phase \
                + 2*numpy.pi*freq*(n_samples-1), 2*numpy.pi)

        return phasor

    def cfo_correct(self, in_sig):
        return in_sig*self.vco_advance_vec(self.fine_freq_shift, self.M)

    def work(self, input_items, output_items):
        in0 = input_items[0]
        out0 = output_items[0]

        n_syms = len(in0)//self.M

        for i in range(0, n_syms):
            samples = in0[i*self.M:(i+1)*self.M]

            if self.state == _STATE_WAIT:
                self.state = self.wait.work(samples)

                if self.state == _STATE_UP: #On state change
                    tag_offset = self.nitems_written(0) + (i+1)*self.M
                    self.add_item_tag(0, tag_offset, pmt.intern('STATE_UP'), pmt.PMT_NIL)

                    self.init_phase = 0.0
                    self.fine_freq_shift = self.wait.get_fine_freq_shift()

            elif self.state == _STATE_UP:
                self.state = self.up.work(self.cfo_correct(samples))

                if self.state == _STATE_SYNC: #On state change
                    tag_offset = self.nitems_written(0) + (i+1)*self.M
                    self.add_item_tag(0, tag_offset, pmt.intern('STATE_SYNC'), pmt.PMT_NIL)

                    self.sym_up = self.up.get_up()
                    self.neigh_up_val = self.up.get_neigh_up_val()

            elif self.state == _STATE_SYNC:
                self.state = self.sync.work(self.cfo_correct(samples), self.sym_up)

                if self.state == _STATE_DOWN: #On state change
                    tag_offset = self.nitems_written(0) + (i+1)*self.M
                    self.add_item_tag(0, tag_offset, pmt.intern('STATE_DOWN'), pmt.PMT_NIL)

                    self.sync_val = self.sync.get_sync_val()

            else:
                self.state = self.down.work(self.cfo_correct(samples), \
                        self.sym_up, self.neigh_up_val)

                if self.state == _STATE_WAIT: #On state change
                    tag_offset = self.nitems_written(0) + (i+1)*self.M
                    self.add_item_tag(0, tag_offset, pmt.intern('SYNCED'), pmt.PMT_NIL)

                    self.freq_shift = self.down.get_freq_shift()

                    self.fine_time_shift = -self.down.get_fine_time_shift()
                    self.time_shift = self.down.get_time_shift()

                    self.tag_end_preamble(i+1)

        #Copy input to output
        out0[:] = in0[:]

        return len(output_items[0])
