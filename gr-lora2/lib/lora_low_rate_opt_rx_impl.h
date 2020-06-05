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

#ifndef INCLUDED_LORA2_LORA_LOW_RATE_OPT_RX_IMPL_H
#define INCLUDED_LORA2_LORA_LOW_RATE_OPT_RX_IMPL_H

#include <lora2/lora_low_rate_opt_rx.h>

namespace gr {
  namespace lora2 {

    class lora_low_rate_opt_rx_impl : public lora_low_rate_opt_rx
    {
      public:
        lora_low_rate_opt_rx_impl();

        // Where all the action really happens
        int work(
            int noutput_items,
            gr_vector_const_void_star &input_items,
            gr_vector_void_star &output_items
            );
    };

  } // namespace lora2
} // namespace gr

#endif /* INCLUDED_LORA2_LORA_LOW_RATE_OPT_RX_IMPL_H */

