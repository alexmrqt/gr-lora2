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


#ifndef INCLUDED_LORA2_CSS_LLR_CONVERTER_H
#define INCLUDED_LORA2_CSS_LLR_CONVERTER_H

#include <lora2/api.h>
#include <gnuradio/sync_block.h>

namespace gr {
namespace lora2 {

/*!
 * \brief A block to compute bitwise log-likelihood ratios (LLR) for CSS signals.
 * \ingroup lora2
 *
 * Assuming an \f$M\f$-arry CSS system, the input of this block must be vectors
 * of \f$M\f$ elements:
 * \f[
 * in[k] = (in_0[k] \dots in_{M-1}[k])^T \in \mathbb{R}^M
 * \f]
 * These elements must represent either the real part (using coherent demodulation)
 * or the absolute value (using non-coherent demodulation) of the output of the
 * CSS correlator.
 *
 * Then, this block outputs the \f$\log_2(M)\f$ LLR of each bit comprising the
 * CSS symbol:
 * \f[
 * out_l[k] = {\max}^*_{c\in[0;M-1] s.t b_l(c)=0} \left\{in_c[k] / \sigma_n^2\right\}
 * - {\max}^*_{c\in[0;M-1] s.t b_l(c)=1} \left\{in_c[k] / \sigma_n^2\right\}
 *   \quad \forall l\in[0 ; \log_2(M)-1]
 * \f]
 * Where:
 * * \f$b_l(c)\f$ is the value of the \f$l\f$-th bit of the binary
 * representation of \f$c\f$.
 * * If `true_llr = false`
 *   * \f${\max}^*_{c\in\mathbb{I}} \{in_c\}
 * = \max_{c\in\mathbb{I}} \{in_c\} \f$ returns the greatest value of
 * \f$in_c \: \forall c\in\mathbb{I}\f$.
 *   * \f$\sigma_n^2 = 1\f$.
 * * If `true_llr = true`
 *   * \f${\max}^*_{c\in\mathbb{I}} \{in_c\}
 * = \log\left(\sum_{c\in\mathbb{I}} e^{in_c}\right)\f$.
 *   * \f$\sigma_n^2\f$ represents the variance of the noise.
 *
 * The final output takes the form of a vector of \f$\log_2(M)\f$ elements as:
 * \f[
 * out[k] = (out_0[k] \dots out_{M-1}[k])^T \in \mathbb{R}^{\log_2(M)}
 * \f]
 *
 */
class LORA2_API css_llr_converter : virtual public gr::sync_block
{
	public:
		typedef boost::shared_ptr<css_llr_converter> sptr;

		/*!
		 * \brief Return a shared_ptr to a new instance of lora2::css_llr_converter.
		 *
		 * \param M Arity of the CSS modulated signal (\f$\log_2(M)\f$ being
		 * the number of bits per symbol).
		 * \param true_llr Compute exact LLR if set to `true`.
		 * Else, approximates \f$\log\left(\sum_{c\in\mathbb{I}} e^{in_c}\right)
		 * \approx {\max}_{c\in\mathbb{I}} \{in_c\}\f$.
		 * \param sigma_n Standard deviation of the noise (assumed to be gaussian).
		 */
		static sptr make(int M, bool true_llr = false, float sigma_n = 0.0);
};

} // namespace lora2
} // namespace gr

#endif /* INCLUDED_LORA2_CSS_LLR_CONVERTER_H */

