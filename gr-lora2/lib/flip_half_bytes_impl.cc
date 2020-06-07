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
#include "flip_half_bytes_impl.h"

namespace gr {
  namespace lora2 {

    flip_half_bytes::sptr
    flip_half_bytes::make()
    {
      return gnuradio::get_initial_sptr
        (new flip_half_bytes_impl());
    }


    /*
     * The private constructor
     */
    flip_half_bytes_impl::flip_half_bytes_impl()
      : gr::sync_block("flip_half_bytes",
          gr::io_signature::make(1, 1, sizeof(char)),
          gr::io_signature::make(1, 1, sizeof(char)))
    {
    }

    int
    flip_half_bytes_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
      const unsigned char *in = (const unsigned char *) input_items[0];
      unsigned char *out = (unsigned char *) output_items[0];


      for (int i=0 ; i < noutput_items ; ++i) {
        out[i] = ((in[i] << 4) | (in[i] >> 4))&0xFF;
      }

      // Tell runtime system how many output items we produced.
      return noutput_items;
    }

  } /* namespace lora2 */
} /* namespace gr */

