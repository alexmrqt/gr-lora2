#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: GPL-3.0
#
##################################################
# GNU Radio Python Flow Graph
# Title: LoRa TX
# Generated: Tue Dec 11 17:55:04 2018
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
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio import iio
from gnuradio import qtgui
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from gnuradio.qtgui import Range, RangeWidget
from optparse import OptionParser
import lora2
import math
import numpy
import sip
import sys
from gnuradio import qtgui


class lora_tx(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "LoRa TX")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("LoRa TX")
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

        self.settings = Qt.QSettings("GNU Radio", "lora_tx")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())


        ##################################################
        # Variables
        ##################################################
        self.SF = SF = 9
        self.chan_bw = chan_bw = 125000
        self.M = M = 2**SF
        self.interp = interp = 2
        self.chan_margin = chan_margin = 75000
        self.chan_freq = chan_freq = 868.1e6
        self.attenuation = attenuation = 20
        self.T = T = float(M)/chan_bw
        self.RF_samp_rate = RF_samp_rate = 2304000

        ##################################################
        # Blocks
        ##################################################
        self._attenuation_range = Range(0.0, 89.75, 0.25, 20, 200)
        self._attenuation_win = RangeWidget(self._attenuation_range, self.set_attenuation, 'Attenuation', "counter_slider", float)
        self.top_grid_layout.addWidget(self._attenuation_win)
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=RF_samp_rate,
                decimation=chan_bw*interp,
                taps=None,
                fractional_bw=None,
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
        	1.0, #samp_rate
        	"Symbols", #name
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
        self.qtgui_sink_x_0 = qtgui.sink_c(
        	1024, #fftsize
        	firdes.WIN_BLACKMAN_hARRIS, #wintype
        	0, #fc
        	RF_samp_rate, #bw
        	"", #name
        	True, #plotfreq
        	True, #plotwaterfall
        	True, #plottime
        	True, #plotconst
        )
        self.qtgui_sink_x_0.set_update_time(1.0/10)
        self._qtgui_sink_x_0_win = sip.wrapinstance(self.qtgui_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_sink_x_0_win)

        self.qtgui_sink_x_0.enable_rf_freq(False)



        self.pluto_sink_0 = iio.pluto_sink('ip:192.168.3.1', int(chan_freq), RF_samp_rate, int(chan_bw + chan_margin), 0xFFFF, False, attenuation, '', True)
        self.lora2_css_mod_0 = lora2.css_mod(M, interp, "packet_len")
        self.blocks_vector_source_x_0_0_0_0 = blocks.vector_source_s([0, M/2], True, 1, [])
        self.blocks_short_to_float_0 = blocks.short_to_float(1, 1)
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf(1.0/numpy.pi)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.qtgui_time_sink_x_1, 0))
        self.connect((self.blocks_short_to_float_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.blocks_vector_source_x_0_0_0_0, 0), (self.blocks_short_to_float_0, 0))
        self.connect((self.blocks_vector_source_x_0_0_0_0, 0), (self.lora2_css_mod_0, 0))
        self.connect((self.lora2_css_mod_0, 0), (self.analog_quadrature_demod_cf_0, 0))
        self.connect((self.lora2_css_mod_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.pluto_sink_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.qtgui_sink_x_0, 0))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "lora_tx")
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
        self.qtgui_time_sink_x_1.set_samp_rate(self.chan_bw)
        self.pluto_sink_0.set_params(int(self.chan_freq), self.RF_samp_rate, int(self.chan_bw + self.chan_margin), self.attenuation, '', True)
        self.set_T(float(self.M)/self.chan_bw)

    def get_M(self):
        return self.M

    def set_M(self, M):
        self.M = M
        self.qtgui_time_sink_x_0.set_y_axis(0, self.M)
        self.blocks_vector_source_x_0_0_0_0.set_data([0, self.M/2], [])
        self.set_T(float(self.M)/self.chan_bw)

    def get_interp(self):
        return self.interp

    def set_interp(self, interp):
        self.interp = interp

    def get_chan_margin(self):
        return self.chan_margin

    def set_chan_margin(self, chan_margin):
        self.chan_margin = chan_margin
        self.pluto_sink_0.set_params(int(self.chan_freq), self.RF_samp_rate, int(self.chan_bw + self.chan_margin), self.attenuation, '', True)

    def get_chan_freq(self):
        return self.chan_freq

    def set_chan_freq(self, chan_freq):
        self.chan_freq = chan_freq
        self.pluto_sink_0.set_params(int(self.chan_freq), self.RF_samp_rate, int(self.chan_bw + self.chan_margin), self.attenuation, '', True)

    def get_attenuation(self):
        return self.attenuation

    def set_attenuation(self, attenuation):
        self.attenuation = attenuation
        self.pluto_sink_0.set_params(int(self.chan_freq), self.RF_samp_rate, int(self.chan_bw + self.chan_margin), self.attenuation, '', True)

    def get_T(self):
        return self.T

    def set_T(self, T):
        self.T = T

    def get_RF_samp_rate(self):
        return self.RF_samp_rate

    def set_RF_samp_rate(self, RF_samp_rate):
        self.RF_samp_rate = RF_samp_rate
        self.qtgui_sink_x_0.set_frequency_range(0, self.RF_samp_rate)
        self.pluto_sink_0.set_params(int(self.chan_freq), self.RF_samp_rate, int(self.chan_bw + self.chan_margin), self.attenuation, '', True)


def main(top_block_cls=lora_tx, options=None):

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
