#!/usr/bin/env python
from EMAN import *
from sys import argv

img=readImages(argv[1],-1,-1)
img2=range(len(img))

ref=img.makeAverage()
ref.writeImage("avg.hed",-1)

for j in range(8):
	for i in range(len(img)):
		x=img[i].copy(0,0)
		x.transAlign(ref)
		x.rotateAndTranslate()
		img2[i]=x
	
	ref=img2.makeAverage()
	ref.writeImage("avg.hed",-1)

