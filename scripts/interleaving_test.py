import copy
import numpy

def interleave_mtx(CR, SF, mtx):
    mtx = numpy.fliplr(mtx)

    #Go column-by-column through the matrx
    for i in range(0, mtx.shape[1]):
        mtx[:,i] = numpy.roll(mtx[:,i], -i)

    return mtx

def interleave_vect(CR, SF, vect):
    mtx = vect.reshape((SF, CR+4))
    
    intlvd_mtx = interleave_mtx(CR, SF, mtx)
    
    return numpy.fliplr(intlvd_mtx.transpose()).flatten()

def deinterleave_mtx(CR, SF, mtx):
        
    #Go column-by-column through the matrix
    for i in range(0, mtx.shape[1]):
        mtx[:,i] = numpy.roll(mtx[:,i], i)

    mtx = numpy.fliplr(mtx)

    return mtx

def deinterleave_vect(CR, SF, vect):
    mtx = numpy.flipud(vect.reshape((CR+4, SF)).transpose())
    
    deintlvd_mtx = deinterleave_mtx(CR, SF, mtx)
    
    return deintlvd_mtx.flatten()

if __name__ == "__main__":
    
    ###########TESTS WITH ROBYNS EXAMPLES###########
    CR= 4
    SF= 7
    
    ###########MATRIX TEST###########
    input_mtx = [
            [0,1,1,1,0,0,1,0],
            [1,1,1,0,1,0,0,0],
            [1,0,1,0,0,0,1,1],
            [0,0,0,0,0,0,0,0],
            [0,0,1,0,1,1,1,0],
            [1,1,0,1,0,0,0,1],
            [1,1,1,1,1,1,1,1]]

    input_mtx = numpy.array(input_mtx, dtype=numpy.int8)

    intlvd_mtx = interleave_mtx(CR,SF, copy.copy(input_mtx))

    deintlvd_mtx = deinterleave_mtx(CR,SF, copy.copy(intlvd_mtx))

    if (input_mtx == deintlvd_mtx).all():
        print('Matrix-based: PASS')
    else:
        print('Matrix-based: FAIL')

        print("Input matrix:")
        print(input_mtx)

        print("Interleaved matrix")
        print(intlvd_mtx)

        print("Output matrix:")
        print(deintlvd_mtx)
        
#    ###########MATRIX REDUCED RATE MODE TEST###########
#    
#    deintlvd_mtx = deinterleave_mtx(CR,SF, copy.copy(intlvd_mtx), reduced_rate=True)
#    exp_deintlvd_mtx = [
#            [1,0,1,0,0,1,1,0],
#            [0,0,0,0,0,0,0,1],
#            [0,0,1,1,1,1,1,1],
#            [1,1,1,1,0,0,1,1],
#            [1,1,1,0,1,0,0,0]]
#    exp_deintlvd_mtx = numpy.array(exp_deintlvd_mtx, dtype=numpy.int8)
#    
#    if (deintlvd_mtx == exp_deintlvd_mtx).all():
#        print("Reduced rate: PASS")
#    else:
#        print("Reduced rate: FAIL")
#        
#        print("Input matrix:")
#        print(input_mtx)
#
#        print("Interleaved matrix")
#        print(intlvd_mtx)
#        
#        print("Deinterleaved matrix")
#        print(deintlvd_mtx)
#        
#        print("Expected deinterleaved matrix")
#        print(exp_deintlvd_mtx)

    ###########VECTOR TEST###########
    input_vect = input_mtx.flatten()
    
    intlvd_vect = interleave_vect(CR, SF, copy.copy(input_vect))
    
    exp_intlvd_vect = [1,1,0,0,1,0,0,
                       1,1,0,1,0,1,0,
                       0,0,1,0,1,0,0,
                       0,1,0,1,0,1,0,
                       0,0,0,1,1,1,0,
                       1,0,1,1,1,1,0,
                       1,0,0,0,1,1,1,
                       1,1,0,0,1,1,0]
    exp_intlvd_vect = numpy.array(exp_intlvd_vect, dtype=numpy.int8)
    
    deintlvd_vect = deinterleave_vect(CR, SF, copy.copy(intlvd_vect))
    
    if (intlvd_vect == exp_intlvd_vect).all():
        print("Interleaver output: PASS")
    else:
        print("Interleaver output: FAIL")
        
        print("Input vector:")
        print(input_vect)

        print("Interleaved vector")
        print(intlvd_vect)
        
        print("Expected interleaved vector")
        print(exp_intlvd_vect)
        
    
    if (input_vect == deintlvd_vect).all():
        print('Vector-based: PASS')
    else:
        print('Vector-based: FAIL')

        print("Input vector:")
        print(input_vect)

        print("Interleaved vector")
        print(intlvd_vect)

        print("Output vector:")
        print(deintlvd_vect)
        
    ###########RANDOM VECTOR TEST###########
    CR= 4
    SF= 7
    
    input_vect = numpy.random.randint(0, 2, SF*(CR+4))
    
    intlvd_vect = interleave_vect(CR, SF, copy.copy(input_vect))
    
    deintlvd_vect = deinterleave_vect(CR, SF, copy.copy(intlvd_vect))
    
    if (input_vect == deintlvd_vect).all():
        print('Random vector test: PASS')
    else:
        print('Random vector test: FAIL')

        print("Input vector:")
        print(input_vect)

        print("Interleaved vector")
        print(intlvd_vect)

        print("Output vector:")
        print(deintlvd_vect)