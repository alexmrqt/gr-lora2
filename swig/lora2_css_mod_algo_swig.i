/* -*- c++ -*- */

#define LORA2_API

%include "carrays.i"
%include "gnuradio.i"

//load generated python docstrings
%include "lora2_swig_doc.i"

%{
#include "lora2/css_mod_algo.h"
%}

%array_class(unsigned short, ushortArray);
%array_class(gr_complex, grcomplexArray);

%feature("shadow") modulate %{
def modulate(*args):
    import numpy

    assert len(args) == 2

    self = args[0]
    _in = args[1]

    assert isinstance(_in, numpy.ndarray), "Input must be a Numpy Array of unsigned shorts."
    assert _in.dtype == numpy.ushort, "Input must be a Numpy Array of unsigned shorts."

    n_syms = len(_in)
    out_len = n_syms*self.get_M()*self.get_interp()

    in_ushort = ushortArray(n_syms)
    out_grcomplex = grcomplexArray(out_len)

    for i in range(0, n_syms):
        in_ushort[i] = _in[i]

    $action(self, in_ushort, out_grcomplex.cast(), n_syms)

    out = numpy.zeros(out_len, dtype=numpy.complex64)
    for i in range(0, out_len):
        out[i] = out_grcomplex[i]

    return out
%}

namespace gr {
namespace lora2 {

class css_mod_algo
{
public:
    css_mod_algo(int M, int interp=1, bool upchirp=true);
    int get_M();
    int get_interp();
    void modulate(const unsigned short * _in, gr_complex * out, size_t n_syms);
};

};
};
