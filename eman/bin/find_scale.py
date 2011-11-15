#!/usr/bin/env python

#	$Id: find_scale.py,v 1.4 2005/10/19 16:01:16 gtang Exp $
#	find_scale.py	July 2004, Wen Jiang

import os
import sys
import random
import time
import string
try:
	from optparse import OptionParser
except:
	from optik import OptionParser
import EMAN

def main():
	(options,args) =  parse_command_line()

	LOGbegin(sys.argv)

	map1=EMAN.EMData()
	map1.readImage(args[0])

	map2=EMAN.EMData()
	map2.readImage(args[1])
	map2t = map2.copy()

	print "Start searching the scale factor in range [%g, %g]" % (options.scale_min,options.scale_max)
	scale = brent(matching_score,brack=[options.scale_min,options.scale_max],args=(map1,map2t))
	print "Final result: scale = %g" % (scale)
	if options.save_map or options.save_fsc:
		map2.setTAlign(0,0,0)
		map2.setRAlign(0,0,0)
		map2.rotateAndTranslate(scale)
		if options.save_map: 
			map2.writeImage(options.save_map)
			print "Final transformed map2 is saved to %s" % (options.save_map)
		if options.save_fsc: 
			fsc = map1.fsc(map2)
			if options.apix: EMAN.save_data(0,1.0/(options.apix*2.0*len(fsc)),fsc,len(fsc),options.save_fsc)
			else: EMAN.save_data(0,1.0,fsc,len(fsc),options.save_fsc)
			print "Final Fourier Shell Correlation curve is saved to %s" % (options.save_fsc)
	
	LOGend()

def matching_score(scale, map1, map2):
	map2.setTAlign(0,0,0)
	map2.setRAlign(0,0,0)
	map2.rotateAndTranslate(scale)
	fsc = map1.fsc(map2)
	return -sum(fsc)/len(fsc)

def parse_command_line():
	usage="%prog <input map1> <input map2> [options]"
	parser = OptionParser(usage=usage, version="%prog v1.0, July 2004. By Wen Jiang <wjiang@bcm.tmc.edu>")
	parser.add_option("--scale_min",dest="scale_min",type="float",metavar="<minimal scale>",help="the minimal scale to search to transform map2 to match map1",default=0.85)
	parser.add_option("--scale_max",dest="scale_max",type="float",metavar="<maximal scale>",help="the maximal scale to search to transform map2 to match map1",default=1.15)
	parser.add_option("--save_map",dest="save_map", type="string",metavar="<final transformed map>",help="the file name for saving the final transformed map2")
	parser.add_option("--save_fsc",dest="save_fsc", type="string",metavar="<final fsc curve>",help="the file name for saving the final Fourier Shell Correlation curve")
	parser.add_option("--apix",dest="apix", type="float",metavar="<Angstrom/pixel>",help="the sampling for map1")
	
	if len(sys.argv)<3: 
		parser.print_help()
		sys.exit(-1)
	
	(options, args)=parser.parse_args()

	if not len(args):
		parser.print_help()
		print "\nPlease specify the input and output mask maps"
		sys.exit(-1)
	
	return (options, args)

def LOGbegin(ARGV):
	out=open(".emanlog","a")
	b=string.split(ARGV[0],'/')
	ARGV[0]=b[len(b)-1]
	out.write("%d\t%d\t1\t%d\t%s\n"%(os.getpid(),time.time(),os.getppid(),string.join(ARGV," ")))
	out.close()

def LOGend():
	out=open(".emanlog","a")
	out.write("%d\t%d\t2\t-\t\n"%(os.getpid(),time.time()))
	out.close()

# the bracket and brent functions are taken from scipy.optimize.optimize.py
# 
def bracket(func, xa=0.0, xb=1.0, args=(), grow_limit=110.0):
    """Given a function and distinct initial points, search in the downhill
    direction (as defined by the initital points) and return new points
    xa, xb, xc that bracket the minimum of the function:
    f(xa) > f(xb) < f(xc)
    """
    _gold = 1.618034
    _verysmall_num = 1e-21
    fa = apply(func, (xa,)+args)
    fb = apply(func, (xb,)+args)
    if (fa < fb):                      # Switch so fa > fb 
        dum = xa; xa = xb; xb = dum
        dum = fa; fa = fb; fb = dum
    xc = xb + _gold*(xb-xa)
    fc = apply(func, (xc,)+args)
    funcalls = 3
    iter = 0
    while (fc < fb):
        tmp1 = (xb - xa)*(fb-fc)
        tmp2 = (xb - xc)*(fb-fa)
        val = tmp2-tmp1
        if abs(val) < _verysmall_num:
            denom = 2.0*_verysmall_num
        else:
            denom = 2.0*val
        w = xb - ((xb-xc)*tmp2-(xb-xa)*tmp1)/denom
        wlim = xb + grow_limit*(xc-xb)
        if iter > 1000:
            raise RunTimeError, "Too many iterations."
        if (w-xc)*(xb-w) > 0.0:
            fw = apply(func, (w,)+args)
            funcalls += 1
            if (fw < fc):
                xa = xb; xb=w; fa=fb; fb=fw
                return xa, xb, xc, fa, fb, fc, funcalls
            elif (fw > fb):
                xc = w; fc=fw
                return xa, xb, xc, fa, fb, fc, funcalls
            w = xc + _gold*(xc-xb)
            fw = apply(func, (w,)+args)
            funcalls += 1
        elif (w-wlim)*(wlim-xc) >= 0.0:
            w = wlim
            fw = apply(func, (w,)+args)
            funcalls += 1
        elif (w-wlim)*(xc-w) > 0.0:
            fw = apply(func, (w,)+args)
            funcalls += 1
            if (fw < fc):
                xb=xc; xc=w; w=xc+_gold*(xc-xb)
                fb=fc; fc=fw; fw=apply(func, (w,)+args)
                funcalls += 1
        else:
            w = xc + _gold*(xc-xb)
            fw = apply(func, (w,)+args)
            funcalls += 1
        xa=xb; xb=xc; xc=w
        fa=fb; fb=fc; fc=fw
    return xa, xb, xc, fa, fb, fc, funcalls
            
