#!/usr/bin/env python
# checkpitch.py	Steve Ludtke  3/8/04
# This program will check a volume dataset for helical symmetry
# and produce a plot containing quality values for each rotation
# in degrees (total rotation over 1 Z box height). It will
# also create files for each peak in this plot representing
# the qualities of different translational amounts with that
# particular pitch.

from EMAN import *
from sys import argv
from math import *
from sys import stdout,stderr

tst=EMData()
tst.readImage(argv[1],-1)

# tst2 is a copy of tst with the top and bottom 1/4 of the image zeroed
tst2=tst.clip(0,0,tst.zSize()/4,tst.xSize(),tst.ySize(),tst.zSize()/2)
tst2=tst2.clip(0,0,-tst.zSize()/4,tst.xSize(),tst.ySize(),tst.zSize())

#print("Dataset is %dx%dx%d"%(tst.xSize(),tst.ySize(),tst.zSize()))

# we ignore the near-zero shifts that would have small rotations
shifts=range(-tst.zSize()/4,-tst.zSize()/8)+range(tst.zSize()/8,tst.zSize()/4)

dlist=[0,0,0]
dlist2=[[],[],[]]
for da in range(-4*tst.xSize(),4*tst.xSize(),8):
	dot=0
	dots=[]
	for idz in shifts:
		dz=idz+.5
		t2=tst2.copy(0,0)
		t2.setRAlign(0,da*dz*2.0*pi/float(tst.xSize()*tst.zSize()),0)
#		print "\t",dz,"\t",da*dz*2.0*180.0/float(tst.xSize()*tst.zSize())
		t2.setTAlign(0,0,dz)
		t2.rotateAndTranslate()
		dot+=t2.dot(tst)
		dots.append([t2.dot(tst),dz])
	dlist.append((dot,da*2.0*180.0/float(tst.xSize())))
	del dlist[0]
	dlist2.append(dots)
	del dlist2[0]
	if (max(dlist)==dlist[1]) : 
		out=open("spc.%1.0f.txt"%(dlist[1][1]),"w")
		for i in dlist2[1]:
			out.write("%f\t%f\n"%(i[1],i[0]))
		out.close()
#	dot=dot[:len(dot)/4]+dot[3*len(dot)/4:]
	print da*2.0*180.0/float(tst.xSize()),"\t",dot/(tst.zSize()*tst.xSize())
#	print da*2.0*180.0/float(tst.xSize()),"\t",max(dot)[0],"\t",max(dot)[1]
#	print da*2.0*180.0/float(tst.xSize()),"\t",max(dot)[0]
	stdout.flush()

