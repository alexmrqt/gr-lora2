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
#include "lora_soft_hamming_decode_impl.h"

namespace gr {
  namespace lora2 {

    lora_soft_hamming_decode::sptr
    lora_soft_hamming_decode::make(int CR, const std::string &len_tag_key)
    {
      return gnuradio::get_initial_sptr
        (new lora_soft_hamming_decode_impl(CR, len_tag_key));
    }


    lora_soft_hamming_decode_impl::lora_soft_hamming_decode_impl(int CR, const std::string &len_tag_key)
      : gr::block("lora_soft_hamming_decode",
          gr::io_signature::make(1, 1, sizeof(float)),
          gr::io_signature::make(1, 1, sizeof(unsigned char))),
        d_CR(CR), d_cw_len(CR+4), d_len_tag_key(pmt::intern(len_tag_key))
    {

      // Populate d_cw_table_CR4
      for (unsigned char i=0 ; i<16 ; ++i) {
        encode_one_block(4, i, &d_cw_table_CR4[i*8]);
      }

      // Populate d_cw_table_CR3
      for (unsigned char i=0 ; i<16 ; ++i) {
        encode_one_block(3, i, &d_cw_table_CR3[i*7]);
      }

      // Populate d_cw_table_CR2
      for (unsigned char i=0 ; i<16 ; ++i) {
        encode_one_block(2, i, &d_cw_table_CR2[i*6]);
      }

      // Populate d_cw_table_CR1
      for (unsigned char i=0 ; i<16 ; ++i) {
        encode_one_block(1, i, &d_cw_table_CR1[i*5]);
      }

      set_output_multiple(4);
      set_tag_propagation_policy(TPP_CUSTOM);
    }

    void
    lora_soft_hamming_decode_impl::encode_one_block(int CR, unsigned char in,
        bool *out)
    {
      bool in_block[4] = {(bool)((in>>3)&0x01),
                          (bool)((in>>2)&0x01),
                          (bool)((in>>1)&0x01),
                          (bool)(in&0x01)};

      switch(CR) {
        case 4:
          out[0] = in_block[0] ^ in_block[1] ^ in_block[3];
          out[1] = in_block[0] ^ in_block[2] ^ in_block[3];
          out[2] = in_block[0] ^ in_block[1] ^ in_block[2];
          out[3] = in_block[1] ^ in_block[2] ^ in_block[3];

          break;
        case 3:
          out[0] = in_block[0] ^ in_block[1] ^ in_block[3];
          out[1] = in_block[0] ^ in_block[1] ^ in_block[2];
          out[2] = in_block[1] ^ in_block[2] ^ in_block[3];

          break;
        case 2:
          out[0] = in_block[0] ^ in_block[1] ^ in_block[2];
          out[1] = in_block[1] ^ in_block[2] ^ in_block[3];

          break;
        case 1:
          out[0] = in_block[0] ^ in_block[1] ^ in_block[2] ^ in_block[3];
          break;
      }

      // Systematic part
      memcpy(out + CR, in_block, 4*sizeof(bool));
    }

    void
    lora_soft_hamming_decode_impl::decode_one_block(const float *in,
        unsigned char *out)
    {
      unsigned char min_idx = 0;
      float min_dist = FLT_MAX;
      float dist = 0.0;
      bool *cw_table = nullptr;
      const float *in_ptr = in;

      // Select the right cw_table
      switch(d_CR) {
        case 4:
          cw_table = d_cw_table_CR4;
          break;
        case 3:
          cw_table = d_cw_table_CR3;
          break;
        case 2:
          cw_table = d_cw_table_CR2;
          break;
        case 1:
          cw_table = d_cw_table_CR1;
          break;
      }

      // Decode
      for (unsigned char i=0 ; i<16 ; ++i) {

        dist = 0.0;
        in_ptr = in;
        for (int j=0 ; j<(d_CR+4) ; ++j) {
          dist += *(cw_table++) * *(in_ptr++);
        }

        if (dist < min_dist) {
          min_dist = dist;
          min_idx = i;
        }
      }

      // Unpack min_idx
      out[0] = (min_idx>>3)&0x01;
      out[1] = (min_idx>>2)&0x01;
      out[2] = (min_idx>>1)&0x01;
      out[3] = min_idx&0x01;
    }

    void
    lora_soft_hamming_decode_impl::handle_tag_propagation(int in_idx, int out_idx)
    {
      //All tags in input block are moved to the beginning of the output block
      //Length is updated
      uint64_t out_tag_offset = out_idx + nitems_written(0);
      long new_len = 0;
      std::vector<tag_t> tags;

      //Retrieve tags in input block
      get_tags_in_window(tags, 0, in_idx, in_idx+d_cw_len);

      //For each tag
      for (std::vector<tag_t>::iterator \
          tag=tags.begin() ; tag != tags.end() ; ++tag) {

        //Length tag get updated
        if(pmt::equal(tag->key, d_len_tag_key)) {
          new_len = (long)(pmt::to_long(tag->value) * 4.0 / d_cw_len);
          add_item_tag(0, out_tag_offset, tag->key, pmt::from_long(new_len));
        }
        //Other tags are simply put copied to out_idx
        else {
          add_item_tag(0, out_tag_offset, tag->key, tag->value);
        }
      }
    }

    void
    lora_soft_hamming_decode_impl::forecast (int noutput_items,
        gr_vector_int &ninput_items_required)
    {
      ninput_items_required[0] = (noutput_items/4) * d_cw_len;
    }

    int
    lora_soft_hamming_decode_impl::general_work (int noutput_items,
        gr_vector_int &ninput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
      const float *in = (const float *) input_items[0];
      unsigned char *out = (unsigned char *) output_items[0];

      // Number of blocks to be processed
      int n_blocks = std::min(ninput_items[0]/d_cw_len, noutput_items/4);

      for (int i=0 ; i < n_blocks ; ++i) {
        // Decode
        decode_one_block(in, out);

        // Propagate tags
        handle_tag_propagation(i*d_cw_len, i*4);

        // Set pointers to next block
        in += d_cw_len;
        out += 4;
      }

      consume_each(n_blocks * d_cw_len);
      return n_blocks * 4;
    }

  } /* namespace lora2 */
} /* namespace gr */

