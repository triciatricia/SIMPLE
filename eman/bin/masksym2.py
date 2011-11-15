#!/usr/bin/env python

###	masksym2.py	Wen Jiang
### This program extends the original masksym.py to support multiple subunit and symmetry masks
###

import os
import sys
import random
import time
import string
try:
	from optparse import OptionParser
except:
	from optik import OptionParser
from math import pi
import EMAN

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


def parse_command_line():
	usage="%prog <input mask 1> ... <input mask n> <output mask> [options]"
	parser = OptionParser(usage=usage, version="%prog v2.0, June 2004. By Wen Jiang <wjiang@bcm.tmc.edu>")
	parser.add_option("--sym",dest="sym",type="string",metavar="<symmetry>",help="the symmetry to consider when iteratively expanding of the masks")
	parser.add_option("--extend",dest="xtend",type="int",metavar="<n>",help="number of shells to expand")
	
	if len(sys.argv)<4: 
		parser.print_help()
		sys.exit(-1)
	
	(options, args)=parser.parse_args()

	if not len(args):
		parser.print_help()
		print "\nPlease specify the input and output mask maps"
		sys.exit(-1)
	
	return (options, args)

#### MAIN

sym='c1'
xtend=0
maskdata=None
nmask = 1

(options,args) =  parse_command_line()

sym=options.sym
xtend=options.xtend
inmasks = args[0:-1]	# ignore the last output filename (args[-1])
nmask=len(inmasks)	

LOGbegin(sys.argv)

img=EMAN.EMData()

print "Reading %d/%d masks: %s" % ( 1, nmask, inmasks[0])
img.readImage(inmasks[0],-1)
if (img.zSize<2) :
	print "masksym.py only functions on volumetric data"
	sys.exit(1)

# prepare a map inlcuding all masks with values: 1,2,..
out=img.copy(0,0)
out.realFilter(2,.5)
if nmask>1:
	for i in range(1,nmask):
		print "Reading %d/%d masks: %s" % ( i+1, nmask, inmasks[i])
		img.readImage(inmasks[i],-1)
		img.realFilter(2,.5)	# binarize to 0 or 1
		img*=i+1
		out.addAsMask(img)

if sym!="c1":
	out0 = out.copy()
	c = out0.copy()
	
	# now consider all the symmetry related locations
	eul=EMAN.Euler(0,0,0)
	eul.setSym(sym)

	num_sym = eul.getMaxSymEl()
	for n in range(1,num_sym):
		e=eul.SymN(n)
		print "Applying symmetry %d/%d: euler=%g\t%g\t%g" % ( n+1, num_sym, e.alt()*180./pi,e.az()*180./pi,e.phi()*180./pi,)
		c.setRAlign(e.alt(),e.az(),e.phi())
		c.rotateAndTranslate()
		c.realFilter(114)	# int(x)!=x -> x=0 to remove the soft edges
		c+=n*nmask
		c.realFilter(0,n*nmask+0.5)	# x < xmin -> x=0 to remove the background
		out.addAsMask(c)

		n+=1
		e=eul.NextSym()

if (xtend>0) : 
	print "Extending masks ..."
	out.realFilter(111,float(xtend))

out.writeImage(args[-1])

LOGend()

