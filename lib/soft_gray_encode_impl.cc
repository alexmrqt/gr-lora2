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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "soft_gray_encode_impl.h"

namespace gr {
namespace lora2 {

soft_gray_encode::sptr soft_gray_encode::make(unsigned int bpw)
{
	return gnuradio::get_initial_sptr
		(new soft_gray_encode_impl(bpw));
}


/*
 * The private constructor
 */
soft_gray_encode_impl::soft_gray_encode_impl(unsigned int bpw)
	: gr::sync_block("soft_gray_encode",
			gr::io_signature::make(1, 1, bpw*sizeof(float)),
			gr::io_signature::make(1, 1, bpw*sizeof(float))), d_bpw(bpw)
{
}

int soft_gray_encode_impl::work(int noutput_items,
		gr_vector_const_void_star &input_items,
		gr_vector_void_star &output_items)
{
	const float *in = (const float*) input_items[0];
	float *out = (float*) output_items[0];
	
	uint16_t hard_val = 0;

	// For each vector item (of d_bpw elements)
	for (int i=0 ; i < noutput_items ; ++i) {
		// Pack signbits and complement to get binary value
		hard_val = 0;
		for (unsigned int j=0 ; j < d_bpw ; ++j) {
			hard_val |= signbit(in[j])<<j;
		}

		// Gray encode
		hard_val ^= hard_val<<1;

		// Unpack gray encoded sign bits to soft values
		for (unsigned int j=0 ; j < d_bpw ; ++j) {
			*(out++) = copysign(*(in++), 1-2*(hard_val&0x01));
			hard_val >>= 1;
		}
	}

	// Tell runtime system how many output items we produced.
	return noutput_items;
}

} /* namespace lora2 */
} /* namespace gr */

