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

#ifndef INCLUDED_LORA2_CSS_MOD_ALGO_H
#define INCLUDED_LORA2_CSS_MOD_ALGO_H

#include <lora2/api.h>
#include <gnuradio/expj.h>

namespace gr {
namespace lora2 {

/*!
 * \brief A class to modulate CSS signals.
 *
 * This class allows to modulate synmbols \f$c_n \in [0; M-1]\f$ using a M-ary
 * CSS modulation. The resulting signal is expressed as:
 * \f[
 * s[k] = \sum_n e^{\alpha 2\pi f_{c_n}[k] \frac{1}{M.Q} k}\Pi_{M.Q}[k - n.MQ]
 * \f]
 * with:
 * \f[
 * f_c[k] = \frac{k}{2.Q} + c - \frac{M}{2}
 * - M.\left\lfloor \frac{k}{M.Q} - \frac{1}{2} + \frac{c}{M} \right\rceil 
 * \f]
 * where:
 *  - \f$\alpha=1\f$ for upchirp CSS signals, \f$\alpha=0\f$ for downchirp CSS signals.
 *  - \f$\log_2(M)\f$ is the number of bits per symbol.
 *  - \f$Q > 1\f$ is the interpolation factor.
 *  - \f$c_n \in [0;M-1]\f$ is the value taken by the \f$n\f$-th symbol.
 *  - \f$\Pi_M[k] = 1\f$ if \f$k \in [0;M-1]\f$ else \f$\Pi_M[k] = 0\f$: the
 *  rectangular window of length \f$M\f$.
 *
 * When \f$Q=1\f$, the input-output relationship reduces to:
 * \f[
 * s[k] = e^{\alpha j2\pi\frac{k^2}{M}} \sum_n \Pi_M[k-nM] e^{j2\pi\frac{c_n}{M}k}
 * \f]
 *
 */
class LORA2_API css_mod_algo
{
	private:
		//! Number of possible symbols
		int d_M;
		//! Interpolation factor
		int d_Q;
		//! True for upchirp-based CSS modulation, false for downchirp-based.
		bool d_upchirp;

	public:
		/*!
		 * Construct an M-ary CSS modulator
		 *
		 * \param M Arity of the CSS modulated signal (\f$\log_2(M)\f$ being
		 * the number of bits per symbol).
		 * \param interp Interpolation factor, so that the number of samples
		 * per CSS symbol is `M*interp`.
		 * \param upchirp Set this to true for upchirp-based CSS modulation, or
		 * false for downchirp-based.
		 */
		css_mod_algo(int M, int interp=1, bool upchirp=true);


		/*!
		 * Modulates input symbols \f$in[k] \: \in [0:M-1]\f$ using CSS.
		 * Each modulated symbol is made of `M*interp` complex output samples.
		 *
		 * The relationship between `in` and `out` is given as:
		 * \f[
		 * out[k] = \sum_n e^{\alpha 2\pi f_{in[n]}[k] \frac{1}{M.Q} k}\Pi_{M.Q}[k - n.MQ]
		 * \f]
		 * where:
		 * \f[
		 * f_c[k] = \frac{k}{2.Q} + c - \frac{M}{2}
		 * - M.\left\lfloor \frac{k}{M.Q} - \frac{1}{2} + \frac{c}{M} \right\rceil 
		 * \f]
		 * with:
		 * * \f$\Pi_{M.Q}[k]\f$ is the rectangular window of length \f$M.Q\f$
		 * symbols.
		 * * \f$alpha=1\f$ for upchirp-CSS, \f$alpha=0\f$ for downchirp-CSS.
		 * * \f$\left\lfloor \cdot \right\rceil\f$ the nearest integer rounding
		 * operator.
		 *
		 * When \f$Q=1\f$, the input-output relationship reduces to:
		 * \f[
		 * out[k] = e^{\alpha j2\pi\frac{k^2}{M}} \sum_{n=0}^{n\_syms} \Pi_M[k-nM] e^{j2\pi\frac{in[n]}{M}k}
		 * \f]
		 *
		 * \param in Input array of symbols.
		 * Each symbol in the array must be belong to [0;M-1].
		 * The number of elements in `in` must at least equal to `n_syms`.
		 * \param out Output array for samples of the CSS-modulated signal.
		 * Must be allocated with a size at least equal to `n_syms*M*interp`.
		 * \param n_syms Number of symbols in `in`.
		 */
		void modulate(const unsigned short *in, gr_complex *out, size_t n_syms);

		/*!
		 * \return Arity of the CSS modulated signal \f$M\f$ (\f$\log_2(M)\f$
		 * being the number of bits per symbol).
		 */
        int get_M() const { return d_M; };
		/*!
		 * \return Interpolation factor, such that `M*interp` is the number of
		 * complex samples per CSS symbol.
		 */
        int get_interp() const { return d_Q; };
};

} // namespace lora2
} // namespace gr

#endif /* INCLUDED_LORA2_CSS_MOD_ALGO_H */

