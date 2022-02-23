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

#ifndef INCLUDED_LORA2_LORA_SOFT_DEINTERLEAVER_IMPL_H
#define INCLUDED_LORA2_LORA_SOFT_DEINTERLEAVER_IMPL_H

#include <lora2/lora_soft_deinterleaver.h>

namespace gr {
namespace lora2 {

class lora_soft_deinterleaver_impl : public lora_soft_deinterleaver
{
	private:
		int d_SF;
		int d_CR;

		int d_len_block_in;
		int d_len_block_out;

		void handle_tag_propagation(int in_idx, int out_idx);

	public:
		lora_soft_deinterleaver_impl(int SF, int CR, bool reduced_rate);

		void forecast (int noutput_items, gr_vector_int &ninput_items_required);

		int general_work(int noutput_items,
				gr_vector_int &ninput_items,
				gr_vector_const_void_star &input_items,
				gr_vector_void_star &output_items);

};

} // namespace lora2
} // namespace gr

#endif /* INCLUDED_LORA2_LORA_SOFT_DEINTERLEAVER_IMPL_H */

