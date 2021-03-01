/* -*- c++ -*- */
/*
 * Copyright 2020 Alexandre Marquet.
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

#ifndef INCLUDED_LORA2_LORA_SOFT_HAMMING_DECODE_H
#define INCLUDED_LORA2_LORA_SOFT_HAMMING_DECODE_H

#include <lora2/api.h>
#include <gnuradio/block.h>

namespace gr {
namespace lora2 {

/*!
 * \brief LoRa soft Hamming decoder.
 *
 * This block implements a brute force maximum likelihood decoder for the LoRa
 * Hamming code.
 *
 * Let us denote \f$in[n] \in \mathbb{R} \f$ the \f$n\f$-th input sample.
 * The \f$k\f$-th input block is then defined as: 
 * \f$(in[4k] \dots in[4k+CR+3]) = (in_k[0], \dots in_k[CR+3]) = \mathbf{in}_k \in \mathbb{R}^{CR+4}\f$.
 * We also denote \f$ enc\{\mathbf{b}\} = (b[0] \dots b[3]) \in [0;1]^{CR+4} \f$
 * the Hamming encoding of the block \f$\mathbf{b} \in [0;1]^4\f$.
 * Then, this block decodes \f$ \mathbf{in}_k \f$ as:
 * \f[
 * \mathbf{out}_k = \mathrm{argmin}_{\mathbf{\bar{\mathrm{b}}} \in [0;1]^4}
 * \sum_{l=0}^{CR+3} enc\{\mathbf{\bar{\mathrm{b}}}\}[l].in_k[l]
 * \f]
 * where \f$ \mathbf{out}_k = (out_k[0] \dots out_k[3]) = (out[3k] \dots out[3k+3]) \in [0;1]^4\f$
 * is the \f$k\f$-th output block,
 * and \f$out[n] \in [0;1]\f$ is the \f$n\f$-th output sample.
 *
 * This block is not a tagged stream block, but it will update the length tag
 * identified by contructor paramter `len_tag_key`, if any (and if supplied).
 */
class LORA2_API lora_soft_hamming_decode : virtual public gr::block
{
	public:
		typedef boost::shared_ptr<lora_soft_hamming_decode> sptr;

		/*!
		 * \brief Return a shared_ptr to a new instance of lora2::lora_soft_hamming_decode.
		 *
		 * \param CR Coding rate (between 1 and 4).
		 * \param len_tag_key Length tag key to be updated.
		 */
		static sptr make(int CR, const std::string &len_tag_key);
};

} // namespace lora2
} // namespace gr

#endif /* INCLUDED_LORA2_LORA_SOFT_HAMMING_DECODE_H */

