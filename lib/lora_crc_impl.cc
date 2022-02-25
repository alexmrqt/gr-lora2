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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "lora_crc_impl.h"

namespace gr {
namespace lora2 {

lora_crc::sptr lora_crc::make(bool mode)
{
	return gnuradio::get_initial_sptr
		(new lora_crc_impl(mode));
}

uint16_t lora_crc_impl::crc16(uint16_t crc, uint8_t data, uint16_t poly)
{
	for (char i=0 ; i < 8 ; ++i) {
		if (crc&0x8000) {
			crc <<= 1;
			crc &= 0xFFFF;
			crc ^= poly;
		}
		else {
			crc <<= 1;
			crc &= 0xFFFF;
		}
	}

	return crc ^ (uint16_t)data;
}

uint16_t lora_crc_impl::lora_payload_crc(const uint8_t* data, size_t data_len)
{
	uint16_t crc = 0;

	for (const uint8_t* ele=data ; ele < (data+data_len) ; ++ele) {
		crc = crc16(crc, *ele, 0x1021);
	}

	return crc;
}

void lora_crc_impl::handle_check(pmt::pmt_t msg)
{
	pmt::pmt_t hdr = pmt::car(msg);
	const std::vector<uint8_t> payload = pmt::u8vector_elements(pmt::cdr(msg));
	uint16_t crc = 0;
	uint16_t comp_crc = 0;

	if (pmt::equal(pmt::dict_ref(hdr, pmt::intern("has_crc"), pmt::PMT_F), pmt::PMT_T)) {
		crc = (payload[payload.size()-1] << 8) | payload[payload.size()-2];

		comp_crc = lora_payload_crc(&payload[0], payload.size()-2);

		if (crc == comp_crc) {
			message_port_pub(pmt::intern("pdus"), pmt::cons(hdr,
						pmt::init_u8vector(payload.size()-2, &payload[0])));

			GR_LOG_INFO(d_debug_logger, "CRC OK");
		}
		else {
			GR_LOG_INFO(d_debug_logger, "CRC NOK");
		}
	}
	else {
		message_port_pub(pmt::intern("pdus"), msg);
	}
}

void lora_crc_impl::handle_generate(pmt::pmt_t msg)
{
	pmt::pmt_t hdr = pmt::car(msg);
	std::vector<uint8_t> payload(pmt::u8vector_elements(pmt::cdr(msg)));
	uint16_t crc = 0;

	if (pmt::equal(pmt::dict_ref(hdr, pmt::intern("has_crc"), pmt::PMT_F), pmt::PMT_T)) {
		crc = lora_payload_crc(&payload[0], payload.size());

		payload.push_back(crc&0xFF);
		payload.push_back(crc>>8);

		message_port_pub(pmt::intern("pdus"), pmt::cons(hdr,
					pmt::init_u8vector(payload.size(), &payload[0])));
	}
	else {
		message_port_pub(pmt::intern("pdus"), msg);
	}
}

/*
 * The private constructor
 */
lora_crc_impl::lora_crc_impl(bool mode)
	: gr::sync_block("lora_crc",
			gr::io_signature::make(0, 0, 0),
			gr::io_signature::make(0, 0, 0))
{
	message_port_register_in(pmt::intern("pdus"));
	message_port_register_out(pmt::intern("pdus"));

	if (mode) {
		set_msg_handler(pmt::intern("pdus"),
				boost::bind(&lora_crc_impl::handle_check, this, _1));
	}
	else {
		set_msg_handler(pmt::intern("pdus"),
				boost::bind(&lora_crc_impl::handle_generate, this, _1));
	}
}

int lora_crc_impl::work(int noutput_items,
		gr_vector_const_void_star &input_items,
		gr_vector_void_star &output_items)
{
	// Tell runtime system how many output items we produced.
	return noutput_items;
}

} /* namespace lora2 */
} /* namespace gr */

