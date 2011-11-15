#!/usr/bin/env python
import EMAN
import sys
from sys import argv
import os
import math

RD=180.0/math.pi

if (len(argv)<3) :
	print "fsctest.py <refs> <ref #> <ptcl file> <ptcl #>"
	sys.exit(1)

refs=EMAN.readImages(argv[1],-1,-1)
ptcl=EMAN.EMData()
ptcl.readImage(argv[3],int(argv[4]))
ptcl.edgeNormalize()
ptclf=ptcl.copy(0,0);
ptclf.vFlip()


for i in refs:
	i.normalize()

ali=ptcl.RTFAlign(refs[int(argv[2])],ptclf,1)
ali.refineAlign(i)
fsc=(1.0+ali.fscmp(refs[int(argv[2])],None))*500.0
print fsc

