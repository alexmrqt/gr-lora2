/* -*- c++ -*- */
/* 
 * Copyright 2019 Alexandre Marquet.
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


#ifndef INCLUDED_LORA2_CSS_MOD_H
#define INCLUDED_LORA2_CSS_MOD_H

#include <lora2/api.h>
#include <gnuradio/sync_interpolator.h>

namespace gr {
namespace lora2 {

/*!
 * \brief A CSS Modulator.
 *
 * Modulates input symbols \f$in[k] \: \in [0:M-1]\f$ using CSS.
 * Each modulated symbol is made of `M*interp` complex output samples.
 *
 * Denoting \f$Q \in \mathbb{N}^*\f$ the interpolating factor, and considering
 * an input symbol \f$c \: \in [0:M-1]\f$, then the corresponding
 * CSS-modulated symbol is given as:
 * \f[
 * e^{2\pi f_c[k] \frac{1}{M.Q}k} \quad \forall k \in [0:M.Q-1]
 * \f]
 * Where \f$f_c[k]\f$ is the instantaneous frequency of the symbol:
 * \f[
 * f_c[k] = \frac{k}{2.Q} + c - \frac{M}{2}
 * - M.\left\lfloor \frac{k}{M.Q} - \frac{1}{2} + \frac{c}{M} \right\rceil 
 * \f]
 * Where \f$\left\lfloor \cdot \right\rceil\f$ is the nearest integer rounding
 * operator.
 *
 * As a result the input-output relationship of this block is given as:
 * \f[
 * out[k] = \sum_n e^{2\pi f_{in[n]}[k] \frac{1}{M.Q} k}\Pi_{M.Q}[k - n.MQ]
 * \f]
 * with \f$\Pi_{M.Q}[k]\f$ is the rectangular window of length \f$M.Q\f$ symbols.
 *
 * When \f$Q=1\f$, the input-output relationship reduces to:
 * \f[
 * out[k] = e^{j2\pi\frac{k^2}{M}} \sum_n \Pi_M[k-nM] e^{j2\pi\frac{in[n]}{M}k}
 * \f]
 */
class LORA2_API css_mod : virtual public gr::sync_interpolator
{
	public:
		typedef boost::shared_ptr<css_mod> sptr;

		/*!
		 * \brief Return a shared_ptr to a new instance of lora2::css_mod.
		 *
		 * \param M Arity of the CSS modulated signal (\f$\log_2(M)\f$ being
		 * the number of bits per symbol).
		 * \param interp The interpolation factor (length of each symbol is
		 * `M.interp` complex samples).
		 */
		static sptr make(int M, int interp = 1);
};

} // namespace lora2
} // namespace gr

#endif /* INCLUDED_LORA2_CSS_MOD_H */

