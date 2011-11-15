#!/usr/bin/env python
###	masksym.py	Steven Ludtke	3/2003
### This program will symmetrize a mask and optionally extend it
###

#N masksym.py
#F This will apply the given symmetry to a mask, and optionally extend the mask
#T X
#1
#P <mask in>	Input mask file (1 or 0)
#P <mask out>	Output mask file (0-n depending on symmetry)
#P sym=<symmetry>	Standard symmetry specification
#P [xtend=<n shells>]	Expand the masks iteratively after symmetrization (very slow)
#P [maskdata=<volume in>]	This will mask out the individual subunits,align them and save them to MRC files
#D Not documented yet

import os
import sys
import random
import time
import string
from os import system
from os import unlink
from sys import argv
import EMAN
#try:
#	import psyco
#	psyco.full()
#except:
#	print "PSYCO unavailable"

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
	print "masksym.py <mask in> <mask out> sym=<sym> [xtend=<n>] [maskdata=<map in>]"
	sys.exit(1)

sym='c1'
xtend=0
maskdata=None

for i in argv[3:] :
#	s=i.split('=')
	s=string.split(i,'=')
	if (s[0]=="sym") : sym=s[1]
	elif (s[0]=="xtend") : xtend=int(s[1])
	elif (s[0]=="maskdata") : maskdata=s[1]
	else:
		print "Unknown argument ",i
		exit(1)

LOGbegin(argv)

img=EMAN.EMData()
img.readImage(argv[1],-1)
if (img.zSize<2) :
	print "masksym.py only functions on volumetric data"
	sys.exit(1)

out=img.copy(0,0)
eul=EMAN.Euler(0,0,0)
eul.setSym(sym)
e=eul.FirstSym()
e=eul.NextSym()

n=2
while (e.valid()):
	c=img.copy(0,0)
	c.setRAlign(e.alt(),e.az(),e.phi())
	c.rotateAndTranslate()
	c.realFilter(2,.5)
	c*=n
	out.add(c)

	c2=out.copy(0,0)		# this is a mask to get rid of overlaps
	c2.realFilter(2,n+.5)
	c2.realFilter(9,-1,-1)	# inverts the mask
	out.mult(c2)

	n+=1
	e=eul.NextSym()

# this does the iterative expansion of all mask regions simultaneously
#print "Iterative Expansion"
#xs=out.xSize()
#ys=out.ySize()
#zs=out.zSize()
#for i in range(xtend):

#	out2=out.copy(0,0)
#	for z in range(1,zs-1):
#		print "%d/%d"%(z,zs-1)
#		for y in range(1,ys-1):
#			for x in range(1,xs-1):
#				if (out.valueAt(x,y,z)==0) :
#					out.setValueAt(x,y,z,max(out2.valueAt(x-1,y,z),out2.valueAt(x+1,y,z),out2.valueAt(x,y-1,z),out2.valueAt(x,y+1,z),out2.valueAt(x,y,z-1),out2.valueAt(x,y,z+1)))

if (xtend>0) : out.realFilter(111,float(xtend))

out.writeImage(argv[2])

if (maskdata) :
	out.realFilter(14,.5,1.5)	# produces a mask for the first region only
	eul=EMAN.Euler(0,0,0)
	eul.setSym(sym)
	e=eul.FirstSym()
	n=0
	while (e.valid()) :
		img.readImage(maskdata,-1)
		img.setRAlign(e)
		img.rotateAndTranslate()
		img.mult(out)
		img.writeImage("smasked.%d.mrc"%n)
		n+=1
		e=eul.NextSym()

LOGend()

