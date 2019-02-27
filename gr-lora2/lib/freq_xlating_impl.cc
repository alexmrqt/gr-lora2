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
#include "freq_xlating_impl.h"

namespace gr {
  namespace lora2 {

    freq_xlating::sptr
    freq_xlating::make(uint16_t M, float freq, const std::string& freq_tag_key)
    {
      return gnuradio::get_initial_sptr
        (new freq_xlating_impl(M, freq, freq_tag_key));
    }

    /*
     * The private constructor
     */
    freq_xlating_impl::freq_xlating_impl(uint16_t M, float freq, const std::string& freq_tag_key)
      : gr::sync_block("freq_xlating",
              gr::io_signature::make(1, 1, sizeof(uint16_t)),
              gr::io_signature::make(1, 1, sizeof(uint16_t)))
    {
      d_freq_tag_key = pmt::intern(freq_tag_key);

      d_M = M;
      d_freq = freq*d_M;
    }

    int
    freq_xlating_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
      const uint16_t *in = (const uint16_t *) input_items[0];
      uint16_t *out = (uint16_t *) output_items[0];

      //Get tags
      std::vector<tag_t> tags;
      get_tags_in_window(tags, 0, 0, noutput_items, d_freq_tag_key);

      uint64_t start_idx = 0;
      int n_items = 0;
      for(std::vector<tag_t>::iterator tag = tags.begin() ;
		  tag != tags.end() ; ++tag) {

          //Rotate with old frequency up to this point
          n_items = (*tag).offset - nitems_read(0) - start_idx;
		  for (uint64_t i = start_idx ; i < (start_idx+n_items) ; ++i) {
			  out[i] = (in[i] - d_freq)%d_M;
		  }

          //Update start_idx
          start_idx += n_items;

          //Update frequency
		  d_freq = pmt::to_float((*tag).value)*d_M;
      }
      //
      //Rotate remaining items
	  for (uint64_t i = start_idx ; i < noutput_items ; ++i) {
		  out[i] = (in[i] - d_freq)%d_M;
	  }

      // Tell runtime system how many output items we produced.
      return noutput_items;
    }

  } /* namespace lora2 */
} /* namespace gr */

