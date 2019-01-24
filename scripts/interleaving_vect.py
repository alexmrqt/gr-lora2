#!/usr/bin/python

#######################################
#         HAGATA / TEMZI              #
#              2018                   #
#######################################

import numpy

# matrix size
CR= 5
SF= 8

# input random vector
input_vect= numpy.random.randint( 0, 2, size= ( 1, (CR+4)*SF ) )
print input_vect

# convert the vector into a matrix
input_mat= input_vect.reshape((CR+4,SF))

# print the input matrix
print input_mat

# flipping horizontally the input matrix
flipped_horiz= numpy.fliplr( input_mat )

# placeholder for the concatenation
out= numpy.array([], dtype=numpy.int).reshape(0,CR+4)

# non-square matrix offset
offset= SF-(CR+4)

# diagonal concatenation
for x in range( 0, SF ):

    # auxiliar variable for the first iteration
    # aux= numpy.flip( flipped_horiz.diagonal( -x+offset ), 0 )
    aux= numpy.flipud( flipped_horiz.diagonal( -x+offset ) )
    

    # multiple iterations for the size of the matrix:
    # ex: 18x8
    # |   ||   ||   ||   |
    # |   ||   ||   ||   |
    # |   ||   ||   ||   |
    #     8   16   24   32 
    #
    # 18+x / 8 = #of iterations
    # (CR+4+x) / SF

    for y in range( 1, (CR+4+x) / SF +1 ):

        # concatenate the first iteration with each new iteration
        aux= numpy.concatenate( ( aux, numpy.flipud( flipped_horiz.diagonal( y*SF-x+offset ) ) ), axis=0)

    # concatenate vertically the auxilliar vectors
    out= numpy.vstack( (out, aux) )

# print the output
print out

# print the vector version of the output
output_vect= out.reshape(-1)
print output_vect
