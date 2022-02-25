/* -*- c++ -*- */
/*
 * Copyright 2022 Alexandre Marquet.
 *
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 *
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifndef INCLUDED_LORA2_CSS_DEMOD_ALGO_H
#define INCLUDED_LORA2_CSS_DEMOD_ALGO_H

#include <lora2/api.h>
#include <gnuradio/expj.h>
#include <gnuradio/fft/fft.h>
#include <gnuradio/fft/fft_shift.h>
#include <volk/volk.h>

namespace gr {
namespace lora2 {

/*!
 * \brief A class to demodulate CSS signals.
 *
 * This class contains methods to non-coherently demodulate baseband, critically
 * sampled M-ary CSS-modulated signals. Such signals are expressed as:
 * \f[
 * s[k] = e^{\alpha j2\pi\frac{k^2}{M}} \sum_n \Pi_M[k-nM] e^{j2\pi\frac{c_n}{M}k}
 * \f]
 * where:
 *  - \f$\alpha=1\f$ for upchirp CSS signals, \f$\alpha=0\f$ for downchirp CSS signals.
 *  - \f$\log_2(M)\f$ is the number of bits per symbol,
 *  - \f$c_n \in [0;M-1]\f$ is the value taken by the \f$n\f$-th symbol,
 *  - \f$\Pi_M[k] = 1\f$ if \f$k \in [0;M-1]\f$ else \f$\Pi_M[k] = 0\f$: the
 *  rectangular window of length \f$M\f$.
 *
 */
class LORA2_API css_demod_algo
{
	private:
		//! Number of possible symbols
		int d_M;

		/*!
		 * Contains the M samples of the conjugated base chirp:
		 * \f[
		 * chirp[k] = e^{-\alpha j2\pi\frac{k^2}{M}}
		 * \f].
		 */
		gr_complex *chirp;

		//! Object to perform FFT
		fft::fft_complex d_fft;

		//! Object to perform FFT-shift
		fft::fft_shift<gr_complex> d_fft_shift;

	public:
		/*!
		 * Construct an M-ary CSS demodulator.
		 *
		 * \param M Arity of the CSS modulated signal (\f$\log_2(M)\f$ being
		 * the number of bits per symbol).
		 * \param upchirp Set this to false if the signal is a downchirped CSS
		 * modulated signal.
		 */
		css_demod_algo(int M, bool upchirp=true);

		~css_demod_algo();

		/*!
		 * Demodulates CSS-modulated symbols.
		 *
		 * The input/output relationship is given by:
		 * \f[
		 * out[n] = \arg\max_{\hat c \in [0;M-1]} \left|
		 * 		\mathcal{F}_M\left\{e^{-\alpha j2\pi\frac{k^2}{M}}.in[k-nM]\right\}[\hat c]
		 * 		\right| \quad \forall n \in [0 ; n\_syms-1]
		 * \f]
		 * with \f$\mathcal{F}_M{s[k]}[m]\f$ the \f$M\f$-point discrete Fourier
		 * transform of \f$s[k]\f$, evaluated at bin \f$m \in [0;M-1]\f$.
		 *
		 * \param in Input signal. Must contain `n_syms*M` elements.
		 * \param out Estimated symbols. Must be allocated with a size of
		 * `n_syms` elements.
		 * \param n_syms Number of symbols to be demodulated.
		 */
		void demodulate(const gr_complex *in,
				unsigned short *out,
				size_t n_syms);

		/*!
		 * Demodulates CSS-modulated symbols, and gives confidence on the
		 * estimated symbols.
		 *
		 * The input/output relationships are given below.
		 * Define \f$\gamma[n,l]\f$ as the output of the \f$l\f$-th correlator 
		 * for the \f$n\f$-th received symbol:
		 * \f[
		 * \gamma[n,l] = \mathcal{F}_M\left\{e^{-\alpha j2\pi\frac{k^2}{M}}.in[k-nM]\right\}[l]
		 * 		\quad \forall n \in [0 ; n\_syms-1], l \in [0 ; M-1]
		 * \f]
		 * with \f$\mathcal{F}_M{s[k]}[m]\f$ the \f$M\f$-point discrete Fourier
		 * transform of \f$s[k]\f$, evaluated at bin \f$m \in [0;M-1]\f$.
		 * Then, the input output relationship is given by:
		 * \f[
		 * out\_syms[n] = \arg\max_{\hat c \in [0;M-1]} \left|\gamma[n,\hat c]\right|
		 * \quad \forall n \in [0 ; n\_syms-1]
		 * \f]
		 * \f[
		 * out\_soft[n] = \left|\gamma[n,out\_syms[n]]\right|
		 * \quad \forall n \in [0 ; n\_syms-1]
		 * \f]
		 * Note that \f$out\_soft[n] \in [0;M]\f$, where \f$0\f$ is the lowest
		 * confidence, and \f$M\f$ the highest.
		 *
		 * \param in Input signal. Must contain `n_syms*M` elements.
		 * \param out_syms Estimated symbols. Must be allocated with a size of
		 * `n_syms` elements.
		 * \param out_soft Confidence in the estimated symbols.
		 * Must be allocated with a size of `n_syms` elements.
		 * \param n_syms Number of symbols to be demodulated.
		 */
		void soft_demodulate(const gr_complex *in,
				unsigned short *out_syms,
				float *out_soft,
				size_t n_syms);

