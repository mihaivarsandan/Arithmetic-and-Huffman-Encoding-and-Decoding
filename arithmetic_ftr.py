from math import floor, ceil
from sys import stdout as so
from bisect import bisect
from time import sleep
def encode(x):

    precision = 32
    one = int(2**precision - 1)
    quarter = int(ceil(one/4))
    half = 2*quarter
    threequarters = 3*quarter
    
    #creating an initial dictionary with the count
    p = dict([chr(a), dict([chr(a), 1] for a in range(256))] for a in range(256))
    
    
    # creating an initial uniform distribution
    cdf = 0
    f = {} 
    for a in range(256): 
        f[chr(a)] = cdf
        cdf += 1/256


    y = [] # initialise output list
    lo,hi = 0,one # initialise lo and hi to be [0,1.0)
    straddle = 0 # initialise the straddle counter to 0
 
            
    x= x + chr(4)  #append end of transmission character in the end

    for k in range(len(x)): # for every symbol
        # arithmetic coding is slower than vl_encode, so we display a "progress bar"
        # to let the user know that we are processing the file and haven't crashed...
        
        if k % 100 == 0:
            so.write('Arithmetic encoded %d%%    \r' % int(floor(k/len(x)*100)))
            so.flush()

       
        # 1) calculate the interval range to be the difference between hi and lo and 
        # add 1 to the difference. The added 1 is necessary to avoid rounding issues
        # lohi_range = ....
        lohi_range = hi - lo + 1
        # 2) narrow the interval end-points [lo,hi) to the new range [f,f+p]
        # within the old interval [lo,hi], beiang careful to round 'innwards' so
        # the code remains prefix-free (you want to use the functions ceil and
        # floor). This will require two instructions. Note that we start computing
        # the new 'lo', then compute the new 'hi' using the scaled probability as
        # the offset from the new 'lo' to the new 'hi'
        # ...
        # ...


         # for each symbol in the file to encode
        #for the first symbol we must use the uniform distribution
        if k == 0: 
            lo = lo + int(ceil(f[x[k]]*lohi_range))
            hi = lo + int(floor(1/256*lohi_range))
        else:
            n = 0
            for key, val in p[previous].items():
                n += val #add all the frequncies

            cdf = 0
            f = {}
            #compute the cdf for that specific dictionary
            for key, value in p[previous].items():
                f[key] = cdf
                cdf += value/n
            
            lo = lo + int(ceil(f[x[k]]*lohi_range)) # add cdf of a scaled by lohi_range
            hi = lo + int(floor(p[previous][x[k]]/n*lohi_range)) # access the conditional probablity of the letter
        
        if (lo == hi):
            raise NameError('Zero interval!')

        # Now we need to re-scale the interval if its end-points have bits in common,
        # andw output the corresponding bits where appropriate. We will do this with an
        # infinite loop, that will break when none of the conditions for output / straddle
        # are fulfilled
        while True:
            if hi < half: # if lo < hi < 1/2
                # stretch the interval by 2 and output a 0 followed by 'straddle' ones (if any)
                # and zero the straddle after that. In fact, HOLD OFF on doing the stretching:
                # we will do the stretching at the end of the if statement
                y.append(0)#append a zero to the output list y
                y.extend(straddle * [1])#extend by a sequence of 'straddle' ones
                straddle = 0 #zero the straddle counter
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

        if  k == 0:
            pass 
        else:
            p[previous][x[k]] += 1 # Update the conditional dictionary frequencies
        previous = x[k] # set previous letter as current letter
        
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
    
    #creating an initial dictionary with the count
    p = dict([chr(a), dict([chr(a), 1] for a in range(256))] for a in range(256))

    alphabet = list(p)
    
    
    #compute the initial cdf as uniform
    f = [0] 
    for b in p:
        f.append(f[-1] + 1/256)
    f.pop()

    y.extend(precision*[0]) # dummy zeros to prevent index out of bound errors
    x = []

    # initialise by taking first 'precision' bits from y and converting to a number
    value = int(''.join(str(b) for b in y[0:precision]), 2) 
    y_position = precision # position where currently reading y
    
    
    lo,hi = 0,one
    x_position=0
    lohi_range = hi - lo + 1
    a = bisect(f, (value-lo)/lohi_range) - 1 
   

    while 1:

        lohi_range = hi - lo + 1 #it is needed twice so that everytime it goes into the loop it recalculates lohi_range
        
        if len(x) == 0:
            x.append(alphabet[a])
            lo = lo + int(ceil(f[a]*lohi_range))
            hi = lo + int(floor(1/256*lohi_range))
        else:
            n = 0
            for key, val in p[previous].items():
                n += val#add all the frequncies
            
            # Compute the new cdf
            f = [0] 
            for key, count in p[previous].items():
                f.append(f[-1]+count/n)
            f.pop()

            a = bisect(f, (value-lo)/lohi_range) - 1
            x.append(alphabet[a])
            if alphabet[a] == chr(4): # Stop after decoding the end of transmission character
                x.pop()
                break
            
            lo = lo + int(ceil(f[a]*lohi_range)) 
            hi = lo + int(floor(p[previous][alphabet[a]]/n*lohi_range))
        
        if (lo == hi):
            raise NameError('Zero interval!')

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
            x_position += 1
        if y_position == len(y):
            break
        if len(x) == 1:
            pass
        else:  
            p[previous][alphabet[a]] += 1 # Update the frequencies
        previous = alphabet[a] # Update the previous value    
    return(x)
    
