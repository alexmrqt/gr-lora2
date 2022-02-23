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
#include "lora_drop_rem_impl.h"

namespace gr {
namespace lora2 {

lora_drop_rem::sptr lora_drop_rem::make(unsigned char SF, const std::string &len_tag_key)
{
	return gnuradio::get_initial_sptr
		(new lora_drop_rem_impl(SF, len_tag_key));
}


/*
 * The private constructor
 */
lora_drop_rem_impl::lora_drop_rem_impl(unsigned char SF, const std::string &len_tag_key)
	: gr::tagged_stream_block("lora_drop_rem",
			gr::io_signature::make(1, 1, sizeof(char)),
			gr::io_signature::make(1, 1, sizeof(char)), len_tag_key),
	d_nitems_drop((SF-2)*4 - 20)
{
}

int lora_drop_rem_impl::calculate_output_stream_length(const gr_vector_int &ninput_items)
{
	int noutput_items = ninput_items[0] - d_nitems_drop;

	return noutput_items ;
}

int lora_drop_rem_impl::work (int noutput_items,
		gr_vector_int &ninput_items,
		gr_vector_const_void_star &input_items,
		gr_vector_void_star &output_items)
{
	const char *in = (const char *) input_items[0];
	char *out = (char *) output_items[0];

	memcpy(out, in+d_nitems_drop, noutput_items);

	// Tell runtime system how many output items we produced.
	return ninput_items[0] - d_nitems_drop;
}

} /* namespace lora2 */
} /* namespace gr */

