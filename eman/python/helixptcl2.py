#!/usr/bin/env python
# this will chop a tall image into overlapping pieces
# usage:
# helixptcl.py <infile> <outfile> <particle size> <vertical step>


import EMAN
from sys import argv

infile=argv[1]
outfile=argv[2]
ptclsize=int(argv[3])
try : vstep=int(argv[4])
except : vstep=ptclsize/2
if vstep<1 : vstep=ptclsize/2

bigimage=EMAN.EMData()
bigimage.readImage(infile,0)

nx=bigimage.xSize()
ny=bigimage.ySize()

for i in range(0,ny-ptclsize,vstep):
        clip=bigimage.clip(0,i,nx,ptclsize)
        clip.writeImage(outfile,-1)
