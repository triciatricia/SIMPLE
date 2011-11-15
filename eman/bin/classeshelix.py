#!/usr/bin/env python
###	classeshelix.py	Steven Ludtke	10/2003
### Program for classifying and aligning helical segments

#N classeshelix.py
#F This program will align and classify helical segments vs a set of reference projections
#T X
#1
#P <segments>	Unclassified sections of helical data, should be ~1 pitch long
#P <ref>	Set of reference projections to classify against
#P [maxbend=<deg>]	Maximum in-plane rotation of helical segments
#D Not documented yet

import os
import sys
import random
import time
import string
import math
from os import system
from os import unlink
from sys import argv
import EMAN

def LOGbegin(ARGV):
	out=open(".emanlog","a")
	b=string.split(ARGV[0],'/')
	ARGV[0]=b[len(b)-1]
	out.write("%d\t%d\t1\t%d\t%s\n"%(os.getpid(),time.time(),os.getppid(),string.join(ARGV," ")))
	out.close()

def LOGend():
	out=open(".emanlog","a")
	out.write("%d\t%d\t2\t-\t\n"%(os.getpid(),time.time()))
	out.close()


#### MAIN

if (len(argv)<2) :
	print "classeshelix.py <segments> <ref> [maxbend=<deg>]"
	sys.exit(1)

pi=math.pi
maxbend=5.0


for i in argv[3:] :
#	s=i.split('=')
	s=string.split(i,'=')
	if (s[0]=="maxbend") : maxbend=float(s[1])
	else:
		print "Unknown argument ",i
		exit(1)

d=EMAN.EMData()
# get info from first 'particle' image
d.readImage(argv[1],0,1)
nx=d.xSize()
ny=d.ySize()
nptcl=EMAN.fileCount(argv[1])[0]

# Get references
refs=EMAN.readImages(argv[2],-1,-1)
nxr=refs[0].xSize()
nyr=refs[0].ySize()
nref=len(refs)

# initialize class files
for im in refs:
	ind=refs.index(im)
	try:
		unlink("cls%04d.hed"%ind)
		unlink("cls%04d.img"%ind)
	except:
		pass
	im.writeImage("cls%04d.hed"%ind,0)

#for i in refs:
#	i*=1.0/i.SumSq()

LOGbegin(argv)
maxbend=maxbend*pi/180.0
da=math.atan(1.0/ny)
da=maxbend/math.floor(maxbend/da)
print "maxbend=%f da=%f"%(maxbend*180.0/pi,da*180.0/pi)

# main classification loop
for ptcli in range(nptcl):
	# read a particle and resize to match references
	d=EMAN.EMData()
	d.readImage(argv[1],ptcli)
	d.edgeNormalize(2)
	ptcl=d.clip(-(nxr-nx)/2,-(nyr-ny)/2,nxr,nyr);
	best=[1.0e25,-1,0.0,(0,0,0)]

	for iref in range(nref):
		ang=-maxbend
		while (ang<=maxbend) :
			ref=refs[iref].copy(0,0)
			ref.setRAlign(ang,0,0)
			ref.setTAlign(0,0,0)
			ref.rotateAndTranslate()
			ref*=1.0/ref.SumSq()
			ref.transAlign(ptcl,0,1,ny/2)
			dd=(ref.Dx(),ref.Dy())
			ref.rotateAndTranslate()
			max=ref.lcmp(ptcl,1)[0]
#			if (math.fabs(ang)<.0001) : print iref,max
			if (max<best[0]) :
				best=[max,iref,ang,dd]
			ang+=da
#			ccf.display()
	print ptcli,"\t",best,
	ptcl.setRAlign(-best[2],0,0)
	ptcl.setTAlign(0,0);
	ptcl.rotateAndTranslate()

	ptcl.transAlign(refs[best[1]],0,1,ny/2)
	dy=int(ptcl.Dy())
	dx=ptcl.Dx()
	cp=ptcl.copy(0,0)
	ptcl.rotateAndTranslate()
	ptcl.writeImage("cls%04d.hed"%best[1],-1)

	if (dy<0) : sn=-1
	else : sn=1

	cp2=cp.copy(0,1)
	bv=1.0e24
	bd=0
	for d in range(dy+sn*ny-ny/10,dy+sn*ny+ny/10):
		cp2.setTAlign(dx,d)
		cp2.rotateAndTranslate()
		v=refs[best[1]].lcmp(cp2,1)[0]
		if (v<bv) :
			bv=v
			bd=d

	print "\t",dx,dy,bv,bd

	cp2.setTAlign(dx,bd)
	cp2.rotateAndTranslate()
	cp2.writeImage("cls%04d.hed"%best[1],-1)

LOGend()
