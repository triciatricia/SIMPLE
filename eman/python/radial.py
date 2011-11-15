#!/usr/bin/env python

from EMAN import *
from sys import argv

x=EMData()
x.readImage(argv[1],-1)

y=x.project3d(0,0,0,-4)
y.radialAverage()

for i in range(y.xSize()/2):
	print i,y.valueAt(i+y.xSize()/2,y.ySize()/2,0)

