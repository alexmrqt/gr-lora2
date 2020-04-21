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
#include <lora2/lora_header_format.h>

namespace gr {
  namespace lora2 {

    lora_header_format::sptr
    lora_header_format::make(unsigned char SF)
    {
        return lora_header_format::sptr(
            new lora_header_format(SF));
    }

    lora_header_format::lora_header_format(unsigned char SF) :
      header_format_base(), d_SF(SF)
    {
    }

    bool
    lora_header_format::header_ok()
    {
      const uint8_t *d =  d_hdr_reg.header();
      uint8_t crc = 0;

      crc |= (d[0]^d[1]^d[2]^d[3])<<4;
      crc |= (d[0]^d[4]^d[5]^d[6]^d[11])<<3;
      crc |= (d[1]^d[4]^d[7]^d[8]^d[10])<<2;
      crc |= (d[2]^d[5]^d[7]^d[9]^d[10]^d[11])<<1;
      crc |= (d[3]^d[6]^d[8]^d[9]^d[10]^d[11]);

      return (crc == d_crc);
    }

    int
    lora_header_format::header_payload()
    {
      return 0;
    }

    bool
    lora_header_format::format(int nbytes_in, const unsigned char* input,
        pmt::pmt_t& output, pmt::pmt_t& info)
    {
      return false;
    }

    bool
    lora_header_format::parse(int nbits_in, const unsigned char* input,
        std::vector<pmt::pmt_t>& info, int& nbits_processed)
    {
      int n_bits = 0; // Number of coded bits in the payload, excluding those
                      // appended at the end of the header.
      int n_bits_total = 0; // Number of coded bits in the payload, excluding 
                            // those appended at the end of the header, but
                            // including padding.
      int bits_multiple = 0;  // Due to interleaving working on blocks of (CR+4)*SF, 
                              // n_bits_total can only by a multiple of bits_multiple.
      int n_bits_pad = 0; // Number of padding bits, to accomodate for the interleaver.

      //Abort if too few bits received
      if (nbits_in < d_hdr_len) {
        nbits_processed = 0;
        return false;
      }

      //Copy incoming bits to the header buffer
      for (unsigned char i=0 ; i < d_hdr_len ; ++i) {
        d_hdr_reg.insert_bit(input[i]);
      }

      //Extract fields
      d_payload_len = d_hdr_reg.extract_field8(0, 8);
      d_CR = d_hdr_reg.extract_field8(8, 3);
      d_has_crc = d_hdr_reg.extract_field8(11, 1);
      d_crc = d_hdr_reg.extract_field8(12, 8);

      if ((!d_has_crc) || (d_has_crc && header_ok())) {
        //Account for CRC presence in payload length
        d_payload_len += 2*d_has_crc;

        //Compute auxiliary variables
        n_bits = d_payload_len * 8; //Before hamming coding
        n_bits -= (d_SF-2)*4 - d_hdr_len; //Exclude payload bits included at the end of the header
        n_bits /= 4;
        n_bits *= (4+d_CR); //After hamming coding

        bits_multiple = (d_CR + 4) * d_SF;

        n_bits_total = (int)ceil(n_bits/(float)bits_multiple) * bits_multiple;

        n_bits_pad = n_bits_total - n_bits;

        //Make PMT message
        d_info = pmt::make_dict();

        d_info = pmt::dict_add(d_info, pmt::intern("payload_len"),
                pmt::from_long(d_payload_len));

        d_info = pmt::dict_add(d_info, pmt::intern("CR"),
                pmt::from_long(d_CR));

        d_info = pmt::dict_add(d_info, pmt::intern("has_crc"),
                pmt::from_long(d_has_crc));

        d_info = pmt::dict_add(d_info, pmt::intern("header_crc"),
                pmt::from_long(d_crc));

        d_info = pmt::dict_add(d_info, pmt::intern("packet_len_bits"),
                pmt::from_long(n_bits_total));

        d_info = pmt::dict_add(d_info, pmt::intern("pad_len"),
                pmt::from_long(n_bits_pad));

        d_info = pmt::dict_add(d_info, pmt::intern("packet_len_syms"),
                pmt::from_long(n_bits_total / d_SF));

        d_info = pmt::dict_add(d_info, pmt::intern("has_crc"),
                (d_has_crc)?pmt::PMT_T:pmt::PMT_F);

        info.push_back(d_info);

        return true;
        //if 'rem_bits' in parsed_header:
        //    out_msg = pmt.dict_add(out_msg, pmt.intern('rem_bits'),
        //            pmt.init_u8vector(len(parsed_header['rem_bits']), parsed_header['rem_bits']))
      }

      return false;
    }

    size_t
    lora_header_format::header_nbits() const
    {
      return 0;
    }


  } /* namespace lora2 */
} /* namespace gr */

