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
#include "lora_soft_deinterleaver_impl.h"

namespace gr {
namespace lora2 {

lora_soft_deinterleaver::sptr lora_soft_deinterleaver::make(int SF, int CR,
		bool reduced_rate)
{
	return gnuradio::get_initial_sptr
		(new lora_soft_deinterleaver_impl(SF, CR, reduced_rate));
}


/*
 * The private constructor
 */
lora_soft_deinterleaver_impl::lora_soft_deinterleaver_impl(int SF, int CR, bool reduced_rate)
	: gr::block("lora_soft_deinterleaver",
			gr::io_signature::make(1, 1, (reduced_rate?SF-2:SF) * sizeof(float)),
			gr::io_signature::make(1, 1, sizeof(float))),
	d_CR(CR),
	d_len_block_in(CR+4)
{
	d_SF = (reduced_rate)?SF-2:SF;
	d_len_block_out = d_SF*(d_CR+4);

	set_output_multiple(d_len_block_out);
	set_tag_propagation_policy(TPP_CUSTOM);
}

void lora_soft_deinterleaver_impl::handle_tag_propagation(int in_idx, int out_idx)
{
	//All tags in input block are moved to the beginning of the output block
	uint64_t out_tag_offset = out_idx + nitems_written(0);
	std::vector<tag_t> tags;

	//Retrieve tags in input block
	get_tags_in_window(tags, 0, in_idx, in_idx+d_len_block_in);

	//For each tag
	for (std::vector<tag_t>::iterator \
			tag=tags.begin() ; tag != tags.end() ; ++tag) {

		add_item_tag(0, out_tag_offset, tag->key, tag->value);
	}
}

void lora_soft_deinterleaver_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
{
	int n_blocks = noutput_items / d_len_block_out;
	ninput_items_required[0] = n_blocks * d_len_block_in;
}

int lora_soft_deinterleaver_impl::general_work (int noutput_items,
		gr_vector_int &ninput_items,
		gr_vector_const_void_star &input_items,
		gr_vector_void_star &output_items)
{
	const float *in = (const float *) input_items[0];
	float *out = (float *) output_items[0];

	int n_blocks = std::min(ninput_items[0]/d_len_block_in,
			noutput_items/d_len_block_out);

	for(int k=0 ; k < n_blocks ; ++k) {
		// Handle tag propagation
		handle_tag_propagation(k*d_len_block_in, k*d_len_block_out);

		// (Un)shuffle
		for(int i=d_SF-1 ; i >= 0 ; --i) {
			for(int j=(d_CR+4)-1 ; j >= 0 ; --j) {
				*(out++) = in[j*d_SF + (i+j)%d_SF];
			}
		}

		// Update input iterator
		in += d_len_block_in*d_SF;
	}

	consume_each(n_blocks * d_len_block_in);
	return noutput_items;
}

} /* namespace lora2 */
} /* namespace gr */

