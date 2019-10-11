from trees import *
from vl_codes import *
import arithmetic_ftr
import arithmetic
import arithmetic_ftr_adaptive
from itertools import groupby
from json import dump
from sys import argv
import time


def camzip(method, filename):
    
    with open(filename, 'r') as fin:
        x = fin.read()

    frequencies = dict([(key, len(list(group))) for key, group in groupby(sorted(x))])
    n = sum([frequencies[a] for a in frequencies])
    p = dict([(a,frequencies[a]/n) for a in frequencies])

    if method == 'huffman' or method == 'shannon_fano':
        if (method == 'huffman'):
            start =time.time() #start count 
            xt = huffman(p)
            c = xtree2code(xt)
            end = time.time()
            timer = end-start
            print(f'Huffman compression time:{timer}')
        else:
            c = shannon_fano(p)
            xt = code2xtree(c)

        y = vl_encode(x, c)

    elif method == 'arithmetic':
        y = arithmetic.encode(x,p)
        
    elif method == 'arithmetic_adaptive':
        y = arithmetic_ftr_adaptive.encode(x)
    
    elif method == 'context_adaptive':
        y = arithmetic_ftr.encode(x)

    else:
        raise NameError('Compression method %s unknown' % method)
    
    zipped = bits2bytes(y)
    y = bytes(bits2bytes(y))
    
    if method == 'arithmetic':
        outfile = filename + '.cz' +'ar'
    elif method =='arithmetic_adaptive':
        outfile = filename + '.cz' + 'ad'
    elif method =='context_adaptive':
        outfile = filename + '.cz' + 'ca'
    
    else:
        outfile = filename + '.cz' + method[0]

    with open(outfile, 'wb') as fout:
        fout.write(y)

    pfile = filename + '.czp'
    n = len(x)

    with open(pfile, 'w') as fp:
        dump(frequencies, fp)
        
    #finding the entropy and the compression rate
    
    C= 8*len(zipped)/n
    H= lambda p: -sum([p[a]*log2(p[a]) for a in p])
    print(f'Compression Rate:{C}')
    print(f'Entropy :{H(p)}')
    print(f'File size (bytes): {n}')


if __name__ == "__main__":
    if (len(argv) != 3):
        print('Usage: python %s compression_method filename\n' % argv[0])
        print('Example: python %s huffman hamlet.txt' % argv[0])
        print('or:      python %s shannon_fano hamlet.txt' % argv[0])
        print('or:      python %s arithmetic hamlet.txt' % argv[0])
        exit()

    camzip(argv[1], argv[2])

