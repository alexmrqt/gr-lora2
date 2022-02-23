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

#ifndef INCLUDED_LORA2_LORA_INTERLEAVER_H
#define INCLUDED_LORA2_LORA_INTERLEAVER_H

#include <lora2/api.h>
#include <gnuradio/block.h>

namespace gr {
namespace lora2 {

/*!
 * \brief LoRa interleaver.
 *
 * This blocks implements the LoRa diagonal interleaver. It can either act on
 * regular streams, or tagged streams (and update their length tag key as needed).
 *
 * It works on input blocks of `SF.(CR+4)` binary elements,
 * (or `(SF-2).(CR+4)` binary elements if `reduced_rate == true`), and outputs
 * blocks of `CR+4` symbols (each symbol encodes SF bits).
 *
 * The input-output relationship is as follows: let
 * \f$ (in[0] \ldots in[SF.(CR+4)-1]) \in [0;1]^{SF.(CR+4)} \f$ be the input block,
 * and \f$ (out[0] \ldots out[CR+4-1]) \in [0;SF-1]^{CR+4} \f$ be the output block.
 * We further denote \f$ out_l[k] \in [0;1] \f$ the l-th bit of the k-th symbol
 * of the output block.
 * Then, the output items are given as:
 * \f[
 * out_j[i] = in[(SF-1 - ((j - i) \% SF + SF)\%SF).(CR+4) + CR+4-1 - i]
 * \quad \in [0;SF-1]
 * \quad \forall i\in[0;CR+4-1], j\in[0;SF-1]
 * \f]
 *
 */
class LORA2_API lora_interleaver : virtual public gr::block
{
	public:
		typedef boost::shared_ptr<lora_interleaver> sptr;

		/*!
		 * \brief Return a shared_ptr to a new instance of lora2::lora_interleaver.
		 *
		 * \param SF LoRa spreading factor.
		 * \param CR LoRa coding rate (between 1 and 4).
		 * \param len_tag_key Length tag key for the tagged stream.
		 * \param reduced_rate Set to true for LoRa low datarate optimization.
		 */
		static sptr make(int SF, int CR, const std::string &len_tag_key,
				bool reduced_rate=false);
};

} // namespace lora2
} // namespace gr

#endif /* INCLUDED_LORA2_LORA_INTERLEAVER_H */

