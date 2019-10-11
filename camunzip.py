from trees import *
from vl_codes import *
import arithmetic_ftr
import arithmetic
import arithmetic_ftr_adaptive
from json import load
from sys import argv, exit


def camunzip(filename):
    if (filename[-1] == 'h'):
        method = 'huffman'
    elif (filename[-1] == 's'):
        method = 'shannon_fano'
    elif (filename[-2]+filename[-1] == 'ar'):
        print("dfass")
        method = 'arithmetic'
    elif (filename[-2]+filename[-1]=='ad'):
        method = 'arithmetic_adaptive'
    elif (filename[-2]+filename[-1]=='ca'):
        method = 'context_adaptive'
    else:
        raise NameError('Unknown compression method')
    
    with open(filename, 'rb') as fin:
        y = fin.read()
    y = bytes2bits(y)
    if method == 'arithmetic' or method == 'arithmetic_adaptive' or method == 'context_adaptive':
        pfile = filename[:-2] + 'p'
    else:
         pfile = filename[:-1] + 'p'
    with open(pfile, 'r') as fp:
        frequencies = load(fp)
    
    n = sum([frequencies[a] for a in frequencies])
    p = dict([(a,frequencies[a]/n) for a in frequencies])

    if method == 'huffman' or method == 'shannon_fano':
        if (method == 'huffman'):
            xt = huffman(p)
            c = xtree2code(xt)
        else:
            c = shannon_fano(p)
            xt = code2xtree(c)

        x = vl_decode(y, xt)

    elif method == 'arithmetic_adaptive':
        x = arithmetic_ftr_adaptive.decode(y)
        
    elif method =='arithmetic':
        x = arithmetic.decode(y,p,n)
    
    elif method =='context_adaptive':
        x = arithmetic_ftr.decode(y)
    
    else:
        raise NameError('This will never happen (famous last words)')
    
    #'.cuz' for Cam UnZipped (don't want to overwrite the original file...)
    if method == 'arithmetic' or method == 'arithmetic_adaptive' or method == 'context_adaptive':
        outfile= filename[:-5]+'.cuz'
    else:
        outfile = filename[:-4] + '.cuz' 
    with open(outfile, 'w') as fout:
        for c in x:
              fout.write(c)

if __name__ == "__main__":
    if (len(argv) != 2):
        print('Usage: python %s filename\n' % argv[0])
        print('Example: python %s hamlet.txt.czh' % argv[0])
        print('or:      python %s hamlet.txt.czs' % argv[0])
        print('or:      python %s hamlet.txt.czar' % argv[0])
        exit()

    camunzip(argv[1])
