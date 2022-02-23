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
#include "lora_hamming_encode_impl.h"

namespace gr {
namespace lora2 {

lora_hamming_encode::sptr lora_hamming_encode::make(int CR, const std::string &len_tag_key)
{
	return gnuradio::get_initial_sptr
		(new lora_hamming_encode_impl(CR, len_tag_key));
}

lora_hamming_encode_impl::lora_hamming_encode_impl(int CR, const std::string &len_tag_key)
	: gr::block("lora_hamming_encode",
			gr::io_signature::make(1, 1, sizeof(unsigned char)),
			gr::io_signature::make(1, 1, sizeof(unsigned char))),
	d_CR(CR), d_cw_len(CR+4), d_len_tag_key(pmt::intern(len_tag_key))
{
	set_output_multiple(d_cw_len);
	set_tag_propagation_policy(TPP_CUSTOM);
}

void lora_hamming_encode_impl::encode_one_block(const unsigned char *in_block,
		unsigned char *out_block)
{
	switch(d_CR) {
		case 4:
			out_block[0] = in_block[0] ^ in_block[1] ^ in_block[3];
			out_block[1] = in_block[0] ^ in_block[2] ^ in_block[3];
			out_block[2] = in_block[0] ^ in_block[1] ^ in_block[2];
			out_block[3] = in_block[1] ^ in_block[2] ^ in_block[3];

			break;
		case 3:
			out_block[0] = in_block[0] ^ in_block[1] ^ in_block[3];
			out_block[1] = in_block[0] ^ in_block[1] ^ in_block[2];
			out_block[2] = in_block[1] ^ in_block[2] ^ in_block[3];

			break;
		case 2:
			out_block[0] = in_block[0] ^ in_block[1] ^ in_block[2];
			out_block[1] = in_block[1] ^ in_block[2] ^ in_block[3];

			break;
		case 1:
			out_block[0] = in_block[0] ^ in_block[1] ^ in_block[2] ^ in_block[3];
			break;
	}

	// Systematic part
	memcpy(out_block + d_CR, in_block, 4*sizeof(unsigned char));
}

void lora_hamming_encode_impl::handle_tag_propagation(int in_idx, int out_idx)
{
	//All tags in input block are moved to the beginning of the output block
	//Length is updated
	uint64_t out_tag_offset = out_idx + nitems_written(0);
	long new_len = 0;
	std::vector<tag_t> tags;

	//Retrieve tags in input block
	get_tags_in_window(tags, 0, in_idx, in_idx+4);

	//For each tag
	for (std::vector<tag_t>::iterator \
			tag=tags.begin() ; tag != tags.end() ; ++tag) {

		//Length tag get updated
		if(pmt::equal(tag->key, d_len_tag_key)) {
			new_len = (long)(pmt::to_long(tag->value) * d_cw_len / 4.0);
			add_item_tag(0, out_tag_offset, tag->key, pmt::from_long(new_len));
		}
		//Other tags are simply put copied to out_idx
		else {
			add_item_tag(0, out_tag_offset, tag->key, tag->value);
		}
	}
}

void lora_hamming_encode_impl::forecast (int noutput_items,
		gr_vector_int &ninput_items_required)
{
	ninput_items_required[0] = (noutput_items / d_cw_len)*4;
}

int lora_hamming_encode_impl::general_work (int noutput_items,
		gr_vector_int &ninput_items,
		gr_vector_const_void_star &input_items,
		gr_vector_void_star &output_items)
{
	const unsigned char *in = (const unsigned char *) input_items[0];
	unsigned char *out = (unsigned char *) output_items[0];

	// Number of blocks to be processed
	int n_blocks = std::min(ninput_items[0]/4, noutput_items/d_cw_len);

	for (int i=0 ; i < n_blocks ; ++i) {
		// Encode
		encode_one_block(in, out);

		// Propagate tags
		handle_tag_propagation(i*4, i*d_cw_len);

		// Set pointers to next block
		in += 4;
		out += d_cw_len;
	}

	consume_each(n_blocks * 4);
	return n_blocks * d_cw_len;
}

} /* namespace lora2 */
} /* namespace gr */

