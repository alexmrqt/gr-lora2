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

#ifndef INCLUDED_LORA2_LORA_SOFT_DEINTERLEAVER_H
#define INCLUDED_LORA2_LORA_SOFT_DEINTERLEAVER_H

#include <lora2/api.h>
#include <gnuradio/block.h>

namespace gr {
namespace lora2 {

/*!
 * \brief LoRa deinterleaver for soft bits streams.
 *
 * The effect of the interleaver is to shuffle input bits. The deinterleaver
 * then applies de-shuffling, to put bits back in their original position.
 *
 * Here, this block acts on soft bits, that is: values whose size represent the
 * binary value, and whose amplitude gives the confidence on the binary value..
 *
 * This blocks works on blocks of `CR+4` input vectors (`CR` being the coding
 * rate, between 1 and 4), each composed of SF soft bits, and output blocks of
 * `SF.(CR+4)` soft bits, or `(SF-2).(CR+4)` soft bits if `reduced_rate == true`.
 *
 * The input-output relationship is as follows: let
 * \f$ (in[0] \ldots in[CR+4-1]) \in \mathbb{R}^{SF.(CR+4)} \f$ be the input
 * block, and let us denote \f$ in_l[k] \in \mathbb{R} \f$ the l-th soft bit of
 * \f$in[k]\f$ (the k-th symbol of the input block).
 * Then, the output binary items are given as:
 * \f[
 * out[i(CR+4) + j] = in_{SF-1 - (SF-1-i + CR+4-1-j)\%SF}[CR+4-1-j]
 * \quad \in [0;1]
 * \quad \forall i\in[0;SF-1], j\in[0;CR+4-1]
 * \f]
 *
 */
class LORA2_API lora_soft_deinterleaver : virtual public gr::block
{
	public:
		typedef boost::shared_ptr<lora_soft_deinterleaver> sptr;

		/*!
		 * \brief Return a shared_ptr to a new instance of lora2::lora_soft_deinterleaver.
		 *
		 * \param SF LoRa spreading factor.
		 * \param CR LoRa coding rate (between 1 and 4).
		 * \param reduced_rate Set to true for LoRa low datarate optimization.
		 */
		static sptr make(int SF, int CR, bool reduced_rate=false);
};

} // namespace lora2
} // namespace gr

#endif /* INCLUDED_LORA2_LORA_SOFT_DEINTERLEAVER_H */

