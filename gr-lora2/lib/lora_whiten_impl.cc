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
#include "lora_whiten_impl.h"

namespace gr {
  namespace lora2 {

    lora_whiten::sptr
    lora_whiten::make(const std::string &len_tag_key)
    {
      return gnuradio::get_initial_sptr
        (new lora_whiten_impl(len_tag_key));
    }

    /*
     * The private constructor
     */
    lora_whiten_impl::lora_whiten_impl(const std::string &len_tag_key)
      : gr::tagged_stream_block("lora_whiten",
          gr::io_signature::make(1, 1, sizeof(uint8_t)),
          gr::io_signature::make(1, 1, sizeof(uint8_t)), len_tag_key),
      d_seed(0x1a3478f0f1f3f7ff)
    {
      d_has_crc_key = pmt::intern("has_crc");
    }

    int
    lora_whiten_impl::calculate_output_stream_length(const gr_vector_int &ninput_items)
    {
      return ninput_items[0];
    }

    int
    lora_whiten_impl::work (int noutput_items,
        gr_vector_int &ninput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
      const uint8_t *in = (const uint8_t *) input_items[0];
      uint8_t *out = (uint8_t *) output_items[0];
      uint64_t r = d_seed; //Shift register
      bool has_crc = false; //CRC should not be whitened.

      // Recover tags (expected to be on the first item)
      std::vector<tag_t> tags;
      get_tags_in_window(tags, 0, 0, 1, d_has_crc_key);

      if (tags.size() > 0) {
        has_crc = pmt::to_bool(tags[0].value);
      }

      //Whitening
      for (size_t i = 0 ; i < (ninput_items[0] - 16*has_crc) ; ++i) {
        out[i] = in[i]^(r&0x01);
        r = (r >> 1) | (((r >> 32) ^ (r >> 24) ^ (r >> 16) ^ r) << 63);
      }
      for (size_t i = ninput_items[0] - 16*has_crc ; i < ninput_items[0] ; ++i) {
        out[i] = in[i];
      }

      // Tell runtime system how many output items we produced.
      return ninput_items[0];
    }

  } /* namespace lora2 */
} /* namespace gr */
