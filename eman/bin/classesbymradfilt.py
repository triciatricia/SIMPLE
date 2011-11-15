#!/usr/bin/env python
###	classesbymradfilt.py	Steven Ludtke	5/3/2004
### Program for making class-averages of helical segments

#N classesbymradfilt.py
#F This program is a new version of classesbymra using the dfilt option
#T X
#1
#P <particles>	Raw particle filespec	
#P <refrences>	Reference image filespec
#P [frac=<num>/<denom>]	Operate only on a fraction of the raw images
#P [mask=<rad>]	Mask the classified particles, also reduces noise for better classification
#P [refmask]	This will use a mask generated from the reference image. Assumes the 3D model has been sensibly masked.
#P [maxshift=<rad>]	Maximum translation during image alignment
#P [ctfc]	Projections are CTF corrected before comparison
#P [logit=<label>]	This specifies a label to use in the particle.log file. This records particle number classification throughout a refinement.
#P [refine]	Refines 2D alignment done with fast algorithm. Slower, but not 'slow'.
#P [usefilt]	Use the 'filt' version of the input file for classification.

import os
import sys
import time
from sys import argv
from math import *

#def LOGbegin(ARGV):
#	out=open(".emanlog","a")
#	b=ARGV[0].split('/')
#	ARGV[0]=b[len(b)-1]
#	out.write("%d\t%d\t1\t%d\t%s\n"%(os.getpid(),time.time(),os.getppid()," ".join(ARGV)))
#	out.close()

#def LOGend():
#	out=open(".emanlog","a")
#	out.write("%d\t%d\t2\t-\t\n"%(os.getpid(),time.time()))
#	out.close()


#### MAIN

if (len(argv)<3) :
	print "classesbymradfilt.py <particles> <refrences> [frac=<num>/<denom>] [mask=<rad>] [usefilt] [maxshift=<rad>] [ctfc] [logit=<label>] [refine]"
	sys.exit(1)

from EMAN import *

LOGbegin(argv)

frac=(0,1)
maskr=-1
maxshift=-1
ctfc=0
logit=None
refine=0
usefilt=0
ptclfile=argv[1]

for i in argv[3:] :
#	s=i.split('=')
	s=i.split('=')
	if (s[0]=="frac") : 
		t=s[1].split('/')
		frac=(int(t[0]),int(t[1]))
	elif (s[0]=="mask") : 
		if (maskr==-1) : maskr=int(s[1])
	elif (s[0]=="maxshift") : maxshift=int(s[1])
	elif (s[0]=="ctfc") : ctfc=1
	elif (s[0]=="logit") : logit=s[1]
	elif (s[0]=="refine") : refine=1
	elif (s[0]=="usefilt") : 
		ptclfile=argv[1].split(".")[:-1]+["filt"]+[argv[1].split(".")[-1]]
		ptclfile=".".join(ptclfile)
		usefilt=1
	else:
		print "Unknown argument ",i
		exit(1)

refs=readImages(argv[2],-1,-1)		# read all raw references
FLIP=("","flip")

# determine mask for each reference
refmsk=[]
for i in refs:
	n=i.copy(0,0)
	n.applyMask(4,maskr)
	n.realFilter(6)
	refmsk.append(n)
	
n2c=fileCount(ptclfile)[0]
n0=frac[0]*n2c/frac[1]			# first particle to classify
n1=(frac[0]+1)*n2c/frac[1]		# last particle to classify+1

#initialize cls*.lst
#for i in range(len(refs)): 
#	o=file("cls%04d.lst"%i,"w")
#	o.write("#LST\n%d\tproj.hed\n"%i)	
#	o.close()
	
ptcl=EMData()
for i in range(n0,n1):
	ptcl.readImage(ptclfile,i)
	ptcl.edgeNormalize()
#	print ptcl.getEuler().getByType(Euler.EMAN)[0]*57.296,(ptcl.getEuler().getByType(Euler.EMAN)[1]*57.296)%25.71428
#	ptcl.writeImage("a.hed",-1)
	
	best=(0,1.0e30,0,0,0,0)
	for r in range(len(refs)):
		r0=refs[r]
		ref=r0.copy(0,0)
		ref=ref.matchFilter(ptcl)
		refa=ref.RTFAlign(ptcl,None,1,maxshift)		# reference aligned to particle
		if (refine) : refa.refineAlign(ptcl)
		q0=-refa.Dx()
		q1=-refa.Dy()
		qa=-refa.alt()
#		refa.writeImage("a.hed",-1)
				
		mc=refmsk[r].copy(0,0)
		mc.setRAlign(refa.alt(),0,0)
		mc.setTAlign(refa.Dx(),refa.Dy(),0)
		mc.rotateAndTranslate()						# mask aligned to particle
				
		mp=ptcl*mc
		refa=refa.matchFilter(mp)					# match the masked particle
#		mp.writeImage("a.hed",-1)
#		refa.writeImage("a.hed",-1)
		
		cmp=refa.lcmp(ptcl,1)
#		print "%d. %6.2f  %6.2f\t%s"%(refs.index(r0),r0.getEuler().alt()*57.296,r0.getEuler().az()*57.296,str(cmp))
		
		if (cmp[0]<best[1]) : best=(r,cmp[0],qa,q0*cos(qa)+q1*sin(qa),-q0*sin(qa)+q1*cos(qa),refa.isFlipped())

	print "%d %f    %f  %f  %f  %s"%(best[0],best[1],best[2]*57.296,best[3],best[4],FLIP[best[5]])
	o=file("cls%04d.lst"%best[0],"a")
	o.write("%d\t%s\t%1.3f,  %1.5f,%1.5f,%1.5f,%d\n"%(i,argv[1],best[1],best[2],best[3],best[4],best[5]))
	o.close()

LOGend()


