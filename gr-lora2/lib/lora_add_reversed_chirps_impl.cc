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
#include "lora_add_reversed_chirps_impl.h"

namespace gr {
namespace lora2 {

lora_add_reversed_chirps::sptr lora_add_reversed_chirps::make(int SF, int interp,
		const std::string &len_tag_key,
		const std::string &payload_tag_key,
		const std::string &rev_chirp_tag_key)
{
	return gnuradio::get_initial_sptr
		(new lora_add_reversed_chirps_impl(SF, interp,
										   len_tag_key,
										   payload_tag_key,
										   rev_chirp_tag_key));
}


lora_add_reversed_chirps_impl::lora_add_reversed_chirps_impl(int SF, int interp,
		const std::string &len_tag_key,
		const std::string &payload_tag_key,
		const std::string &rev_chirp_tag_key)
	: gr::block("lora_add_reversed_chirps",
			gr::io_signature::make(1, 1, sizeof(gr_complex)),
			gr::io_signature::make(1, 1, sizeof(gr_complex))),
	d_M((int)std::pow(2.0, SF)), d_interp(interp), d_copied_prev_pass(0),
	d_len_tag_key(pmt::intern(len_tag_key)),
	d_payload_tag_key(pmt::intern(payload_tag_key)), 
	d_rev_chirps_tag_key(pmt::intern(rev_chirp_tag_key))
{
	// Symbols to be modulated
	const unsigned short syms[] = {0, 0, 0};
	// Create a downchirp modulator
	css_mod_algo modulator = css_mod_algo(d_M, d_interp, false);

	// Initialize d_rev_chirps to fit 3 downchirps
	d_rev_chirps.resize(3*d_M*d_interp);

	// Generate 3 downchirps
	modulator.modulate(syms, &d_rev_chirps[0], 3);

	// Shrink d_rev_chirps to make the lora downchirp synchronization pattern
	d_rev_chirps.resize((2*d_M + d_M/4 - 1)*d_interp);

	// Custom tag propagation
	set_tag_propagation_policy(TPP_DONT);
}

void lora_add_reversed_chirps_impl::forecast (int noutput_items,
		gr_vector_int &ninput_items_required)
{
	// When no chirps is to be appened, this block is a sync block
	ninput_items_required[0] = noutput_items;
}

void lora_add_reversed_chirps_impl::handle_tag_propagation(size_t length)
{
	long tag_value = 0;
	uint64_t tag_offset = 0;
	std::vector<tag_t> tags_orig;

	get_tags_in_window(tags_orig, 0, 0, length);
	for (std::vector<tag_t>::iterator tag=tags_orig.begin() ;
			tag != tags_orig.end() ; ++tag) {

		// Update tag position
		tag_offset = tag->offset + nitems_written(0) - nitems_read(0);

		// If needed, update length tag
		if (pmt::equal(tag->key, d_len_tag_key)) {
			tag_value = pmt::to_long(tag->value);
			tag_value += d_rev_chirps.size();
			add_item_tag(0, tag_offset, tag->key, pmt::from_long(tag_value));
		}
		else {
			add_item_tag(0, tag_offset, tag->key, tag->value);
		}
	}
}

int lora_add_reversed_chirps_impl::append_downchirps(const gr_complex* input_items,
		gr_complex* output_items, int ninput_items, int noutput_items)
{
	int nitems = std::min(d_rev_chirps.size() + 1 - d_copied_prev_pass,
			(size_t)noutput_items);

	// Add a tag to denote begining of reversed chirps sequence
	if (d_copied_prev_pass == 0) {
		add_item_tag(0, nitems_written(0), d_rev_chirps_tag_key, pmt::PMT_NIL);
	}

	// If there is enough room for everything
	if (noutput_items >= (d_rev_chirps.size() + 1 - d_copied_prev_pass)) {
		// Add downchirps
		if (nitems-1 > 0) {
			memcpy(output_items, &d_rev_chirps[d_copied_prev_pass],
					(nitems-1) * sizeof(gr_complex));
		}

		// Copy and handle tag propagation for first payload item
		output_items[nitems-1] = input_items[0];
		//handle_tag_propagation(1);
		// Add payload tag on first payload item
		add_item_tag(0,
				nitems_written(0) + d_rev_chirps.size() - d_copied_prev_pass,
				d_payload_tag_key, pmt::PMT_NIL);

		// The whole downchirp pattern has been added
		// And the first payload item has been processed
		d_copied_prev_pass = 0;
		consume(0, 1);
	}
	// If there is not
	else {
		// Add of chunk of the downchirp pattern
		memcpy(output_items, &d_rev_chirps[d_copied_prev_pass],
				nitems * sizeof(gr_complex));

		// noutput_items more items have been added
		// No item has been processed
		d_copied_prev_pass += noutput_items;
		consume(0, 0);
	}

	return nitems;
}

int lora_add_reversed_chirps_impl::general_work (int noutput_items,
		gr_vector_int &ninput_items,
		gr_vector_const_void_star &input_items,
		gr_vector_void_star &output_items)
{
	const gr_complex *in = (const gr_complex *) input_items[0];
	gr_complex *out = (gr_complex *) output_items[0];

	int nitems = 0;
	std::vector<tag_t> tags;

	// A downchirp pattern is being added
	if (d_copied_prev_pass > 0) {
		return append_downchirps(in, out, ninput_items[0], noutput_items);
	}

	// Retrieve tags with payload_tag_key
	get_tags_in_window(tags, 0, 0, ninput_items[0], d_payload_tag_key);

	// If no tags is present, copy input to output and return.
	if (tags.size() == 0) {
		nitems = std::min(ninput_items[0], noutput_items);
		memcpy(out, in, nitems * sizeof(gr_complex));

		// Handle tags associated with this data
		handle_tag_propagation(nitems);

		// nitems items has been consumed and produced
		consume(0, nitems);
		return nitems;
	}
	else {
		// Make sure tag is on the first item
		nitems = tags[0].offset - nitems_read(0);
		if (nitems > 0) {
			nitems = std::min(nitems, noutput_items);
			memcpy(out, in, nitems * sizeof(gr_complex));

			// Handle tags associated with this data
			handle_tag_propagation(nitems);

			// nitems items has been consumed and produced
			consume(0, nitems);
			return nitems;
		}

		// Append reversed chirps and first payload item
		return append_downchirps(in, out, ninput_items[0], noutput_items);
	}
}

} /* namespace lora2 */
} /* namespace gr */

