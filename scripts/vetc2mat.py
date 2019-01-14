#!/usr/bin/python

#######################################
#         HAGATA / TEMZI              #
#              2018                   #
#######################################

import numpy

# matrix size
CR= 5
SF= 8

# input random matrix
input_vect= numpy.random.randint( 0, 2, size= ( 1, (CR+4)*SF ) )
print input_vect

input_mat= input_vect.reshape((CR+4,SF))
print input_mat

output_vect= input_mat.reshape(-1)
print output_vect
