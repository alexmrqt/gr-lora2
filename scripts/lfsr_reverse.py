#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 29 14:54:29 2019

@author: amarquet
"""

import binascii
import numpy
from lfsr_utils import lfsr, can_poly_lfsr, search_poly_lfsr

######Generate synthetic sequence######
      
#L=9
#poly = [0, 0, 1, 1, 1, 0, 1, 1, 1]
#seed = [0, 1, 1, 0, 1, 1, 1, 0, 0]
##L=5
##poly=[0,1,1,0,1]
##seed=[0,1,0,0,0]
#
#print('Polyniomial: ' + str(poly))
#print('Seed: ' + str(seed))
#
#seq = lfsr(poly, seed, 3*L+1)

base_shift = 0

CR = 4 
# seq_hexstr = b"d1005cffe8ff00ffd12e725c65e84b0017d1ff722e655c4be817d1ffa32ec65c8de89ad1b4a3e8c6008d009a00b400e8d1007200b400e800d1d1a37217b42ee85cd1e8a3d117722eb45c39e872d165724bb417392e725c65e84b0017002e005cd1e8a300c6005c0039d172a3b4c6395c7239b47239b4a339c6728db44b3917a32ec65c8d394b7217b42ee85c00390072d1b472e865009a0065d14b72c6658d9a4b65c64b8dc69a8d654b4bc6c68d5c9a3965724b65c64b5cc6395c72e865004bd1c6a35c17e8ff00ffd12ea38d174bffc6ff8d2e4b8d174bffc62e8d8d4b9a1765ff4b2e178d2e9a8d659a4bb417e82ed18d729ab4b4e8e800d1d172a3b4c6e88d004bd1c6a35cc6e88dd14ba3c6175cffe82ed15ca33917a3ff172e2e5c5c3939a3a317c62e5c5ce839d1a372c6655c4be8c6d18d729a65b44b39c6728db49ae8b4d139727265b49ae8b4d139727265659a9ab465399a72b465399aa365179a2eb48d394ba317172e2e8d8d4b4bc6175c2e398da34b17c6ff5c2e398da34b1717ffff2eff8dff4b2e178dff9affb4ff392ea38dc69a5cb43939a3a3c6c68d5c9a3965a39ac6b48de89ad165a39ac6b45ce8e8d100a300c6d15ca3e817002e008dd19aa365179a2e658d9a9a65654b9a1765ff9aff652e4b5c1739ff72ff652e9a5cb439e8720065d19a72b4b4e83900a3d11772ffb4ff39ffa3ff17e83965e8a3db9b716e0afa0530c8"
# seq_hexstr = b"0010cf8f0f1e2c58b071f2e5cb871f3e6cd8a143860d0a040810204080113274e8c183172e4c982152b479e2c58b070e0c183060c09123469c2942943962d4b973e6cd9b274e8c0902142850a051b265dab56bd6ad5bb66dca952b56bc69c2850b163c78f0f1e3d7bf6fdebd7bf6eddba75fbe7dead5ab478e1d2a448801123468d0b163c68d1b367cf8e1c3973f7eecc993376ecc8913265cb861d2a54b962d4a84192254a84192255aa459a2459a357ae4d9b377eeddbb67ce9d3b76fce9d3b77ffefdfbe7dfaf4f9e3d6ac4993366dca953a64d8a153a64c88103061c3870e0d1a357ae5daa55ba75faf5ebc79f2f5eac4982051a2448903172f4f9f3f7895831a2e0f098"
seq_hexstr = b"ffefcf8f0f1e2c58b071f2e5cb871f3e6cd8a143860d0a040810204080113274e8c183172e4c982152b479e2c58b070e0c183060c09123469c2942943962d4b973e6cd9b274e8c0902142850a051b265dab56bd6ad5bb66dca952b56bc69c2850b163c78f0f1e3d7bf6fdebd7bf6eddba75fbe7dead5ab478e1d2a448801123468d0b163c68d1b367cf8e1c3973f7eecc993376ecc8913265cb861d2a54b962d4a84192254a84192255aa459a2459a357ae4d9b377eeddbb67ce9d3b76fce9d3b77ffefdfbe7dfaf4f9e3d6ac4993366dca953a64d8a153a64c88103061c3870e0d1a357ae5daa55ba75faf5ebc79f2f5eac4982051a2448903172f4f9f3f7895831a2e0f098"
# shift=0

# CR=3
# seq_hexstr = b"a202e7fd1fc07fa2bb95ccba25802f47ff25d96e4bd05e8ff46ba35c1ba0d51688f446003401a00d0068a2039006803400a3451f22ed1768b947423a25f92e6971ce8e5472f296d0bb95dcae65d12c01700b805ca3a11808c02e0073479236919cdce4e5a7272d11b98dc86b496e4ba35d1ae0d732f91768bb45c00e4072a2d3968ca00d00cb465f28d9469a979634b1b18d0dcb2e5c68c36e1a739794bcb1a5dc8ce6e72d19404ba3191dc2fa3f80ff457231a5e5ff8dfc6ae9634bcbff1970d1b2cd17cbfe5ae2e3571a1b94d4b685f42ea23791a68d346801468f246d23681a025d18c8ee46d0368cb4718bdcffa1751b88dc9747fcbae5d72e39728d1978cbae5cd0e68a3e51b2dc97a23511bc8d65692dcc6e435a1ad0d28b9e5cb2b435a1a5173cb965ca68d34cae4d726995c9a4794b9a5cd06b9968cb975cb868d972e317b8b9c8d472cbc6ff717391a8e5972ffffaefe37fcb5c5c6ff35fda7f72b918d8c6ae3472e51a38d186dc34e72a33519a0dd06a8e5466a334b9a3451008c046a3711e82e017001b44d23ca5cd2eca34d1acb9659a2f97f9aff9574bb85dcffe5ff2ae3571a39d1c8065a26b93469a1c804744bf2fed3fb9fe8ff97d0e72e846e0727c6afe1a0fc0"
# shift=2

# CR=2
# seq_hexstr = b"44073fa3f03f46ec9c9682c05d1ff2ba570ba1747f8ee19c368691d23a0600d01a034028440c80d00a004518f25f4ba8711a23457caed1ce68c919722f45f9bb2725a0b01702e01c4688c0180700e51ca3d06e5ccb9d32e748f91b23742f95e3b8670de4bc97d2ea1c039032474ca89406809512f21a535a2e518b34668d94b2c618d71ae65c8b9462dc1b9732a2500b4468dc5e8fc0fd1ba33572ff1bf36e2cd5cbfc6b8d34b69797f2ee5cdb9a36568bd17a2e44dc9ad34a280114728f41a83402d11a3706a0d44b8c65dcfe8b91723e578ff5eeb9c739e638d71ae71ca39463c8695c2e81913726a5d0be46c8dd1aa34479cb29746a8d11e72ca595a6b49796b2d25e5a8e55dabb43792e35d7bae34d2cb19772ee4d8cb5c6fdcbb93632d75fffeefcdfcbb9737f6bfd3fe6e8cd19a734e798e318635c6b9963686d0da1a4658da1b4728a1102300645c8e85c0b803516a39576ae94d69a9652da5e5fdafe5b8b717e7fcbf96e69cd39a3202545acb4d28e408d15f2ff4ff9fe3fd7a399688cc2a08446d50a10"
# shift=4

# CR=1
# seq_hexstr = b"8818fc3c0f8fa4c2e360bc5f2f159bc5e2f1f8ccee151a0f060740a0501888240a03008c472bd3d8647038de5ea3138944b2dd2e9f4985c6c170780c8e060301804c643a192c926924d06934bb4da6e3f199d4ee57a7b0c024128d258281402c772317aad94dbe995d2ef663758a4965b29b6c32592c141b8986cbe1e07c7c3edf6f33fbedf6fb79bddeed572bf7ebf7cae955ba5f1e8f64aa5318046321d0d8e837130d86c763b19aec7e3d160d371befef318948c773798cc2623918acde0d1ec945a6d269768ac5229948b4562914ca452a9542a552a152a196eaf53a9d8ef7f7bbddecd76793d1eee67b3c9e8f77bbdfe7f5fbf5faf53e8f4f87d329944a46331bac524a351a9dc2a251a8d46631100c068b078b83c0ec5432dd5e2f54a2976ab95ea797db65d2f93cbe53289c48058aa54a61201c6f27d1e978df7c24b81c06811b1e6080"
# shift=6

#Drop First two bytes (why ?)
#Drop last few bytes (checksum and padding)
seq_hexa = numpy.frombuffer(binascii.unhexlify(seq_hexstr[:-50]), dtype=numpy.uint8)
seq = numpy.unpackbits(numpy.array(seq_hexa, dtype=numpy.uint8))

# shift = base_shift - shift
# nl=(len(seq)-shift)//(CR+4)
# newlen=(CR+4)*nl
# seq2 = numpy.reshape(seq[shift:newlen+shift], (nl, (CR+4)))

# nl=len(seq)//(CR+4)
# newlen=(CR+4)*nl
nl=len(seq)//4
newlen=4*nl
seq2 = numpy.reshape(seq[:newlen], (nl, 4))

#whitened_seq = seq2[:,CR:].flatten()[base_shift:]
whitened_seq = seq2.flatten()[base_shift:]

# #######Find Hamming code parameters######
# def encode_one_block(CR, data_block):
#     out = numpy.zeros(CR+4, dtype=numpy.uint8)

#     if CR == 4:
#         out[0] = data_block[0] ^ data_block[1] ^ data_block[3]
#         out[1] = data_block[0] ^ data_block[2] ^ data_block[3]
#         out[2] = data_block[0] ^ data_block[1] ^ data_block[2]
#         out[3] = data_block[1] ^ data_block[2] ^ data_block[3]

#         #Systematic part
#         out[4:] = data_block
#     elif CR == 3:
#         out[0] = data_block[0] ^ data_block[2] ^ data_block[3]
#         out[1] = data_block[0] ^ data_block[1] ^ data_block[2]
#         out[2] = data_block[1] ^ data_block[2] ^ data_block[3]

#         #Systematic part
#         out[3:] = data_block
#     elif CR == 2:
#         out[0] = data_block[0] ^ data_block[1] ^ data_block[2]
#         out[1] = data_block[1] ^ data_block[2] ^ data_block[3]

#         #Systematic part
#         out[2:] = data_block
#     elif CR == 1:
#         out[0] = data_block[0] ^ data_block[1] ^ data_block[2] ^ data_block[3]

#         #Systematic part
#         out[1:] = data_block
#     else:
#         out[4:] = numpy.zeros(CR)

#     return out

# seq3 = numpy.zeros((nl, (CR+4)), dtype=numpy.uint8)
# for i in range(0,nl):
#     seq3[i,:] = encode_one_block(CR, whitened_seq[(4*i):(4*i + 4)])


# #######Find LFSR parameters######

est_poly = -1
est_seed = -1
L = 63
found = False

while not found:
    L+=1
    
    if(L>64):
        break
    
    print('Searching a candidate polyniomial...')
    #est_poly = search_poly_lfsr(whitened_seq, L)
    est_poly = can_poly_lfsr(whitened_seq[:3*L], L)
    est_seed = numpy.flipud(whitened_seq[0:L])

    if len(est_poly) == 0:
        print('\n No candidate found for L = ' + str(L))
        continue

    print('Testing sequence generated by estimated LFSR...')    
    for can_poly in est_poly:
        can_poly = numpy.unpackbits(numpy.frombuffer(binascii.unhexlify(can_poly), dtype=numpy.uint8)).tolist()
        print('Trying with poly=' + str(binascii.hexlify(numpy.packbits(can_poly)))
              + ' and seed=' + str(binascii.hexlify(numpy.packbits(est_seed))))
        #print('Trying with poly=' + str(can_poly) + ' and seed=' + str(est_seed))
        est_seq = lfsr(can_poly, est_seed, len(whitened_seq))
        if (whitened_seq == est_seq).all():
            print('\nFound!')
            found = True
            break
        else:
            print('Reference and generated sequence have ' + str(numpy.sum(numpy.abs(whitened_seq - est_seq))) + ' bits that differs.')
    
    if not found:
        print('No sequence correspond.\n')