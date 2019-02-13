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
              gr::io_signature::make(1, 1, sizeof(uint8_t)), len_tag_key)
    {
		if (CR == 4) {
			d_seed[0] = SEED_CR4_0;
			d_seed[1] = SEED_CR4_1;

			d_poly[0] = POLY_CR4_0;
			d_poly[1] = POLY_CR4_1;
		}
		else {
			d_seed[0] = 0;
			d_seed[1] = 0;

			d_poly[0] = 0;
			d_poly[1] = 0;
		}

		reset();
	}

    int
    lora_whiten_impl::calculate_output_stream_length(const gr_vector_int &ninput_items)
    {
      return ninput_items[0];
    }

	uint8_t
	lora_whiten_impl::shift()
	{
		uint8_t new_in = 0, new_out = 0, tmp=0;
		uint64_t xor_ = 0;

		//Compute new output and input
		new_out = d_state[1]&0x01;

		xor_ = d_state[0]&d_poly[0];
		while (xor_ != 0) {
			new_in ^= (xor_&0x01);
			xor_ >>= 1;
		}
		xor_ = d_state[1]&d_poly[1];
		while (xor_ != 0) {
			new_in ^= (xor_&0x01);
			xor_ >>= 1;
		}

		//Shift register
		tmp = d_state[0]&0x01;
		d_state[0] >>= 1;
		d_state[1] >>= 1;
		d_state[1] |= ((uint64_t)tmp<<63);

		//Append new input to the register
		d_state[0] |= ((uint64_t)new_in<<63);

		return new_out;
	}

	void
	lora_whiten_impl::reset()
	{
		d_state[0] = d_seed[0];
		d_state[1] = d_seed[1];
	}

    int
    lora_whiten_impl::work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      const uint8_t *in = (const uint8_t *) input_items[0];
      uint8_t *out = (uint8_t *) output_items[0];

	  //Reset LFSR
	  reset();

	  for (int i=0 ; i < ninput_items[0] ; ++i) {
		  //Cor incoming bits with LFSR output
		  out[i] = in[i] ^ shift();
	  }

      // Tell runtime system how many output items we produced.
      return ninput_items[0];
    }

  } /* namespace lora2 */
} /* namespace gr */

