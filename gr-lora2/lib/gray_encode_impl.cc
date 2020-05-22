/* -*- c++ -*- */
/*
 * Copyright 2020 Alexandre Marquet.
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
#include "gray_encode_impl.h"

namespace gr {
  namespace lora2 {

    gray_encode::sptr
    gray_encode::make()
    {
      return gnuradio::get_initial_sptr
        (new gray_encode_impl());
    }


    /*
     * The private constructor
     */
    gray_encode_impl::gray_encode_impl()
    : gr::sync_block("gray_encode",
        gr::io_signature::make(1, 1, sizeof(uint16_t)),
        gr::io_signature::make(1, 1, sizeof(uint16_t)))
    {
    }

    int
    gray_encode_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
      const uint16_t *in = (const uint16_t*) input_items[0];
      uint16_t *out = (uint16_t*) output_items[0];

      for(int i=0 ; i < noutput_items ; ++i) {
        out[i] = in[i] ^ (in[i]>>1);
      }

      // Tell runtime system how many output items we produced.
      return noutput_items;
    }

  } /* namespace lora2 */
} /* namespace gr */

