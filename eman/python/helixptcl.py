#!/usr/bin/env python
# this will chop a tall image into overlapping pieces
# usage:
# helixptcl.py <infile> <outfile> <particle size>


import EMAN
from sys import argv

infile=argv[1]
outfile=argv[2]
ptclsize=int(argv[3])
bigimage=EMAN.EMData()
bigimage.readImage(infile,0)

nx=bigimage.xSize()
ny=bigimage.ySize()

for i in range(0,ny-ptclsize,ptclsize/2):
        clip=bigimage.clip(0,i,nx,ptclsize)
        clip.writeImage(outfile,-1)
