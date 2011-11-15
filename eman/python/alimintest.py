#!/usr/bin/env python
import EMAN
import sys
from sys import argv
import os
import math

RD=180.0/math.pi

d3=0
doang=0

if (len(argv)<3) :
	print "alimintest.py <ref> <ptcl #> <ptcl file> <ptcl #> [p,l,f,d]"
	sys.exit(1)

ref=EMAN.EMData()
ref.readImage(argv[1],int(argv[2]))

ptcl=EMAN.EMData()
ptcl.readImage(argv[3],int(argv[4]))
ptclf=ptcl.copy(0,0);
ptclf.vFlip()

ali=ptcl.RTFAlign(ref,ptclf,1)

if (len(argv)>5) : meth=argv[5][0]
else : meth="f"

#sdx=ali.Dx()
#sdy=ali.Dy()
#salt=ali.alt()

sdx=0
sdy=0
salt=0

if (d3) :
	result=EMAN.EMData()
	result.setSize(48,48,48)

	for x in range(-24,24,1):
		for y in range(-24,24,1):
			for a in range(-24,24,1):
				dx=float(x)/10.0+sdx
				dy=float(y)/10.0+sdy
				da=float(a)*10.0/(RD*24)+salt
				ali.setTAlign(dx,dy,0)
				ali.setRAlign(da)
				ali.rotateAndTranslate()
				if (meth=="d") : c=ali.dot(ref)
				elif (meth=="l") : c=2.0-ali.lcmp(ref,1)
				elif (meth=="p") : c=3.0-ali.pcmp(ref,None)
				elif (meth=="f") : c=ali.fscmp(ref,None)
				result.setValueAt(x+24,y+24,a+24,c)
				print("%f %f %f %f  (%d %d %d)"%(dx,dy,da,c,x,y,a))

	result.update()
	result.writeImage("result.mrc")
	
elif doang:
	result=EMAN.EMData()
	result.setSize(64,64,1)
	for x in range(-32,32,1):
		for a in range(-32,32,1):
			dx=float(x)/10.0+sdx
			da=float(a)*10.0/(RD*32)+salt
			ali.setTAlign(dx,0,0)
			ali.setRAlign(da)
			ali.rotateAndTranslate()
			if (meth=="d") : c=ali.dot(ref)
			elif (meth=="l") : c=2.0-ali.lcmp(ref,1)
			elif (meth=="p") : c=3.0-ali.pcmp(ref,None)
			elif (meth=="f") : c=ali.fscmp(ref,None)
			result.setValueAt(x+32,a+32,0,c)
			print("%f %f %f"%(dx,da,c))
	result.update()
	result.writeImage("result.mrc")
else:
	result=EMAN.EMData()
	result.setSize(64,64,1)
	for x in range(-32,32,1):
		for y in range(-32,32,1):
				dx=float(x)/10.0+sdx
				dy=float(y)/10.0+sdy
				ali.setTAlign(dx,dy,0)
				ali.rotateAndTranslate()
				if (meth=="d") : c=ali.dot(ref)
				elif (meth=="l") : c=2.0-ali.lcmp(ref,1)
				elif (meth=="p") : c=3.0-ali.pcmp(ref,None)
				elif (meth=="f") : c=ali.fscmp(ref,None)
				print("%f %f %f"%(dx,dy,c))
				result.setValueAt(x+32,y+32,0,c)
	result.update()
	result.writeImage("result.mrc")

