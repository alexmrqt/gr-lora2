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
#include "lora_soft_merge_rem_impl.h"

namespace gr {
  namespace lora2 {

    lora_soft_merge_rem::sptr
    lora_soft_merge_rem::make(int SF, const std::string &len_tag_key)
    {
      return gnuradio::get_initial_sptr
        (new lora_soft_merge_rem_impl(SF, len_tag_key));
    }


    /*
     * The private constructor
     */
    lora_soft_merge_rem_impl::lora_soft_merge_rem_impl(int SF, const std::string &len_tag_key)
      : gr::tagged_stream_block("lora_soft_merge_rem",
              gr::io_signature::make(1, 1, sizeof(float)),
              gr::io_signature::make(1, 1, sizeof(float)), len_tag_key),
		d_SF(SF)
    {
		//Number of payload bits remaining in header
        d_rem_key = pmt::intern("rem_bits");

		//Set tag propagation to custom
		set_tag_propagation_policy(TPP_CUSTOM);
	}

    int
    lora_soft_merge_rem_impl::calculate_output_stream_length(const gr_vector_int &ninput_items)
    {
		//Allocate for worst case (CR+4 == 8)
		return ninput_items[0] + (d_SF-7)*8;
    }

    int
    lora_soft_merge_rem_impl::work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      const float *in = (const float *) input_items[0];
      float *out = (float *) output_items[0];
	  std::vector<float> rem_bits;

      // Recover tags (expected to be on the first item)
      std::vector<tag_t> tags;
      get_tags_in_window(tags, 0, 0, 1, d_rem_key);

      // If no tag containing the remainder is present, just copy input to
      // output.
      if (tags.size() == 0) {
        memcpy(out, in, ninput_items[0]);

        return ninput_items[0];
      }

      //Copy payload bits remaining in header at the begining of the payload
	  rem_bits = pmt::f32vector_elements(tags[0].value);
      memcpy(out, &rem_bits[0], rem_bits.size()*sizeof(float));

      //Copy the rest of the payload
      memcpy(out+rem_bits.size(), in, ninput_items[0]*sizeof(float));

      //Handle tag propagation (taken from gr-digital's crc_32_bb)
      tags.clear();
      get_tags_in_range(tags, 0, nitems_read(0), nitems_read(0) + ninput_items[0]);

      for (size_t i = 0; i < tags.size(); i++) {
		//Compute relative index
        tags[i].offset -= nitems_read(0);

        add_item_tag(0, nitems_written(0) + tags[i].offset,
                     tags[i].key,
                     tags[i].value);
      }

      // Tell runtime system how many output items we produced.
      return ninput_items[0] + rem_bits.size();
    }

  } /* namespace lora2 */
} /* namespace gr */