		/*!
		 * Demodulates CSS-modulated symbols. For each symbol, gives the
		 * corresponding complex value at the output of the correlator.
		 *
		 * The input/output relationships are given below.
		 * Define \f$\gamma[n,l]\f$ as the output of the \f$l\f$-th correlator 
		 * for the \f$n\f$-th received symbol:
		 * \f[
		 * \gamma[n,l] = \mathcal{F}_M\left\{e^{-\alpha j2\pi\frac{k^2}{M}}.in[k-nM]\right\}[l]
		 * 		\quad \forall n \in [0 ; n\_syms-1], l \in [0 ; M-1]
		 * \f]
		 * with \f$\mathcal{F}_M{s[k]}[m]\f$ the \f$M\f$-point discrete Fourier
		 * transform of \f$s[k]\f$, evaluated at bin \f$m \in [0;M-1]\f$.
		 * Then, the input output relationship is given by:
		 * \f[
		 * out\_syms[n] = \arg\max_{\hat c \in [0;M-1]} \left|\gamma[n,\hat c]\right|
		 * \quad \forall n \in [0 ; n\_syms-1]
		 * \f]
		 * \f[
		 * out\_complex[n] = \gamma[n,out\_syms[n]]
		 * \quad \forall n \in [0 ; n\_syms-1]
		 * \f]
		 *
		 * \param in Input signal. Must contain `n_syms*M` elements.
		 * \param out_syms Estimated symbols. Must be allocated with a size of
		 * `n_syms` elements.
		 * \param out_complex Complex value at the output of the correlator
		 * associated with each demodulated symbol. Must be allocated with a
		 * size of `n_syms` elements.
		 * \param n_syms Number of symbols to be demodulated.
		 */
		void complex_demodulate(const gr_complex *in,
				unsigned short *out_syms,
				gr_complex *out_complex,
				size_t n_syms);

		/*!
		 * Demodulates CSS-modulated symbols. For each symbol, gives the \f$M\f$
		 * complex values at the output of the correlator.
		 *
		 * The input/output relationships are given below.
		 * Define \f$\gamma[n,l]\f$ as the output of the \f$l\f$-th correlator 
		 * for the \f$n\f$-th received symbol:
		 * \f[
		 * \gamma[n,l] = \mathcal{F}_M\left\{e^{-\alpha j2\pi\frac{k^2}{M}}.in[k-nM]\right\}[l]
		 * 		\quad \forall n \in [0 ; n\_syms-1], l \in [0 ; M-1]
		 * \f]
		 * with \f$\mathcal{F}_M{s[k]}[m]\f$ the \f$M\f$-point discrete Fourier
		 * transform of \f$s[k]\f$, evaluated at bin \f$m \in [0;M-1]\f$.
		 * Then, the input output relationship is given by:
		 * \f[
		 * out\_syms[n] = \arg\max_{\hat c \in [0;M-1]} \left|\gamma[n,\hat c]\right|
		 * \quad \forall n \in [0 ; n\_syms-1]
		 * \f]
		 * \f[
		 * out\_spectrum[n.M+l] = \gamma[n,l]
		 * \quad \forall n \in [0 ; n\_syms-1], l \in [0 ; M-1]
		 * \f]
		 * Note that \f$out\_soft[n] \in [0;M]\f$, where \f$0\f$ is the lowest
		 * confidence, and \f$M\f$ the highest.
		 *
		 * \param in Input signal. Must contain `n_syms*M` elements.
		 * \param out_syms Estimated symbols. Must be allocated with a size of
		 * `n_syms` elements.
		 * \param out_spectrum Output of the bank of correlators, for each
		 * demodulated symbol. Must be allocated with a size of `n_syms*M`
		 * elements.
		 * \param n_syms Number of symbols to be demodulated.
		 */
		void demodulate_with_spectrum(const gr_complex *in,
				unsigned short *out_syms,
				gr_complex *out_spectrum,
				size_t n_syms);

		/*!
		 * \return Arity of the CSS modulated signal \f$M\f$ (\f$\log_2(M)\f$
		 * being the number of bits per symbol).
		 */
		int get_M() const { return d_M; }
};

} // namespace lora2
} // namespace gr

#endif /* INCLUDED_LORA2_CSS_DEMOD_ALGO_H */

