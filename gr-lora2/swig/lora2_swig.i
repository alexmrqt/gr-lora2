/* -*- c++ -*- */

#define LORA2_API

%include "gnuradio.i"           // the common stuff

//load generated python docstrings
%include "lora2_swig_doc.i"

%{
#include "lora2/css_llr_converter.h"
#include "lora2/css_mod.h"
#include "lora2/lora_add_preamble.h"
#include "lora2/lora_depad.h"
#include "lora2/lora_merge_rem.h"
#include "lora2/lora_whiten.h"
#include "lora2/lora_soft_depad.h"
#include "lora2/lora_header_format.h"
#include "lora2/lora_pad.h"
#include "lora2/lora_drop_rem.h"
#include "lora2/gray_encode.h"
#include "lora2/gray_decode.h"
#include "lora2/gray_deindexer.h"
#include "lora2/lora_low_rate_opt_tx.h"
#include "lora2/lora_low_rate_opt_rx.h"
#include "lora2/flip_half_bytes.h"
#include "lora2/lora_crc.h"
#include "lora2/lora_soft_low_rate_opt_rx.h"
#include "lora2/lora_interleaver.h"
#include "lora2/lora_deinterleaver.h"
#include "lora2/lora_soft_deinterleaver.h"
#include "lora2/lora_hamming_encode.h"
#include "lora2/lora_hamming_decode.h"
%}

%include "lora2/css_llr_converter.h"
GR_SWIG_BLOCK_MAGIC2(lora2, css_llr_converter);
%include "lora2/css_mod.h"
GR_SWIG_BLOCK_MAGIC2(lora2, css_mod);
%include "lora2/lora_add_preamble.h"
GR_SWIG_BLOCK_MAGIC2(lora2, lora_add_preamble);
%include "lora2/lora_depad.h"
GR_SWIG_BLOCK_MAGIC2(lora2, lora_depad);
%include "lora2/lora_merge_rem.h"
GR_SWIG_BLOCK_MAGIC2(lora2, lora_merge_rem);

%include "lora2/lora_whiten.h"
GR_SWIG_BLOCK_MAGIC2(lora2, lora_whiten);
%include "lora2/lora_soft_depad.h"
GR_SWIG_BLOCK_MAGIC2(lora2, lora_soft_depad);

%include "lora2/lora_header_format.h"
%template(lora_header_format_sptr) boost::shared_ptr<gr::lora2::lora_header_format>;
%pythoncode %{
lora_header_format_sptr.__repr__ = lambda self: "<lora_header_format>"
lora_header_format = lora_header_format.make;
%}

%include "lora2/lora_pad.h"
GR_SWIG_BLOCK_MAGIC2(lora2, lora_pad);
%include "lora2/lora_drop_rem.h"
GR_SWIG_BLOCK_MAGIC2(lora2, lora_drop_rem);
%include "lora2/gray_encode.h"
GR_SWIG_BLOCK_MAGIC2(lora2, gray_encode);
%include "lora2/gray_decode.h"
GR_SWIG_BLOCK_MAGIC2(lora2, gray_decode);
%include "lora2/gray_deindexer.h"
GR_SWIG_BLOCK_MAGIC2(lora2, gray_deindexer);
%include "lora2/lora_low_rate_opt_tx.h"
GR_SWIG_BLOCK_MAGIC2(lora2, lora_low_rate_opt_tx);
%include "lora2/lora_low_rate_opt_rx.h"
GR_SWIG_BLOCK_MAGIC2(lora2, lora_low_rate_opt_rx);
%include "lora2/flip_half_bytes.h"
GR_SWIG_BLOCK_MAGIC2(lora2, flip_half_bytes);
%include "lora2/lora_crc.h"
GR_SWIG_BLOCK_MAGIC2(lora2, lora_crc);
%include "lora2/lora_soft_low_rate_opt_rx.h"
GR_SWIG_BLOCK_MAGIC2(lora2, lora_soft_low_rate_opt_rx);
%include "lora2/lora_interleaver.h"
GR_SWIG_BLOCK_MAGIC2(lora2, lora_interleaver);
%include "lora2/lora_deinterleaver.h"
GR_SWIG_BLOCK_MAGIC2(lora2, lora_deinterleaver);
%include "lora2/lora_soft_deinterleaver.h"
GR_SWIG_BLOCK_MAGIC2(lora2, lora_soft_deinterleaver);
%include "lora2/lora_hamming_encode.h"
GR_SWIG_BLOCK_MAGIC2(lora2, lora_hamming_encode);
%include "lora2/lora_hamming_decode.h"
GR_SWIG_BLOCK_MAGIC2(lora2, lora_hamming_decode);
