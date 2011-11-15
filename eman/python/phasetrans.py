#!/usr/bin/env python
import EMAN
from EMAN import EMData
import sys
from sys import argv
import os
import math
from math import pi

# this applies appropriate phase shifts
# for a real-space translation
def rephase(i,dx,dy):
	i.ri2ap()
	xs=i.xSize()/2
	ys=i.ySize()/2
	for y in range(-ys,ys):
		for x in range(xs):
			p=i.valueAt(x*2+1,y+ys,0)
			p+=pi*(dx*x/xs+dy*y/ys)
			i.setValueAt(x*2+1,y+ys,0,p)
	i.ap2ri()

# this will perform a rotation in Fourier space
def rotate(i,da):
	i.ap2ri()
	i2=i.copy(0,0)
	

RD=180.0/math.pi

if (len(argv)<3) :
	print "usage:"
	sys.exit(1)

d=EMData()
d.readImage(argv[1],int(argv[2]))

f=d.doFFT()
d.gimmeFFT()

rephase(f,0.25,0.0)
d=f.doIFT()
f.gimmeFFT()
d.writeImage("dx1.hed",-1)

rephase(f,0.25,0.0)
d=f.doIFT()
f.gimmeFFT()
d.writeImage("dx1.hed",-1)

rephase(f,0.25,0.0)
d=f.doIFT()
f.gimmeFFT()
d.writeImage("dx1.hed",-1)

rephase(f,0.25,0.0)
d=f.doIFT()
f.gimmeFFT()
d.writeImage("dx1.hed",-1)
