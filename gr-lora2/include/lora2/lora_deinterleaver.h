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

#ifndef INCLUDED_LORA2_LORA_DEINTERLEAVER_H
#define INCLUDED_LORA2_LORA_DEINTERLEAVER_H

#include <lora2/api.h>
#include <gnuradio/block.h>

namespace gr {
namespace lora2 {

/*!
 * \brief LoRa deinterleaver.
 *
 * Let us denote \f$ \mathbf{d} \in [0;1]^N\f$ some binary LoRa data, and
 * \f$ D(\mathbf(d)) \in [0;1]^N\f$ the corresponding interleaved LoRa data.
 * Then, the deinterleaving operation \f$ D^{-1} \f$ is such that
 * \f$ D^{-1}(D(\mathbf(d))) = \mathbf(d) \f$: it cancels the effect of the
 * interleaver on the binary stream.
 *
 * This blocks works on blocks of `CR+4` input symbols (`CR` being the coding
 * rate, between 1 and 4, each symbol encoding SF bits), and output blocks of
 * `SF.(CR+4)` binary elements, or `(SF-2).(CR+4)` binary elements if
 * `reduced_rate == true`.
 *
 * The input-output relationship is as follows: let
 * \f$ (in[0] \ldots in[CR+4-1]) \in [0;SF-1]^{CR+4} \f$ be the input block,
 * and let us denote \f$ in_l[k] \in [0;1] \f$ the l-th bit of \f$in[k]\f$
 * (the k-th symbol of the input block).
 * Then, the output binary items are given as:
 * \f[
 * out[i(CR+4) + j] = in_{SF-1 - (SF-1-i + CR+4-1-j)\%SF}[CR+4-1-j]
 * \quad \in [0;1]
 * \quad \forall i\in[0;SF-1], j\in[0;CR+4-1]
 * \f]
 *
 */
class LORA2_API lora_deinterleaver : virtual public gr::block
{
	public:
		typedef boost::shared_ptr<lora_deinterleaver> sptr;

		/*!
		 * \brief Return a shared_ptr to a new instance of lora2::lora_deinterleaver.
		 *
		 * \param SF LoRa spreading factor.
		 * \param CR LoRa coding rate (between 1 and 4).
		 * \param reduced_rate Set to true for LoRa low datarate optimization.
		 */
		static sptr make(int SF, int CR, bool reduced_rate = false);
};

} // namespace lora2
} // namespace gr

#endif /* INCLUDED_LORA2_LORA_DEINTERLEAVER_H */

