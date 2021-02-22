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

#ifndef INCLUDED_LORA2_LORA_HAMMING_DECODE_H
#define INCLUDED_LORA2_LORA_HAMMING_DECODE_H

#include <lora2/api.h>
#include <gnuradio/block.h>

namespace gr {
namespace lora2 {

/*!
 * \brief LoRa Hamming decoder.
 *
 * This block implements a syndrome decoder (a.k.a: maximum likelihood hard
 * decoder) for the LoRa hamming code.
 *
 * Denoting \f$in[n] \in [0,1] \f$ the \f$n\f$-th input sample, the \f$k\f$-th
 * input block is defined as
 * \f$(in[4k] \dots in[4k+CR+3]) = (in_k[0], \dots in_k[CR+3]) \in [0;1]^{CR+4}\f$.
 * The syndrome \f$ s_k\in[0;1]^{CR} \f$ of this input block is computed as:
 * \f{align*}{
 * 	s_k &= (in_k[0] \oplus in_k[1] \oplus in_k[2] \oplus in_k[3] \oplus in_k[4])
 *	 	\: \mbox{ for } CR=1 \\
 * 	s_k &= (in_k[0] \oplus in_k[2] \oplus in_k[3] \oplus in_k[4],
 * 		in_k[1] \oplus in_k[3] \oplus in_k[4] \oplus in_k[5])
 * 		\: \mbox{ for } CR=2 \\
 * 	s_k &= (in_k[0] \oplus in_k[3] \oplus in_k[4] \oplus in_k[6],
 * 		in_k[1] \oplus in_k[3] \oplus in_k[4] \oplus in_k[5],
 * 		in_k[2] \oplus in_k[4] \oplus in_k[5] \oplus in_k[6])
 * 		\: \mbox{ for } CR=3 \\
 * 	s_k &= (in_k[0] \oplus in_k[5] \oplus in_k[5] \oplus in_k[7],
 * 		in_k[1] \oplus in_k[4] \oplus in_k[6] \oplus in_k[7],
 * 		in_k[2] \oplus in_k[4] \oplus in_k[5] \oplus in_k[6],
 * 		in_k[3] \oplus in_k[5] \oplus in_k[6] \oplus in_k[7])
 * 		\: \mbox{ for } CR=4
 * \f}
 * Each syndrome is associated with, of all \f$2^{CR+4}\f$possible error vectors,
 * the one having the lowest hammming weight (that is, the lower number of ones).
 * It is denoted \f$e(s_k) = (e_0 \dots e_{CR+3}) \in [0;1]^{CR+4}\f$.
 * Using the error vector, the output block is computed as:
 * \f[
 * 	(in[4k+CR] \oplus e_0 \dots in[4k+CR+3] \oplus e_3) \: \in [0;1]^4
 * \f]
 *
 * This block is not a tagged stream block, but it will update the length tag
 * identified by contructor paramter `len_tag_key`, if any (and if supplied).
 */
class LORA2_API lora_hamming_decode : virtual public gr::block
{
	public:
		typedef boost::shared_ptr<lora_hamming_decode> sptr;

		/*!
		 * \brief Return a shared_ptr to a new instance of lora2::lora_hamming_decode.
		 *
		 * \param CR Coding rate (between 1 and 4).
		 * \param len_tag_key Length tag key to be updated.
		 */
		static sptr make(int CR, const std::string &len_tag_key);
};

} // namespace lora2
} // namespace gr

#endif /* INCLUDED_LORA2_LORA_HAMMING_DECODE_H */

