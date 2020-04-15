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
    lora_whiten::make(uint8_t CR, const std::string &len_tag_key)
    {
      return gnuradio::get_initial_sptr
        (new lora_whiten_impl(CR, len_tag_key));
    }

    /*
     * The private constructor
     */
    lora_whiten_impl::lora_whiten_impl(uint8_t CR, const std::string &len_tag_key)
      : gr::tagged_stream_block("lora_whiten",
          gr::io_signature::make(1, 1, sizeof(uint8_t)),
          gr::io_signature::make(1, 1, sizeof(uint8_t)), len_tag_key),
      d_CR(CR), d_seed(0x8e0d1a3478f0f1f3), d_n_skip(8)
    {
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

      //For some reason, the 8 first bits of the packet should be ignored...
      memcpy(out, &in[0], d_n_skip);

      //Whitening
      for (size_t i = d_n_skip ; i < (ninput_items[0]-d_n_skip) ; ++i) {
        out[i] = in[i]^(r&0x01);
        r = (r >> 1) | (((r >> 32) ^ (r >> 24) ^ (r >> 16) ^ r) << 63);
      }

      // Tell runtime system how many output items we produced.
      return ninput_items[0];
    }

  } /* namespace lora2 */
} /* namespace gr */
