#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  1 16:17:16 2019

@author: amarquet
"""

import copy
import numpy
from gf2_utils import sum_GF2, mtx_mul_GF2, mtx_inv_GF2

def lfsr(poly, seed, n_bits):
    sr = seed
    
    out = numpy.zeros(n_bits, dtype=numpy.int)
    
    for i in range(0, n_bits):
        #Extract current output of the LFSR
        out[i] = sr[-1]
        
        #Calculate new input from poly and current content of the shift register
        next_input = sum_GF2(numpy.bitwise_and(sr, poly))
        
        #Shift register
        sr = numpy.roll(sr,1)
        sr[0] = next_input
    
    return out

def find_poly_lfsr(seq, L):
    if len(seq) != 2*L:
        raise Exception('find_poly_lfsr: need a sequence of length 2*L.')
    
    #Construct matrix S of shifted outputs
    S = numpy.zeros((L, L), dtype = numpy.int)
    for i in range(0, L):
        S[i,:] = seq[i:i+L]
    S = numpy.fliplr(numpy.flipud(S))
    
    #Invert S
    invS = mtx_inv_GF2(S)
    
    #Retrieve last vector of outputs
    s = numpy.flipud(numpy.matrix(seq[-L:]).transpose())
    
    #resolve equation to find polyniomial
    return mtx_mul_GF2(invS, s).flatten()

def search_poly_lfsr(seq, Lmin):
    Lmax = len(seq)//2
    
    for L in range(Lmin,Lmax+1):
        print('search_poly_lfsr: trying with L = ' + str(L))
        
        try:
            #Initial estimate of the polyniomial
            init_poly = find_poly_lfsr(seq[0:2*L], L)
            
#            #This estimate should be the same for all items in the sequence
#            for i in range(1,len(seq)-2*L):
#                seq_tmp = seq[i:i + 2*L]
#                if (find_poly_lfsr(seq_tmp, L) != init_poly).any():
#                    break
            
            print('search_poly_lfsr: found!')
            return init_poly.tolist()[0]
        except Exception as e:
            continue
    
    print('search_poly_lfsr: no polyniomial found.')

def construct_lfsr_trellis(poly):
    L = len(poly)
    trellis = dict()
    #States in which LFSR end-up stuck, and states leading to these states
    #Includes at least the all-zeros state
    useless_states = [(0,0), (0,1)]
    
    #Add useful states
    for curr_state in range(1, 2**L):
        curr_state_bin = numpy.frombuffer(numpy.binary_repr(curr_state, L).encode(), dtype='S1')
        curr_state_bin = numpy.array(curr_state_bin, dtype=numpy.int)
        
        #Calculate next output and next state
        next_output = curr_state&0x01
        next_input = sum_GF2(curr_state_bin*poly)
        next_state = (curr_state>>1)|(next_input<<(L-1))
        
        #trellis[curr_state] = (next_state, next_output)
        
        if next_state == curr_state:
            useless_states.append((next_state, 0))
            useless_states.append((next_state, 1))
        else:
            trellis[curr_state] = (next_state, next_output)
    
    #Recursively add states leading to useless states to the list of useless states
    to_be_processed = copy.copy(useless_states)
    trellis_values = list(trellis.values())
    
    while len(to_be_processed) != 0:
        ustate = to_be_processed.pop()
        
        if ustate in trellis_values:
            #Find states leading to this useless states
            #new_ustates = trellis_keys[trellis_values.index(ustate)]
            new_ustates = [key for (key, val) in trellis.items() if val == ustate]
            
            for new_ustate in new_ustates:            
                if new_ustate not in useless_states:
                    useless_states.append((new_ustate,0))
                    useless_states.append((new_ustate,1))
                    
                    to_be_processed.append((new_ustate,0))
                    to_be_processed.append((new_ustate,1))
    
    #Remove useless_states from trellis
    [trellis.pop(i[0]) for i in useless_states if i[0] in trellis]
    
    return trellis

class Node:
    def __init__(self, state_id, time_idx, pred):
        self.state_id = state_id
        self.time_idx = time_idx
        self.pred = pred
    
    def __lt__(self, other):
        return False
    
    def __str__(self):
        out = 'State idx ' + str(self.state_id) + ' at time idx ' + str(self.time_idx)
        if self.pred is not None:
            out +=  ' with predecessor ' + str(self.pred.state_id)
        
        return out

def search_seed_lfsr(trellis, seq):
    hq = []
    final_node = None
    
    #Initialize
    for state in trellis:
        hq.append(Node(state, 0, None))
    
    #Search
    while len(hq) != 0:
        u_node = hq.pop()
        
        next_state_id = trellis[u_node.state_id][0]
        next_output = trellis[u_node.state_id][1]
        
        if next_output ^ seq[u_node.time_idx] == 0:
            v_node = Node(next_state_id, u_node.time_idx + 1, u_node)       
            hq.append(v_node)
            
            if v_node.time_idx == (len(seq) - 1):
                final_node = v_node
                break
    
    #Traceback
    if final_node is not None:
        node = final_node
        
        while node.pred is not None:
            node = node.pred
        
        return node.state_id
    else:
        print('search_seed_lfsr: cannot find a seed with given sequence.')
        
        return -1

def search_seed_lfsr2(poly, seq):
    hq = []
    final_node = None
    
    L = len(poly)
    poly_int = 0
    for i in range(0, L):
        poly_int |= (poly[i])<<(L-i-1)

    #Initialize
    for i in range(0,2**L):
        hq.append(Node(i, 0, None))
    
    #Search
    while len(hq) != 0:
        u_node = hq.pop()
        
        next_output = u_node.state_id&0x01
        xor = u_node.state_id&poly_int
        next_input = 0
        while xor != 0:
            next_input ^= xor&0x01
            xor >>= 1
        
        next_state_id = (u_node.state_id>>1)|(next_input<<(L-1))
        
        #If state is not useless (leading to itself), and distance is 0
        if (next_state_id != u_node.state_id) and (next_output ^ seq[u_node.time_idx] == 0):
            v_node = Node(next_state_id, u_node.time_idx + 1, u_node)       
            hq.append(v_node)
            
            if v_node.time_idx == (len(seq) - 1):
                final_node = v_node
                break
    
    #Traceback
    if final_node is not None:
        node = final_node
        
        while node.pred is not None:
            node = node.pred
        
        return node.state_id
    else:
        print('search_seed_lfsr: cannot find a seed with given sequence.')
        
        return -1