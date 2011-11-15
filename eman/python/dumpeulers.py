#!/usr/bin/env python

# this simple script will read an input file and convert its Euler angles into Spider
# format, then printing them to standard out.

import sys
from EMAN import *
from math import *

r2d=180.0/pi

n=fileCount(sys.argv[1])[0]
if (n<1) :
	print "Please specify a filename"
	sys.exit(1)

image=EMData()
for i in range(n):
	image.readImage(sys.argv[1],i,1)
	eul=image.getEuler()
	print eul.phiSpider()*r2d,eul.thetaSpider()*r2d,eul.gammaSpider()*r2d
