#!/usr/bin/python

#######################################
#         HAGATA / TEMZI              #
#              2018                   #
#######################################

import numpy

# matrix size
CR= 4
SF= 9

# input random vector
input_vect= numpy.random.randint( 0, 2, size= ( 1, (CR+4)*SF ) )
print input_vect

# convert the vector into a matrix
input_mat= input_vect.reshape((CR+4,SF))

# print the input matrix
print input_mat

# transpose input matrix
transposed= numpy.transpose( input_mat )

# split matrix into row vectors
array= numpy.split( transposed, SF )

# placeholder for the concatenation
out= numpy.array([], dtype=numpy.int).reshape(0,CR+4)

# shift index
i=0

# vector loop
for v in array:

    # circular shift each vector by i
    v= numpy.roll( v, i )

    # store the vector in the new matrix
    out= numpy.vstack( (out, v) )

    # increse de shift index
    i=i+1
    
# flip vertially the result matrix
out= numpy.flipud( out )

# print output
print out

# print the vector version of the output
output_vect= out.reshape(-1)
print output_vect
