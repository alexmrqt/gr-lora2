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
#include <lora2/css_mod_algo.h>

namespace gr {
  namespace lora2 {

    css_mod_algo::css_mod_algo(int M, int interp, bool upchirp)
      : d_M(M), d_Q(interp), d_upchirp(upchirp)
    {
    }

    void
    css_mod_algo::modulate(const short *in, gr_complex *out, size_t n_syms)
    {
      float out_freq = 0.0;
      float out_phase = 0.0;

      for (int i=0 ; i < n_syms ; ++i) {
        for (int k = 0 ; k < d_M*d_Q ; ++k) {
          if (d_upchirp) {
            out_freq = k/(2.0*d_Q) - d_M/2.0 + in[i] \
                       - d_M * round((float)k/(d_M*d_Q) - 0.5 + (float)in[i]/d_M);
          }
          else {
            out_freq = -k/(2.0*d_Q) - d_M/2.0 + in[i] \
                       - d_M * round((float)-k/(d_M*d_Q) - 0.5 + (float)in[i]/d_M);
          }
          out_phase = 2.0 * M_PI * out_freq / (d_M*d_Q) * k;

          *(out++) = gr_expj(out_phase);
        }
      }
    }

  } /* namespace lora2 */
} /* namespace gr */

