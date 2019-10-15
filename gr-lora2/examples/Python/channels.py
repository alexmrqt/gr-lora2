import numpy
from gnuradio import gr
from gnuradio import analog, blocks, channels, filter
from lora2 import tag_delay

class awgn(gr.hier_block2):
    """
    A block that adds a complex-circular random Additive White Gaussian Noise.

    param noisevar: the variance of the noise
    """
    def __init__(self, noisevar):
        gr.hier_block2.__init__(
            self, "AWNG channel",
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1))

        ##################################################
        # Variables
        ##################################################

        self.noisevar = noisevar

        ##################################################
        # Blocks
        ##################################################

        self.noise_src = analog.noise_source_c(analog.GR_GAUSSIAN,
                self.noisevar, numpy.random.randint(65535))
        self.noise_adder = blocks.add_vcc(1)

        ##################################################
        # Connections
        ##################################################

        self.connect((self, 0), (self.noise_adder, 0))
        self.connect((self.noise_src, 0), (self.noise_adder, 1))
        self.connect((self.noise_adder, 0), (self, 0))

    def set_noisevar(self, noisevar):
        self.noise_src.set_amplitude(noisevar)

class basic_t_sel(gr.hier_block2):
    """
    A block that adds a basic time-selective channel.
    It performs the following operation:
        r[k] = s[k] * [cos(2*pi*k/M) + 1.0] for k in [0 ; M-1],
    and normalizes the power, on blocks of M samples.

    param M: the length of the channel.
    """
    def __init__(self, M):
        gr.hier_block2.__init__(
            self, "Basic time-selective channel",
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1))

        ##################################################
        # Variables
        ##################################################

        time_sel = numpy.cos(2*numpy.pi*numpy.arange(0,M)/M) + 1.0
        time_sel /= numpy.mean(numpy.abs(time_sel)**2)

        ##################################################
        # Blocks
        ##################################################

        self.gen = blocks.vector_source_c(time_sel, True)
        self.mult = blocks.multiply_cc()

        ##################################################
        # Connections
        ##################################################

        self.connect((self, 0), (self.mult, 0))
        self.connect((self.gen, 0), (self.mult, 1))
        self.connect((self.mult, 0), (self, 0))

class proakis_b(gr.hier_block2):
    """
    A block that adds the frequency-selective channel described in chapter 9.4
    of Proakis, J. & Salehi, M. Digital Communications McGraw-Hill, 2008.
    It performs the following operation:
        r[k] = (0.407.z^{-1} + 0.815 + 0.407.z).s[k], forall k in Z,
    where z^{-1} represents a delay of 1 sample.
    """
    def __init__(self):
        gr.hier_block2.__init__(
            self, "Basic time-selective channel",
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1))

        ##################################################
        # Blocks
        ##################################################

        self.chan = filter.fir_filter_ccf(1, [0.407, 0.815, 0.407])
        self.delay = blocks.skiphead(gr.sizeof_gr_complex, 1)
        self.tag_delay = tag_delay(1)

        ##################################################
        # Connections
        ##################################################

        self.connect((self, 0), (self.chan, 0))
        self.connect((self.chan, 0), (self.tag_delay, 0))
        self.connect((self.tag_delay, 0), (self.delay, 0))
        self.connect((self.delay, 0), (self, 0))

class itu_outdoor_indoor_ped(gr.hier_block2):
    """
    A block that adds an ITU Channel Model for Outdoor to Indoor and Pedestrian
    Test Environment, as described in the recommendation ITU-R M.1225.
    Profile A corresponds to a low delay spread.
    Profile B corresponds to a medium delay spread.

    param max_doppler: Maximum Doppler shift, in Hz.
    param bw: Bandwidth of the signal, in Hz.
    param AB: Profile A if True, profile B otherwise.
    """
    def __init__(self, max_doppler, bw, AB):
        gr.hier_block2.__init__(
            self, "ITU outdoor to indoor/pedestrian channel",
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1))

        ##################################################
        # Variables
        ##################################################

        seed = numpy.random.randint(65535)
        ntaps = 16
        if AB:
            delays = numpy.array([0.0, 110.0, 190.0, 410.0]) #in ns
            mags = numpy.array([0.0, -9.7, -19.2, -22.8]) #in dB
        else:
            delays = numpy.array([0.0, 200.0, 800.0, 1200.0, 2300.0, 3700.0]) #in ns
            mags = numpy.array([0.0, -0.9, -4.9, -8.0, -7.8, -23.9]) #in dB

        #Mags from dB to natural
        mags = numpy.power(10.0, mags/10.0)
        #Delay from ns to normalized delay
        delays *= 10**(-9) * bw

        ##################################################
        # Blocks
        ##################################################

        self.chan = channels.selective_fading_model(8, max_doppler/float(bw),
                False, 4, seed, delays, mags, ntaps)

        ##################################################
        # Connections
        ##################################################

        self.connect((self, 0), (self.chan, 0), (self, 0))
        #self.connect((self, 0), (self.chan, 0))
        #self.connect((self.chan, 0), (self.delay, 0))
        #self.connect((self.delay, 0), (self, 0))
