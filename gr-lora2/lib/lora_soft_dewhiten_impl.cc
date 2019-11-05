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
#include "lora_soft_dewhiten_impl.h"

namespace gr {
  namespace lora2 {
    lora_soft_dewhiten::sptr
    lora_soft_dewhiten::make(uint8_t CR, const std::string &len_tag_key)
    {
      return gnuradio::get_initial_sptr
        (new lora_soft_dewhiten_impl(CR, len_tag_key));
    }

    /*
     * The private constructor
     */
    lora_soft_dewhiten_impl::lora_soft_dewhiten_impl(uint8_t CR, const std::string &len_tag_key)
      : gr::tagged_stream_block("lora_soft_dewhiten",
              gr::io_signature::make(1, 1, sizeof(float)),
              gr::io_signature::make(1, 1, sizeof(float)), len_tag_key),
        d_CR(CR), d_seed1((1 == CR)?0x4048C0C0C4C4CCCC:0x724AE1F0F7F4FEFF),
		d_seed2((1 == CR)?0x2C426AC0C2C4C6CC:0X1D734BF0F1F7F4FF)
    {
	}

    int
    lora_soft_dewhiten_impl::calculate_output_stream_length(const gr_vector_int &ninput_items)
    {
      return ninput_items[0];
    }

	void
	lora_soft_dewhiten_impl::soft_lfsr(const float *in, float *out, const size_t bufferSize, const int bitOfs)
	{
		uint64_t r[2] = {d_seed1, d_seed2};

		int i,j;
		for (i = 0 ; i < bitOfs ; i++){
			r[i & 1] = (r[i & 1] >> 1) | (((r[i & 1] >> 32) ^ (r[i & 1] >> 24) ^ (r[i & 1] >> 16) ^ r[i & 1]) << 63);   // poly: 0x1D
		}
		for (j = 0 ; j < bufferSize ; j++,i++) {
			out[j] = (r[i & 1]&0x01)?-in[j]:in[j];
			r[i & 1] = (r[i & 1] >> 1) | (((r[i & 1] >> 32) ^ (r[i & 1] >> 24) ^ (r[i & 1] >> 16) ^ r[i & 1]) << 63);
		}
	}


    int
    lora_soft_dewhiten_impl::work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      const float *in = (const float *) input_items[0];
      float *out = (float *) output_items[0];

	  //Dewhiten
      soft_lfsr(in, out, noutput_items, 0);

      // Tell runtime system how many output items we produced.
      return ninput_items[0];
    }

  } /* namespace lora2 */
} /* namespace gr */

