#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  1 16:18:06 2019

@author: amarquet
"""

import numpy

def sum_GF2(a):
    return numpy.sum(a)%2

def mtx_mul_GF2(a, b):
    a = numpy.matrix(a)
    b = numpy.matrix(b)
    
    return numpy.mod(a*b, 2)

def mtx_det_GF2(A):
    A = numpy.matrix(A)
    if len(A.shape) != 2:
        raise Exception('A must be a matrix')
        
    if A.shape[0] != A.shape[1]:
        raise Exception('A must be square')
    
    return mtx_det_algo(A)

def mtx_det_algo(A):
    if A.shape[0] == 1:
        return A[0,0]
    
    if A.shape[0] == 2:
        return (A[0,0]&A[1,1]) ^ (A[0,1]&A[1,0])

    if A.shape[0] == 3:
        out = A[0,0] & ( (A[1,1]&A[2,2]) + (A[1,2]&A[2,1]) )
        out ^= A[0,1] & ( (A[1,0]&A[2,2]) + (A[1,2]&A[2,0]) )
        out ^= A[0,2] & ( (A[1,0]&A[2,1]) + (A[1,1]&A[2,0]) )
        
        return out

    out = 0
    for i in range(0, A.shape[0]):
        if A[0,i] == 1:
            selector = [x for x in range(0, A.shape[0]) if x != i]
            out ^= mtx_det_algo(A[1:,:][:,selector])
        
    return out

def mtx_inv_algo(mtx):
    out = numpy.matrix(numpy.zeros(mtx.shape),dtype=numpy.int8)
    
    for i in range(0, mtx.shape[0]):
        line_selector = [x for x in range(0, mtx.shape[0]) if x != i]
        for j in range(0, mtx.shape[0]):
            column_selector = [x for x in range(0, mtx.shape[0]) if x != j]
        
            out[j,i] = mtx_det_algo(mtx[line_selector,:][:,column_selector])
           
    return out

def mtx_inv_GF2(mtx):
    mtx = numpy.matrix(mtx)
    if len(mtx.shape) != 2:
        raise Exception('mtx must be a matrix')
        
    if mtx.shape[0] != mtx.shape[1]:
        raise Exception('mtx must be square')
    
    if mtx_det_algo(mtx) == 0:
        raise Exception('Non invertible matrix.\n' + str(mtx))

    return mtx_inv_algo(mtx)

def test_mtx_inv_2():
    I = numpy.eye(2)
    
    A = []
    A.append([[0, 0], [0, 0]])
    A.append([[0, 0], [0, 1]])
    A.append([[0, 0], [1, 0]])
    A.append([[0, 0], [1, 1]])
    A.append([[0, 1], [0, 0]])
    A.append([[0, 1], [0, 1]])
    A.append([[0, 1], [1, 0]])
    A.append([[0, 1], [1, 1]])
    A.append([[1, 0], [0, 0]])
    A.append([[1, 0], [0, 1]])
    A.append([[1, 0], [1, 0]])
    A.append([[1, 0], [1, 1]])
    A.append([[1, 1], [0, 0]])
    A.append([[1, 1], [0, 1]])
    A.append([[1, 1], [1, 0]])
    A.append([[1, 1], [1, 1]])
    
    for ele in A:
        try:
            B = mtx_inv_GF2(ele)
           
            I1 = mtx_mul_GF2(ele, B)
            I2 = mtx_mul_GF2(B, ele)
            
            if (I1 != I).any() or (I2 != I).any():
                print('Matrix inversion failed with A:')
                print(str(ele) + '\n')
        except Exception as e:
            print('Cannot inverse A:')
            print(ele)
            print(str(e) + '\n')
