#!/usr/bin/env python
# This is used to align a tomographic tilt series translationally
# it will start at the middle and do translational alignments in both directions

from EMAN import *
from sys import argv,stdout
from math import floor

input=readImages(argv[1],-1,-1)
mask=input[0].copy(0,0)
mask.applyMask(mask.xSize()/3,7)
for i in input:
	i.maskNormalize(mask)

cen=len(input)/2

output=range(len(input))
output[cen]=input[cen].copy(0,0)
for i in range(cen-1,-1,-1):
	a=input[i].copy(0,0)
	a.applyMask(a.xSize()/2-10,4)
	a.realFilter(105,float(argv[3]),0)
	b=output[i+1].copy(0,0)
	if (i<cen-1) : b+=output[i+2]
	b.filter(a.xSize()/128.0,9999.0,8)
	b.maskNormalize(mask)
	b.applyMask(a.xSize()/2-10,4)
	b.realFilter(105,float(argv[3]),0)
	a.transAlign(b,0,0,a.xSize()/4)
	a.writeImage("tst.hed",-1)
	output[i+1].writeImage("tst.hed",-1)
	dx=a.Dx()
	dy=a.Dy()
	a=input[i].copy(0,0)
	a.setTAlign(dx,dy)
	a.rotateAndTranslate()
	print i,dx,dy
	output[i]=a

for i in range(cen+1,len(input)):
	a=input[i].copy(0,0)
	a.applyMask(a.xSize()/2-10,4)
	a.realFilter(105,float(argv[3]),0)
	b=output[i-1].copy(0,0)
	if (i>cen+1) : b+=output[i-2]
	b.filter(a.xSize()/128.0,9999.0,8)
	b.maskNormalize(mask)
	b.applyMask(a.xSize()/2-10,4)
	b.realFilter(105,float(argv[3]),0)
	a.transAlign(b,0,0,a.xSize()/4)
	dx=a.Dx()
	dy=a.Dy()
	a=input[i].copy(0,0)
	a.setTAlign(dx,dy)
	a.rotateAndTranslate()
	print i,dx,dy
	output[i]=a

for i,j in enumerate(output):
	j.writeImage(argv[2],i)
