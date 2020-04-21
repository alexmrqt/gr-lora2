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

#ifndef INCLUDED_LORA2_LORA_HEADER_FORMAT_H
#define INCLUDED_LORA2_LORA_HEADER_FORMAT_H

#include <lora2/api.h>

#include <cmath>
#include <gnuradio/digital/header_buffer.h>
#include <gnuradio/digital/header_format_base.h>
#include <pmt/pmt.h>
#include <boost/enable_shared_from_this.hpp>

namespace gr {
  namespace lora2 {

    /*!
     * \brief Construct or parse a LoRa header.
     *
     * LoRa Header have the following structure:
     *
     * | Payload length |   CR    | Has CRC | CRC (opt.) | 1st bits of payload |
     * <-----8 bits----><-3 bits-><-1 bit--><---8 bits-->
     * <--------------------------(SF-2) * 4 bits----------------------------->
     *
     * The reason why there is some payload bits in the header is explained
     * hereafter.
     * The header must fill an interleaving matrix, that is SF*(CR+4) bits before
     * decoding and deinterleaving.
     * The header is sent in reduced rate mode, thus there are only
     * (SF-2)*(CR+4) bits after deinterleaving.
     * Finally, the header is coded with CR = 4, which gives (SF-2)*4 bits
     * after decoding.
     * Of these (SF-2)*4 bits, only 20 bits are used by header fields.
     *
     */
    class LORA2_API lora_header_format : public gr::digital::header_format_base
    {
      private:
        const unsigned char d_SF;
        const unsigned char d_hdr_len = 20;

        uint8_t d_payload_len = 0;
        uint8_t d_CR = 0;
        uint8_t d_has_crc = 0;
        uint8_t d_crc = 0;

      protected:
        //! Verify that the header is valid
        virtual bool header_ok();

        /*! Get info from the header; return payload length and package
         *  rest of data in d_info dictionary.
         */
        virtual int header_payload();

      public:
        //typedef boost::shared_ptr<lora_header_format> sptr;
        typedef boost::shared_ptr<gr::digital::header_format_base> sptr;

        lora_header_format(unsigned char SF);
        virtual ~lora_header_format()
        {
        }

        virtual bool format(int nbytes_in,
                            const unsigned char* input,
                            pmt::pmt_t& output,
                            pmt::pmt_t& info);

        virtual bool parse(int nbits_in,
                           const unsigned char* input,
                           std::vector<pmt::pmt_t>& info,
                           int& nbits_processed);

        virtual size_t header_nbits() const;

        static sptr make(unsigned char SF);
    };

  } // namespace lora2
} // namespace gr

#endif /* INCLUDED_LORA2_LORA_HEADER_FORMAT_H */
