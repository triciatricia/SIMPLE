#!/usr/bin/env python
# This example will read a set of h,k,amp,phase entries from a text file
# and construct a 2D real-space image of the defined crystal

from EMAN import *
from math import *

dh=10
dk=10

f=EMData()
f.setSize(130,128,1)
f.zero()
f.setComplex(1)
f.ri2ap()
nx=f.xSize()
ny=f.ySize()

infile=open("datax","r")
lines=infile.readlines()
infile.close()

for l in lines:
	v=l.split()
	x=int(floor(dh*int(v[0])+.5)*2)
	y=int(ny/2+floor(dk*int(v[1])+.5))
	f.setValueAt(x,y,0,float(v[2]))
	f.setValueAt(x+1,y,0,float(v[3])*pi/180.0)

f.update()
f.ap2ri()
# r.toCorner()
r=f.doIFT()
# r*=-1

r.writeImage("real.mrc")