def brent(func, args=(), brack=None, tol=1.48e-8, full_output=0, maxiter=500):
    """ Given a function of one-variable and a possible bracketing interval,
    return the minimum of the function isolated to a fractional precision of
    tol. A bracketing interval is a triple (a,b,c) where (a<b<c) and
    func(b) < func(a),func(c).  If bracket is two numbers then they are
    assumed to be a starting interval for a downhill bracket search
    (see bracket)

    Uses inverse parabolic interpolation when possible to speed up convergence
    of golden section method.

    """
    _mintol = 1.0e-11
    _cg = 0.3819660
    if brack is None:
        xa,xb,xc,fa,fb,fc,funcalls = bracket(func, args=args)
    elif len(brack) == 2:
        xa,xb,xc,fa,fb,fc,funcalls = bracket(func, xa=brack[0], xb=brack[1], args=args)
    elif len(brack) == 3:
        xa,xb,xc = brack
        if (xa > xc):  # swap so xa < xc can be assumed
            dum = xa; xa=xc; xc=dum
        assert ((xa < xb) and (xb < xc)), "Not a bracketing interval."
        fa = apply(func, (xa,)+args)
        fb = apply(func, (xb,)+args)
        fc = apply(func, (xc,)+args)
        assert ((fb<fa) and (fb < fc)), "Not a bracketing interval."
        funcalls = 3
    else:
        raise ValuError, "Bracketing interval must be length 2 or 3 sequence."

    x=w=v=xb
    fw=fv=fx=apply(func, (x,)+args)
    if (xa < xc):
        a = xa; b = xc
    else:
        a = xc; b = xa
    deltax= 0.0
    funcalls = 1
    iter = 0
    while (iter < maxiter):
        tol1 = tol*abs(x) + _mintol
        tol2 = 2.0*tol1
        xmid = 0.5*(a+b)
        if abs(x-xmid) < (tol2-0.5*(b-a)):  # check for convergence
            xmin=x; fval=fx
            break
        if (abs(deltax) <= tol1):           
            if (x>=xmid): deltax=a-x       # do a golden section step
            else: deltax=b-x
            rat = _cg*deltax
        else:                              # do a parabolic step
            tmp1 = (x-w)*(fx-fv)
            tmp2 = (x-v)*(fx-fw)
            p = (x-v)*tmp2 - (x-w)*tmp1;
            tmp2 = 2.0*(tmp2-tmp1)
            if (tmp2 > 0.0): p = -p
            tmp2 = abs(tmp2)
            dx_temp = deltax
            deltax= rat
            # check parabolic fit
            if ((p > tmp2*(a-x)) and (p < tmp2*(b-x)) and (abs(p) < abs(0.5*tmp2*dx_temp))):
                rat = p*1.0/tmp2        # if parabolic step is useful.
                u = x + rat
                if ((u-a) < tol2 or (b-u) < tol2):
                    if xmid-x >= 0: rat = tol1
                    else: rat = -tol1
            else:
                if (x>=xmid): deltax=a-x # if it's not do a golden section step
                else: deltax=b-x
                rat = _cg*deltax

        if (abs(rat) < tol1):            # update by at least tol1
            if rat >= 0: u = x + tol1
            else: u = x - tol1
        else:
            u = x + rat
        fu = apply(func, (u,)+args)      # calculate new output value
        funcalls += 1

        if (fu > fx):                 # if it's bigger than current
            if (u<x): a=u
            else: b=u
            if (fu<=fw) or (w==x):
                v=w; w=u; fv=fw; fw=fu
            elif (fu<=fv) or (v==x) or (v==w):
                v=u; fv=fu
        else: 
            if (u >= x): a = x
            else: b = x
            v=w; w=x; x=u
            fv=fw; fw=fx; fx=fu
        
    xmin = x
    fval = fx
    if full_output:
        return xmin, fval, iter, funcalls
    else:
        return xmin
    
if __name__ == "__main__": main()
