/* -*- c++ -*- */
/*
 * Copyright 2022 Alexandre Marquet.
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

#include <pmt/pmt.h>
#include <lora2/lora_whiten.h>


namespace gr {
namespace lora2 {

class lora_whiten_impl : public lora_whiten
{
	private:
		const uint64_t d_seed;
		pmt::pmt_t d_has_crc_key;

	protected:
		int calculate_output_stream_length(const gr_vector_int &ninput_items);
		void lfsr(const uint8_t *in, uint8_t *out, const size_t bufferSize);

	public:
		lora_whiten_impl(const std::string &len_tag_key);

		// Where all the action really happens
		int work(int noutput_items,
				gr_vector_int &ninput_items,
				gr_vector_const_void_star &input_items,
				gr_vector_void_star &output_items);
};

} // namespace lora2
} // namespace gr

#endif /* INCLUDED_LORA2_LORA_WHITEN_IMPL_H */
