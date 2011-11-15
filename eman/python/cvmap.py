#!/usr/bin/env python

#N cvmap.py
#F Generate the coefficient fo variantion (CV) map
#T X
#1
#P <standard deviation map file>    standard deviation map file produced by calculateMapVariance.py
#P <averaged map file>    averaged map file produced by calculateMapVariance.py
#P <cutoff density>    voxels with value below this density value should be treated as 0 
#P <output CV map file>    Output coefficient of variantion map
#U cvmap.py sdmap.mrc avg.mrc 0.5 cvmap.mrc
#D This program will generate the coefficient of variation map
#E contact okgeorge@gmail.com.

# cvmap.py <standard deviation map file> <averaged map file> <cutoff density> <output CV map file>

from EMAN import *
import os
import sys
import string
from sys import argv

if (len(argv)<5):
    print "cvmap.py <standard deviation map file> <averaged map file> <cutoff density> <output CV map file>"
    sys.exit(1)

map_name_1=argv[1]
map_name_2=argv[2]
delta=float(argv[3])

map_1=EMData()
map_2=EMData()

map_1.readImage(map_name_1)
map_2.readImage(map_name_2)

nx=map_1.xSize()
ny=map_1.ySize()
nz=map_1.zSize()

map_out=EMData()
map_out.setSize(nx,ny,nz)

for x in range(nx):
    for y in range(ny):
        for z in range(nz):
            value_1=map_1.valueAt(x,y,z)
            value_2=map_2.valueAt(x,y,z)
            if value_2<=delta:
                map_out.setValueAt(x,y,z,0.0)
            else:
                map_out.setValueAt(x,y,z,value_1/value_2)

scale=map_1.Mean()/map_out.Mean()

for x in range(nx):
    for y in range(ny):
        for z in range(nz):
            t=map_out.valueAt(x,y,z)
            map_out.setValueAt(x,y,z,t*scale)

map_out.writeImage(argv[4])

print map_1.Mean()
print map_2.Mean()
print map_out.Mean()

