#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019 Alexandre Marquet.
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#

import pmt
import numpy
from gnuradio import gr

from lora2 import css_mod_algo
from lora2 import css_demod_algo

class lora_detect_sof(gr.sync_block):
    """
    docstring for block lora_detect_sof
    """
    def __init__(self, SF, interp):
        gr.sync_block.__init__(self,
            name="lora_detect_sof",
            in_sig=[numpy.complex64],
            out_sig=[numpy.complex64])

        self.M = 2**SF
        self.Q = interp
        self.demod = css_demod_algo(self.M)
        self.mod = css_mod_algo.css_mod_algo(self.M, self.Q)

        self.set_output_multiple(3*(self.M*self.Q))
        self.set_history(self.M*self.Q+1)

        self.set_tag_propagation_policy(gr.TPP_CUSTOM)

    def propagate_tags(self, rel_start, rel_end):
        tags = self.get_tags_in_window(0, rel_start, rel_end)

        #Propagate all tags except those produced by the preamble detector
        for tag in tags:
            if (pmt.to_python(tag.key) != 'coarse_freq_offset') \
            and (pmt.to_python(tag.key) != 'fine_freq_offset') \
            and (pmt.to_python(tag.key) != 'sync_word') \
            and (pmt.to_python(tag.key) != 'time_offset'):
                self.add_item_tag(0, tag.offset, tag.key, tag.value)

    def delay_uncert_detect(self, sig):
        decim_sig = sig[::self.Q]
        #Demodulate available symbols w/o shifting, and retrieve confidence
        syms_noshift = self.demod.soft_demodulate(decim_sig)[1]
        #Demodulate available symbols w/ M/2 shifting, and retrieve confidence
        syms_shift = self.demod.soft_demodulate(decim_sig[self.M//2:-self.M//2])[1]

        #Differentiate to find a difference in confidence
        diff_noshift = numpy.abs(numpy.diff(syms_noshift))
        diff_shift = numpy.abs(numpy.diff(syms_shift))

        max_noshift = numpy.max(diff_noshift)
        argmax_noshift = numpy.argmax(diff_noshift)
        max_shift = numpy.max(diff_shift)
        argmax_shift = numpy.argmax(diff_shift)

        if max_noshift > max_shift:
            offset = self.M*self.Q*argmax_noshift

            #Fine offset
            reconst_sig = numpy.zeros(self.M*self.Q + self.Q, dtype=numpy.complex64)
            reconst_sig[self.Q//2:-self.Q//2] = self.mod.modulate([argmax_noshift])

            fine_offset = numpy.argmax(numpy.abs(numpy.correlate(\
                    sig[:self.M*self.Q], reconst_sig))) - self.Q//2

        else:
            offset = self.M*self.Q*argmax_shift + self.M*self.Q/2

            #Fine offset
            reconst_sig = numpy.zeros(self.M*self.Q + self.Q, dtype=numpy.complex64)
            reconst_sig[self.Q//2:-self.Q//2] = self.mod.modulate([argmax_shift])

            fine_offset = numpy.argmax(numpy.abs(numpy.correlate(\
                    sig[self.M*self.Q:-self.M*self.Q], reconst_sig))) - self.Q//2


        return (offset, fine_offset)

    def relocate_tags(self, offset, fine_offset):
        tag_offset = self.nitems_written(0) + offset + fine_offset

        #Tag packet start, if not already there
        self.add_item_tag(0, tag_offset, pmt.intern('pkt_start'), pmt.PMT_NIL)

        #Relocate tags produced by preamble detector to tag_offset
        tag_time = self.get_tags_in_window(0, 0, 1, pmt.intern('time_offset'))
        tag_coarse_freq = \
            self.get_tags_in_window(0, 0, 1, pmt.intern('coarse_freq_offset'))
        tag_fine_freq = \
            self.get_tags_in_window(0, 0, 1, pmt.intern('fine_freq_offset'))
        tag_sync = self.get_tags_in_window(0, 0, 1, pmt.intern('sync_word'))

        self.add_item_tag(0, tag_offset, tag_sync[0].key, tag_sync[0].value)
        self.add_item_tag(0, tag_offset, tag_time[0].key, tag_time[0].value)
        self.add_item_tag(0, tag_offset, pmt.intern('fine_time_offset'),
                pmt.to_pmt(int(fine_offset)))
        self.add_item_tag(0, tag_offset, tag_coarse_freq[0].key,
                tag_coarse_freq[0].value)
        self.add_item_tag(0, tag_offset, tag_fine_freq[0].key,
                tag_fine_freq[0].value)

    def work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]

        #Retrieve tags
        tags = self.get_tags_in_window(0, 0, len(in0), pmt.intern('time_offset'))

        #If no tag found, copy input to output and return
        if len(tags) == 0:
            out[:] = in0[self.M*self.Q:]

            return len(output_items[0])

        #Relative offset of first tag
        rel_offset = tags[0].offset - self.nitems_read(0)

        #If first tag is not alligned on the first item, consume (copy) every
        #item, up to the tag
        if rel_offset != 0:
            n_items = rel_offset

            out[0:n_items] = in0[self.M*self.Q:(self.M*self.Q+n_items)]
            self.propagate_tags(0, n_items)

            return n_items

        #Find offset and relocate tags accordingly
        (offset, fine_offset) = self.delay_uncert_detect(in0)
        self.relocate_tags(offset, fine_offset)

        #Copy items up to the next tag
        if len(tags) > 1:
            next_tag_rel_offset = tags[1].offset - self.nitems_read(0)

            out[0:next_tag_rel_offset] = \
                    in0[self.M*self.Q:(self.M*self.Q+next_tag_rel_offset)]
            self.propagate_tags(0, next_tag_rel_offset)

            return next_tag_rel_offset
        else: #len(tags)==1
            out[:] = in0[self.M*self.Q:]
            self.propagate_tags(0, len(in0))

            return len(output_items[0])
