#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 29 14:54:29 2019

@author: amarquet
"""

import numpy
from lfsr_utils import lfsr, search_poly_lfsr, construct_lfsr_trellis, search_seed_lfsr,search_seed_lfsr2

######Generate synthetic sequence######
      
#L=9
#poly = [0, 0, 1, 1, 1, 0, 1, 1, 1]
#seed = [0, 1, 1, 0, 1, 1, 1, 0, 0]
#L=5
#poly=[0,1,1,0,1]
#seed=[0,1,0,0,0]
#
#print('Polyniomial: ' + str(poly))
#print('Seed: ' + str(seed))
#
#seq = lfsr(poly, seed, 3*L+1)

seq_hexa = [0x2e, 0x0, 0xa, 0xc, 0xc, 0x1e, 0x3c, 0x1e]
seq = numpy.unpackbits(numpy.array(seq_hexa, dtype=numpy.uint8))
print(seq)

#######Find LFSR parameters######

est_poly = -1
est_seed = -1
Lmin = 2

while est_seed == -1:
    print('I - Searching a candidate polyniomial...')
    est_poly = search_poly_lfsr(seq, Lmin)
    est_L = len(est_poly)
    
    Lmin = est_L + 1

    print('II - Building LFSR trellis...')
    #trellis = construct_lfsr_trellis(est_poly)

    print('III - Searching a candidate seed...')
    #est_seed = search_seed_lfsr(trellis, seq)
    est_seed = search_seed_lfsr2(est_poly, seq)
    print('\n')
   
print('Estimated polyniomial: ' + str(est_poly))

est_seed_bin = numpy.frombuffer(numpy.binary_repr(est_seed, est_L).encode(), dtype='S1')
est_seed_bin = numpy.array(est_seed_bin, dtype=numpy.int)
print('Estimated seed: ' + str(est_seed_bin))