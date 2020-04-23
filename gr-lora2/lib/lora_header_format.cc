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
      header_format_base(), d_SF(SF), d_hdr_tot_len((SF-2)*4)
    {
    }

    uint8_t
    lora_header_format::compute_crc(uint16_t d)
    {
      uint8_t crc = 0;

      crc |= (((d>>11)&0x01) ^ ((d>>10)&0x01) ^ ((d>>9)&0x01) ^ ((d>>8)&0x01))<<4;
      crc |= (((d>>11)&0x01) ^ ((d>>7)&0x01) ^ ((d>>6)&0x01) ^ ((d>>5)&0x01) ^ (d&0x01))<<3;
      crc |= (((d>>10)&0x01) ^ ((d>>7)&0x01) ^ ((d>>4)&0x01) ^ ((d>>3)&0x01) ^ ((d>>1)&0x01))<<2;
      crc |= (((d>>9)&0x01) ^ ((d>>6)&0x01) ^ ((d>>4)&0x01) ^ ((d>>2)&0x01) ^ ((d>>1)&0x01) ^ (d&0x01))<<1;
      crc |= (((d>>8)&0x01) ^ ((d>>5)&0x01) ^ ((d>>3)&0x01) ^ ((d>>2)&0x01) ^ ((d>>1)&0x01) ^ (d&0x01));

      return crc;
    }

    bool
    lora_header_format::header_ok()
    {
      uint16_t data =  d_hdr_reg.extract_field16(0, 12);
      uint8_t crc = 0;

      if (d_hdr_reg.length() < d_hdr_len) {
        return false;
      }

      crc = compute_crc(data);

      return (crc == d_crc);
    }

    int
    lora_header_format::header_payload()
    {
      int n_bits = 0; // Number of coded bits in the payload, excluding those
                      // appended at the end of the header.
      int n_bits_total = 0; // Number of coded bits in the payload, excluding 
                            // those appended at the end of the header, but
                            // including padding.
      int bits_multiple = 0;  // Due to interleaving working on blocks of (CR+4)*SF, 
                              // n_bits_total can only by a multiple of bits_multiple.
      int n_bits_pad = 0; // Number of padding bits, to accomodate for the interleaver.
      
      //Compute auxiliary variables
      n_bits = (d_payload_len + 2*d_has_crc) * 8; // Integrating CRC length,
                                                  // and before hamming coding
      n_bits -= (d_SF-2)*4 - d_hdr_len; // Excluding payload bits included at
                                        // the end of the header
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

      d_info = pmt::dict_add(d_info, pmt::intern("packet_len_bits"),
              pmt::from_long(n_bits_total));

      d_info = pmt::dict_add(d_info, pmt::intern("pad_len"),
              pmt::from_long(n_bits_pad));

      d_info = pmt::dict_add(d_info, pmt::intern("packet_len_syms"),
              pmt::from_long(n_bits_total / d_SF));

      d_info = pmt::dict_add(d_info, pmt::intern("has_crc"),
              (d_has_crc)?pmt::PMT_T:pmt::PMT_F);

      if ((d_hdr_tot_len-d_hdr_len) > 0) {
          d_info = pmt::dict_add(d_info, pmt::intern("rem_bits"),
                  pmt::init_u8vector(d_hdr_tot_len-d_hdr_len, d_rem));
      }

      return n_bits;
    }

    bool
    lora_header_format::format(int nbytes_in, const unsigned char* input,
        pmt::pmt_t& output, pmt::pmt_t& info)
    {
      uint16_t buffer = 0;
      uint8_t* unpacked_hdr = (uint8_t*)volk_malloc(header_nbits(),
          volk_get_alignment());

      //Extract payload length
      d_payload_len = (unsigned char)nbytes_in/8;
      //Extract CR (default is 4)
      d_CR = (uint8_t)pmt::to_long(pmt::dict_ref(info,
            pmt::intern("CR"), pmt::from_long(4)));
      //Extract has_crc (true by default)
      d_has_crc = (uint8_t)pmt::to_bool(pmt::dict_ref(info,
            pmt::intern("has_crc"), pmt::PMT_T));
      //Remove the 2 bytes of the CRC from payload length
      d_payload_len -= 2*d_has_crc;

      //Add these three fields to the buffer
      buffer |= d_payload_len << 4;
      buffer |= d_CR << 1;
      buffer |= d_has_crc;

      //Compute CRC
      d_crc = compute_crc(buffer);

      //Unpack buffer to unpacked_hdr
      for(char i = 0 ; i < 12 ; ++i) {
        unpacked_hdr[i] = (buffer>>(11-i))&0x01;
      }
      //Unpack crc to unpacked_hdr
      for(char i = 0 ; i < 8 ; ++i) {
        unpacked_hdr[i+12] = (d_crc>>(7-i))&0x01;
      }
      //Put first bits of the payload at the end of the header
      for(char i = 0 ; i < (d_hdr_tot_len-d_hdr_len) ; ++i) {
        unpacked_hdr[i+12+8] = input[i];
      }

      // Package output data into a PMT vector
      output = pmt::init_u8vector(header_nbits(), unpacked_hdr);

      // Creating the output pmt copies data; free our own here.
      volk_free(unpacked_hdr);

      return true;
    }

    bool
    lora_header_format::parse(int nbits_in, const unsigned char* input,
        std::vector<pmt::pmt_t>& info, int& nbits_processed)
    {
      //Abort if too few bits received
      if (nbits_in < d_hdr_tot_len) {
        nbits_processed = 0;
        return true;
      }

      //Copy data into buffer
      for (int i = 0 ; i < d_hdr_len ; ++i) {
        d_hdr_reg.insert_bit(input[i]);
      }
      for (int i=0 ; i < (d_hdr_tot_len-d_hdr_len) ; ++i) {
        d_rem[i] = input[i+d_hdr_len];
      }
      nbits_processed = d_hdr_tot_len;

      //Extract fields
      d_payload_len = d_hdr_reg.extract_field8(0, 8);
      d_CR = d_hdr_reg.extract_field8(8, 3);
      d_has_crc = d_hdr_reg.extract_field8(11, 1);
      d_crc = d_hdr_reg.extract_field8(12, 8);

      if ((!d_has_crc) || (d_has_crc && header_ok())) {
        //Populate d_info
        header_payload();

        info.push_back(d_info);

        //Clear header register and return success
        d_hdr_reg.clear();
        return true;
      }

      //Clear header register and return success
      d_hdr_reg.clear();
      return false;
    }

    size_t
    lora_header_format::header_nbits() const
    {
      return d_hdr_tot_len;
    }


  } /* namespace lora2 */
} /* namespace gr */

