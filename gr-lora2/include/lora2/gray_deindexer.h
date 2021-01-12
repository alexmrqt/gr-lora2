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

#ifndef INCLUDED_LORA2_GRAY_DEINDEXER_H
#define INCLUDED_LORA2_GRAY_DEINDEXER_H

#include <lora2/api.h>
#include <gnuradio/sync_block.h>

namespace gr {
namespace lora2 {

/*!
 * \brief A Gray-code deindexer (demapper).
 *
 * Assuming an \f$M\f$-arry CSS system, the input of this block must be vectors
 * of \f$M\f$ floats:
 * \f[
 * in[k] = (in_0[k] \dots in_{M-1}[k])^T \in \mathbb{R}^M
 * \f]
 * These elements must represent either the real part (using coherent demodulation)
 * or the absolute value (using non-coherent demodulation) of the output of the
 * CSS correlator.
 *
 * In LoRa, symbols are gray mapped, so that consecutive symbol indices encodes
 * binary values that only differs by one bit.
 * This means that \f$in_i[k]\f$ (\f$i \in [0;M-1]\f$) is the confidence of
 * having received \f$gray^{-1}(i)\f$ (the Gray decoded value of \f$i\f$).
 * Equivalently, this means that \f$in_{gray(i)}\f$ is the confidence of having
 * received the symbol \f$i\f$.
 *
 * This bloc, rearrange the input vector so that \f$out_i[k]\f$ is the
 * confidence of having received the symbol \f$i\f$.
 *
 * The input-output relationship of this block is:
 * \f[
 * out_{gray(i)}[k] = in_i[k]
 * \f]
 *
 */
class LORA2_API gray_deindexer : virtual public gr::sync_block
{
	public:
		typedef boost::shared_ptr<gray_deindexer> sptr;

		/*!
		 * \brief Return a shared_ptr to a new instance of lora2::gray_deindexer.
		 *
		 * \param M Arity of the CSS modulated signal (\f$\log_2(M)\f$ being
		 * the number of bits per symbol).
		 */
		static sptr make(unsigned int M);
};

} // namespace lora2
} // namespace gr

#endif /* INCLUDED_LORA2_GRAY_DEINDEXER_H */

