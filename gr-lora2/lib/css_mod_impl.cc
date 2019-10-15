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
#include "css_mod_impl.h"

namespace gr {
  namespace lora2 {

    css_mod::sptr
    css_mod::make(int M, int interp)
    {
      return gnuradio::get_initial_sptr
        (new css_mod_impl(M, interp));
    }

    /*
     * The private constructor
     */
    css_mod_impl::css_mod_impl(int M, int interp)
      : gr::sync_interpolator("css_mod",
              gr::io_signature::make(1, 1, sizeof(short)),
              gr::io_signature::make(1, 1, sizeof(gr_complex)), M*interp),
	  d_M(M), d_Q(interp)
    {}

    int
    css_mod_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
      const short *in = (const short *) input_items[0];
      gr_complex *out = (gr_complex *) output_items[0];

	  int n_syms = noutput_items / (d_M * d_Q);
	  float out_freq = 0.0;
	  float out_phase = 0.0;

	  for (int i=0 ; i < n_syms ; ++i) {
		  for (int k = 0 ; k < d_M*d_Q ; ++k) {
			  out_freq = k/(2.0*d_Q) - d_M/2.0 + in[i] \
						 - d_M * round((float)k/(d_M*d_Q) - 0.5 + (float)in[i]/d_M);
			  out_phase = 2.0 * M_PI * out_freq / (d_M*d_Q) * k;

			  *(out++) = gr_expj(out_phase);
		  }
	  }

      // Tell runtime system how many output items we produced.
      return noutput_items;
    }

  } /* namespace lora2 */
} /* namespace gr */

