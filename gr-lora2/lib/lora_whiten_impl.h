/* -*- c++ -*- */
/*
 * Copyright 2019 Alexandre Marquet..
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

#ifndef INCLUDED_LORA2_LORA_WHITEN_IMPL_H
#define INCLUDED_LORA2_LORA_WHITEN_IMPL_H

#include <lora2/lora_whiten.h>

#define POLY_CR4_0 0x0000000000000001
#define POLY_CR4_1 0x0001000100000001
#define SEED_CR4_0 0x00D217A63A4E748B
#define SEED_CR4_1 0xFF00FF17FF3AFF74

namespace gr {
  namespace lora2 {

    class lora_whiten_impl : public lora_whiten
    {
     private:
		 uint64_t d_state[2], d_poly[2], d_seed[2];

     protected:
      int calculate_output_stream_length(const gr_vector_int &ninput_items);
	  uint8_t shift();
	  void reset();

     public:
      lora_whiten_impl(uint8_t CR, const std::string &len_tag_key);

      // Where all the action really happens
      int work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);
    };

  } // namespace lora2
} // namespace gr

#endif /* INCLUDED_LORA2_LORA_WHITEN_IMPL_H */
