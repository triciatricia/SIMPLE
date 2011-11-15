#!/usr/bin/env python
###	classalignhelix.py	Steven Ludtke	11/2003
### Program for making class-averages of helical segments

#N classalignhelix.py
#F This program will take helical cls files and make class-averages
#T X
#1
#P <cls file>	Class file
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
from EMAN import *

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
	print "classalignhelix.py <cls file>"
	sys.exit(1)

pi=math.pi
maxbend=5.0
square=0
single=0
quiet=0
pitch=None

for i in argv[2:] :
#	s=i.split('=')
	s=string.split(i,'=')
	if (s[0]=="maxbend") : maxbend=float(s[1])
	elif (s[0]=="quiet") : quiet=1
	elif (s[0]=="square") : square=1
	elif (s[0]=="symhelix") :
		pitch=s[1].split('/')   # angle(deg)/pixels relates an object to the next one
		pitch[0]=float(pitch[0])
		pitch[1]=float(pitch[1])
	elif (s[0]=="single") : single=1
	else:
		print "Unknown argument ",i
		exit(1)

if (not quiet) : LOGbegin(argv)

ref=EMData()
ref.readImage(argv[1],0)

avg=ref.copyHead()
avg.zero()

tmp=EMData()

toav=readImages(argv[1],1,-1)
if len(toav)==0 : sys.exit(0)
for im in toav:
	im.realFilter(112,1)
#	im.writeImage("zz.hed",-1)
avg.makeAverage(toav,None,1)
avg.setRAlign(ref.alt(),ref.az(),ref.phi())
avg.setNImg(len(toav))

count=avg.copy(0,0)
count.zero()
for im in toav:
	im.realFilter(6)
	count.add(im)

#avg.display()

#ccf=avg.calcCCF(avg,1)
#ccf.display()

if (pitch==None) : pitch=(360.0,avg.ySize()/2)

avgsrc=avg.copy(0,0)
avgsrc.setRAlign(ref.alt(),ref.az(),ref.phi())

for step in range(int(360.0/pitch[0])):
	if (single) :
		avg=avgsrc.clip(0,int(avgsrc.ySize()/8+pitch[1]*step),avgsrc.xSize(),avgsrc.ySize()/2)
		avg.setRAlign(avgsrc.alt(),avgsrc.az()+step*pitch[0]/57.295779,avgsrc.phi())
		avg.setNImg(len(toav))
		if (step==0) :
			ref=ref.clip(0,ref.ySize()/4,ref.xSize(),ref.ySize()/2)
			ref.setRAlign(avgsrc.alt(),avgsrc.az(),avgsrc.phi())
	else:
		avg=avgsrc.clip(0,pitch[1]*step,avg.xSize(),avg.ySize())

	if (square) :
		avg=avg.clip(-(avg.ySize()-avg.xSize())/2,0,avg.ySize(),avg.ySize())
		avg.setRAlign(avgsrc.alt(),avgsrc.az()+step*pitch[0]/57.295779,avgsrc.phi())
		avg.setNImg(len(toav))
		if (step==0) :
			ref=ref.clip(-(ref.ySize()-ref.xSize())/2,0,ref.ySize(),ref.ySize())
			ref.setRAlign(avgsrc.alt(),avgsrc.az(),avgsrc.phi())

	if (step==0) :
		ref.writeImage("classes.hed",-1)
		avg.writeImage("classes.hed",-1)

	avg.writeImage("classes.hlx.hed",-1)
#n=fileCount(argv[1])[0]
#for i in range(n-1):
#	tmp.readImage(argv[1],i+1)
#	ccf=tmp.calcCCF(ref,1)
#	ccf.display()


if (not quiet) : LOGend()
