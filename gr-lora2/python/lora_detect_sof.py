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

from lora2 import css_demod_algo

class lora_detect_sof(gr.sync_block):
    """
    docstring for block lora_detect_sof
    """
    def __init__(self, SF):
        gr.sync_block.__init__(self,
            name="lora_detect_sof",
            in_sig=[numpy.complex64],
            out_sig=[numpy.complex64])

        self.M = 2**SF
        self.demod = css_demod_algo(self.M)

        self.set_output_multiple(3*self.M)
        self.set_history(self.M+1)

        self.set_tag_propagation_policy(gr.TPP_CUSTOM)

    def propagate_tags(self, rel_start, rel_end):
        tags = self.get_tags_in_window(0, rel_start, rel_end)

        #Propagate all tags except those produced by the preamble detector
        for tag in tags:
            if (pmt.to_python(tag.key) != 'freq_offset') \
            and (pmt.to_python(tag.key) != 'fine_freq_offset') \
            and (pmt.to_python(tag.key) != 'sync_word') \
            and (pmt.to_python(tag.key) != 'time_offset'):
                self.add_item_tag(0, tag.offset, tag.key, tag.value)

    def work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]

        #Retrieve tags
        tags = self.get_tags_in_window(0, 0, len(in0), pmt.intern('time_offset'))

        #If no tag found, copy input to output and return
        if len(tags) == 0:
            out[:] = in0[self.M:]

            return len(output_items[0])

        #Relative offset of first tag
        rel_offset = tags[0].offset - self.nitems_read(0)

        #If first tag is not alligned on the first item, consume (copy) every
        #item, up to the tag
        if rel_offset != 0:
            n_items = rel_offset

            out[0:n_items] = in0[self.M:(self.M+n_items)]
            self.propagate_tags(0, n_items)

            return n_items

        #Demodulate available symbols w/o shifting, and retrieve confidence
        syms_noshift = self.demod.soft_demodulate(in0)[1]
        #Demodulate available symbols w/ M/2 shifting, and retrieve confidence
        syms_shift = self.demod.soft_demodulate(in0[self.M/2:-self.M/2])[1]

        diff_noshift = numpy.abs(numpy.diff(syms_noshift))
        diff_shift = numpy.abs(numpy.diff(syms_shift))

        max_noshift = numpy.max(diff_noshift)
        argmax_noshift = numpy.argmax(diff_noshift)
        max_shift = numpy.max(diff_shift)
        argmax_shift = numpy.argmax(diff_shift)

        tag_offset = 0
        if max_noshift > max_shift:
            tag_offset = self.nitems_written(0) + self.M*argmax_noshift
        else:
            tag_offset = self.nitems_written(0) + self.M*argmax_shift + self.M/2

        #Tag packet start, if not already there
        self.add_item_tag(0, tag_offset, pmt.intern('pkt_start'), pmt.PMT_NIL)

        #Relocate tags produced by preamble detector to tag_offset
        tag_time = self.get_tags_in_window(0, 0, 1, pmt.intern('time_offset'))
        tag_freq = self.get_tags_in_window(0, 0, 1, pmt.intern('freq_offset'))
        tag_fine_freq = \
            self.get_tags_in_window(0, 0, 1, pmt.intern('fine_freq_offset'))
        tag_sync = self.get_tags_in_window(0, 0, 1, pmt.intern('sync_word'))

        self.add_item_tag(0, tag_offset, tag_sync[0].key, tag_sync[0].value)
        self.add_item_tag(0, tag_offset, tag_time[0].key, tag_time[0].value)
        self.add_item_tag(0, tag_offset, tag_freq[0].key, tag_freq[0].value)
        self.add_item_tag(0, tag_offset, tag_fine_freq[0].key, tag_fine_freq[0].value)

        #Copy items up to the next tag
        if len(tags) > 1:
            next_tag_rel_offset = tags[1].offset - self.nitems_read(0)

            out[0:next_tag_rel_offset] = in0[self.M:(self.M+next_tag_rel_offset)]
            self.propagate_tags(0, next_tag_rel_offset)

            return next_tag_rel_offset
        else:
            out[:] = in0[self.M:]
            self.propagate_tags(0, len(in0))

            return len(output_items[0])
