#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  1 16:17:16 2019

@author: amarquet
"""

import binascii
import copy
import numpy
from gf2_utils import sum_GF2, solve_lin_system

def lfsr(poly, seed, n_bits, skip_mod = 0):
    sr = seed
    
    out = numpy.zeros(n_bits, dtype=numpy.int)
    
    j=0
    for i in range(0, n_bits):
        if (skip_mod > 0) and ((j%skip_mod) == 0):
            next_input = sum_GF2(numpy.bitwise_and(sr, poly))
            sr = numpy.concatenate(([next_input], sr[:-1]))
            
        #Extract current output of the LFSR
        out[i] = sr[-1]
        
        #Calculate new input from poly and current content of the shift register
        next_input = sum_GF2(numpy.bitwise_and(sr, poly))
        
        #Shift register
        sr = numpy.concatenate(([next_input], sr[:-1]))
            
        j += 1
    
    return out

def find_poly_lfsr(seq, L):
    if len(seq) != 2*L:
        raise Exception('find_poly_lfsr: need a sequence of length 2*L.')
    
    #Construct matrix S of shifted outputs
    S = numpy.zeros((L, L), dtype = numpy.int)
    for i in range(0, L):
        S[i,:] = seq[i:i+L]
    S = numpy.fliplr(numpy.flipud(S))

    #Retrieve last vector of outputs
    s = numpy.flipud(numpy.matrix(seq[-L:]).transpose())

    #resolve equation to find polyniomial
    return solve_lin_system(S, s).flatten()

def search_poly_lfsr(seq, L):
    print('search_poly_lfsr: trying with L = ' + str(L))
    
    #This estimate should be the same for all items in the sequence
    try:
        poly = find_poly_lfsr(seq[0:2*L], L)

        for i in range(1,len(seq)-2*L):
            seq_tmp = seq[i:i + 2*L]
            can_poly = find_poly_lfsr(seq_tmp, L).tolist()
            
            if (can_poly != poly).any():
                print('search_poly_lfsr: not found!')
                return

    except Exception as e:
        print('search_poly_lfsr: Error: ' + str(e))
        return
        
    print('search_poly_lfsr: found!')
    return poly

def can_poly_lfsr(seq, L):
    print('search_poly_lfsr: trying with L = ' + str(L))
    polys = []
    
    for i in range(1,len(seq)-2*L):
        try:
            poly = find_poly_lfsr(seq[i:i + 2*L], L)
            poly_hexstr = binascii.hexlify(numpy.packbits(poly))
            
            if poly_hexstr not in polys:
                print(poly_hexstr)
                polys.append(poly_hexstr)
        
        except Exception as e:
            print('search_poly_lfsr: Error: ' + str(e))
        
    return polys