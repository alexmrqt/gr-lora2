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

#ifndef INCLUDED_LORA2_LORA_SOFT_LOW_RATE_OPT_RX_H
#define INCLUDED_LORA2_LORA_SOFT_LOW_RATE_OPT_RX_H

#include <lora2/api.h>
#include <gnuradio/sync_block.h>

namespace gr {
namespace lora2 {

/*!
 * \brief On soft bits, applies the "low data rate optimize" option of LoRa on the receive side.
 *
 * The low data rate optimize option of LoRa make the transmission more robust
 * by only using the \f$\log_2(M)-2\f$ most significant bits of
 * \f$M\f$-ary CSS symbols (that can carry up to \f$\log_2(M)\f$ bits).
 * This allows robustness with respect to small time/frequency impairments that
 * can shifts the demodulated symbols by +/-1.
 *
 * This blocks drops the two last elements of the input vector.
 * Let \f$in[k] = (in_0[k] \dots in_{SF-1}[k]) \: \in \mathbb{R}^{SF}\f$ be the
 * k-th input sample, then the corresponding output sample is given as:
 * \f[
 *	 out[k] = (in_0[k] \dots in_{SF-3}[k]) \: \in \mathbb{R}^{SF-2}
 * \f]
 *
 */
class LORA2_API lora_soft_low_rate_opt_rx : virtual public gr::sync_block
{
	public:
		typedef boost::shared_ptr<lora_soft_low_rate_opt_rx> sptr;

		/*!
		 * \brief Return a shared_ptr to a new instance of lora2::lora_soft_low_rate_opt_rx.
		 *
		 * \param SF LoRa spreading factor.
		 *
		 */
		static sptr make(int SF);
};

} // namespace lora2
} // namespace gr

#endif /* INCLUDED_LORA2_LORA_SOFT_LOW_RATE_OPT_RX_H */

