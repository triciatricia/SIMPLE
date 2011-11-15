#!/usr/bin/env python

from EMAN import *
from math import *
import os

xsize=64
ysize=64
zsize=128
border=12
pitch=64
star=1
lumprepeat=8.0
lumpsize=3.0
dz=0.0

rad=(xsize-border*2)/2

im=EMData()
im.setSize(xsize,ysize,zsize)
im.zero()

for z in range(zsize):
	cz=lumprepeat/2.0+z-(z%lumprepeat)
	cx=.75*rad*cos(-2.0*cz*pi/pitch)+xsize/2
	cy=.75*rad*sin(-2.0*cz*pi/pitch)+ysize/2
	for y in range(border,ysize-border):
		for x in range(border,xsize-border):
			r=hypot(x-xsize/2.0,y-ysize/2.0)
			if (r>rad): continue
			a=atan2(y-ysize/2.0,x-xsize/2.0)

			v=0.0
			# this is a smooth, continuous helix
			v+=(1.0+tanh(r))*(1.0-tanh(r-rad+3))*cos(a/2.0+(z-dz)*pi/pitch)**4

			# These are lumps
			v+=4.0*exp(-((cx-x)**2+(cy-y)**2+(cz-(z-dz))**2)/lumpsize**2)
			v+=4.0*exp(-((cx-x)**2+(cy-y)**2+(cz-(z-dz-lumpsize*2.0))**2)/lumpsize**2)

			im.setValueAt(x,y,z,v)

im3=im.copy(0,0)
for i in range(1,star):
	im2=im3.copy(0,0)
	im2.setRAlign(0,float(i)/star*pi*2.0,0)
	im2.rotateAndTranslate()
	im+=im2

im.writeImage("helix.mrc")
os.system("chimera helix.mrc")
