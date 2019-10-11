from math import floor, ceil
from sys import stdout as so
from bisect import bisect


def encode(x):

    precision = 32
    one = int(2**precision - 1)
    quarter = int(ceil(one/4))
    half = 2*quarter
    threequarters = 3*quarter
    
    
    #define my dictionary with fr and character
    fr=dict([chr(a),1] for a in range(256))
    s=sum(fr[a] for a in fr) #256
    p = dict([a,fr[a]/s] for a in fr)# eliminate zero probabilities
    
    y = [] # initialise output list
    lo,hi = 0,one # initialise lo and hi to be [0,1.0)
    straddle = 0 # initialise the straddle counter to 0
    x=x +chr(4)
    
    for k in range(len(x)): # for every symbol
        f=[0]
        
        
        # Compute cumulative probability as in Shannon-Fano
        for a in p:
            f.append(f[-1]+p[a])
        f.pop()
        f = dict([(a,mf) for a,mf in zip(p,f)])
        # arithmetic coding is slower than vl_encode, so we display a "progress bar"
        # to let the user know that we are processing the file and haven't crashed...
        if k % 100 == 0:
            so.write('Arithmetic encoded %d%%    \r' % int(floor(k/len(x)*100)))
            so.flush()

        # 1) calculate the interval range to be the difference between hi and lo and 
        # add 1 to the difference. The added 1 is necessary to avoid rounding issues
        lohi_range = hi - lo + 1
        #print(k)
        # 2) narrow the interval end-points [lo,hi) to the new range [f,f+p]
        # within the old interval [lo,hi], being careful to round 'innwards' so
        # the code remains prefix-free (you want to use the functions ceil and
        # floor). This will require two instructions. Note that we start computing
        # the new 'lo', then compute the new 'hi' using the scaled probability as
        # the offset from the new 'lo' to the new 'hi'
        lo = lo +int(ceil(lohi_range * f[x[k]]))
        hi = lo +int(floor(lohi_range *p[x[k]]))
        #print(lo,hi)
        if (lo == hi):
            raise NameError('Zero interval!')
            
        
        fr[x[k]]+=1
        s+=1
        p = dict([a,fr[a]/s] for a in fr)
        # Now we need to re-scale the interval if its end-points have bits in common,
        # and output the corresponding bits where appropriate. We will do this with an
        # infinite loop, that will break when none of the conditions for output / straddle
        i=0# are fulfilled
        while True:
            
            #print(f'lo ={lo}')
            #print(f'hi = {hi}')
            if hi < half: # if lo < hi < 1/2
                # stretch the interval by 2 and output a 0 followed by 'straddle' ones (if any)
                # and zero the straddle after that. In fact, HOLD OFF on doing the stretching:
                # we will do the stretching at the end of the if statement
                y.append(0) # append a zero to the output list y
                y.extend(straddle * [1]) # extend by a sequence of 'straddle' ones
                straddle = 0 # zero the straddle counter
            elif lo >= half: # if hi > lo >= 1/2
                # stretch the interval by 2 and substract 1, and output a 1 followed by 'straddle'
                # zeros (if any) and zero straddle after that. Again, HOLD OFF on doing the stretching
                # as this will be done after the if statement, but note that 2*interval - 1 is equivalent
                # to 2*(interval - 1/2), so for now just substract 1/2 from the interval upper and lower
                # bound (and don't forget that when we say "1/2" we mean the integer "half" we defined
                # above: this is an integer arithmetic implementation!
                y.append(1) # append a 1 to the output list y
                y.extend(straddle *[0]) # extend 'straddle' zeros
                straddle = 0 # reset the straddle counter
                hi = hi - half
                lo = lo - half# substract half from lo and hi
            
            
            
            
            elif lo >= quarter and hi < threequarters: # if 1/4 < lo < hi < 3/4
                # we can increment the straddle counter and stretch the interval around
                # the half way point. This can be impemented again as 2*(interval - 1/4),
                # and as we will stretch by 2 after the if statement all that needs doing
                # for now is to subtract 1/4 from the upper and lower bound
                straddle +=1 
                hi = hi - quarter
                lo = lo - quarter
        
            else:
                break # we break the infinite loop if the interval has reached an un-stretchable state
            # now we can stretch the interval (for all 3 conditions above) by multiplying by 2
            lo*= 2 
            hi = hi *2 +1# multiply hi by 2 and add 1 (I DON'T KNOW WHY +1 IS NECESSARY BUT IT IS. THIS IS MAGIC.
                # A BOX OF CHOCOLATES FOR ANYONE WHO GIVES ME A WELL ARGUED REASON FOR THIS... It seems
            
    # to solve a minor precision problem.)
    # termination bits
    # after processing all input symbols, flush any bits still in the 'straddle' pipeline
    straddle += 1 # adding 1 to straddle for "good measure" (ensures prefix-freeness)
    if lo < quarter: # the position of lo determines the dyadic interval that fits
        y.append(0) # output a zero followed by "straddle" ones
        y.extend(straddle *[1])
    else:
        y.append(1)
        y.extend(straddle * [0])# output a 1 followed by "straddle" zeros

    return(y)




