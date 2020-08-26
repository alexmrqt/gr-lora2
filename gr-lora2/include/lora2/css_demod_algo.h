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

#ifndef INCLUDED_LORA2_CSS_DEMOD_ALGO_H
#define INCLUDED_LORA2_CSS_DEMOD_ALGO_H

#include <lora2/api.h>
#include <gnuradio/expj.h>
#include <gnuradio/fft/fft.h>
#include <volk/volk.h>

namespace gr {
namespace lora2 {

/*!
 * \brief <+description+>
 *
 */
class LORA2_API css_demod_algo
{
	private:
		int d_M;
		gr_complex *chirp;
		fft::fft_complex d_fft;

	public:
		css_demod_algo(int M, bool upchirp=true);
		~css_demod_algo();

		void demodulate(const gr_complex *in,
				unsigned short *out,
				size_t n_syms);

		void soft_demodulate(const gr_complex *in,
				unsigned short *out_syms,
				float *out_soft,
				size_t n_syms);

		void demodulate_with_spectrum(const gr_complex *in,
				unsigned short *out_syms,
				gr_complex *out_spectrum,
				size_t n_syms);
};

} // namespace lora2
} // namespace gr

#endif /* INCLUDED_LORA2_CSS_DEMOD_ALGO_H */

