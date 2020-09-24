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

#ifndef INCLUDED_LORA2_LORA_LOW_RATE_OPT_RX_H
#define INCLUDED_LORA2_LORA_LOW_RATE_OPT_RX_H

#include <lora2/api.h>
#include <gnuradio/sync_block.h>

namespace gr {
namespace lora2 {

/*!
 * \brief Applies the "low data rate optimize" option of LoRa on the receive side.
 * \ingroup lora2
 *
 * The low data rate optimize option of LoRa make the transmission more robust
 * by only using the \f$\log_2(M)-2\f$ most significant bits of
 * \f$M\f$-ary CSS symbols (that can carry up to \f$\log_2(M)\f$ bits).
 * This allows robustness with respect to small time/frequency impairments that
 * can shifts the demodulated symbols by +/-1.
 *
 * The input-output relationship of this block is given as:
 *
 *     out[n] = in[n] >> 2;
 *
 */
class LORA2_API lora_low_rate_opt_rx : virtual public gr::sync_block
{
	public:
		typedef boost::shared_ptr<lora_low_rate_opt_rx> sptr;

		/*!
		 * \brief Return a shared_ptr to a new instance of lora2::lora_low_rate_opt_rx.
		 *
		 * To avoid accidental use of raw pointers, lora2::lora_low_rate_opt_rx's
		 * constructor is in a private implementation
		 * class. lora2::lora_low_rate_opt_rx::make is the public interface for
		 * creating new instances.
		 */
		static sptr make();
};

} // namespace lora2
} // namespace gr

#endif /* INCLUDED_LORA2_LORA_LOW_RATE_OPT_RX_H */

