#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: GPL-3.0
#
##################################################
# GNU Radio Python Flow Graph
# Title: LoRa RX
# Generated: Tue Dec 11 17:38:25 2018
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
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio import iio
from gnuradio import qtgui
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from gnuradio.qtgui import Range, RangeWidget
from grc_css_demod import grc_css_demod  # grc-generated hier_block
from optparse import OptionParser
import math
import numpy
import sip
from gnuradio import qtgui


class lora_rx(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "LoRa RX")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("LoRa RX")
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

        self.settings = Qt.QSettings("GNU Radio", "lora_rx")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())


        ##################################################
        # Variables
        ##################################################
        self.SF = SF = 9
        self.chan_bw = chan_bw = 125000
        self.M = M = 2**SF
        self.samp_rate = samp_rate = chan_bw
        self.n_syms = n_syms = 10
        self.freq_offset = freq_offset = 4*chan_bw
        self.coarse_freq_adjust = coarse_freq_adjust = -250
        self.chan_margin = chan_margin = 75000
        self.chan_freq = chan_freq = 868.1e6
        self.attenuation = attenuation = 20
        self.T = T = float(M)/chan_bw
        self.RF_samp_rate = RF_samp_rate = 2304000

        ##################################################
        # Blocks
        ##################################################
        self._coarse_freq_adjust_range = Range(-RF_samp_rate/2, RF_samp_rate/2, 2.0, -250, 200)
        self._coarse_freq_adjust_win = RangeWidget(self._coarse_freq_adjust_range, self.set_coarse_freq_adjust, "coarse_freq_adjust", "counter_slider", float)
        self.top_grid_layout.addWidget(self._coarse_freq_adjust_win)
        self._attenuation_range = Range(0.0, 89.75, 0.25, 20, 200)
        self._attenuation_win = RangeWidget(self._attenuation_range, self.set_attenuation, 'Attenuation', "counter_slider", float)
        self.top_grid_layout.addWidget(self._attenuation_win)
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=chan_bw,
                decimation=int(RF_samp_rate),
                taps=None,
                fractional_bw=0.47,
        )
        self.qtgui_time_sink_x_1 = qtgui.time_sink_f(
        	40*M, #size
        	chan_bw, #samp_rate
        	"Frequency of modulated signal", #name
        	1 #number of inputs
        )
        self.qtgui_time_sink_x_1.set_update_time(0.10)
        self.qtgui_time_sink_x_1.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_1.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_1.enable_tags(-1, True)
        self.qtgui_time_sink_x_1.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_1.enable_autoscale(False)
        self.qtgui_time_sink_x_1.enable_grid(False)
        self.qtgui_time_sink_x_1.enable_axis_labels(True)
        self.qtgui_time_sink_x_1.enable_control_panel(True)
        self.qtgui_time_sink_x_1.enable_stem_plot(False)

        if not True:
          self.qtgui_time_sink_x_1.disable_legend()

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

        for i in xrange(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_1.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_1.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_1.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_1.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_1.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_1.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_1.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_1_win = sip.wrapinstance(self.qtgui_time_sink_x_1.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_1_win)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
        	128, #size
        	samp_rate, #samp_rate
        	"Demodulated symbols", #name
        	1 #number of inputs
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(0, M)

        self.qtgui_time_sink_x_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0.enable_tags(-1, True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0.enable_grid(False)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(True)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)

        if not True:
          self.qtgui_time_sink_x_0.disable_legend()

        labels = ["Non-coherent", "Coherent", '', '', '',
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

        for i in xrange(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_win)
        self.pluto_source_0 = iio.pluto_source('ip:192.168.2.1', int(chan_freq + freq_offset), RF_samp_rate, int(chan_bw + chan_margin), 0xFFFFF, True, True, True, "manual", attenuation, '', True)
        self.grc_css_demod_0 = grc_css_demod(
            M=M,
        )
        self.freq_xlating_fir_filter_xxx_0 = filter.freq_xlating_fir_filter_ccc(1, (1, ), -freq_offset+coarse_freq_adjust, RF_samp_rate)
        self.blocks_short_to_float_0 = blocks.short_to_float(1, 1)
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf(1.0/numpy.pi)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.qtgui_time_sink_x_1, 0))
        self.connect((self.blocks_short_to_float_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.grc_css_demod_0, 0), (self.blocks_short_to_float_0, 0))
        self.connect((self.pluto_source_0, 0), (self.freq_xlating_fir_filter_xxx_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.analog_quadrature_demod_cf_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.grc_css_demod_0, 0))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "lora_rx")
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
        self.set_freq_offset(4*self.chan_bw)
        self.qtgui_time_sink_x_1.set_samp_rate(self.chan_bw)
        self.pluto_source_0.set_params(int(self.chan_freq + self.freq_offset), self.RF_samp_rate, int(self.chan_bw + self.chan_margin), True, True, True, "manual", self.attenuation, '', True)
        self.set_T(float(self.M)/self.chan_bw)

    def get_M(self):
        return self.M

    def set_M(self, M):
        self.M = M
        self.qtgui_time_sink_x_0.set_y_axis(0, self.M)
        self.grc_css_demod_0.set_M(self.M)
        self.set_T(float(self.M)/self.chan_bw)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.qtgui_time_sink_x_0.set_samp_rate(self.samp_rate)

    def get_n_syms(self):
        return self.n_syms

    def set_n_syms(self, n_syms):
        self.n_syms = n_syms

    def get_freq_offset(self):
        return self.freq_offset

    def set_freq_offset(self, freq_offset):
        self.freq_offset = freq_offset
        self.pluto_source_0.set_params(int(self.chan_freq + self.freq_offset), self.RF_samp_rate, int(self.chan_bw + self.chan_margin), True, True, True, "manual", self.attenuation, '', True)
        self.freq_xlating_fir_filter_xxx_0.set_center_freq(-self.freq_offset+self.coarse_freq_adjust)

    def get_coarse_freq_adjust(self):
        return self.coarse_freq_adjust

    def set_coarse_freq_adjust(self, coarse_freq_adjust):
        self.coarse_freq_adjust = coarse_freq_adjust
        self.freq_xlating_fir_filter_xxx_0.set_center_freq(-self.freq_offset+self.coarse_freq_adjust)

    def get_chan_margin(self):
        return self.chan_margin

    def set_chan_margin(self, chan_margin):
        self.chan_margin = chan_margin
        self.pluto_source_0.set_params(int(self.chan_freq + self.freq_offset), self.RF_samp_rate, int(self.chan_bw + self.chan_margin), True, True, True, "manual", self.attenuation, '', True)

    def get_chan_freq(self):
        return self.chan_freq

    def set_chan_freq(self, chan_freq):
        self.chan_freq = chan_freq
        self.pluto_source_0.set_params(int(self.chan_freq + self.freq_offset), self.RF_samp_rate, int(self.chan_bw + self.chan_margin), True, True, True, "manual", self.attenuation, '', True)

    def get_attenuation(self):
        return self.attenuation

    def set_attenuation(self, attenuation):
        self.attenuation = attenuation
        self.pluto_source_0.set_params(int(self.chan_freq + self.freq_offset), self.RF_samp_rate, int(self.chan_bw + self.chan_margin), True, True, True, "manual", self.attenuation, '', True)

    def get_T(self):
        return self.T

    def set_T(self, T):
        self.T = T

    def get_RF_samp_rate(self):
        return self.RF_samp_rate

    def set_RF_samp_rate(self, RF_samp_rate):
        self.RF_samp_rate = RF_samp_rate
        self.pluto_source_0.set_params(int(self.chan_freq + self.freq_offset), self.RF_samp_rate, int(self.chan_bw + self.chan_margin), True, True, True, "manual", self.attenuation, '', True)


def main(top_block_cls=lora_rx, options=None):

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
