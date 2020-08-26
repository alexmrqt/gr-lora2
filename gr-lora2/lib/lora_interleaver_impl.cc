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
#include "lora_interleaver_impl.h"

namespace gr {
namespace lora2 {

lora_interleaver::sptr lora_interleaver::make(int SF, int CR, const std::string &len_tag_key,
		bool reduced_rate)
{
	return gnuradio::get_initial_sptr
		(new lora_interleaver_impl(SF, CR, len_tag_key, reduced_rate));
}


/*
 * The private constructor
 */
lora_interleaver_impl::lora_interleaver_impl(int SF, int CR,
		const std::string &len_tag_key, bool reduced_rate)
	: gr::block("lora_interleaver",
			gr::io_signature::make(1, 1, sizeof(unsigned char)),
			gr::io_signature::make(1, 1, sizeof(unsigned short))),
	d_CR(CR),
	d_len_tag_key(pmt::intern(len_tag_key)),
	d_len_block_out(CR+4)
{
	d_SF = (reduced_rate)?SF-2:SF;
	d_len_block_in = d_SF*(d_CR+4);

	set_output_multiple(d_len_block_out);
	set_tag_propagation_policy(TPP_CUSTOM);
}

void lora_interleaver_impl::handle_tag_propagation(int in_idx, int out_idx)
{
	//All tags in input block are moved to the beginning of the output block
	//Length is updated
	uint64_t out_tag_offset = out_idx + nitems_written(0);
	long new_len = 0;
	std::vector<tag_t> tags;

	//Retrieve tags in input block
	get_tags_in_window(tags, 0, in_idx, in_idx+d_len_block_in);

	//For each tag
	for (std::vector<tag_t>::iterator \
			tag=tags.begin() ; tag != tags.end() ; ++tag) {

		//Length tag get updated
		if(pmt::equal(tag->key, d_len_tag_key)) {
			new_len = pmt::to_long(tag->value) / d_SF;
			add_item_tag(0, out_tag_offset, tag->key, pmt::from_long(new_len));
		}
		//Other tags are simply put copied to out_idx
		else {
			add_item_tag(0, out_tag_offset, tag->key, tag->value);
		}
	}
}

void lora_interleaver_impl::forecast (int noutput_items,
		gr_vector_int &ninput_items_required)
{
	int n_blocks = noutput_items / d_len_block_out;
	ninput_items_required[0] = n_blocks * d_len_block_in;
}

int lora_interleaver_impl::general_work (int noutput_items,
		gr_vector_int &ninput_items,
		gr_vector_const_void_star &input_items,
		gr_vector_void_star &output_items)
{
	const unsigned char *in = (const unsigned char*) input_items[0];
	unsigned short *out = (unsigned short *) output_items[0];

	int idx=0;
	int n_blocks = std::min(ninput_items[0]/d_len_block_in,
			noutput_items/d_len_block_out);

	for(int k=0 ; k < n_blocks ; ++k) {
		// Handle tag propagation
		handle_tag_propagation(k*d_len_block_in, k*d_len_block_out);

		// Shuffle
		for (int i = 0 ; i < d_CR+4 ; ++i) {
			out[i] = 0; // Initialize out[i]

			for (int j = 0 ; j < d_SF ; ++j) {
				idx = (d_SF-1 - ((j - i) % d_SF + d_SF)%d_SF) * (d_CR+4) + d_CR+4-1 - i;
				out[i] |= (in[idx])<<(d_SF-j-1);
			}
		}

		// Update iterators
		in += d_len_block_in;
		out += d_len_block_out;
	}

	consume_each(n_blocks * d_len_block_in);
	return noutput_items;
}

} /* namespace lora2 */
} /* namespace gr */

