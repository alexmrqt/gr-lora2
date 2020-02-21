import scipy
import numpy
import json

f_base = 'UNCOH_LORA_BER_basic_t_sel'

fid = open(f_base + '.raw')
BER = scipy.fromfile(fid)
fid.close()

EbN0dB = numpy.linspace(0,10,11)

fmt = {
        'EbN0dB': EbN0dB.tolist(),
        'BER': BER.tolist()
        }

fid = open(f_base + '.json', 'w')
json.dump(fmt, fid)
fid.close()
