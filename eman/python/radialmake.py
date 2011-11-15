#!/usr/bin/env python
# This will make a spherically symmetric volume with a given radial profile

from EMAN import *
from sys import argv
from math import *

def gaus(x,c,w) : return exp(-((x-c)/w)**2)

a=EMData()
a.setSize(128,128,128)
a.zero()

for x in range(128):
	for y in range(128):
		for z in range(128):
			r=sqrt((x-64)**2+(y-64)**2+(z-64)**2)
			a.setValueAt(x,y,z,gaus(r,40,4)+gaus(r,50,4))

a.writeImage("x.mrc",0)
a.display()

