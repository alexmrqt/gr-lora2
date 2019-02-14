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

class store_tags(gr.sync_block):
    """
    docstring for block count_tags
    """
    def __init__(self, sizeof_stream_item=numpy.complex64, key_filter=""):
        gr.sync_block.__init__(self,
            name="count_tags",
            in_sig=[sizeof_stream_item],
            out_sig=[])

        if len(key_filter) != 0:
            self.key_filter = pmt.intern(key_filter)
        else:
            self.key_filter = -1

        self.num_tags = 0
        self.tags = []

    def get_num_tags(self):
        return self.num_tags

    def get_tags(self):
        return self.tags

    def work(self, input_items, output_items):
        in0 = input_items[0]

        tags = []
        if self.key_filter == -1:
            tags = self.get_tags_in_window(0, 0, len(in0))
        else:
            tags = self.get_tags_in_window(0, 0, len(in0), self.key_filter)

        self.num_tags += len(tags)

        for tag in tags:
            self.tags.append(tag)

        return len(input_items[0])

