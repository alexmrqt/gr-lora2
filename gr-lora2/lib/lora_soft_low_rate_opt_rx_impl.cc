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
#include "lora_soft_low_rate_opt_rx_impl.h"

namespace gr {
  namespace lora2 {

    lora_soft_low_rate_opt_rx::sptr
    lora_soft_low_rate_opt_rx::make(int SF)
    {
      return gnuradio::get_initial_sptr
        (new lora_soft_low_rate_opt_rx_impl(SF));
    }


    lora_soft_low_rate_opt_rx_impl::lora_soft_low_rate_opt_rx_impl(int SF)
      : gr::sync_block("lora_soft_low_rate_opt_rx",
          gr::io_signature::make(1, 1, SF*sizeof(float)),
          gr::io_signature::make(1, 1, (SF-2)*sizeof(float))), d_SF(SF)
    {
    }

    int
    lora_soft_low_rate_opt_rx_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
      const float *in = (const float*) input_items[0];
      float *out = (float*) output_items[0];

      for (int i=0 ; i < noutput_items ; ++i) {
        //Copy d_SF-2 elements of input vector to output vector
        memcpy(out, in, (d_SF-2)*sizeof(float));

        in += d_SF;
        out += d_SF-2;
      }

      // Tell runtime system how many output items we produced.
      return noutput_items;
    }

  } /* namespace lora2 */
} /* namespace gr */

