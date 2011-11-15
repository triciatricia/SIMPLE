#!/usr/bin/env python
# powdcmp  6/5/03  Steve Ludtke
# Copyright 2003  Baylor College of Medicine

#N powdcmp
#F This will determine a set of orthogonal basis images from a set of projections
#T LA
#1
#P <images>	Input file, images to be analyzed
#P <basis>	Output file, set of orthogonal basis images
#P [n=<n basis>]	Number of basis images to output (<= number of input images)
#P [mask=<radius>]	Mask radius in pixels (use the smallest reasonable value)
#U powdcmp proj.hed basis.hed
#D This program is designed to produce a set of orthogonal basis images to
#E use for noise reduction on raw particles. Typically this program will
#E be used on a set of projections covering the asymmetric triangle, but
#E with no in-plane rotation. Unlike geodcmp, this program will sequence the
#E images in order of dissimilarity. In addition, each projection is aligned
#E to the existing basis set. This alignment should deal with the problem
#E of a single particle orientation having several possible 'best' orientations
#E when using total projected power as an orientation measure.

import os
import sys
import random
import time
import string
from os import system
from os import unlink
from sys import argv
import EMAN
from math import *

#### MAIN

if (len(argv)<2) :
	print "Usage:/npowdcmp <images> <basis> [n=<nbasis>] [mask=<radius>]"
	sys.exit(1)

nbasis=20
mask=-1

for i in argv[3:] :
#	s=i.split('=')
	s=string.split(i,'=')
	if (s[0]=="n") : nbasis=int(s[1])
	elif (s[0]=="mask") : mask=int(s[1])
	else:
		print "Unknown argument ",i
		exit(1)

EMAN.LOGbegin(argv)

n=EMAN.fileCount(argv[1])
if (n<2) :
	print("Umm... I'd really be happier if the input file had at least 2 images...")
	sys.exit(1)

nbasis=min(n,nbasis)
print "%d source images to consider\nGenerating %d basis images\n"%(n,nbasis)

basis=[EMAN.EMData()]			# the actual basis vectors
basisn=[0]						# list of the input image number used to generate each basis vector
basis[0].readImage(argv[1],0)
basis[0].realFilter(30)			# 'true' normalization. We'll use this a lot
nx=basis[0].xSize()
da=atan2(1.0,nx/2.0)			# da represents 1 pixel at the edge of the image

orig=EMAN.EMData()
ali=orig.copy()
ali.setTAlign(0,0,0)
for bn in range(1,nbasis):		# this loops over the output basis images

	for i in range(1,n):		# loops over the unused input images
		if i in basisn: continue
		orig.readImage(argv[1],i)

		a=0
		while (a<pi*2):
			ali.setRAlign(a,0,0)
			ali.rotateAndTranslate()
			ali.realFilter(30)
			pwr=ali.copyHead()
			pwr.zero()
			for b in basis:
				ccf=ali.calcCCF(b)
				ccf.mult(ccf)


EMAN.LOGend()