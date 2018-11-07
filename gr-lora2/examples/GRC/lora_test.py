#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: GPL-3.0
#
##################################################
# GNU Radio Python Flow Graph
# Title: LoRa Test
# Generated: Wed Nov  7 10:59:22 2018
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

import os
import sys
sys.path.append(os.environ.get('GRC_HIER_PATH', os.path.expanduser('~/.grc_gnuradio')))

from PyQt4 import Qt
from gnuradio import analog
from gnuradio import blocks
from gnuradio import channels
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import qtgui
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from gnuradio.qtgui import Range, RangeWidget
from grc_lora_add_preamble import grc_lora_add_preamble  # grc-generated hier_block
from optparse import OptionParser
import lora2
import math
import numpy
import sip
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
        self.chan_bw = chan_bw = 125000
        self.M = M = 2**SF
        self.theta = theta = 0
        self.sig_amp = sig_amp = 0
        self.samp_rate = samp_rate = chan_bw
        self.noise_amp = noise_amp = 0
        self.f_delta = f_delta = 0
        self.T = T = float(M)/chan_bw

        ##################################################
        # Blocks
        ##################################################
        self._theta_range = Range(0, 2*numpy.pi, 0.1, 0, 200)
        self._theta_win = RangeWidget(self._theta_range, self.set_theta, "theta", "counter_slider", float)
        self.top_grid_layout.addWidget(self._theta_win)
        self._sig_amp_range = Range(0, 2, 0.1, 0, 200)
        self._sig_amp_win = RangeWidget(self._sig_amp_range, self.set_sig_amp, "sig_amp", "counter_slider", float)
        self.top_grid_layout.addWidget(self._sig_amp_win)
        self._noise_amp_range = Range(0, 10, 0.1, 0, 200)
        self._noise_amp_win = RangeWidget(self._noise_amp_range, self.set_noise_amp, "noise_amp", "counter_slider", float)
        self.top_grid_layout.addWidget(self._noise_amp_win)
        self._f_delta_range = Range(-samp_rate/2, samp_rate/2, 1, 0, 200)
        self._f_delta_win = RangeWidget(self._f_delta_range, self.set_f_delta, "f_delta", "counter_slider", float)
        self.top_grid_layout.addWidget(self._f_delta_win)
        self.qtgui_time_sink_x_2 = qtgui.time_sink_c(
        	40*M, #size
        	1.0, #samp_rate
        	"", #name
        	2 #number of inputs
        )
        self.qtgui_time_sink_x_2.set_update_time(0.10)
        self.qtgui_time_sink_x_2.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_2.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_2.enable_tags(-1, True)
        self.qtgui_time_sink_x_2.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_2.enable_autoscale(False)
        self.qtgui_time_sink_x_2.enable_grid(False)
        self.qtgui_time_sink_x_2.enable_axis_labels(True)
        self.qtgui_time_sink_x_2.enable_control_panel(True)
        self.qtgui_time_sink_x_2.enable_stem_plot(False)

        if not True:
          self.qtgui_time_sink_x_2.disable_legend()

        labels = ['', '', '', '', '',
                  '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
                  "magenta", "yellow", "dark red", "dark green", "blue"]
        styles = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
                   -1, -1, -1, -1, -1]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]

        for i in xrange(4):
            if len(labels[i]) == 0:
                if(i % 2 == 0):
                    self.qtgui_time_sink_x_2.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_2.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_2.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_2.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_2.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_2.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_2.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_2.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_2_win = sip.wrapinstance(self.qtgui_time_sink_x_2.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_2_win)
        self.lora2_lora_preamble_detect_0 = lora2.lora_preamble_detect(9, 8, 0x12, 0.9)
        self.lora2_css_mod_0 = lora2.css_mod(M)
        self.grc_lora_add_preamble_0 = grc_lora_add_preamble(
            SF=9,
            preamble_len=8,
            sync_word=0x12,
        )
        self.channels_channel_model_0_0 = channels.channel_model(
        	noise_voltage=noise_amp,
        	frequency_offset=f_delta,
        	epsilon=(1.0+1e-7),
        	taps=(1.0 , ),
        	noise_seed=0,
        	block_tags=False
        )
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_tag_gate_0 = blocks.tag_gate(gr.sizeof_gr_complex * 1, False)
        self.blocks_tag_gate_0.set_single_key("")
        self.blocks_stream_to_tagged_stream_0 = blocks.stream_to_tagged_stream(gr.sizeof_gr_complex, 1, 10*M, 'packet_len')
        self.blocks_multiply_const_vxx_1 = blocks.multiply_const_vcc((sig_amp, ))
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vcc((numpy.exp(1j*theta), ))
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.blocks_delay_0_0 = blocks.delay(gr.sizeof_gr_complex*1, 3)
        self.analog_random_source_x_0 = blocks.vector_source_s(map(int, numpy.random.randint(0, M-1, 1000)), True)
        self.analog_quadrature_demod_cf_0_0 = analog.quadrature_demod_cf(1.0)
        self.analog_agc_xx_0 = analog.agc_cc(1e-4, 1.0, 1.0)
        self.analog_agc_xx_0.set_max_gain(65536)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_agc_xx_0, 0), (self.lora2_lora_preamble_detect_0, 0))
        self.connect((self.analog_quadrature_demod_cf_0_0, 0), (self.blocks_float_to_complex_0, 0))
        self.connect((self.analog_random_source_x_0, 0), (self.lora2_css_mod_0, 0))
        self.connect((self.blocks_delay_0_0, 0), (self.blocks_multiply_const_vxx_1, 0))
        self.connect((self.blocks_float_to_complex_0, 0), (self.qtgui_time_sink_x_2, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.channels_channel_model_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_1, 0), (self.analog_agc_xx_0, 0))
        self.connect((self.blocks_stream_to_tagged_stream_0, 0), (self.grc_lora_add_preamble_0, 0))
        self.connect((self.blocks_tag_gate_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.blocks_tag_gate_0, 0))
        self.connect((self.channels_channel_model_0_0, 0), (self.blocks_delay_0_0, 0))
        self.connect((self.grc_lora_add_preamble_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.lora2_css_mod_0, 0), (self.blocks_stream_to_tagged_stream_0, 0))
        self.connect((self.lora2_lora_preamble_detect_0, 0), (self.analog_quadrature_demod_cf_0_0, 0))
        self.connect((self.lora2_lora_preamble_detect_0, 1), (self.qtgui_time_sink_x_2, 1))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "lora_test")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_SF(self):
        return self.SF

    def set_SF(self, SF):
        self.SF = SF
        self.set_M(2**self.SF)

    def get_chan_bw(self):
        return self.chan_bw

    def set_chan_bw(self, chan_bw):
        self.chan_bw = chan_bw
        self.set_samp_rate(self.chan_bw)
        self.set_T(float(self.M)/self.chan_bw)

    def get_M(self):
        return self.M

    def set_M(self, M):
        self.M = M
        self.blocks_stream_to_tagged_stream_0.set_packet_len(10*self.M)
        self.blocks_stream_to_tagged_stream_0.set_packet_len_pmt(10*self.M)
        self.set_T(float(self.M)/self.chan_bw)

    def get_theta(self):
        return self.theta

    def set_theta(self, theta):
        self.theta = theta
        self.blocks_multiply_const_vxx_0.set_k((numpy.exp(1j*self.theta), ))

    def get_sig_amp(self):
        return self.sig_amp

    def set_sig_amp(self, sig_amp):
        self.sig_amp = sig_amp
        self.blocks_multiply_const_vxx_1.set_k((self.sig_amp, ))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)

    def get_noise_amp(self):
        return self.noise_amp

    def set_noise_amp(self, noise_amp):
        self.noise_amp = noise_amp
        self.channels_channel_model_0_0.set_noise_voltage(self.noise_amp)

    def get_f_delta(self):
        return self.f_delta

    def set_f_delta(self, f_delta):
        self.f_delta = f_delta
        self.channels_channel_model_0_0.set_frequency_offset(self.f_delta)

    def get_T(self):
        return self.T

    def set_T(self, T):
        self.T = T


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