def decode(y):
    precision = 32
    one = int(2**precision - 1)
    quarter = int(ceil(one/4))
    half = 2*quarter
    threequarters = 3*quarter

    fr=dict([chr(a),1] for a in range(256))
    s=sum(fr[a] for a in fr)
    p = dict([a,fr[a]/s] for a in fr)# eliminate zero probabilities
    
    alphabet = list(p)


    y.extend(precision*[0])
    # dummy zeros to prevent index out of bound errors
    #x = n*[0] # initialise all zeros 
    x=[]
    # initialise by taking first 'precision' bits from y and converting to a number
    value = int(''.join(str(a) for a in y[0:precision]), 2)
    #print(y[0:precision])
    y_position = precision # position where currently reading y
    lo,hi = 0,one
    x_position =0
    
    while 1:
        #if x_position % 100 == 0:
            #so.write('Arithmetic decoded %d%%    \r' % int(floor(x_position/n*100)))
            #so.flush()
        
        
        f = [0]
        for a in p:
            f.append(f[-1]+p[a])
        f.pop()
        fa = dict([(a,mf) for a,mf in zip(p,f)])
        
        
        
        lohi_range = hi - lo + 1
        # This is an essential subtelty: the slowest part of the decoder is figuring out
        # which symbol lands us in an interval that contains the encoded binary string.
        # This can be extremely wasteful (o(n) where n is the alphabet size) if you proceed
        # by simple looping and comparing. Here we use Python's "bisect" function that
        # implements a binary search and is 100 times more efficient. Try
        # for a = [a for a in f if f[a]<(value-lo)/lohi_range)][-1] for a MUCH slower solution.
        a = bisect(f , (value-lo)/lohi_range) - 1
        x.append(alphabet[a]) # output alphabet[a]
        
        if x[x_position]==chr(4):
            x.pop()
            break
        
        lo = lo + int(ceil(fa[alphabet[a]]*lohi_range))
        hi = lo + int(floor(p[alphabet[a]]*lohi_range))
        if (lo == hi):
            raise NameError('Zero interval!')
       
        
        
        fr[alphabet[a]]+=1
        s+=1
        p = dict([a,fr[a]/s] for a in fr)
        
        
        while True:
            if hi < half:
                # do nothing
                pass
            elif lo >= half:
                lo = lo - half
                hi = hi - half
                value = value - half
            elif lo >= quarter and hi < threequarters:
                lo = lo - quarter
                hi = hi - quarter
                value = value - quarter
            else:
                break
            lo = 2*lo
            hi = 2*hi + 1
            value = 2*value + y[y_position]
            y_position += 1
            if y_position == len(y):
                    break
        
        x_position +=1
        if y_position == len(y):
            break
    
    return(x)
    

