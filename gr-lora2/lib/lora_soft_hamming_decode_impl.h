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

#ifndef INCLUDED_LORA2_LORA_SOFT_HAMMING_DECODE_IMPL_H
#define INCLUDED_LORA2_LORA_SOFT_HAMMING_DECODE_IMPL_H

#include <pmt/pmt.h>
#include <lora2/lora_soft_hamming_decode.h>

namespace gr {
  namespace lora2 {

    class lora_soft_hamming_decode_impl : public lora_soft_hamming_decode
    {
      private:
        int d_CR;
        int d_cw_len;
        pmt::pmt_t d_len_tag_key;

        // Store codewords corresponding to any possible input.
        // Input blocks are 4 bits long, so there is 16 possibilities, and
        // each codeword contains 5 to 8 bits, depending on CR value.
        // i-th bit of the codeword corresponding to the input j \in [0;15] is
        // given by d_cw_table_CRx[j*(4+x) + i].
        bool d_cw_table_CR4[16*8] = {0};
        bool d_cw_table_CR3[16*7] = {0};
        bool d_cw_table_CR2[16*6] = {0};
        bool d_cw_table_CR1[16*5] = {0};

      public:
        lora_soft_hamming_decode_impl(int CR, const std::string &len_tag_key);

        void encode_one_block(int CR, unsigned char in, bool *out);

        void decode_one_block(const float *in, unsigned char *out);

        void handle_tag_propagation(int in_idx, int out_idx);

        void forecast (int noutput_items, gr_vector_int &ninput_items_required);

        int general_work(int noutput_items,
            gr_vector_int &ninput_items,
            gr_vector_const_void_star &input_items,
            gr_vector_void_star &output_items);

    };

  } // namespace lora2
} // namespace gr

#endif /* INCLUDED_LORA2_LORA_SOFT_HAMMING_DECODE_IMPL_H */

