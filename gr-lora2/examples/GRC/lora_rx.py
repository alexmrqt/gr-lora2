#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: GPL-3.0
#
##################################################
# GNU Radio Python Flow Graph
# Title: LoRa RX
# Generated: Mon Mar 25 19:06:39 2019
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
from gnuradio import blocks
from gnuradio import digital
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
import pmt
import sip
import sys
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
        self.interp = interp = 2
        self.freq_offset = freq_offset = 6*chan_bw
        self.chan_margin = chan_margin = 75000
        self.chan_freq = chan_freq = 868e6
        self.attenuation = attenuation = 20
        self.T = T = float(M)/chan_bw
        self.RF_samp_rate = RF_samp_rate = int(8e6)
        self.CR = CR = 4

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=chan_bw*interp,
                decimation=int(RF_samp_rate),
                taps=None,
                fractional_bw=None,
        )
        self.qtgui_time_sink_x_0_0 = qtgui.time_sink_f(
        	8*(n_syms+8+2+2)*M, #size
        	1.0, #samp_rate
        	"", #name
        	3 #number of inputs
        )
        self.qtgui_time_sink_x_0_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0_0.set_y_axis(0, M)

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

        labels = ['', "Freq", "Time", '', '',
                  '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
                  "magenta", "yellow", "dark red", "dark green", "blue"]
        styles = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        markers = [8, 8, -1, -1, -1,
                   -1, -1, -1, -1, -1]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]

        for i in xrange(3):
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
        self.low_pass_filter_0 = filter.fir_filter_ccf(interp, firdes.low_pass(
        	1, chan_bw*interp, (chan_bw + chan_margin)/2, (chan_bw + chan_margin)/8, firdes.WIN_HAMMING, 6.76))
        self.lora2_lora_whiten_0 = lora2.lora_whiten(4, 'packet_len_bits')
        self.lora2_lora_preamble_detect_0_0 = lora2.lora_preamble_detect(SF, 8, thres=1e-4)
        self.lora2_lora_merge_rem_0 = lora2.lora_merge_rem(SF, 'packet_len_bits')
        self.lora2_lora_low_rate_opt_rx_0 = lora2.lora_low_rate_opt_rx()
        self.lora2_lora_header_decode_0 = lora2.lora_header_decode(SF, True)
        self.lora2_lora_hamming_decode_0 = lora2.lora_hamming_decode(4, '')
        self.lora2_lora_detect_sof_0 = lora2.lora_detect_sof(9)
        self.lora2_lora_depad_0 = lora2.lora_depad('packet_len_bits', 0)
        self.lora2_lora_deinterleaver_0_0 = lora2.lora_deinterleaver(SF, CR, False)
        self.lora2_lora_deinterleaver_0 = lora2.lora_deinterleaver(SF, 4, True)
        self.lora2_gray_encode_0_0 = lora2.gray_encode()
        self.lora2_gray_encode_0 = lora2.gray_encode()
        self.lora2_freq_xlating_0 = lora2.freq_xlating(0.0)
        self.lora2_css_sync_and_vectorize_0 = lora2.css_sync_and_vectorize(M)
        self.lora2_css_demod_0 = lora2.css_demod(M, 0.1, 0.05)
        self.freq_xlating_fir_filter_xxx_0 = filter.freq_xlating_fir_filter_ccc(1, (1, ), -freq_offset, RF_samp_rate)
        self.digital_header_payload_demux_0 = digital.header_payload_demux(
        	  8,
        	  1,
        	  0,
        	  "packet_len_syms",
        	  "pkt_start",
        	  False,
        	  gr.sizeof_short,
        	  '',
                  samp_rate,
                  (),
                  0,
            )
        self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, M)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_tagged_stream_to_pdu_0 = blocks.tagged_stream_to_pdu(blocks.byte_t, 'packet_len_bits')
        self.blocks_tag_debug_0_0 = blocks.tag_debug(gr.sizeof_gr_complex*1, 'Preamble detect', ""); self.blocks_tag_debug_0_0.set_display(True)
        self.blocks_repeat_0_0 = blocks.repeat(gr.sizeof_float*1, M)
        self.blocks_repeat_0 = blocks.repeat(gr.sizeof_float*1, M)
        self.blocks_repack_bits_bb_0 = blocks.repack_bits_bb(1, 8, 'packet_len_bits', False, gr.GR_MSB_FIRST)
        self.blocks_message_debug_0 = blocks.message_debug()
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_gr_complex*1, '/home/amarquet/Documents/postdoc-imt/projets-S5/2018/sdr/emetteur-recepteur-lora-sdr/scripts/zeros.raw', True)
        self.blocks_file_source_0.set_begin_tag(pmt.PMT_NIL)
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(1)
        self._attenuation_range = Range(0.0, 89.75, 0.25, 20, 200)
        self._attenuation_win = RangeWidget(self._attenuation_range, self.set_attenuation, 'Attenuation', "counter_slider", float)
        self.top_grid_layout.addWidget(self._attenuation_win)



        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_tagged_stream_to_pdu_0, 'pdus'), (self.blocks_message_debug_0, 'print_pdu'))
        self.msg_connect((self.lora2_lora_header_decode_0, 'hdr'), (self.digital_header_payload_demux_0, 'header_data'))
        self.connect((self.blocks_complex_to_mag_0, 0), (self.qtgui_time_sink_x_0_0, 0))
        self.connect((self.blocks_file_source_0, 0), (self.freq_xlating_fir_filter_xxx_0, 0))
        self.connect((self.blocks_repack_bits_bb_0, 0), (self.blocks_tagged_stream_to_pdu_0, 0))
        self.connect((self.blocks_repeat_0, 0), (self.qtgui_time_sink_x_0_0, 1))
        self.connect((self.blocks_repeat_0_0, 0), (self.qtgui_time_sink_x_0_0, 2))
        self.connect((self.blocks_throttle_0, 0), (self.lora2_lora_preamble_detect_0_0, 0))
        self.connect((self.blocks_vector_to_stream_0, 0), (self.blocks_complex_to_mag_0, 0))
        self.connect((self.digital_header_payload_demux_0, 1), (self.lora2_gray_encode_0_0, 0))
        self.connect((self.digital_header_payload_demux_0, 0), (self.lora2_lora_low_rate_opt_rx_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.lora2_css_demod_0, 2), (self.blocks_repeat_0, 0))
        self.connect((self.lora2_css_demod_0, 3), (self.blocks_repeat_0_0, 0))
        self.connect((self.lora2_css_demod_0, 1), (self.blocks_vector_to_stream_0, 0))
        self.connect((self.lora2_css_demod_0, 0), (self.digital_header_payload_demux_0, 0))
        self.connect((self.lora2_css_sync_and_vectorize_0, 0), (self.lora2_css_demod_0, 0))
        self.connect((self.lora2_freq_xlating_0, 0), (self.lora2_css_sync_and_vectorize_0, 0))
        self.connect((self.lora2_gray_encode_0, 0), (self.lora2_lora_deinterleaver_0, 0))
        self.connect((self.lora2_gray_encode_0_0, 0), (self.lora2_lora_deinterleaver_0_0, 0))
        self.connect((self.lora2_lora_deinterleaver_0, 0), (self.lora2_lora_hamming_decode_0, 0))
        self.connect((self.lora2_lora_deinterleaver_0_0, 0), (self.lora2_lora_depad_0, 0))
        self.connect((self.lora2_lora_depad_0, 0), (self.lora2_lora_merge_rem_0, 0))
        self.connect((self.lora2_lora_detect_sof_0, 0), (self.blocks_tag_debug_0_0, 0))
        self.connect((self.lora2_lora_detect_sof_0, 0), (self.lora2_freq_xlating_0, 0))
        self.connect((self.lora2_lora_hamming_decode_0, 0), (self.lora2_lora_header_decode_0, 0))
        self.connect((self.lora2_lora_low_rate_opt_rx_0, 0), (self.lora2_gray_encode_0, 0))
        self.connect((self.lora2_lora_merge_rem_0, 0), (self.lora2_lora_whiten_0, 0))
        self.connect((self.lora2_lora_preamble_detect_0_0, 0), (self.lora2_lora_detect_sof_0, 0))
        self.connect((self.lora2_lora_whiten_0, 0), (self.blocks_repack_bits_bb_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.low_pass_filter_0, 0))

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
        self.set_freq_offset(6*self.chan_bw)
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.chan_bw*self.interp, (self.chan_bw + self.chan_margin)/2, (self.chan_bw + self.chan_margin)/8, firdes.WIN_HAMMING, 6.76))
        self.set_T(float(self.M)/self.chan_bw)

    def get_M(self):
        return self.M

    def set_M(self, M):
        self.M = M
        self.qtgui_time_sink_x_0_0.set_y_axis(0, self.M)
        self.blocks_repeat_0_0.set_interpolation(self.M)
        self.blocks_repeat_0.set_interpolation(self.M)
        self.set_T(float(self.M)/self.chan_bw)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)

    def get_n_syms(self):
        return self.n_syms

    def set_n_syms(self, n_syms):
        self.n_syms = n_syms

    def get_interp(self):
        return self.interp

    def set_interp(self, interp):
        self.interp = interp
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.chan_bw*self.interp, (self.chan_bw + self.chan_margin)/2, (self.chan_bw + self.chan_margin)/8, firdes.WIN_HAMMING, 6.76))

    def get_freq_offset(self):
        return self.freq_offset

    def set_freq_offset(self, freq_offset):
        self.freq_offset = freq_offset
        self.freq_xlating_fir_filter_xxx_0.set_center_freq(-self.freq_offset)

    def get_chan_margin(self):
        return self.chan_margin

    def set_chan_margin(self, chan_margin):
        self.chan_margin = chan_margin
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.chan_bw*self.interp, (self.chan_bw + self.chan_margin)/2, (self.chan_bw + self.chan_margin)/8, firdes.WIN_HAMMING, 6.76))

    def get_chan_freq(self):
        return self.chan_freq

    def set_chan_freq(self, chan_freq):
        self.chan_freq = chan_freq

    def get_attenuation(self):
        return self.attenuation

    def set_attenuation(self, attenuation):
        self.attenuation = attenuation

    def get_T(self):
        return self.T

    def set_T(self, T):
        self.T = T

    def get_RF_samp_rate(self):
        return self.RF_samp_rate

    def set_RF_samp_rate(self, RF_samp_rate):
        self.RF_samp_rate = RF_samp_rate

    def get_CR(self):
        return self.CR

    def set_CR(self, CR):
        self.CR = CR


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
