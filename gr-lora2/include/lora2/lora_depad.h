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


#ifndef INCLUDED_LORA2_LORA_DEPAD_H
#define INCLUDED_LORA2_LORA_DEPAD_H

#include <lora2/api.h>
#include <gnuradio/tagged_stream_block.h>

namespace gr {
namespace lora2 {

/*!
 * \brief Removes padding bits of LoRa packets.
 *
 * This tagged stream block removed padding bits, appended by the transmitter
 * at the end of the LoRa packet in order to satisfy the block length
 * constraints of the LoRa interleaver.
 *
 * The input-output relationship is as follows: let
 * \f$ (in[0] \ldots in[L-1], 0 \ldots 0) \in [0;1]^{L+L_{pad}} \f$ be the input
 * block, then the output block is given as:
 * \f[
 * 		(in[0] \ldots in[L-1]) \in [0;1]^L
 * \f].
 * The padding length must be supplied either at the block construction, as a
 * parameter, or at runtime, using a tag with key `pad_len`.
 *
 */
class LORA2_API lora_depad : virtual public gr::tagged_stream_block
{
	public:
		typedef boost::shared_ptr<lora_depad> sptr;

		/*!
		 * \brief Return a shared_ptr to a new instance of lora2::lora_depad.
		 *
		 * \param len_tag_key Length tag key for the tagged stream.
		 * \param n_pad The number of padding bits to be trimmed (can be changed
		 * at runtime, using a tag with key `pad_len`).
		 */
		static sptr make(const std::string &len_tag_key, const uint8_t n_pad);
};

} // namespace lora2
} // namespace gr

#endif /* INCLUDED_LORA2_LORA_DEPAD_H */

