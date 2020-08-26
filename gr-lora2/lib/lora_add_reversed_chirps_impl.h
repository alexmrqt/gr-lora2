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

#ifndef INCLUDED_LORA2_LORA_ADD_REVERSED_CHIRPS_IMPL_H
#define INCLUDED_LORA2_LORA_ADD_REVERSED_CHIRPS_IMPL_H

#include <lora2/lora_add_reversed_chirps.h>
#include <pmt/pmt.h>

#include <lora2/css_mod_algo.h>

namespace gr {
namespace lora2 {

class lora_add_reversed_chirps_impl : public lora_add_reversed_chirps
{
	private:
		int d_M;
		int d_interp;
		size_t d_copied_prev_pass;
		pmt::pmt_t d_len_tag_key;
		pmt::pmt_t d_payload_tag_key;
		pmt::pmt_t d_rev_chirps_tag_key;
		std::vector<gr_complex> d_rev_chirps;


	public:
		lora_add_reversed_chirps_impl(int SF, int interp,
				const std::string &len_tag_key,
				const std::string &payload_tag_key,
				const std::string &rev_chirp_tag_key);

		void forecast (int noutput_items, gr_vector_int &ninput_items_required);

		void handle_tag_propagation(size_t length);

		int append_downchirps(const gr_complex* input_items,
				gr_complex* output_items, int ninput_items, int noutput_items);

		int general_work(int noutput_items,
				gr_vector_int &ninput_items,
				gr_vector_const_void_star &input_items,
				gr_vector_void_star &output_items);

};

} // namespace lora2
} // namespace gr

#endif /* INCLUDED_LORA2_LORA_ADD_REVERSED_CHIRPS_IMPL_H */

