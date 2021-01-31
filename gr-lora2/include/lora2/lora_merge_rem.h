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


#ifndef INCLUDED_LORA2_LORA_MERGE_REM_H
#define INCLUDED_LORA2_LORA_MERGE_REM_H

#include <lora2/api.h>
#include <gnuradio/tagged_stream_block.h>

namespace gr {
namespace lora2 {

/*!
 * \brief Merge back the `20 - (SF-2)*4` payload bits included at the end of the
 * header.
 *
 * This tagged stream block will merge the `20 - (SF-2)*4` payload bits included
 * at the end of the header to the tagged stream.
 * These `20 - (SF-2)*4` payload bits are to be suplied as a tag with key
 * "rem_bits" (and a PMT `u8_vector` as value, where each element of the vector
 * carries one bit) associated to the first sample of the input tagged stream.
 *
 * If no such tag is found, this block will simply copy its input to its output.
 * Otherwise, it will append `20 - (SF-2)*4` samples to the begining of this
 * tagged stream.
 *
 */
class LORA2_API lora_merge_rem : virtual public gr::tagged_stream_block
{
	public:
		typedef boost::shared_ptr<lora_merge_rem> sptr;

		/*!
		 * \brief Return a shared_ptr to a new instance of lora2::lora_merge_rem.
		 *
		 * \param SF LoRa spreading factor.
		 * \param len_tag_key Length tag key for the tagged stream.
		 */
		static sptr make(int SF, const std::string &len_tag_key);
};

} // namespace lora2
} // namespace gr

#endif /* INCLUDED_LORA2_LORA_MERGE_REM_H */

