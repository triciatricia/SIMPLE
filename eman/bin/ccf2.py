#!/usr/bin/env python

import os
import sys
import random
import time
import string
import EMAN
from math import *
from sys import argv

if (len(argv)!=3) :
	print "Usage: ccf.py <target> <probe>"
	sys.exit(1)

target=EMAN.EMData()
target.readImage(argv[1],-1)
if (target.xSize()%2==1 or target.ySize()%2==1) :
	sys.exit(1)

probe=EMAN.EMData()
probe.readImage(argv[2],-1)
if (probe.xSize()%2==1 or probe.ySize()%2==1) :
	sys.exit(1)

targets=target.copy(0,0)
#targets.edgeNormalize()

probes=probe.copy(0,0)
#probes.edgeNormalize()

ccf=targets.calcCCF(probes)
ccf.toCorner()
print "Max correlation value %f at %s "%(ccf.Max(),ccf.MinLoc())
print "correlation value at center: %f"%(ccf.valueAt(probe.xSize()/2,probe.ySize()/2,probe.zSize()/2))
ccf.writeImage("ccf.mrc")
