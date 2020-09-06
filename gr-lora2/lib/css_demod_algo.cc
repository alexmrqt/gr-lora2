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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include <lora2/css_demod_algo.h>

namespace gr {
namespace lora2 {

css_demod_algo::css_demod_algo(int M, bool upchirp):
	d_M(M), d_fft(fft::fft_complex(M)),
        d_fft_shift(fft::fft_shift<gr_complex>(M))
{
	// Allocate memory for chirp
	chirp = (gr_complex*)volk_malloc(M*sizeof(gr_complex), volk_get_alignment());

	// Construct chirp
	if (upchirp) {
		for (int k=0 ; k < M ; ++k) {
			chirp[k] = gr_expj(-M_PI*(float)k/M*k);
		}
	}
	else {
		for (int k=0 ; k < M ; ++k) {
			chirp[k] = gr_expj(M_PI*(float)k/M*k);
		}
	}
}

css_demod_algo::~css_demod_algo()
{
	// Free memory
	volk_free(chirp);
}

void css_demod_algo::demodulate(const gr_complex *in,
		unsigned short *out, size_t n_syms)
{
	gr_complex *fft_in = d_fft.get_inbuf();
	gr_complex *fft_out = d_fft.get_outbuf();

	for (size_t i=0 ; i < n_syms ; ++i) {
		// Dechirp and populate FFT input buffer
		volk_32fc_x2_multiply_32fc(fft_in, in, chirp, d_M);

		// Compute FFT
		d_fft.execute();

		// Find index of max(|d_fft|)
		volk_32fc_index_max_16u(out, fft_out, d_M);

                // Post-FFT FFT-shift
                *out = (*out + d_M/2)%d_M;

		// Update pointers
		in += d_M;
		++out;
	}
}

void css_demod_algo::soft_demodulate(const gr_complex *in,
		unsigned short *out_syms, float *out_soft, size_t n_syms)
{
	gr_complex *fft_in = d_fft.get_inbuf();
	gr_complex *fft_out = d_fft.get_outbuf();
	float *fft_abs = (float*)volk_malloc(d_M*sizeof(float), volk_get_alignment());

	for (size_t i=0 ; i < n_syms ; ++i) {
		// Dechirp and populate FFT input buffer
		volk_32fc_x2_multiply_32fc(fft_in, in, chirp, d_M);

		// Compute FFT
		d_fft.execute();

		// Compute |d_fft|
		volk_32fc_magnitude_squared_32f(fft_abs, fft_out, d_M);

		// Find index of max(|d_fft|)
		volk_32f_index_max_16u(out_syms, fft_abs, d_M);

		// Store FFT-magnitude value of demodulated symbol
		*out_soft = fft_abs[*out_syms];

                // Post-FFT FFT-shift
                *out_syms = (*out_syms + d_M/2)%d_M;

		// Update pointers
		in += d_M;
		++out_syms;
		++out_soft;
	}

	// Free memory
	volk_free(fft_abs);
}

void css_demod_algo::demodulate_with_spectrum(const gr_complex *in,
		unsigned short *out_syms, gr_complex *out_spectrum, size_t n_syms)
{
	gr_complex *fft_in = d_fft.get_inbuf();
	gr_complex *fft_out = d_fft.get_outbuf();

	for (size_t i=0 ; i < n_syms ; ++i) {
		// Dechirp and populate FFT input buffer
		volk_32fc_x2_multiply_32fc(fft_in, in, chirp, d_M);

		// Compute FFT
		d_fft.execute();

                // FFT-shift
                d_fft_shift.shift(fft_out, d_M);

		// Find index of max(|d_fft|)
		volk_32fc_index_max_16u(out_syms, fft_out, d_M);

		// Store FFT spectrum
		memcpy(out_spectrum, fft_out, d_M*sizeof(gr_complex));

		// Update pointers
		in += d_M;
		out_spectrum += d_M;
		++out_syms;
	}
}

} /* namespace lora2 */
} /* namespace gr */

