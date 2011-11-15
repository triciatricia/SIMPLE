#!/usr/bin/env python
# This script will read a text file containing a list of image
# filenames. Each image should represent an aligned helical segment.
# It will generate an incoherently averaged power spectrum

from EMAN import *
from math import *
import sys
import os

if (len(sys.argv)<2) : 
	print "xtalresan.py <file> [<size>]"
	os.exit(1)
	

infile=open(sys.argv[1],"r")
imlist=infile.readlines()
infile.close()

if (len(sys.argv)>2) : size=int(sys.argv[2])
else :size=4096

print "Generating average size %d x %d"%(size,size)
	
single=EMData()
avg=EMData()
avg.setSize(size+2,size,1)
avg.zero()
avg.setComplex(1)
for img in imlist:
	img=img.strip()
	single.readImage(img,0)
	nx=single.xSize()
	ny=single.ySize()

	if (ny<size) : 
		print "Process: ",img
		single.edgeNormalize()
		pad=single.clip(-(size-nx)/2,-(size-ny)/2,size,size)
		padf=pad.doFFT()
		avg.addIncoherent(padf)
	else :
		for i in range(0,int(ceil(ny/size))) :
			print "Process (%d/%d): %s"%(i,int(ceil(ny/size)),img)
			y=i*size
			if (y+size>ny) : y=ny-size
			pad=single.clip(-(size-nx)/2,y,size,size)
			pad.edgeNormalize()
			padf=pad.doFFT()
			avg.addIncoherent(padf)

avg.writeImage("sum.mrc")


