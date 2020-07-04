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
#include "lora_hamming_decode_impl.h"

namespace gr {
  namespace lora2 {

    lora_hamming_decode::sptr
    lora_hamming_decode::make(int CR, const std::string &len_tag_key)
    {
      return gnuradio::get_initial_sptr
        (new lora_hamming_decode_impl(CR, len_tag_key));
    }


    lora_hamming_decode_impl::lora_hamming_decode_impl(int CR,
        const std::string &len_tag_key): gr::block("lora_hamming_decode",
          gr::io_signature::make(1, 1, sizeof(unsigned char)),
          gr::io_signature::make(1, 1, sizeof(unsigned char))),
        d_CR(CR), d_cw_len(CR+4), d_len_tag_key(pmt::intern(len_tag_key))
    {
      set_output_multiple(4);
      set_tag_propagation_policy(TPP_CUSTOM);
    }

    unsigned char
    lora_hamming_decode_impl::pack_8bits(const unsigned char *in)
    {
      unsigned char out = *(in++) << 7;
      out |= *(in++) << 6;
      out |= *(in++) << 5;
      out |= *(in++) << 4;
      out |= *(in++) << 3;
      out |= *(in++) << 2;
      out |= *(in++) << 1;
      out |= *in;

      return out;
    }

    unsigned char
    lora_hamming_decode_impl::pack_7bits(const unsigned char *in)
    {
      unsigned char out = *(in++) << 6;
      out |= *(in++) << 5;
      out |= *(in++) << 4;
      out |= *(in++) << 3;
      out |= *(in++) << 2;
      out |= *(in++) << 1;
      out |= *in;

      return out;
    }

    unsigned char
    lora_hamming_decode_impl::pack_6bits(const unsigned char *in)
    {
      unsigned char out = *(in++) << 5;
      out |= *(in++) << 4;
      out |= *(in++) << 3;
      out |= *(in++) << 2;
      out |= *(in++) << 1;
      out |= *in;

      return out;
    }

    unsigned char
    lora_hamming_decode_impl::pack_5bits(const unsigned char *in)
    {
      unsigned char out = *(in++) << 4;
      out |= *(in++) << 3;
      out |= *(in++) << 2;
      out |= *(in++) << 1;
      out |= *in;

      return out;
    }

    void
    lora_hamming_decode_impl::unpack_4bits(const unsigned char in, unsigned char *out)
    {
      *(out++) = (in>>3)&0x01;
      *(out++) = (in>>2)&0x01;
      *(out++) = (in>>1)&0x01;
      *out = in&0x01;
    }

    void
    lora_hamming_decode_impl::decode_one_block(const unsigned char *in, unsigned char *out)
    {
      unsigned char syndrome = 0;
      unsigned char decoded = 0;

      // Decode
      switch(d_CR) {
        case 4:
          syndrome = (in[0]^in[4]^in[5]^in[7])<<3;
          syndrome |= (in[1]^in[4]^in[6]^in[7])<<2;
          syndrome |= (in[2]^in[4]^in[5]^in[6])<<1;
          syndrome |= (in[3]^in[5]^in[6]^in[7]);

          decoded = (pack_8bits(in) ^ d_syndrome_table_CR4[syndrome]);

          break;
        case 3:
          syndrome = (in[0]^in[3]^in[4]^in[6])<<2;
          syndrome |= (in[1]^in[3]^in[4]^in[5])<<1;
          syndrome |= (in[2]^in[4]^in[5]^in[6]);

          decoded = (pack_7bits(in) ^ d_syndrome_table_CR3[syndrome]);

          break;
        case 2:
          syndrome = (in[0]^in[2]^in[3]^in[4])<<1;
          syndrome |= (in[1]^in[3]^in[4]^in[5]);

          decoded = (pack_6bits(in) ^ d_syndrome_table_CR2[syndrome]);

          break;
        case 1:
          syndrome = (in[0]^in[1]^in[2]^in[3]^in[4]);

          decoded = (pack_5bits(in) ^ d_syndrome_table_CR1[syndrome]);

          break;
      }

      // Unpack decoded bits
      unpack_4bits(decoded, out);
    }

    void
    lora_hamming_decode_impl::handle_tag_propagation(int in_idx, int out_idx)
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
    lora_hamming_decode_impl::forecast(int noutput_items,
        gr_vector_int &ninput_items_required)
    {
      ninput_items_required[0] = (noutput_items/4) * d_cw_len;
    }

    int
    lora_hamming_decode_impl::general_work(int noutput_items,
        gr_vector_int &ninput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
      const unsigned char *in = (const unsigned char *) input_items[0];
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

