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

#ifndef INCLUDED_LORA2_CSS_LLR_CONVERTER_IMPL_H
#define INCLUDED_LORA2_CSS_LLR_CONVERTER_IMPL_H

#include <cmath>
#include <limits>
#include <lora2/css_llr_converter.h>

namespace gr {
namespace lora2 {

class css_llr_converter_impl : public css_llr_converter
{
	private:
		int d_M;
		int d_SF;
		bool d_true_llr;
		float d_sigma_n2;

		float max_star(float A, float B);

		void compute_block_true_llr(const float* in_block, float* out_block);
		void compute_block_llr(const float* in_block, float* out_block);

	public:
		css_llr_converter_impl(int M, bool true_llr, float sigma_n);

		// Where all the action really happens
		int work(int noutput_items,
				gr_vector_const_void_star &input_items,
				gr_vector_void_star &output_items);
};

} // namespace lora2
} // namespace gr

#endif /* INCLUDED_LORA2_CSS_LLR_CONVERTER_IMPL_H */

