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
#include "lora_pad_impl.h"

namespace gr {
namespace lora2 {

lora_pad::sptr lora_pad::make(const std::string &len_tag_key, unsigned char SF,
		unsigned char CR, bool reduced_rate)
{
	return gnuradio::get_initial_sptr
		(new lora_pad_impl(len_tag_key, SF, CR, reduced_rate));
}


/*
 * The private constructor
 */
lora_pad_impl::lora_pad_impl(const std::string &len_tag_key, unsigned char SF,
		unsigned char CR, bool reduced_rate)
	: gr::tagged_stream_block("lora_pad",
			gr::io_signature::make(1, 1, sizeof(char)),
			gr::io_signature::make(1, 1, sizeof(char)), len_tag_key),
	d_SF(SF), d_CR(CR), d_reduced_rate(reduced_rate)
{
}

int lora_pad_impl::calculate_output_stream_length(const gr_vector_int &ninput_items)
{
	//Compute padding length
	if ((ninput_items[0] % ((d_SF - 2*d_reduced_rate)*(4+d_CR))) != 0) {
		d_pad_len = (d_SF - 2*d_reduced_rate)*(4+d_CR) \
					- (ninput_items[0] % ((d_SF - 2*d_reduced_rate)*(4+d_CR)));
	}
	else {
		d_pad_len = 0;
	}

	int noutput_items = ninput_items[0] + d_pad_len;
	return noutput_items;
}

int lora_pad_impl::work (int noutput_items,
		gr_vector_int &ninput_items,
		gr_vector_const_void_star &input_items,
		gr_vector_void_star &output_items)
{
	const char *in = (const char *) input_items[0];
	char *out = (char *) output_items[0];

	//Copy input to output
	memcpy(out, in, ninput_items[0]*sizeof(char));

	//Add padding
	memset(out+ninput_items[0], 0, d_pad_len);

	// Tell runtime system how many output items we produced.
	return ninput_items[0] + d_pad_len;
}

} /* namespace lora2 */
} /* namespace gr */

