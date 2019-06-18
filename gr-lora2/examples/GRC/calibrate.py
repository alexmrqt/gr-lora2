#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: GPL-3.0
#
##################################################
# GNU Radio Python Flow Graph
# Title: Calibrate
# Generated: Tue Dec 11 16:52:48 2018
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
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio import iio
from gnuradio import qtgui
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from gnuradio.qtgui import Range, RangeWidget
from optparse import OptionParser
import sip
import sys
from gnuradio import qtgui


class calibrate(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Calibrate")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Calibrate")
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

        self.settings = Qt.QSettings("GNU Radio", "calibrate")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())


        ##################################################
        # Variables
        ##################################################
        self.pluto_samp_rate = pluto_samp_rate = 2304000
        self.chan_margin = chan_margin = 75000
        self.chan_bw = chan_bw = 125000
        self.freq_offset = freq_offset = 4*chan_bw
        self.coarse_freq_adjust = coarse_freq_adjust = 0

        self.channel_filter_taps = channel_filter_taps = firdes.low_pass(1.0, pluto_samp_rate, chan_bw, chan_margin/2, firdes.WIN_HAMMING, 6.76)

        self.chan_freq = chan_freq = 868.1e6
        self.attenuation = attenuation = 20

        ##################################################
        # Blocks
        ##################################################
        self._coarse_freq_adjust_range = Range(-pluto_samp_rate/2, pluto_samp_rate/2, 2.0, 0, 200)
        self._coarse_freq_adjust_win = RangeWidget(self._coarse_freq_adjust_range, self.set_coarse_freq_adjust, "coarse_freq_adjust", "counter_slider", float)
        self.top_grid_layout.addWidget(self._coarse_freq_adjust_win)
        self._attenuation_range = Range(0.0, 89.75, 0.25, 20, 200)
        self._attenuation_win = RangeWidget(self._attenuation_range, self.set_attenuation, 'Attenuation', "counter_slider", float)
        self.top_grid_layout.addWidget(self._attenuation_win)
        self.qtgui_sink_x_0 = qtgui.sink_c(
        	16384, #fftsize
        	firdes.WIN_BLACKMAN_hARRIS, #wintype
        	0, #fc
        	pluto_samp_rate, #bw
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



        self.pluto_source_0 = iio.pluto_source('ip:192.168.2.1', int(chan_freq + freq_offset), pluto_samp_rate, int(chan_bw + chan_margin), 0x8000, True, True, True, "manual", attenuation, '', True)
        self.pluto_sink_0_0 = iio.pluto_sink('ip:192.168.3.1', int(chan_freq), pluto_samp_rate, int(chan_bw + chan_margin), 0x8000, False, attenuation, '', True)
        self.freq_xlating_fir_filter_xxx_0 = filter.freq_xlating_fir_filter_ccc(1, (channel_filter_taps), -freq_offset+coarse_freq_adjust, pluto_samp_rate)
        self.analog_const_source_x_0 = analog.sig_source_c(0, analog.GR_CONST_WAVE, 0, 0, 1.0)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_const_source_x_0, 0), (self.pluto_sink_0_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.qtgui_sink_x_0, 0))
        self.connect((self.pluto_source_0, 0), (self.freq_xlating_fir_filter_xxx_0, 0))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "calibrate")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_pluto_samp_rate(self):
        return self.pluto_samp_rate

    def set_pluto_samp_rate(self, pluto_samp_rate):
        self.pluto_samp_rate = pluto_samp_rate
        self.qtgui_sink_x_0.set_frequency_range(0, self.pluto_samp_rate)
        self.pluto_source_0.set_params(int(self.chan_freq + self.freq_offset), self.pluto_samp_rate, int(self.chan_bw + self.chan_margin), True, True, True, "manual", self.attenuation, '', True)
        self.pluto_sink_0_0.set_params(int(self.chan_freq), self.pluto_samp_rate, int(self.chan_bw + self.chan_margin), self.attenuation, '', True)

    def get_chan_margin(self):
        return self.chan_margin

    def set_chan_margin(self, chan_margin):
        self.chan_margin = chan_margin
        self.pluto_source_0.set_params(int(self.chan_freq + self.freq_offset), self.pluto_samp_rate, int(self.chan_bw + self.chan_margin), True, True, True, "manual", self.attenuation, '', True)
        self.pluto_sink_0_0.set_params(int(self.chan_freq), self.pluto_samp_rate, int(self.chan_bw + self.chan_margin), self.attenuation, '', True)

    def get_chan_bw(self):
        return self.chan_bw

    def set_chan_bw(self, chan_bw):
        self.chan_bw = chan_bw
        self.set_freq_offset(4*self.chan_bw)
        self.pluto_source_0.set_params(int(self.chan_freq + self.freq_offset), self.pluto_samp_rate, int(self.chan_bw + self.chan_margin), True, True, True, "manual", self.attenuation, '', True)
        self.pluto_sink_0_0.set_params(int(self.chan_freq), self.pluto_samp_rate, int(self.chan_bw + self.chan_margin), self.attenuation, '', True)

    def get_freq_offset(self):
        return self.freq_offset

    def set_freq_offset(self, freq_offset):
        self.freq_offset = freq_offset
        self.pluto_source_0.set_params(int(self.chan_freq + self.freq_offset), self.pluto_samp_rate, int(self.chan_bw + self.chan_margin), True, True, True, "manual", self.attenuation, '', True)
        self.freq_xlating_fir_filter_xxx_0.set_center_freq(-self.freq_offset+self.coarse_freq_adjust)

    def get_coarse_freq_adjust(self):
        return self.coarse_freq_adjust

    def set_coarse_freq_adjust(self, coarse_freq_adjust):
        self.coarse_freq_adjust = coarse_freq_adjust
        self.freq_xlating_fir_filter_xxx_0.set_center_freq(-self.freq_offset+self.coarse_freq_adjust)

    def get_channel_filter_taps(self):
        return self.channel_filter_taps

    def set_channel_filter_taps(self, channel_filter_taps):
        self.channel_filter_taps = channel_filter_taps
        self.freq_xlating_fir_filter_xxx_0.set_taps((self.channel_filter_taps))

    def get_chan_freq(self):
        return self.chan_freq

    def set_chan_freq(self, chan_freq):
        self.chan_freq = chan_freq
        self.pluto_source_0.set_params(int(self.chan_freq + self.freq_offset), self.pluto_samp_rate, int(self.chan_bw + self.chan_margin), True, True, True, "manual", self.attenuation, '', True)
        self.pluto_sink_0_0.set_params(int(self.chan_freq), self.pluto_samp_rate, int(self.chan_bw + self.chan_margin), self.attenuation, '', True)

    def get_attenuation(self):
        return self.attenuation

    def set_attenuation(self, attenuation):
        self.attenuation = attenuation
        self.pluto_source_0.set_params(int(self.chan_freq + self.freq_offset), self.pluto_samp_rate, int(self.chan_bw + self.chan_margin), True, True, True, "manual", self.attenuation, '', True)
        self.pluto_sink_0_0.set_params(int(self.chan_freq), self.pluto_samp_rate, int(self.chan_bw + self.chan_margin), self.attenuation, '', True)


def main(top_block_cls=calibrate, options=None):

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
