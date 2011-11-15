#!/usr/bin/env python

#N makeboxref.py
#F Generates an optimal set of reference projections from a 3D model for use in automatic particle selection
#T LM
#1
#P <threed file>	Input 3D model
#P [sym=<sym>]	Faster results if specified
#P [ang=<dalt>]	Angular increment for initial projection generation. Generally the default is adequate
#P [phi=<dphi>]	Angular increment for in-plane rotation. Generally default is adequate.
#P [nref=<# to gen>]	Number of references to generate, ok to specify more than you need
#P [invert]	Invert the contrast of the output projections (contrast must match micrograph being boxed)
#U makeboxref.py threed.4a.mrc invert
#D This program will generate a set of projections from a 3D model optimally sorted
#E for use as references in particle autoboxing in 'boxer'. The output file (best.hed)
#E contains an ordered list of projections sorted based on their mutual dissimilarity.
#E That is, you may generate 50 or more references, but use only the first 10 or 20. 
#D This file IS sorted, however, so you should ALWAYS use the first N particles in this file.
#E The only decision to make is how large N should be. That is, how many references to use. Most
#E particles will need at least 10 references for adequate boxing, and in many cases 30 or 40
#E is not unreasonable. To an extent this will depend on how much patience you have during
#E the automatic selection process. See the 'boxer' manual for more information.

import os
import sys
import string
import time
from sys import argv
from os import system

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


if (len(argv)<2):
	print "makeboxref.py <threed file> [sym=<sym>] [ang=<dalt>] [phi=<dphi>] [nref=<n to gen>] [invert]"
	sys.exit(1)

sym="c1"
ang=-1
phi=22.5
nref=40
invert=0

LOGbegin(argv)

for i in argv[2:] :
	s=string.split(i,'=')
	if (s[0]=="sym") : sym=s[1]
	elif (s[0]=="ang") : ang=float(s[1])
	elif (s[0]=="phi") : phi=float(s[1])
	elif (s[0]=="nref") : nref=int(s[1])
	elif (s[0]=="invert") : invert=1
	else: error(ERR_EXIT,"Unknown argument "+i)

if (ang==-1):
	ang=22.5
	div=1
	if (sym[0]=="c" or sym[0]=="C"): div=float(sym[1:])/4
	if (sym[0]=="d" or sym[0]=='D'): div=float(sym[1:])/2
	if (div<1.0) : div=1.0
	ang=ang/div
	print "angular spacing set to %f"%ang

system("project3d %s out=allphi.hed sym=%s prop=%f phitoo=%f"%(argv[1],sym,ang,phi))

system("classesbymra allphi.hed allphi.hed norot matrix split")

system("rm cls*.lst")

system("mx2img matrix.dat matrix.mrc")

system("matrixembed matrix.mrc self.loc euler=allphi.hed bestref=%d"%nref)

if (invert==1) : system ("proc2d best.hed best.hed inplace invert")

print "\n\nProcessing complete. Best refs are in 'best.hed'."

LOGend()
