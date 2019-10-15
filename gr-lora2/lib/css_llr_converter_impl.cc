/* -*- c++ -*- */
/* 
 * Copyright 2019 Alexandre Marquet.
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
#include "css_llr_converter_impl.h"

namespace gr {
  namespace lora2 {

    css_llr_converter::sptr
    css_llr_converter::make(int M, bool true_llr, float sigma_b)
    {
      return gnuradio::get_initial_sptr
        (new css_llr_converter_impl(M, true_llr, sigma_b));
    }

    /*
     * The private constructor
     */
    css_llr_converter_impl::css_llr_converter_impl(int M, bool true_llr, float sigma_b)
      : gr::sync_block("css_llr_converter",
              gr::io_signature::make(1, 1, sizeof(float)*M),
              gr::io_signature::make(1, 1, sizeof(float)*(int)log2(M))),
	  d_M(M), d_SF((int)log2(M)), d_true_llr(true_llr), d_sigma_b2(sigma_b*sigma_b)
    {}

	float
	css_llr_converter_impl::max_star(float A, float B)
	{
		if (A > B) {
			return A + logf(1.0 + expf(B-A));
		}
		else {
			return B + logf(1.0 + expf(A-B));
		}
	}

	void
	css_llr_converter_impl::compute_block_true_llr(const float* in_block, float* out_block)
	{
		float p0 = -std::numeric_limits<float>::max();
		float p1 = -std::numeric_limits<float>::max();
		int shift = 0;

		for (int j=0 ; j < d_SF ; ++j) {
			p0 = -std::numeric_limits<float>::max();
			p1 = -std::numeric_limits<float>::max();

			shift = d_SF-1-j;
			for (int i=0 ; i < d_M ; ++i) {
				if ((i>>shift)&0x01) {
					p1 = max_star(p1, in_block[i]/d_sigma_b2);
				}
				else {
					p0 = max_star(p0, in_block[i]/d_sigma_b2);
				}
			}

			out_block[j] = p0 - p1;
		}
	}

	void
	css_llr_converter_impl::compute_block_llr(const float* in_block, float* out_block)
	{
		float p0 = -std::numeric_limits<float>::max();
		float p1 = -std::numeric_limits<float>::max();
		int shift = 0;

		for (int j=0 ; j < d_SF ; ++j) {
			p0 = -std::numeric_limits<float>::max();
			p1 = -std::numeric_limits<float>::max();

			shift = d_SF-1-j;
			for (int i=0 ; i < d_M ; ++i) {
				if ((i>>shift)&0x01) {
					p1 = fmax(p1, in_block[i]);
				}
				else {
					p0 = fmax(p0, in_block[i]);
				}
			}

			out_block[j] = p0 - p1;
		}
	}

    int
    css_llr_converter_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
      const float *in = (const float *) input_items[0];
      float *out = (float *) output_items[0];

	  if (d_true_llr) {
		  for (int i=0 ; i < noutput_items ; ++i) {
			  compute_block_true_llr(in, out);
			  in += d_M;
			  out += d_SF;
		  }
	  }
	  else {
		  for (int i=0 ; i < noutput_items ; ++i) {
			  compute_block_llr(in, out);
			  in += d_M;
			  out += d_SF;
		  }
	  }

      // Tell runtime system how many output items we produced.
      return noutput_items;
    }

  } /* namespace lora2 */
} /* namespace gr */

