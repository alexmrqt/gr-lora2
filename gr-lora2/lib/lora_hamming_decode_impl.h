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

#ifndef INCLUDED_LORA2_LORA_HAMMING_DECODE_IMPL_H
#define INCLUDED_LORA2_LORA_HAMMING_DECODE_IMPL_H

#include <pmt/pmt.h>
#include <lora2/lora_hamming_decode.h>

namespace gr {
  namespace lora2 {

    class lora_hamming_decode_impl : public lora_hamming_decode
    {
      private:
        int d_CR;
        int d_cw_len;
        pmt::pmt_t d_len_tag_key;

        const unsigned char d_syndrome_table_CR4[16] = {0x00, 0x10, 0x20, 0x09,
                                                        0x40, 0x0C, 0x05, 0x02,
                                                        0x80, 0x0A, 0x03, 0x04,
                                                        0x06, 0x01, 0x08, 0x18};

        const unsigned char d_syndrome_table_CR3[8] = {0x00, 0x10, 0x20, 0x02,
                                                       0x40, 0x01, 0x08, 0x04};

        const unsigned char d_syndrome_table_CR2[4] = {0x00, 0x01, 0x08, 0x02};

        const unsigned char d_syndrome_table_CR1[2] = {0x00, 0x01};

      public:
        lora_hamming_decode_impl(int CR, const std::string &len_tag_key);

        unsigned char pack_8bits(const unsigned char *in);
        unsigned char pack_7bits(const unsigned char *in);
        unsigned char pack_6bits(const unsigned char *in);
        unsigned char pack_5bits(const unsigned char *in);

        void unpack_4bits(const unsigned char in, unsigned char *out);

        void decode_one_block(const unsigned char *in, unsigned char *out);

        void handle_tag_propagation(int in_idx, int out_idx);

        void forecast (int noutput_items, gr_vector_int &ninput_items_required);

        int general_work(int noutput_items,
            gr_vector_int &ninput_items,
            gr_vector_const_void_star &input_items,
            gr_vector_void_star &output_items);

    };

  } // namespace lora2
} // namespace gr

#endif /* INCLUDED_LORA2_LORA_HAMMING_DECODE_IMPL_H */

