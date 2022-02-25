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

#ifndef INCLUDED_LORA2_LORA_HAMMING_ENCODE_H
#define INCLUDED_LORA2_LORA_HAMMING_ENCODE_H

#include <lora2/api.h>
#include <gnuradio/block.h>

namespace gr {
namespace lora2 {

/*!
 * \brief LoRa Hamming encoder.
 * 
 * The LoRa Hamming encoder is a systematic block error correcting codre,
 * acting on input blocks of 4 bits, and producing encoded blocks of 4+CR bits,
 * with \f$CR \in \{1,2,3,4\}\f$.
 * Consequently, the code has an efficiency \f$\eta = 4/(CR+4)\f$.
 *
 * Denoting \f$in[n] \in [0,1] \f$ the \f$n\f$-th input sample, the \f$k\f$-th
 * input block is defined as \f$(in[4k] \dots in[4k+3]) \in [0;1]^4\f$.
 * Similarly, the \f$k\f$-th output block is given as:
 * \f{align*}{
 * 	&(p_0, in_k[4k] \dots in[4k+3]) \: \mbox{ for } CR=1 \\
 * 	&(p_2, p_1, in[4k] \dots in[4k+3]) \: \mbox{ for } CR=2 \\
 * 	&(p_3, p_2, p_1, in[4k] \dots in[4k+3]) \: \mbox{ for } CR=3 \\
 * 	&(p_3, p_4, p_2, p_1, in[4k] \dots in[4k+3]) \: \mbox{ for } CR=4
 * \f}
 * Where, denoting \f$a \oplus b\f$ the exclusive-or (XOR) operation betwee,
 * \f$ a, b \in[0;1] \f$ :
 * \f{align*}{
 * 	p_0 &= in[4k] \oplus in[4k+1] \oplus in[4k+2] \oplus in[4k+3]\\
 * 	p_1 &= in[4k+1] \oplus in[4k+2] \oplus in[4k+3]\\
 * 	p_2 &= in[4k] \oplus in[4k+1] \oplus in[4k+2] \\
 * 	p_3 &= in[4k] \oplus in[4k+1] \oplus in[4k+3] \\
 * 	p_4 &= in[4k] \oplus in[4k+2] \oplus in[4k+3]
 * \f}
 *
 * This block is not a tagged stream block, but it will update the length tag
 * identified by contructor paramter `len_tag_key`, if any (and if supplied).
 *
 */
class LORA2_API lora_hamming_encode : virtual public gr::block
{
	public:
		typedef boost::shared_ptr<lora_hamming_encode> sptr;

		/*!
		 * \brief Return a shared_ptr to a new instance of lora2::lora_hamming_encode.
		 *
		 * \param CR Coding rate (between 1 and 4).
		 * \param len_tag_key Length tag key to be updated.
		 */
		static sptr make(int CR, const std::string &len_tag_key);
};

} // namespace lora2
} // namespace gr

#endif /* INCLUDED_LORA2_LORA_HAMMING_ENCODE_H */

