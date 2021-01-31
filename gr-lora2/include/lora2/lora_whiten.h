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


#ifndef INCLUDED_LORA2_LORA_WHITEN_H
#define INCLUDED_LORA2_LORA_WHITEN_H

#include <lora2/api.h>
#include <gnuradio/tagged_stream_block.h>

namespace gr {
namespace lora2 {

/*!
 * \brief Add/remove the LoRa whitening sequence to an input stream.
 *
 * This tagged stream block adds (modulo 2), the LoRa whitening sequence to the
 * input bits of the tagged streams.
 * LoRa does not whiten the CRC. Hence, if the input packet contains a CRC, then
 * a tag with key "has_crc" with value `pmt::PMT_T` must be present on the first
 * item of the tagged stream.
 * In the latter situation, the last 16 bits of the packet are not whitened.
 *
 * The input-output relationship of this block is as follows.
 * Let \f$ \mathbf{in} = (in[0] \dots in[L-1]) \: \in [0;1]^L \f$ be the input
 * stream, then the output stream in given as:o
 * \f[
 *  \mathbf{out} = \mathbf{in} \oplus \mathbf{w} \: \in [0;1]^L
 * \f]
 * where \f$ \oplus \f$ denotes the binary exclusive OR (XOR) operation, and
 * \f$ \mathbf{w} \: \in [0;1]^L \f$ is the whitening sequence, with
 * \f$ \mathbf{w} = (w[0] \dots w[L-1])\f$ is no CRC is
 * present and \f$ \mathbf{w} = (w[0] \dots w[L-16-1] \: 0 \dots 0)\f$ if a CRC is
 * present.
 *
 * The whitening sequence itself is generated using a 64-bit linear feedback
 * shift register (LFSR) with seed `0x1a3478f0f1f3f7ff` and polynomial
 * \f$ x^{64} + x^{48} + x^{40} + x^{32} + 1\f$.
 *
 */
class LORA2_API lora_whiten : virtual public gr::tagged_stream_block
{
	public:
		typedef boost::shared_ptr<lora_whiten> sptr;

		/*!
		 * \brief Return a shared_ptr to a new instance of lora2::lora_whiten.
		 *
		 * \param len_tag_key Length tag key for the tagged stream. 
		 */
		static sptr make(const std::string &len_tag_key);
};

} // namespace lora2
} // namespace gr

#endif /* INCLUDED_LORA2_LORA_WHITEN_H */

