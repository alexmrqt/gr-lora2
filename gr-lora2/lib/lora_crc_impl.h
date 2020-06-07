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

#ifndef INCLUDED_LORA2_LORA_CRC_IMPL_H
#define INCLUDED_LORA2_LORA_CRC_IMPL_H

#include <lora2/lora_crc.h>
#include <pmt/pmt.h>

namespace gr {
  namespace lora2 {

    class lora_crc_impl : public lora_crc
    {
      private:
        uint16_t crc16(uint16_t crc, uint8_t data, uint16_t poly);
        uint16_t lora_payload_crc(const uint8_t* data, size_t data_len);
        void handle_check(pmt::pmt_t msg);
        void handle_generate(pmt::pmt_t msg);

      public:
        lora_crc_impl(bool mode);

        // Where all the action really happens
        int work(
            int noutput_items,
            gr_vector_const_void_star &input_items,
            gr_vector_void_star &output_items
            );
    };

  } // namespace lora2
} // namespace gr

#endif /* INCLUDED_LORA2_LORA_CRC_IMPL_H */

