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

#ifndef INCLUDED_LORA2_GRAY_ENCODE_H
#define INCLUDED_LORA2_GRAY_ENCODE_H

#include <lora2/api.h>
#include <gnuradio/sync_block.h>

namespace gr {
namespace lora2 {

/*!
 * \brief A Gray code encoder.
 *
 * This block Gray-encodes 16-bit (short) values.
 * Let `in[k]` be the input value then, after Gray encoding, the output is given
 * as `out[k]=in[k]^(in[k]>>1)`.
 *
 */
class LORA2_API gray_encode : virtual public gr::sync_block
{
	public:
		typedef boost::shared_ptr<gray_encode> sptr;

		/*!
		 * \brief Return a shared_ptr to a new instance of lora2::gray_encode.
		 */
		static sptr make();
};

} // namespace lora2
} // namespace gr

#endif /* INCLUDED_LORA2_GRAY_ENCODE_H */

