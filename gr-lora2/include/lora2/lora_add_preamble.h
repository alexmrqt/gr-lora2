/* -*- c++ -*- */
/* 
 * Copyright 2018 Alexandre Marquet.
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


#ifndef INCLUDED_LORA2_LORA_ADD_PREAMBLE_H
#define INCLUDED_LORA2_LORA_ADD_PREAMBLE_H

#include <lora2/api.h>
#include <gnuradio/tagged_stream_block.h>

namespace gr {
namespace lora2 {

/*!
 * \brief Construct and append a LoRa preamble to a packet (payload and headers).
 *
 * This tagged stream block appends `pre_len` 0 items, followed by two items
 * encoding the `sync_word`, to the beginning of each tagged stream received..
 *
 * Let \f$s \in [0 ; 255]\f$ be the sync word value, then it is encoded by two
 * symbols with values `((s>>4)&0xF)*8` and `(s&0xF)*8`, respectively.
 *
 * The input-output relationship is as follows: let `(in[0] ... in[N-1])` be the
 * tagged stream at the input of the block (payload), then the output is given
 * by `(0 ... 0, ((s>>4)&0xF)*8, (s&0xF)*8, in[0] ... in[N-1])`.
 *
 */
class LORA2_API lora_add_preamble : virtual public gr::tagged_stream_block
{
	public:
		typedef boost::shared_ptr<lora_add_preamble> sptr;

		/*!
		 * \brief Return a shared_ptr to a new instance of lora2::lora_add_preamble.
		 *
		 * \param pre_len Number of leading zeros to append to received packets.
		 * \param sync_word Synchronization word value, between 0 and 255.
		 * \param len_tag_key Length tag key for the tagged stream. 
		 * \param sync_word_tag_key Name of the tag key used to identify the
		 * first sync_word item.
		 * \param payload_tag_key Name of the tag key used to identify the first
		 * payload item.
		 */
		static sptr make(int pre_len, int sync_word,
				const std::string &len_tag_key,
				const std::string &sync_word_tag_key,
				const std::string &payload_tag_key);
};

} // namespace lora2
} // namespace gr

#endif /* INCLUDED_LORA2_LORA_ADD_PREAMBLE_H */

