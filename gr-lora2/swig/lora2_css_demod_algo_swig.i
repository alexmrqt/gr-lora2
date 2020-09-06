/* -*- c++ -*- */

#define LORA2_API

%include "carrays.i"
%include "gnuradio.i"

//load generated python docstrings
%include "lora2_swig_doc.i"

%{
#include "lora2/css_demod_algo.h"
%}

%array_class(unsigned short, ushortArray);
%array_class(float , ufloatArray);
%array_class(gr_complex, grcomplexArray);

%feature("shadow") demodulate %{
def demodulate(*args):
    import numpy

    assert len(args) == 2

    self = args[0]
    _in = args[1]

    assert isinstance(_in, numpy.ndarray), "Input must be a Numpy Array of complex64."
    assert _in.dtype == numpy.complex64, "Input must be a Numpy Array of complex64."

    n_syms = len(_in) // self.get_M()

    in_grcomplex = grcomplexArray(len(_in))
    out_ushort = ushortArray(n_syms)

    for i in range(0, len(_in)):
        in_grcomplex[i] = complex(_in[i])

    $action(self, in_grcomplex.cast(), out_ushort, n_syms)

    out = numpy.zeros(n_syms, dtype=numpy.ushort)
    for i in range(0, n_syms):
        out[i] = out_ushort[i]

    return out
%}

%feature("shadow") soft_demodulate %{
def soft_demodulate(*args):
    import numpy

    assert len(args) == 2

    self = args[0]
    _in = args[1]

    assert isinstance(_in, numpy.ndarray), "Input must be a Numpy Array of complex64."
    assert _in.dtype == numpy.complex64, "Input must be a Numpy Array of complex64."

    n_syms = len(_in) // self.get_M()

    in_grcomplex = grcomplexArray(len(_in))
    out_syms_ushort = ushortArray(n_syms)
    out_confidence_float = ufloatArray(n_syms)

    for i in range(0, len(_in)):
        in_grcomplex[i] = complex(_in[i])

    $action(self, in_grcomplex.cast(), out_syms_ushort, out_confidence_float, n_syms)

    out_syms = numpy.zeros(n_syms, dtype=numpy.ushort)
    out_confidence = numpy.zeros(n_syms, dtype=numpy.float)
    for i in range(0, n_syms):
        out_syms[i] = out_syms_ushort[i]
        out_confidence[i] = out_confidence_float[i]

    return (out_syms, out_confidence)
%}

namespace gr {
namespace lora2 {

class css_demod_algo
{
public:
    css_demod_algo(int M, bool upchirp=true);
    ~css_demod_algo();

    int get_M();

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

};
};

