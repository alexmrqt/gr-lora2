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

#ifndef INCLUDED_LORA2_LORA_CRC_H
#define INCLUDED_LORA2_LORA_CRC_H

#include <lora2/api.h>
#include <gnuradio/sync_block.h>

namespace gr {
namespace lora2 {

/*!
 * \brief Check or compute the CRC of LoRa packets (as PDUs).
 * \ingroup lora2
 *
 * Depending on parameter `mode`, this block acts either as a CRC validator
 * (`mode = true`), or a CRC generator (`mode = false`).
 *
 * When acting as a CRC generator, the CRC of the payload is computed and
 * appended to it.
 *
 * When acting as a CRC validator, and if the metadata contains a field
 * `has_crc` set to `PMT_T`, then the CRC is checked, and the packet, stripped
 * from its CRC, is passed to the output.
 * Else, if the metadata contains no `has_crc` field, or if it is set to `PMT_F`,
 * then the input is passed to the output unaltered.
 *
 * The LoRa CRC is a 16 bit CCITT CRC, with polyniomial
 * `\f$x^16 + x^12 + x^5 + 1\f$, and seed `0x0000`
 * (see annex 1 of ITU-T Rec. V.41).
 *
 */
class LORA2_API lora_crc : virtual public gr::sync_block
{
	public:
		typedef boost::shared_ptr<lora_crc> sptr;

		/*!
		 * \brief Return a shared_ptr to a new instance of lora2::lora_crc.
		 *
		 * To avoid accidental use of raw pointers, lora2::lora_crc's
		 * constructor is in a private implementation
		 * class. lora2::lora_crc::make is the public interface for
		 * creating new instances.
		 */
		static sptr make(bool mode=true);
};

} // namespace lora2
} // namespace gr

#endif /* INCLUDED_LORA2_LORA_CRC_H */

