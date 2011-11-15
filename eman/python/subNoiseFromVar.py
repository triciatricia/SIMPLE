#!/usr/bin/env python

# This program will substract the standard deviation introduced by noise from the total sigma map
# Junjie Zhang

from EMAN import *
from math import *
import os
import sys
import string
from sys import argv

if (len(argv)<4):
    print "subNoiseFromVar.py <standard deviation map file of total> <standard deviation map file from noise> <output noise-free sigma map>"
    sys.exit(1)

map_name_1=argv[1]
map_name_2=argv[2]

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
            map_out.setValueAt(x,y,z,sqrt(value_1*value_1-value_2*value_2))

map_out.writeImage(argv[3])


