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

#ifndef INCLUDED_LORA2_LORA_MERGE_REM_IMPL_H
#define INCLUDED_LORA2_LORA_MERGE_REM_IMPL_H

#include <pmt/pmt.h>
#include <lora2/lora_merge_rem.h>

namespace gr {
namespace lora2 {

class lora_merge_rem_impl : public lora_merge_rem
{
	private:
		int d_SF;
		size_t d_rem_len;
		pmt::pmt_t d_rem_key;

	protected:
		int calculate_output_stream_length(const gr_vector_int &ninput_items);

		void handle_tag_propagation(int ninput_items);

	public:
		lora_merge_rem_impl(int SF, const std::string &len_tag_key);

		// Where all the action really happens
		int work(int noutput_items,
				gr_vector_int &ninput_items,
				gr_vector_const_void_star &input_items,
				gr_vector_void_star &output_items);
};

} // namespace lora2
} // namespace gr

#endif /* INCLUDED_LORA2_LORA_MERGE_REM_IMPL_H */

