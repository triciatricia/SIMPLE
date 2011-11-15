#!/usr/bin/env python
from EMAN import *
from sys import argv

ref=EMData()
ref.readImage(argv[1],0)

n=fileCount(argv[2])
for i in range(n):
	x=EMData()
	x.readImage(argv[2],i)
	x.edgeNormalize()
	x.transAlign(ref,0,0,x.xSize()/4)
	x.setTAlign(x.Dx(),0)
	x.rotateAndTranslate()
	x.writeImage(argv[3],-1)
