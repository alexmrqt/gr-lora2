#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 14:57:53 2019

@author: amarquet
"""

import numpy
import scipy

def deinterleave_mtx(CR, SF, mtx, reduced_rate=False):
        
    #Go column-by-column through the matrix
    for i in range(0, mtx.shape[1]):
        mtx[:,i] = numpy.roll(mtx[:,i], i)

    mtx = numpy.fliplr(mtx)

    return mtx

def deinterleave_vect(CR, SF, vect, reduced_rate = False):
    mtx = numpy.flipud(vect.reshape((CR+4, SF)).transpose())
    
    if reduced_rate:
        mtx = mtx[:-2,:]
    
    deintlvd_mtx = deinterleave_mtx(CR, SF, mtx, reduced_rate)
    
    return deintlvd_mtx.flatten()

def hamming_decode(vect):
    n_cw = int(len(vect)/(CR+4))
    mtx = vect.reshape((n_cw, CR+4))
    
    return mtx[:,4:8]

def compute_hdr_crc(vect):
    res = numpy.zeros(8, dtype=numpy.uint8)
    
    res[3] = numpy.sum(vect[[0,1,2,3]])%2
    res[4] = numpy.sum(vect[[0,4,5,6,11]])%2
    res[5] = numpy.sum(vect[[1,4,7,8,10]])%2
    res[6] = numpy.sum(vect[[1,5,6,9,10,11]])%2
    res[7] = numpy.sum(vect[[3,6,8,9,10,11]])%2

    return res

def find_possible_crc_poly(data, crc_ref):
    possible_poly = [[], [], [], [], []]
    
    for i in range(0, 2**len(data)):
        i_str = numpy.binary_repr(i, len(data))
        i_bin = numpy.frombuffer(i_str.encode(), dtype='S1')
        i_bin = numpy.array(i_bin, dtype=numpy.uint8)
        
        chk = numpy.sum(i_bin*data)%2
        
        for j in range(0, len(possible_poly)):
            if crc_ref[j] == chk:
                possible_poly[j].append(i)
    
    return possible_poly

def find_common_crc_poly(data_list, crc_ref_list):
    possible_poly = find_possible_crc_poly(data_list[0], crc_ref_list[0])
    
    for i in range(1, len(data_list)):
        possible_poly_1 = find_possible_crc_poly(data_list[i], crc_ref_list[i])
        
        for j in range(0, len(possible_poly)):
            possible_poly[j] = numpy.intersect1d(possible_poly[j], possible_poly_1[j])
            
            if len(possible_poly[j]) == 0:
                print('No matching poly for digit ' + str(j) + '. Caused by data ' + str(i) + ' ' +  str(data_list[i]) + ' and CRC ' + str(crc_ref_list[i]))

    return possible_poly

def extract_hdr(vect):
    hdr = vect[0:20]
    
    length = vect[0:8]
    CR = vect[8:11]
    has_crc = vect[11]
    chk = vect[12:20]
    
    rest = vect[20:]
    
    return (hdr, length, CR, has_crc, chk, rest)

def decode_hdr(vect, SF):
    CR=4
    
    #Convert to matrix of binary value
    #Where each line contains a chirp
    f_bin_str = [numpy.binary_repr(ele, SF) for ele in vect]
    f_bin = [numpy.frombuffer(ele.encode(), dtype='S1') for ele in f_bin_str]
    f_bin = numpy.array(f_bin, dtype=numpy.uint8)

    print('Received:')
    print(f)
    print(f_bin)
    
    n_blocks = int(f_bin.shape[0]/(CR+4))
    rr = True
    if rr:
        deintlvd = numpy.zeros((n_blocks, (SF-2)*(CR+4)), dtype=numpy.uint8)
    else:
        deintlvd = numpy.zeros((n_blocks, SF*(CR+4)), dtype=numpy.uint8)
    
    for i in range(0, n_blocks):
        deintlvd[i][:] = deinterleave_vect(CR, SF, f_bin[i*(CR+4):(i+1)*(CR+4)][:].flatten(), reduced_rate = rr)
    
    deintlvd = deintlvd.flatten()
    
    print('Deinterleaved:')
    print(deintlvd)
    
    decoded = hamming_decode(deintlvd)
    decoded = decoded.flatten()
    
    print('Decoded:')
    print(decoded)
    
    hdr_content = extract_hdr(decoded)
    
    print('Header:')
    print(hdr_content[0])
    print(hdr_content[0][0:12])
    
    print('Header (length):')
    print(hdr_content[1])
    
    print('Header (CR):')
    print(hdr_content[2])
    
    print('Header (has_crc):')
    print(hdr_content[3])
    
    print('Header (CRC):')
    print(hdr_content[4])
    print('CRC (computed)):')
    print(compute_hdr_crc(hdr_content[0][0:12]))

    return hdr_content[5]

#These are the parameters of the transmission
SF=9
CR=4

#File containing the packet
f = scipy.fromfile(open("capture_Ping_4_8.raw"), dtype=scipy.uint16)
#f = scipy.fromfile(open("capture_Ping_4_7.raw"), dtype=scipy.uint16)
#f = f[0:SF*10]
#f = scipy.fromfile(open("capture_Ping_4_6.raw"), dtype=scipy.uint16)
#f = f[1:SF*10]
#f = scipy.fromfile(open("capture_Ping_4_5.raw"), dtype=scipy.uint16)
#f = scipy.fromfile(open("capture_rndm1_4_8.raw"), dtype=scipy.uint16)
#f = scipy.fromfile(open("capture_rndm2_4_8.raw"), dtype=scipy.uint16)
#f = scipy.fromfile(open("capture_rndm3_4_8.raw"), dtype=scipy.uint16)
#f = scipy.fromfile(open("capture_rndm4_4_8.raw"), dtype=scipy.uint16)
#f = scipy.fromfile(open("capture_rndm5_4_8.raw"), dtype=scipy.uint16)
#f = scipy.fromfile(open("capture_rndm6_4_8.raw"), dtype=scipy.uint16)
#f = scipy.fromfile(open("capture_rndm7_4_8.raw"), dtype=scipy.uint16)
#f = scipy.fromfile(open("capture_rndm8_4_8.raw"), dtype=scipy.uint16)
#f = scipy.fromfile(open("capture_rndm9_4_8.raw"), dtype=scipy.uint16)
#f = scipy.fromfile(open("capture_rndm13_4_8.raw"), dtype=scipy.uint16)
#f = f[0:SF*10]

rest = decode_hdr(f, SF)
print('Remaining bits in header')
print(rest)