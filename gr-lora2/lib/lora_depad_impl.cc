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
#include "lora_depad_impl.h"

namespace gr {
  namespace lora2 {

    lora_depad::sptr
    lora_depad::make(const std::string &len_tag_key, const uint8_t n_pad)
    {
      return gnuradio::get_initial_sptr
        (new lora_depad_impl(len_tag_key, n_pad));
    }

    /*
     * The private constructor
     */
    lora_depad_impl::lora_depad_impl(const std::string &len_tag_key,
			const uint8_t n_pad)
      : gr::tagged_stream_block("lora_depad",
              gr::io_signature::make(1, 1, sizeof(uint8_t)),
              gr::io_signature::make(1, 1, sizeof(uint8_t)), len_tag_key),
      d_n_pad(n_pad)
    {
		//Populate attributes
        d_n_pad_key = pmt::intern("pad_len");

		//Set tag propagation to custom
		set_tag_propagation_policy(TPP_CUSTOM);
	}

    int
    lora_depad_impl::calculate_output_stream_length(const gr_vector_int &ninput_items)
    {
      //Let's allocate the maximum output buffer, in case the padding is zero.
      int noutput_items = ninput_items[0];
      return noutput_items;
    }
    
    void
    lora_depad_impl::update_length_tags(int n_produced, int n_ports)
    {
        //Do not update len_tag_key
        return;
    }

    int
    lora_depad_impl::work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      const uint8_t *in = (const uint8_t *) input_items[0];
      uint8_t *out = (uint8_t *) output_items[0];
      uint8_t n_pad = d_n_pad;

      //Override padding from tag value, if any.
      //Tag is expected to be on the first item.
      std::vector<tag_t> tags;
      get_tags_in_window(tags, 0, 0, 1, d_n_pad_key);
      if (tags.size() > 0) {
          n_pad = (uint8_t)pmt::to_long(tags[0].value);
      }

      //Update noutput_items to take padding into account
      noutput_items = ninput_items[0] - n_pad;

      //Copy noutput_items for input to output
      memcpy(out, in, noutput_items);

      //Handle tag propagation (taken from gr-digital's crc_32_bb)
      tags.clear();
      get_tags_in_range(tags, 0, nitems_read(0), nitems_read(0) + noutput_items);

      for (size_t i = 0; i < tags.size(); i++) {
		//Compute relative index
        tags[i].offset -= nitems_read(0);

		//Shift tags assigned to dropped items to the last output item
        if (tags[i].offset >= (unsigned int)noutput_items) {
          tags[i].offset = noutput_items - 1;
        }
        add_item_tag(0, nitems_written(0) + tags[i].offset,
                     tags[i].key,
                     tags[i].value);
      }

      // Tell runtime system how many output items we produced.
      return noutput_items;
    }

  } /* namespace lora2 */
} /* namespace gr */

