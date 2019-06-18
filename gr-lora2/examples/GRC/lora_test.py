#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: GPL-3.0
#
##################################################
# GNU Radio Python Flow Graph
# Title: LoRa Test
# Generated: Fri Mar 15 16:25:09 2019
# GNU Radio version: 3.7.12.0
##################################################

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"

from PyQt4 import Qt
from gnuradio import analog
from gnuradio import blocks
from gnuradio import channels
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio import qtgui
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from gnuradio.qtgui import Range, RangeWidget
from optparse import OptionParser
import lora2
import numpy
import sip
import sys
from gnuradio import qtgui


class lora_test(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "LoRa Test")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("LoRa Test")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "lora_test")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())


        ##################################################
        # Variables
        ##################################################
        self.SF = SF = 9
        self.n_bytes = n_bytes = 100
        self.chan_bw = chan_bw = 125000
        self.M = M = 2**SF
        self.theta = theta = 0
        self.sig_amp = sig_amp = 1
        self.noise_amp = noise_amp = 0.4
        self.n_syms = n_syms = int(numpy.ceil((n_bytes*8.0)/SF))
        self.interp = interp = 1
        self.f_delta = f_delta = 0
        self.chan_margin = chan_margin = 75000
        self.T = T = float(M)/chan_bw
        self.RF_samp_rate = RF_samp_rate = 2304000

        ##################################################
        # Blocks
        ##################################################
        self._noise_amp_range = Range(0, 10, 0.1, 0.4, 200)
        self._noise_amp_win = RangeWidget(self._noise_amp_range, self.set_noise_amp, "noise_amp", "counter_slider", float)
        self.top_grid_layout.addWidget(self._noise_amp_win)
        self._f_delta_range = Range(-1.0, 1.0, 1.0/(4*M), 0, 200)
        self._f_delta_win = RangeWidget(self._f_delta_range, self.set_f_delta, "f_delta", "counter_slider", float)
        self.top_grid_layout.addWidget(self._f_delta_win)
        self._theta_range = Range(0, 2*numpy.pi, 0.1, 0, 200)
        self._theta_win = RangeWidget(self._theta_range, self.set_theta, "theta", "counter_slider", float)
        self.top_grid_layout.addWidget(self._theta_win)
        self._sig_amp_range = Range(0, 2, 0.1, 1, 200)
        self._sig_amp_win = RangeWidget(self._sig_amp_range, self.set_sig_amp, "sig_amp", "counter_slider", float)
        self.top_grid_layout.addWidget(self._sig_amp_win)
        self.qtgui_time_sink_x_0_0_1 = qtgui.time_sink_f(
        	2*(n_syms+8+2+2), #size
        	1.0, #samp_rate
        	"", #name
        	1 #number of inputs
        )
        self.qtgui_time_sink_x_0_0_1.set_update_time(0.10)
        self.qtgui_time_sink_x_0_0_1.set_y_axis(-M, M)

        self.qtgui_time_sink_x_0_0_1.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_0_1.enable_tags(-1, True)
        self.qtgui_time_sink_x_0_0_1.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0_0_1.enable_autoscale(False)
        self.qtgui_time_sink_x_0_0_1.enable_grid(False)
        self.qtgui_time_sink_x_0_0_1.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_0_1.enable_control_panel(True)
        self.qtgui_time_sink_x_0_0_1.enable_stem_plot(False)

        if not True:
          self.qtgui_time_sink_x_0_0_1.disable_legend()

        labels = ["Symbols", '', '', '', '',
                  '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
                  "magenta", "yellow", "dark red", "dark green", "blue"]
        styles = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        markers = [8, -1, -1, -1, -1,
                   -1, -1, -1, -1, -1]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]

        for i in xrange(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0_0_1.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0_0_1.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_0_1.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_0_1.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_0_1.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_0_1.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_0_1.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_0_1_win = sip.wrapinstance(self.qtgui_time_sink_x_0_0_1.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_0_1_win)
        self.qtgui_time_sink_x_0_0_0_0 = qtgui.time_sink_f(
        	2*(n_syms+8+2+2), #size
        	1.0, #samp_rate
        	"Time_est", #name
        	1 #number of inputs
        )
        self.qtgui_time_sink_x_0_0_0_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0_0_0_0.set_y_axis(-2.0*numpy.pi, 2.0*numpy.pi)

        self.qtgui_time_sink_x_0_0_0_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_0_0_0.enable_tags(-1, True)
        self.qtgui_time_sink_x_0_0_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0_0_0_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0_0_0_0.enable_grid(False)
        self.qtgui_time_sink_x_0_0_0_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_0_0_0.enable_control_panel(True)
        self.qtgui_time_sink_x_0_0_0_0.enable_stem_plot(False)

        if not True:
          self.qtgui_time_sink_x_0_0_0_0.disable_legend()

        labels = ["Phase est", "Phase est", '', '', '',
                  '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
                  "magenta", "yellow", "dark red", "dark green", "blue"]
        styles = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        markers = [8, -1, -1, -1, -1,
                   -1, -1, -1, -1, -1]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]

        for i in xrange(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0_0_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0_0_0_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_0_0_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_0_0_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_0_0_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_0_0_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_0_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_0_0_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0_0_0_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_0_0_0_win)
        self.qtgui_time_sink_x_0_0_0 = qtgui.time_sink_f(
        	2*(n_syms+8+2+2), #size
        	1.0, #samp_rate
        	"CFO est", #name
        	1 #number of inputs
        )
        self.qtgui_time_sink_x_0_0_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0_0_0.set_y_axis(-1.0/M, 1.0/M)

        self.qtgui_time_sink_x_0_0_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_0_0.enable_tags(-1, True)
        self.qtgui_time_sink_x_0_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0_0_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0_0_0.enable_grid(False)
        self.qtgui_time_sink_x_0_0_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_0_0.enable_control_panel(True)
        self.qtgui_time_sink_x_0_0_0.enable_stem_plot(False)

        if not True:
          self.qtgui_time_sink_x_0_0_0.disable_legend()

        labels = ["CFO est", "Phase est", '', '', '',
                  '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
                  "magenta", "yellow", "dark red", "dark green", "blue"]
        styles = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        markers = [8, -1, -1, -1, -1,
                   -1, -1, -1, -1, -1]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]

        for i in xrange(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0_0_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_0_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_0_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_0_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_0_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_0_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0_0_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_0_0_win)
        self.qtgui_time_sink_x_0_0 = qtgui.time_sink_f(
        	2*(n_syms+8+2+2)*M, #size
        	1.0, #samp_rate
        	"", #name
        	1 #number of inputs
        )
        self.qtgui_time_sink_x_0_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0_0.set_y_axis(-M, M)

        self.qtgui_time_sink_x_0_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_0.enable_tags(-1, True)
        self.qtgui_time_sink_x_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0_0.enable_grid(False)
        self.qtgui_time_sink_x_0_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_0.enable_control_panel(True)
        self.qtgui_time_sink_x_0_0.enable_stem_plot(False)

        if not True:
          self.qtgui_time_sink_x_0_0.disable_legend()

        labels = ['', '', '', '', '',
                  '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
                  "magenta", "yellow", "dark red", "dark green", "blue"]
        styles = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        markers = [8, -1, -1, -1, -1,
                   -1, -1, -1, -1, -1]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]

        for i in xrange(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_0_win)
        self.lora2_lora_preamble_detect_0_0 = lora2.lora_preamble_detect(SF, 8, thres=1e-5)
        self.lora2_lora_detect_sof_0 = lora2.lora_detect_sof(9)
        self.lora2_lora_add_reversed_chirps_0 = lora2.lora_add_reversed_chirps(SF, interp, "packet_len", "payload", "rev_chirps")
        self.lora2_lora_add_preamble_0 = lora2.lora_add_preamble(8, 0x12, "packet_len", "sync_word", "payload")
        self.lora2_gray_decode_0 = lora2.gray_decode()
        self.lora2_freq_xlating_0 = lora2.freq_xlating(0.0)
        self.lora2_css_sync_and_vectorize_0 = lora2.css_sync_and_vectorize(M)
        self.lora2_css_mod_0 = lora2.css_mod(M, interp, 'packet_len')
        self.lora2_css_demod_0 = lora2.css_demod(M, 0.1, 0.1)
        self.fractional_interpolator_xx_0 = filter.fractional_interpolator_cc(0.0, 1.0)
        self.channels_channel_model_0_0 = channels.channel_model(
        	noise_voltage=noise_amp,
        	frequency_offset=f_delta,
        	epsilon=1.0,
        	taps=(1.0 , ),
        	noise_seed=0,
        	block_tags=True
        )
        self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, M)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, chan_bw*interp,True)
        self.blocks_stream_to_tagged_stream_0 = blocks.stream_to_tagged_stream(gr.sizeof_short, 1, n_syms, 'packet_len')
        self.blocks_short_to_float_0 = blocks.short_to_float(1, 1)
        self.blocks_delay_0 = blocks.delay(gr.sizeof_gr_complex*1, 3)
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(1)
        self.analog_const_source_x_0 = analog.sig_source_s(0, analog.GR_CONST_WAVE, 0, 0, 0)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_const_source_x_0, 0), (self.blocks_stream_to_tagged_stream_0, 0))
        self.connect((self.blocks_complex_to_mag_0, 0), (self.qtgui_time_sink_x_0_0, 0))
        self.connect((self.blocks_delay_0, 0), (self.channels_channel_model_0_0, 0))
        self.connect((self.blocks_short_to_float_0, 0), (self.qtgui_time_sink_x_0_0_1, 0))
        self.connect((self.blocks_stream_to_tagged_stream_0, 0), (self.lora2_gray_decode_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.blocks_delay_0, 0))
        self.connect((self.blocks_vector_to_stream_0, 0), (self.blocks_complex_to_mag_0, 0))
        self.connect((self.channels_channel_model_0_0, 0), (self.fractional_interpolator_xx_0, 0))
        self.connect((self.fractional_interpolator_xx_0, 0), (self.lora2_lora_preamble_detect_0_0, 0))
        self.connect((self.lora2_css_demod_0, 0), (self.blocks_short_to_float_0, 0))
        self.connect((self.lora2_css_demod_0, 1), (self.blocks_vector_to_stream_0, 0))
        self.connect((self.lora2_css_demod_0, 2), (self.qtgui_time_sink_x_0_0_0, 0))
        self.connect((self.lora2_css_demod_0, 3), (self.qtgui_time_sink_x_0_0_0_0, 0))
        self.connect((self.lora2_css_mod_0, 0), (self.lora2_lora_add_reversed_chirps_0, 0))
        self.connect((self.lora2_css_sync_and_vectorize_0, 0), (self.lora2_css_demod_0, 0))
        self.connect((self.lora2_freq_xlating_0, 0), (self.lora2_css_sync_and_vectorize_0, 0))
        self.connect((self.lora2_gray_decode_0, 0), (self.lora2_lora_add_preamble_0, 0))
        self.connect((self.lora2_lora_add_preamble_0, 0), (self.lora2_css_mod_0, 0))
        self.connect((self.lora2_lora_add_reversed_chirps_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.lora2_lora_detect_sof_0, 0), (self.lora2_freq_xlating_0, 0))
        self.connect((self.lora2_lora_preamble_detect_0_0, 0), (self.lora2_lora_detect_sof_0, 0))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "lora_test")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_SF(self):
        return self.SF

    def set_SF(self, SF):
        self.SF = SF
        self.set_M(2**self.SF)
        self.set_n_syms(int(numpy.ceil((self.n_bytes*8.0)/self.SF)))

    def get_n_bytes(self):
        return self.n_bytes

    def set_n_bytes(self, n_bytes):
        self.n_bytes = n_bytes
        self.set_n_syms(int(numpy.ceil((self.n_bytes*8.0)/self.SF)))

    def get_chan_bw(self):
        return self.chan_bw

    def set_chan_bw(self, chan_bw):
        self.chan_bw = chan_bw
        self.blocks_throttle_0.set_sample_rate(self.chan_bw*self.interp)
        self.set_T(float(self.M)/self.chan_bw)

    def get_M(self):
        return self.M

    def set_M(self, M):
        self.M = M
        self.qtgui_time_sink_x_0_0_1.set_y_axis(-self.M, self.M)
        self.qtgui_time_sink_x_0_0_0.set_y_axis(-1.0/self.M, 1.0/self.M)
        self.qtgui_time_sink_x_0_0.set_y_axis(-self.M, self.M)
        self.set_T(float(self.M)/self.chan_bw)

    def get_theta(self):
        return self.theta

    def set_theta(self, theta):
        self.theta = theta

    def get_sig_amp(self):
        return self.sig_amp

    def set_sig_amp(self, sig_amp):
        self.sig_amp = sig_amp

    def get_noise_amp(self):
        return self.noise_amp

    def set_noise_amp(self, noise_amp):
        self.noise_amp = noise_amp
        self.channels_channel_model_0_0.set_noise_voltage(self.noise_amp)

    def get_n_syms(self):
        return self.n_syms

    def set_n_syms(self, n_syms):
        self.n_syms = n_syms
        self.blocks_stream_to_tagged_stream_0.set_packet_len(self.n_syms)
        self.blocks_stream_to_tagged_stream_0.set_packet_len_pmt(self.n_syms)

    def get_interp(self):
        return self.interp

    def set_interp(self, interp):
        self.interp = interp
        self.blocks_throttle_0.set_sample_rate(self.chan_bw*self.interp)

    def get_f_delta(self):
        return self.f_delta

    def set_f_delta(self, f_delta):
        self.f_delta = f_delta
        self.channels_channel_model_0_0.set_frequency_offset(self.f_delta)

    def get_chan_margin(self):
        return self.chan_margin

    def set_chan_margin(self, chan_margin):
        self.chan_margin = chan_margin

    def get_T(self):
        return self.T

    def set_T(self, T):
        self.T = T

    def get_RF_samp_rate(self):
        return self.RF_samp_rate

    def set_RF_samp_rate(self, RF_samp_rate):
        self.RF_samp_rate = RF_samp_rate


def main(top_block_cls=lora_test, options=None):

    from distutils.version import StrictVersion
    if StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()
    tb.start()
    tb.show()

    def quitting():
        tb.stop()
        tb.wait()
    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    qapp.exec_()


if __name__ == '__main__':
    main()
