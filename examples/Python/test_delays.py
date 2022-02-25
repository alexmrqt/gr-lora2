from gnuradio import blocks
from gnuradio import gr

import pmt
import numpy
from matplotlib import pyplot as plt

import channels

class test_delays(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self, "test delays")

        max_doppler = 10.0
        bw = 125e3
        AB = True

        n_samples = 50
        self.sig = numpy.random.randn(n_samples)

        tag = gr.tag_t()
        tag.key = pmt.to_pmt('start')
        tag.value = pmt.to_pmt(0)

        self.gen = blocks.vector_source_c(self.sig, False, 1, [tag])
        self.chan = channels.itu_outdoor_indoor_ped(max_doppler, bw, AB)
        self.sink = blocks.vector_sink_c()
        self.tag_sink = blocks.tag_debug(gr.sizeof_gr_complex, 'tag_sink')

        self.connect((self.gen, 0), (self.chan, 0))
        self.connect((self.chan, 0), (self.sink, 0))
        self.connect((self.chan, 0), (self.tag_sink, 0))

if __name__ == '__main__':
    tb = test_delays()
    tb.run()
    tb.wait()

    em_sig = tb.sig
    rcvd_sig = tb.sink.data()

    plt.plot(numpy.real(em_sig))
    plt.plot(numpy.real(rcvd_sig))

    plt.show()
