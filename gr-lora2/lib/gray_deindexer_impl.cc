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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "gray_deindexer_impl.h"

namespace gr {
namespace lora2 {

gray_deindexer::sptr gray_deindexer::make(unsigned int M)
{
	return gnuradio::get_initial_sptr
		(new gray_deindexer_impl(M));
}


/*
 * The private constructor
 */
gray_deindexer_impl::gray_deindexer_impl(unsigned int M)
	: gr::sync_block("gray_deindexer",
			gr::io_signature::make(1, 1, M*sizeof(float)),
			gr::io_signature::make(1, 1, M*sizeof(float))), d_M(M)
{
}

int gray_deindexer_impl::work(int noutput_items,
		gr_vector_const_void_star &input_items,
		gr_vector_void_star &output_items)
{
	const float *in = (const float*) input_items[0];
	float *out = (float*) output_items[0];

	// For each vector item (of d_M elements)
	for (int i=0 ; i < noutput_items ; ++i) {

		// Shuffle vector
		for (unsigned int j=0 ; j < d_M ; ++j) {
			// out[gray[j]] = in[j]
			out[j^(j>>1)] = *(in++);
		}

		// Go to next vector
		out += d_M;
	}

	// Tell runtime system how many output items we produced.
	return noutput_items;
}

} /* namespace lora2 */
} /* namespace gr */

