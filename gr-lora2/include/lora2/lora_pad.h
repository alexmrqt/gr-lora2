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

#ifndef INCLUDED_LORA2_LORA_PAD_H
#define INCLUDED_LORA2_LORA_PAD_H

#include <lora2/api.h>
#include <gnuradio/tagged_stream_block.h>

namespace gr {
namespace lora2 {

/*!
 * \brief Block to pad a LoRa packet with zeros.
 *
 * This tagged stream block appends zeros at the end of LoRa packets, in order
 * to match their length with the input block sizes expected by the LoRa
 * interleaver: `SF.(CR+4)` binary elements (or `(SF-2).(CR+4)` binary elements
 * if `reduced_rate == true`).
 *
 * The input-output relationship is as follows: let
 * \f$ (in[0] \ldots in[L-1]) \in [0;1]^{L} \f$ be the input block,
 * then the output block is given as:
 * \f[
 * 		(in[0] \ldots in[L-1], 0 \ldots 0) \in [0;1]^{L+L_{pad}}
 * \f].
 * The number of zeros appended to the packet is given as:
 * \f[
 * 		L_{pad} = \left\{
 * 		\begin{array}{ll}
 * 			0 & {\rm if} \quad L \: {\rm mod} \: (SF.(4+CR)) = 0 \\
 *	 		SF.(4+CR) - L \: {\rm mod} \: (SF.(4+CR)) & {\rm if} \quad reduced\_rate = false \\
 *	 		(SF-2).(4+CR) - L \: {\rm mod} \: ((SF-2).(4+CR)) & {\rm otherwise}
 *	 	\end{array} \right.
 * \f]
 *
 *
 */
class LORA2_API lora_pad : virtual public gr::tagged_stream_block
{
	public:
		typedef boost::shared_ptr<lora_pad> sptr;

		/*!
		 * \brief Return a shared_ptr to a new instance of lora2::lora_pad.
		 *
		 * \param len_tag_key Length tag key for the tagged stream.
		 * \param SF LoRa spreading factor.
		 * \param CR LoRa coding rate (between 1 and 4).
		 * \param reduced_rate Set to true for LoRa low datarate optimization.
		 */
		static sptr make(const std::string &len_tag_key, unsigned char SF,
				unsigned char CR, bool reduced_rate = false);
};

} // namespace lora2
} // namespace gr

#endif /* INCLUDED_LORA2_LORA_PAD_H */

