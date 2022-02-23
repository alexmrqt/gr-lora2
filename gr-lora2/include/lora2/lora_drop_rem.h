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

#ifndef INCLUDED_LORA2_LORA_DROP_REM_H
#define INCLUDED_LORA2_LORA_DROP_REM_H

#include <lora2/api.h>
#include <gnuradio/tagged_stream_block.h>

namespace gr {
namespace lora2 {

/*!
 * \brief Removes the first `20 - (SF-2)*4` payload bits, that are to be
 * transmitted with the header.
 *
 * This tagged stream block will drop the first `(20 - (SF-2)*4)` samples of the
 * tagged stream, and update its length tag accordingly.
 * Let `L_in` the the length of the input tagged stream, then the output tagged
 * stream will have a length of `L_out = L_in - (20 - (SF-2)*4)` samples, with
 * `SF` the LoRa spreading factor.
 *
 * In LoRa, the header contains 20 information bit. Also, the header uses "low
 * datarate optimize" and `CR=4`.
 * Recalling that the minimum block size in LoRa, when taking into account the
 * low datarate optimization, is `(SF-2)*4` (enforced by the interleaver), then
 * extra bits `(20 - (SF-2)*4)` can be transmitted along with the header
 * (for SF>7), within the header block.
 * While zero-padding could be a possibility, LoRa use those extra bits to
 * transmit the first bits of the payload.
 *
 * Note that these extra bits use the same transmission parameters as the rest
 * of the header: they are encoded with `CR=4` and use low datarate optimization.
 *
 */
class LORA2_API lora_drop_rem : virtual public gr::tagged_stream_block
{
	public:
		typedef boost::shared_ptr<lora_drop_rem> sptr;

		/*!
		 * \brief Return a shared_ptr to a new instance of lora2::lora_drop_rem.
		 *
		 * \param SF LoRa spreading factor.
		 * \param len_tag_key Length tag key for the tagged stream.
		 */
		static sptr make(unsigned char SF, const std::string &len_tag_key);
};

} // namespace lora2
} // namespace gr

#endif /* INCLUDED_LORA2_LORA_DROP_REM_H */

