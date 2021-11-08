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
    """
    Class for the preamble detection state.

    This states takes M=2^SF (with SF the LoRa spreading factor) complex
    samples of a signal, and tries to detect if a LoRa preamble is present.

    A LoRa preamble is declared present if when the probability that `N_up/2`
    consecutive demodulated symbols being the same value exceeds a threshold
    \f$T \in ]0;1[\f$.

    When a preamble is detected, this state also estimates the fine frequency
    offset between of the received upchirps.
    """
    def __init__(self, M, N_up, thres):
        """
        Construct a preamble detection state.

        Args:
            M       -- Arity of the CSS modulated signal
                    (\f$log_2(M)\f$ being the number of bits per symbol). 
            N_up    -- Number of upchirp in a preamble.
            thres   -- Detection threshold, between 0 and 1.
        """
        self.M = M
        self.N_up = N_up
        self.thres = thres

        self.demod = css_demod_algo(self.M)

        self.buffer = numpy.zeros(self.N_up//2, dtype=numpy.int) - 1
        self.buffer_phi = numpy.zeros(self.N_up//2-1)

        self.cmplx_val_pre = 0.0

        self.phi = 0.0 #Fine frequency shift estimate

    def init_buffers(self):
        """
        (Re)Initialize internal buffers, in order to detect a new preamble.

    This function is called at each changement of state.
        """
        self.buffer = numpy.zeros(self.N_up//2, dtype=numpy.int) - 1
        self.buffer_phi = numpy.zeros(self.N_up//2-1)

    def compute_phi(self, cmplx_val_pre, cmplx_val):
        """
        Fine frequency offset estimator.

    Estimate the frequency offset between `cmplx_val` and `cmplx_val_pre`.
    The estimate is computed as:
    \f[
        \phi = \frac{1}{2.\pi} \arg\left\{z_{k-1}.z_k^*\right\}
    \f]
    Where \f$z_{k-1} = \f$`cmplx_val_pre`, and \f$z_k=\f$`cmplx_val`.

        Args:
            cmplx_val_pre   -- Complex number.
            cmplx_val       -- Complex number.

        Returns:
            An estimate of the frequency offset between the two complex arguments.
        """
        return numpy.angle(cmplx_val_pre * numpy.conjugate(cmplx_val)) / (2*numpy.pi)

    def detect_preamble(self):
        """
        LoRa preamble detector.

    This functions uses the lase `N_up/2` (see constructor) received symbols
    to detect a preamble.

    Let us denote \f$c_n \in \mathbb{C}\f$ the \f$n\f$-th demodulated value.
    A preamble is then detected if the following condition is met.
    \f[
        \frac{1}{M^2}.\sum_{n=0}^{N_{up}/2-1} |c_n - \mu|^2 < \epsilon
    \f]
    Where:
    * \f$ \mu = \sum_{n=0}^{N_{up}/2-1} c_n \f$
    * \f$ \epsilon= \f$`thres` (see constructor).

        Returns:
            True if a preamble is detected, else False.
        """
        #Buffer not full yet
        if self.buffer[0] == -1:
            return False

        mean = numpy.mean(self.buffer[-self.N_up//2:])
        mean_err_sq = numpy.sum(numpy.abs(self.buffer[-self.N_up//2:] - mean)**2)
        max_err_sq = self.M**2

        if(mean_err_sq/max_err_sq < self.thres):
            return True

        return False


    def work(self, samples):
        """
        Process M (2^SF) samples and gives next state (state_wait or state_up).

    Denoting SF the LoRa spreading factor, this functions process M=2^SF
    samples, and tries to detect a preamble.
    If a preamble is detected, then this function return `_STATE_UP`, for the
    FSM to go into the upchirp detection state.
    Else, it returns `_STATE_WAIT` to stay in the preamble detection state.

        Args:
            samples -- M=2^SF complex samples of a received signal.

        Returns:
            `_STATE_UP` if a preamble has been detected, or `_STATE_WAIT`.
        """
        self.buffer = numpy.roll(self.buffer, -1)
        (self.buffer[-1], cmplx_val) = self.demod.complex_demodulate(samples)

        self.buffer_phi = numpy.roll(self.buffer_phi, -1)
        self.buffer_phi[-1] = self.compute_phi(self.cmplx_val_pre, cmplx_val)

        if self.detect_preamble():
            self.phi = numpy.mean(self.buffer_phi) / self.M

            self.init_buffers()
            return _STATE_UP

        self.cmplx_val_pre = cmplx_val

        return _STATE_WAIT

    def get_fine_freq_shift(self):
        """
        Return the fine frequency offset associated with the last detected preamble.

    The returned value of this method is valid only if the last call to
    `work()` returned `_STATE_UP`.
        """
        return self.phi

class state_up:
    """
    Class for the upchirp processing state.

    This state counts \f$N_{up}/2\f$ LoRa symbols before passing to the next
    state (state_sync).
    It is also used to retrieve auxiliary quantities that allows to estimate the
    time and frequency offset of the incoming LoRa transmission (state_down),
    as well as the LoRa sync word (state_sync).
    """
    def __init__(self, M, N_up):
        """
        Construct an upchirp processing state.

        Args:
            M       -- Arity of the CSS modulated signal
                    (\f$log_2(M)\f$ being the number of bits per symbol). 
            N_up    -- Number of upchirp in a preamble.
        """
        self.M = M
        self.N_up = N_up

        self.demod = css_demod_algo(self.M)

        self.buffer = numpy.zeros((self.N_up//2, M), dtype=numpy.complex64)

        self.up_cnt = 0

        self.up = 0
        self.neigh_up_val = numpy.zeros(3, dtype=numpy.complex64)

    def init_buffer(self):
        """
        (Re)Initialize internal buffers.

    This function is called at each changement of state.
        """
        self.buffer = numpy.zeros((self.N_up//2, self.M), dtype=numpy.complex64)

    def work(self, samples):
        """
        Process M (2^SF) samples and gives next state (state_up or state_sync).

    Denoting SF the LoRa spreading factor, this functions process M=2^SF
    samples.
    It returns `_STATE_UP` for the first `N_{up}/2-1` calls, then returns
    `_STATE_SYNC`.

        Args:
            samples -- M=2^SF complex samples of a received signal.

        Returns:
            `_STATE_UP` for the first `N_{up}/2` calls, then `_STATE_SYNC`.
        """
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
        """
        Return the demodulated value representative of the last `N_up/2` symbols of the preamble.

    Let \f$ r_n = (r_n[0] \dots r_n[M-1]) \in \mathbb{C}^M, n\in[0, N_{up}/2]\f$
    be the n-th input of the state (n-th call to `work()`).
    We define:
    \f[
    \bar r = \left(\frac{2}{N_{up}}\sum_{n=0}^{N_{up}/2} r_n[0] \dots
    \frac{2}{N_{up}}\sum_{n=0}^{N_{up}/2} r_n[M-1]\right)
    \f]

    Then this method returns the CSS demodulated symbol corresponding to
    \f$\bar r\f$, using a non-coherent demodulator.
    It will be denoted \f$\hat{S}_{up}\f$ in the rest of the document.

    The returned value of this method is valid only if the last call to
    `work()` returned `_STATE_SYNC`.

        Returns:
            The demodulated value representative of the last `N_up/2` symbols
            of the preamble.
        """
        return self.up

    def get_neigh_up_val(self):
        """
        Return demodulated and adjacent symbols and associated correlator outputs.

    Return the correlator output corresponding to the demodulated value
    representative of the last `N_up/2` symbols of the preamble, as well
    as the two adjacent correlator outputs.

    Let \f$ r_n = (r_n[0] \dots r_n[M-1]) \in \mathbb{C}^M, n\in[0, N_{up}/2]\f$
    be the n-th input of the state (n-th call to `work()`).
    We define:
    \f[
    \bar r = \left(\frac{2}{N_{up}}\sum_{n=0}^{N_{up}/2} r_n[0] \dots
    \frac{2}{N_{up}}\sum_{n=0}^{N_{up}/2} r_n[M-1]\right)
    \f]

    Next, we define \f$\hat{S}_{up}\f$ and \f$ \bar R = (R[0] \dots R[M-1]) \in \mathbb{C}^M \f$,
    the demodulated symbol associated with samples \f$\bar r\f$ (using
    non-coherent demodulation), and the output of the non-coherent demodulator
    correlator, respectively.

    Then, this function returns
    \f$ R[(\hat{S}_{up} - 1) \text{mod} M] ; R[\hat{S}_{up}] ; R[(\hat{S}_{up} + 1) \text{mod} M] \f$
    as an array of three complex values.

    The returned value of this method is valid only if the last call to
    `work()` returned `_STATE_SYNC`.

        Returns:
            \f$ R[(\hat{S}_{up} - 1) \text{mod} M] ; R[\hat{S}_{up}] ; R[(\hat{S}_{up} + 1) \text{mod} M] \f$
            as an array of three complex values.
        """
        return self.neigh_up_val

class state_sync:
    """
    Class for the LoRa sync word processing state.

    This state counts 2 LoRa symbols before passing to the next state (state_down).
    It is also used to estimate the LoRa sync word, based on the demodulated
    value representative of the last `N_up/2` symbols of the preamble,
    determined in state_up.
    """
    def __init__(self, M):
        """
        Construct LoRa sync word processing state.

        Args:
            M       -- Arity of the CSS modulated signal
                    (\f$log_2(M)\f$ being the number of bits per symbol). 
        """
        self.M = M

        self.demod = css_demod_algo(self.M)

        self.sync_cnt = 0

        self.sync_val = 0
        self.sync_idx = numpy.zeros(2, dtype=numpy.int)
        self.sync_conf = numpy.zeros(2, dtype=numpy.float32)

    def work(self, samples, sym_up):
        """
        Process M (2^SF) samples and gives next state (state_sync or state_down).

    Denoting SF the LoRa spreading factor, this functions process \f$M=2^\text{SF}\f$
    samples.
    It returns _STATE_SYNC for the first call, then returns _STATE_DOWN.

        Args:
            samples -- M=2^SF complex samples of a received signal.
            sym_up  -- The demodulated value representative of the last `N_up/2`
                    symbols of the preamble.

        Returns:
            _STATE_SYNC for the first call, then _STATE_DOWN.
        """
        if self.sync_cnt == 0:
            self.sync_cnt += 1

            # TODO: demodulate instead of soft_demodulate
            (self.sync_idx[0], self.sync_conf[0]) = self.demod.soft_demodulate(samples)

            return _STATE_SYNC
        else:
            # TODO: demodulate instead of soft_demodulate
            (self.sync_idx[1], self.sync_conf[1]) = self.demod.soft_demodulate(samples)

            self.sync_val = 0
            self.sync_val |= numpy.uint16( numpy.round(((self.sync_idx[0]-sym_up)%self.M)/8) ) << 4
            self.sync_val |= numpy.uint16( numpy.round(((self.sync_idx[1]-sym_up)%self.M)/8) )

            self.sync_cnt = 0
            return _STATE_DOWN

    def get_sync_val(self):
        """
        Return the estimated LoRa sync word.

    Let `c0` and `c1` be the demodulated values of the two LoRa symbols in
    the sync word section of the preamble.
    Let `c_up` be the demodulated value representative of the last `N_up/2`
    symbols of the preamble.
    Then this function decodes the sync word as
    `sync_word = (((c0-c_up)%M)/8 << 4) | ((c1-c_up)%M)/8`.

    The returned value of this method is valid only if the last call to
    `work()` returned `_STATE_DOWN`.

        Returns:
            The estimated LoRa sync word.
        """
        return self.sync_val

class state_down:
    """
    Class for the LoRa down chirp processing state.

    This state counts 2 LoRa symbols before passing to the next state (state_wait).
    It is also used to estimate the coarse time and frequency offset, as well as
    the fine time frequency offset, based on the outputs of state_up.
    """
    def __init__(self, M):
        """
        Construct LoRa sync word processing state.

        Args:
            M       -- Arity of the CSS modulated signal
                    (\f$log_2(M)\f$ being the number of bits per symbol). 
        """
        self.M = M

        self.demod = css_demod_algo(self.M, upchirp=False)

        self.down_cnt = 0

        self.down_val = numpy.zeros(2, dtype=numpy.uint16)
        self.neigh_down_val = numpy.zeros((2, 3), dtype=numpy.complex64)

        self.freq_shift = 0
        self.fine_time_shift = 0
        self.time_shift = 0

    def compute_freq_shift(self, up, down, neigh_up_val, neigh_down_val):
        """
        Estimate the coarse frequency offset of the received preamble.

    This function is an implementation of the integer frequency offset
    described in Misc Xhonneux, M. et al., "A Low-complexity Synchronization
    Scheme for LoRa End Nodes", 2019.

    The estimated integer frequency offet is estimated as \f$\hat L/M\f$, with:
    \f[
        \hat L = \left\lceil \frac{1}{2}\Gamma_{2.SF}\left((\hat{S}_{up} + \hat{S}_{down} + \gamma) mod M\right)\right\rceil
    \f]
    and where:
    * \f$ \Gamma_N[k] = k \: \forall k\in[0;N/2[\f$, \f$\Gamma_N[k] = k-N \: \forall k\in[N/2;N[\f$,
    * \f$ \gamma = \nu \f$ if \f$ \nu = \nu^* \f$ else \f$\gamma = 0\f$,
    * \f$ \nu = sgn\left(|R[\hat{S_{up}}+1]| - |R[\hat{S_{up}}-1]|\right) \f$
        if \f$\left| |R[\hat{S_{up}}+1]| - |R[\hat{S_{up}}-1]| \right| > 10^{-6} \f$ else 
        \f$ \nu=0 \f$
    * \f$ \nu^* = sgn\left(|R^*[\hat{S_{down}}+1]| - |R^*[\hat{S_{down}}-1]|\right) \f$
        if \f$\left| |R^*[\hat{S_{down}}+1]| - |R^*[\hat{S_{down}}-1]| \right| > 10^{-6} \f$ else 
        \f$ \nu^*=0 \f$
    * \f$ R[k] \: \forall k\in[0;M-1]\f$ is the output of the non-coherent
        CSS correlator associated with the received upchirps in the first part
        of the preamble.
    * \f$ \hat{S}_{up} \f$ is the demodulated symbol value associated with
       \f$ R[k] \f$.
    * \f$ R^*[k] \: \forall k\in[0;M-1]\f$ is the output of the correlator
        associated the received downchirps.
    * \f$ \hat{S}_{down} \f$ is the demodulated symbol value associated
        with \f$ R^*[k] \f$.

        Args:
            up              -- Estimated demodulated value of the upchirp symbols.
                            See \f$ \hat{S}_{up} \f$ above.
            down            -- Estimated demodulated value of the downchirp symbols
                            See \f$ \hat{S}_{down} \f$ above.
            neigh_up_val    -- Output of the upchirp correlator at indices
                            `up-1`, `up` and `up+1` (as an array).
                            Equivalent to \f$ R[\hat{S_{up}}-1]\f$,
                            \f$ R[\hat{S_{up}}]\f$ and \f$ R[\hat{S_{up}}+1]\f$,
                            see above.
            neigh_down_val  -- Output of the downchirp correlator at indices
                            `down-1`, `down` and `down+1` (as an array).
                            Equivalent to \f$ R^*[\hat{S_{down}}-1]\f$,
                            \f$ R^*[\hat{S_{down}}]\f$ and \f$ R^*[\hat{S_{down}}+1]\f$,
                            see above.
        """
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

        Gamma = lambda N,k: k if (k < N//2) else (k-N)

        tmp = int(up) + int(down) + gamma
        self.freq_shift = int(numpy.ceil(0.5*Gamma(self.M, tmp%self.M)))

    def compute_time_shift(self, up):
        """
        Estimate the coarse timing offset of the received preamble.

    Knowing the value of the unmodulated upchirp symbols at the beginning
    of the preamble, as well as the coarse frequency offset, then it can be
    shown that the coarse timing offset is given as:
    \f[
        \hat{M} = \left(\hat{S}_{up} - \hat{L}\right) \: mod \: M
    \f]
    where :
     - \f$ \hat{S}_{up} \f$ is the estimated value of the unmodulated
         upchirp symbols at the beginning of the preamble.
     - \f$ \hat{L} \f$ is the estimated coarse frequency.

    See Xhonneux, M. et al., "A Low-complexity Synchronization Scheme for LoRa
    End Nodes", 2019.

        Args:
            up  -- Estimated demodulated value of the upchirp symbols.
        """
        tmp = int(up) - int(self.freq_shift)
        self.time_shift = numpy.uint16(tmp%self.M)

    def compute_fine_time_shift(self, neigh_up_val):
        """
        Estimate the fine timing offset of the received preamble.

    The estimator uses the following formula:
    \f[
        \hat\lambda = -\mathcal{R}\left\{\frac{W^{-\hat{M}}.R[(\hat{S_{up}}+1)\text{mod}M] - W^{\hat{M}}.R[(\hat{S_{up}}-1)\text{mod}M]}{2.R[\hat{S_{up}}] - W^{-\hat{M}}.R[(\hat{S_{up}}+1)\text{mod}M] - W^{\hat{M}}.R[(\hat{S_{up}}-1)\text{mod}M]}\right\}
    \f]
    Where:
    * \f$\mathcal{R}\{z\}\f$ is the real part or \f$z \in \mathbb{C}\f$.
    * \f$W^k = e^{j2\pi\frac{k}{M}}\f$
    * \f$M\f$ is the arity of the CSS modulated signal.
    * \f$\hat{M}\f$ is the coarse timing offset, as estimated by compute_time_shift().
    * \f$ R[k] \: \forall k\in[0;M-1]\f$ is the output of the non-coherent
        CSS correlator associated with the received upchirps in the first part
        of the preamble.
    * \f$ \hat{S}_{up} \f$ is the demodulated symbol value associated with
       \f$ R[k] \f$.

    See Xhonneux, M. et al., "A Low-complexity Synchronization Scheme for LoRa
    End Nodes", 2019.

    Note that the fine time shift is set to 0.0 if \f$|\hat\lambda| < 1.0\f$ or
    if the computation resulted in an invalid value (NaN).
    Otherwite, the fine time shift value is set to \f$\hat\lambda\f$.
        
        Args:
            neigh_up_val    -- \f$ R[(\hat{S}_{up} - 1) \text{mod} M] ; R[\hat{S}_{up}] ; R[(\hat{S}_{up} + 1) \text{mod} M] \f$ as an array of three complex values.
        """
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

    def work(self, samples, sym_up, neigh_up_val):
        """
        Process M (2^SF) samples and gives next state (state_down or state_wait).

    Denoting SF the LoRa spreading factor, this functions process \f$M=2^\text{SF}\f$
    samples.
    It returns _STATE_DOWN for the first call, then returns _STATE_WAIT.

    Of the two received downchirps, the one that leads to the (non-coherently)
    demodulated symbol associated with the highest correlator output is used to
    estimate the coarse frequency offset (see compute_freq_shift()).

        Args:
            samples -- \f$M=2^\text{SF}\f$ complex samples of a received signal.
            sym_up  -- The demodulated value representative of the last `N_up/2`
                    symbols of the preamble.
            neigh_up_val    -- Output of the upchirp correlator at indices
                            `sym_up-1`, `sym_up` and `sym_up+1` (as an array).

        Returns:
            _STATE_DOWN for the first call, then _STATE_WAIT.
        """
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
                self.compute_freq_shift(sym_up, self.down_val[0], neigh_up_val, self.neigh_down_val[0])
            else:
                self.compute_freq_shift(sym_up, self.down_val[1], neigh_up_val, self.neigh_down_val[1])

            self.compute_time_shift(sym_up)
            self.compute_fine_time_shift(neigh_up_val)

            self.down_cnt = 0
            return _STATE_WAIT

    def get_freq_shift(self):
        """
        Returns the estimated coarse frequency offset.

    The returned value of this method is only valid if the last call to work()
    returned _STATE_WAIT.

        Returns:
            The estimated coarse frequency offset.
        """
        return self.freq_shift / self.M

    def get_fine_time_shift(self):
        """
        Returns the estimated fine frequency offset.

    The returned value of this method is only valid if the last call to work()
    returned _STATE_WAIT.

        Returns:
            the estimated fine frequency offset.
        """
        return self.fine_time_shift

    def get_time_shift(self):
        """
        Returns the estimated coarse timing offset.

    The returned value of this method is only valid if the last call to work()
    returned _STATE_WAIT.

        Returns:
            the estimated coarse timing offset.
        """
        return self.time_shift

class lora_preamble_detect(gr.sync_block):
    """
    A block to detect the begining of a LoRa packet.

    Inputs are critically sampled (\f$M\f$ samples per symbol, with
    \f$M=2^{SF}\f$ and \f$SF\f$ the spreading factor), baseband complex
    equivalent of an incoming LoRa signal to be demodulated.

    Inputs are passed to the output, but upon detection of a LoRa preamble, the
    last sample of the preamble received the following tags:
     - fine_freq_offset: the estimated fine frequency offset
     (\f$\lt \pm 1/M\f$) of the LoRa signal,
     - coarse_freq_offset: the coarse fine frequency offset
     (\f$\geq \pm 1/M\f$) of the LoRa signal
     - time_offset: the estimated coarse timing offset, as a number of samples
     (used to position the tags on the last sample of the preamble),
     - fine_freq_offset: the fractional timing offset
     (i.e.: fraction of a sample) of the LoRa signal,
     - sync_word: estimated value of the LoRa sync word.

    This block implements a finite state machine with four states:
     - wait (class state_wait): detects `preamble_len/2` similar symbols
     and estimates fine frequency offset,
     - up (class state_up): uses the remaining `preamble_len/2` symbols of the
     start of frame pattern to estimate auxiliary quantities for the next states.
     - sync (class state_sync): estimates the LoRa preamble so-called "sync word".
     - down (class state_down): estimates coarse frequency offset coarse
     and fine timing offset.
    """

    def __init__(self, SF, preamble_len, thres=1e-4):
        """
        Constructs a LoRa preamble detector.

        Args:
            SF              -- LoRa spreading factor.
            preamble_len    -- Number of identical LoRa symbols at the begining
                            of the preamble (length of the start of frame pattern).
            thres           -- Detection threshold for the start of frame
                            pattern, between 0 and 1.
        """
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
        """
        Add tags at the end of the preamble.

    The following tags are added on the estimated last sample of the preamble:
     - `fine_freq_offset`,
     - `coarse_freq_offset`,
     - `sync_word`,
     - `time_offset`,
     - `fine_time_offset`.

        Args:
            sof_idx -- The index of the LoRa symbol on which the end of the
                    preamble was detected.
        """

        time_shift = (self.M - self.time_shift) if self.time_shift != 0 else 0

        #Prepare tag
        tag_offset = self.nitems_written(0) + time_shift + sof_idx*self.M \
                + self.M//4 -1

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
        r"""
        Run the voltage controlled oscillator on several samples.

    Let \f$\phi_0\f$ be the initial phase of the oscillator, then this
    function return `n_samples` samples as:
    \f[
    e^{j2\pi.f.k}.e^{j\phi_0} \quad \forall k\in[0 ; \text{n_samples}[
    \f]
    where \f$f\f$ takes the value of input parameter `freq`.

        Args:
            freq        -- Frequency of the VCO.
            n_samples   -- Number of samples to generate.

        Returns:
            A phasor of `n_samples` samples oscillating at frequency `freq`
        """
        k = numpy.arange(0, n_samples)

        phasor = numpy.exp(1j*2*numpy.pi*freq*k + 1j*self.vco_phase,
                dtype=numpy.complex64)

        #Update initial phase
        self.vco_phase = numpy.mod(self.vco_phase \
                + 2*numpy.pi*freq*(n_samples-1), 2*numpy.pi)

        return phasor

    def cfo_correct(self, in_sig):
        """Correct the carrier frequency offset (CFO) of input signal `in_sig`"""
        return in_sig*self.vco_advance_vec(self.fine_freq_shift, self.M)

    def work(self, input_items, output_items):
        """Process input items to find a preamble, estimate parameters, and tag the output stream."""
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
