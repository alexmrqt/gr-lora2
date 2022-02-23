#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 Alexandre Marquet.
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

import math
import pmt
import numpy
import scipy
import scipy.signal
from gnuradio import gr

from lora2 import css_mod_algo
from lora2 import css_demod_algo

class css_demod(gr.basic_block):
    """
    A block to demodulate CSS signals while tracking delay and carrier frequency offset.

    Delay and frequency offsets are tracked using first order feedback loops,
    as described below.
    <pre>
           +---------+      +-----+
    ------>| Variable+----->|Mixer+------------------------------------+--------------+------>
           |  delay  |      +-----+                                    |              |
           +---------+         ^                                       |              |
                ^              |                                       v              |
                |              |          +-----------+        +----------------+     |
                |           +--+--+       |    a_f    |        |Frequency offset|     |
                |           | VCO |<------+ --------- |<-------+    estimator   |     |
                |           +-----+       | 1-z**(-1) |        +----------------+     |
                |                         +-----------+                               |
                |                                                                     |
                |                         +-----------+         +-------------+       |
                |                         |    a_t    |         |Timing offset|<------+
                +-------------------------+ --------- |<--------+  estimator  |
                                          | 1-z**(-1) |         +-------------+
                                          +-----------+
    </pre>
    Where \f$\frac{a}{1-z^{-1}}\f$ represents a discrete integrator with gain \f$a\f$.

    This block has one input, and four outputs:
     * Input 1: Critically sampled (M samples per CSS symbol), complex baseband equivalent of a CSS signal.
     * Output 1: Demodulated CSS symbols (uint16).
     * Output 2: Output of the bank of demodulators, see `gr::lora2::css_demod_algo::demodulate_with_spectrum()` (vector of M complex float).
     * Output 3: Estimated CFO (output of the discrete integrator) (float).
     * Output 4: Accumulated delay (output of the discrete integrator) (float).

    It can receive initial estimates of the tracking delay and carrier
    frequency offset, using the following tags:
     * `fine_time_offset`: fractional delay (float in [0;1[),
     * `coarse_freq_offset`: coarse frequency offset (float in [0/M;1[, expected steps of 1/M),
     * `fine_freq_offset`: fractional frequency offset (float in [0/M, 1/M[).
    these tags are expected to be received on the sample identifying the start
    of the packet (that is, the sample carrying a `pkt_start` tag).

    In this implementation:
        - Variable delay has a limited resolution (see parameter `Q_res` of the constructor).
        - Mixer and VCO are grouped in method `cfo_correct()`.
        - Frequency offset estimator is based on quadrature detection, see method `cfo_detect()`.
        - Timing offset estimator is based on correlation with a time-shifted version of the estimated received symbol, see method `delay_detect()`.
    """

    def __init__(self, M, a_f, a_t, Q_res, Q_det=4):
        """
        Constructs a CSS demodulator.

        Args:
            M       -- Arity of the CSS modulated signal (\f$\log_2(M)\f$ being
                    the number of bits per symbol).
            a_f     -- Gain of the frequency offset discrete integrator (float).
            a_t     -- Gain of the timing offset discrete integrator (float).
            Q_res   -- Resolution of the fractional variable delayer (integer).
            Q_det   -- Resolution of the timing offset detector (integer).
        """
        gr.basic_block.__init__(self,
            name="css_demod",
            in_sig=[numpy.complex64],
            out_sig=[numpy.uint16, (numpy.complex64, M), numpy.float32,
                numpy.float32])

        self.M = M
        self.Q_det = Q_det
        self.Q_res = Q_res
        self.demodulator = css_demod_algo(self.M)
        self.modulator = css_mod_algo(self.M, self.Q_det)
        self.global_sym_count = 0

        ##CFO-related attributes
        self.a1_cfo = a_f
        self.est_cfo = 0.0
        self.init_phase = 0.0
        #Keep track of the last two phases
        self.phase_buff = numpy.zeros(2, dtype=numpy.float32)

        ##Delay-related attributes
        self.a1_delay = a_t
        self.init_delay = 0
        self.delay = 0.0
        self.cum_delay = 0.0

        ##GNURadio
        self.set_tag_propagation_policy(gr.TPP_CUSTOM)
        self.set_relative_rate(1.0/self.M)

    def forecast(self, noutput_items, ninput_items_required):
        #Most of the time, this block simply decimates by M
        ninput_items_required[0] = self.M * noutput_items

    def delay_detect(self, sig, hard_sym):
        """
        A correlator-based timing offset estimator.

    Based on an estimated received symbol, this functions search for the
    delay that maximizes the correlation between the received signal and
    a reconstructed delayed version of the transmitted signal.

    Assuming an estimated symbol \f$\hat c_n \in [0;M-1]\f$ from a received signal \f$r_n[k]\f$,
    then the estimated fractional delay is given by:
    \f[
        \delta k = \frac{1}{Q_\text{det}} \arg\max_{n\in[0;Q_\text{det}[\subset\mathbb{N}} \sum_{k=0}^{M-1} r_n[k]g_{\hat c_n}^*[k.Q_\text{det} - n]
    \f]
    where \f$g_{c}[k]\f$ is the discrete baseband-equivalent modulated chirp
    corresponding to the symbol \f$c\in[0;M-1]\f$, using an interpolating factor
    of \f$Q_\text{det}\f$ (see `gr::lora2::css_mod_algo()`).

    Args:
        sig         -- Received signal (chirp) corresponding to the estimated symbol `hard_sym` (array of `M` complex values).
        hard_sym    -- Symbol estimated from the received signal (chirp) `sig` (integer in [0;M-1]).

    Returns:
        Estimation of the timing offset (float).

        """
        reconst_sig = self.modulator.modulate(hard_sym).reshape((self.Q_det, self.M), order='F')
        reconst_sig[self.Q_det//2:,:] = numpy.roll(reconst_sig[self.Q_det//2:,:], 1)

        delay = numpy.argmax(numpy.abs(numpy.dot(reconst_sig, numpy.conj(sig))))
        if delay >= self.Q_det//2:
            delay -= self.Q_det
        return -delay/self.Q_det

    def frac_delay(self, sig, delay):
        """
        A fractional delayer based on `scipy.signal.resample_poly`.

    This functions interpolates the input signal by a factor `Q_res`, then
    delayes the interpolated signal by `floor(delay * Q_res)` samples, and
    finally decimates the delayed signal by a factor `Q_res`, effectively
    performing a fractional delay.

    Args:
        sig     -- Signal (chirp) to be delayed (array of complex values).
        delay   -- Fractional delay (float in [0;1[).

    Returns:
        Fractionally-delayed version of the input signal.

        """
        int_delay = int(delay*self.Q_res)
        gcd = math.gcd(int_delay, self.Q_res)
        new_delay = int_delay//gcd
        new_interp = self.Q_res//gcd

        return scipy.signal.resample_poly(sig, new_interp, 1)[new_delay::new_interp].astype(numpy.complex64)

    def cfo_detect(self):
        """
        A quadrature-based frequency offset etimator.

    Based on the phase of the two last demodulated symbols (see output
    `out_complex` of `gr::lora2::css_demod_algo::complex_demodulate`),
    denoted \f$\phi_n, \phi_{n-1} \in [0;2\pi[\f$, the CFO \f$\hat\delta f\f$ is
    estimated as:
    \f[
        \hat\delta_f = \frac{1}{2\pi M}\arg\left\{e^{j\phi_n}e^{-j\phi_{n-1}}\right\}
    \f]
    with \f$_M\f$ the arity of the CSS modulated signal.

    Returns:
        An estimation of the CFO.
        """
        #Frequency discriminator
        phase_diff = numpy.mod(numpy.diff(self.phase_buff)+numpy.pi, 2*numpy.pi)-numpy.pi

        #Compute error
        return phase_diff*0.5/(self.M*numpy.pi)

    def vco_advance(self, freq, n_samples):
        """
        Voltage control oscillator.

    Generates a carrier with a given frequency, and maintains phase
    continuity accross subsecant calls:
    \f[
        out[n] = out[n-1].e^{j2\pi f_0}
    \f]
    with \f$f_0=\f$`freq`, the desired frequency.
    The initial value `out[n-1]` is set to `exp(self.init_phase)`.
    At the end of the function we set `self.init_phase = arg{out[n_samples-1]}`.

    Args:
        freq        --  Frequency of the generated carrier (float).
        n_samples   -- Number of samples to produce (integer > 0).

    Returns:
        A carrier with frequency `freq` (`n_samples` complex floats).
        """
        #self.init_phase *= numpy.exp(1j*2*numpy.pi*freq*step)
        k = numpy.arange(0, n_samples)

        phasor = numpy.exp(1j*2*numpy.pi*freq*k + 1j*self.init_phase, dtype=numpy.complex64)

        #Update initial phase
        self.init_phase = numpy.mod(self.init_phase \
                + 2*numpy.pi*freq*(n_samples-1), 2*numpy.pi)

        return phasor

    def cfo_correct(self, in_sig):
        """
        Correct estimated CFO.

    The CFO correction is made by mixing (multiplying) the input signal
    with a carrier with frequency opposite to the integrated CFO estimation:
    \f[
        out[n] = in[n].e^{-j2\pi\hat{\delta f} n}
    \f]
    With \f$\delta f=\f$`-self.est_cfo`.
    In order to maintain phase consistency of the generated carrier, a VCO is
    used to generate the carrier, see `vco_advance()`.

    Args:
        in_sig  -- Input signal to be CFO-corrected (array of M complex floats).

    Returns:
        CFO-corrected signal (array of M complex floats).
        """
        return in_sig*self.vco_advance(-self.est_cfo, self.M)

    def init_est_cfo_with_tag(self, start, stop):
        """
        Use values contained in tags to initialize the estimated CFO.

    The function looks for the tags:
     * `fine_freq_offset`
     * `coarse_freq_offset`
    Then sets `self.est_cfo` as the sum of the value carried by the two tags,
    and resets the VCO: `self.init_phase = 0` (see `vco_advance()`).

    Args:
        start   -- Will be passed to `get_tags_in_window()` of `gr::block`, as parameter `rel_start`.
        stop   -- Will be passed to `get_tags_in_window()` of `gr::block`, as parameter `rel_stop`.
        """
        tags_fine_cfo = self.get_tags_in_window(0, start, stop, \
                pmt.intern('fine_freq_offset'))
        tags_coarse_cfo = self.get_tags_in_window(0, start, stop, \
                pmt.intern('coarse_freq_offset'))

        #Init to 0 if no tag found
        if (len(tags_fine_cfo) == 0) and (len(tags_coarse_cfo) == 0):
            self.est_cfo = 0.0

        if (len(tags_fine_cfo) > 0) and (len(tags_coarse_cfo) > 0):
            self.est_cfo = pmt.to_python(tags_fine_cfo[0].value) \
                    + pmt.to_python(tags_coarse_cfo[0].value)
        elif (len(tags_coarse_cfo) > 0):
            self.est_cfo = pmt.to_python(tags_coarse_cfo[0].value)
        else:
            self.est_cfo = pmt.to_python(tags_fine_cfo[0].value)

        #Reset VCO phase
        self.init_phase = 0.0

    def init_delay_with_tag(self, start, stop):
        """
        Use values contained in tags to initialize the estimated timing offset.

    The function looks for the tag `fine_time_offset`, then sets `self.delay`
    with its value.

    Args:
        start   -- Will be passed to `get_tags_in_window()` of `gr::block`, as
                parameter `rel_start`.
        stop    -- Will be passed to `get_tags_in_window()` of `gr::block`, as
                parameter `rel_stop`.
        """
        tags_fine_delay = self.get_tags_in_window(0, start, stop, \
                pmt.intern('fine_time_offset'))

        #Init to 0 if no tag found
        if (len(tags_fine_delay) == 0):
            self.delay = 0.0
        else:
            self.delay = pmt.to_python(tags_fine_delay[0].value)

    def handle_tag_prop(self, in_start_idx, in_stop_idx, out_idx):
        """
        Propagates tags.

    This function gathers all the tags between items indices `in_start_idx` and
    `in_stop_idx`, then add them all to the index `out_idx` of all output streams.

    Args:
        in_start_idx    -- Will be passed to `get_tags_in_window()` of
                        `gr::block`, as parameter `rel_start`.
        in_stop_idx     -- Will be passed to `get_tags_in_window()` of
                        `gr::block`, as parameter `rel_stop`.
        out_idx         -- Relative index of the output streams item that will
                        receive tags.
        """
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
        """
        Handles CSS demodulation with timing offset and CFO correction and tracking.

    Upon reception of a tag `pkt_start`, this function will initialize
    delay and CFO estimates, using values of tags:
     * `fine_freq_offset` (see `init_est_cfo_with_tag()`)
     * `coarse_freq_offset` (see `init_est_cfo_with_tag()`)
     * `fine_time_offset` (see `init_delay_with_tag()`)

    depending on their availability.

    This function directly handles integer timing offsets, while fractional
    timing offsets and CFO are corrected with `frac_delay()` using value of
    `self.delay` and `cfo_correct()` using value of `self.est_cfo`, respectively.

    After each CSS symbol demodulation, an estimate of timing offset and CFO is
    produced based on `cfo_detect()` and `delay_detect()`, respectively.
    These estimates are fed to discrete integrators, in order to update values
    of `self.delay` and `self.est_cfo`.

    Args:
        input_items     -- Input GNURadio buffers (one input).
        output_items    -- Output GNURadio buffers (four outputs).

    Returns:
        Number of demodulated CSS symbols.
        """
        in0 = input_items[0]
        out0 = output_items[0]
        out1 = output_items[1]
        out2 = output_items[2]
        out3 = output_items[3]

        start_idx = self.init_delay
        stop_idx = start_idx + self.M - 1

        #If items are to be deleted, check that we are not missing a pkt_start
        if self.init_delay > 0:
            tags_pkt_start = self.get_tags_in_window(0, 0,
                    self.init_delay, pmt.intern('pkt_start'))

            if len(tags_pkt_start) > 0:
                start_idx = tags_pkt_start[0].offset - self.nitems_read(0)
                stop_idx = start_idx + self.M - 1

        sym_count = 0
        while (stop_idx < len(in0)) and (sym_count < len(out0)):
            ##Check for pkt_start
            tags_pkt_start = self.get_tags_in_window(0, start_idx, stop_idx+1, \
                    pmt.intern('pkt_start'))
            if len(tags_pkt_start) > 0:
                #Initialize CFO estimate
                self.init_est_cfo_with_tag(start_idx, stop_idx+1)

                #Reset delay estimate
                self.init_delay_with_tag(start_idx, stop_idx+1)
                self.cum_delay = self.delay

                can_start_idx = tags_pkt_start[0].offset - self.nitems_read(0)

                if self.delay < -1e-6: #Negative fractional delay must converted to positive
                    can_start_idx -= 1
                    self.delay += 1
                    self.cum_delay += 1

                if can_start_idx != start_idx:
                    #Shift tags by the number of items to be deleted
                    self.handle_tag_prop(start_idx, can_start_idx-1, sym_count)

                    #Skip items to align to can_start_idx
                    start_idx = can_start_idx
                    stop_idx = start_idx + self.M - 1

                    #Reset global symbol counter
                    self.global_sym_count = 0

                    continue

            ##Handle tag propagation
            self.handle_tag_prop(start_idx, stop_idx, sym_count)

            ##Demodulate
            sig = self.cfo_correct(in0[start_idx:(stop_idx+1)])
            sig = self.frac_delay(sig, self.delay)
            (sym, spectrum) = self.demodulator.demodulate_with_spectrum(sig)

            self.phase_buff = numpy.roll(self.phase_buff, -1)
            self.phase_buff[-1] = numpy.angle(spectrum[0][sym])

            ##CFO estimation if at least 2 symbols were demodulated
            cfo_err = 0.0
            old_cfo = self.est_cfo
            if self.global_sym_count > 0:
                cfo_err = self.cfo_detect()
                #Loop Filter
                self.est_cfo += self.a1_cfo * cfo_err
            else:
                self.global_sym_count += 1

            ##Delay estimation
            delay_err = self.delay_detect(sig, sym)
            self.delay += self.a1_delay * delay_err
            self.cum_delay += self.a1_delay * delay_err

            ##Outputs
            out0[sym_count] = sym
            out1[sym_count] = spectrum[0]
            out2[sym_count] = self.est_cfo
            #out2[sym_count] = cfo_err
            #out2[sym_count] = self.phase_buff[-1]
            out3[sym_count] = self.cum_delay
            #out3[sym_count] = delay_err

            ##Increment number of processed symbols in this call of work
            sym_count += 1

            ##Handle delay
            int_delay = int(numpy.round(self.delay))

            #Acount for delay compensation in start_idx
            self.delay -= int_delay
            #Update start/stop indices
            start_idx += self.M + int_delay
            #Negative fractional delay must converted to positive
            if self.delay < -1e-6:
                start_idx -= 1
                self.delay += 1
                int_delay += 1
            stop_idx = start_idx + self.M - 1

            #If items are to be deleted, check that we are not missing a pkt_start
            if int_delay > 0:
                tags_pkt_start = self.get_tags_in_window(0, start_idx - int_delay,
                        start_idx, pmt.intern('pkt_start'))

                if len(tags_pkt_start) > 0:
                    start_idx = tags_pkt_start[0].offset - self.nitems_read(0)
                    stop_idx = start_idx + self.M - 1

                    continue

        #Tell GNURadio how many items were produced
        if start_idx > len(in0):
            start_idx = len(in0)
            self.init_delay = start_idx - len(in0)
        else:
            self.init_delay = 0

        self.consume(0, start_idx)
        return sym_count
