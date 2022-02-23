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
#include "lora_add_preamble_impl.h"

namespace gr {
namespace lora2 {

lora_add_preamble::sptr lora_add_preamble::make(int pre_len, int sync_word,
		const std::string &len_tag_key, const std::string &sync_word_tag_key,
		const std::string &payload_tag_key)
{
	return gnuradio::get_initial_sptr
		(new lora_add_preamble_impl(pre_len, sync_word, len_tag_key,
									sync_word_tag_key, payload_tag_key));
}

/*
 * The private constructor
 */
lora_add_preamble_impl::lora_add_preamble_impl(int pre_len, int sync_word,
		const std::string &len_tag_key,
		const std::string &sync_word_tag_key,
		const std::string &payload_tag_key)
	: gr::tagged_stream_block("lora_add_preamble",
			gr::io_signature::make(1, 1, sizeof(short)),
			gr::io_signature::make(1, 1, sizeof(short)), len_tag_key),
	d_pre_len(pre_len)
{
	d_sync_word_tag_key = pmt::intern(sync_word_tag_key);
	d_payload_tag_key = pmt::intern(payload_tag_key);

	d_sync_word[0] = ((sync_word>>4)&0xF)*8;
	d_sync_word[1] = (sync_word&0xF)*8;
}

int lora_add_preamble_impl::calculate_output_stream_length(const gr_vector_int &ninput_items)
{
	//This blocks add pre_len symbols, plus two symbols for the sync word
	int noutput_items = ninput_items[0] + d_pre_len + d_n_sync_syms;
	return noutput_items ;
}

int lora_add_preamble_impl::work (int noutput_items,
		gr_vector_int &ninput_items,
		gr_vector_const_void_star &input_items,
		gr_vector_void_star &output_items)
{
	const short* in = (const short *) input_items[0];
	short* out = (short *) output_items[0];

	//Add preamble
	for (int i=0 ; i < d_pre_len ; ++i) {
		*out = 0;
		++out;
	}

	//Add sync_word
	*out = d_sync_word[0];
	++out;
	*out = d_sync_word[1];
	++out;

	//Add payload
	memcpy((void*)out, (void*)in, sizeof(short)*ninput_items[0]);

	//Add tag to the sync word
	add_item_tag(0, nitems_written(0) + d_pre_len,
			d_sync_word_tag_key, pmt::PMT_NIL);
	//Add tag to the first item of the payload
	add_item_tag(0, nitems_written(0) + d_pre_len + d_n_sync_syms,
			d_payload_tag_key, pmt::PMT_NIL);

	// Tell runtime system how many output items we produced.
	return ninput_items[0] + d_pre_len + 2;
}

} /* namespace lora2 */
} /* namespace gr */

