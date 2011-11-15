#!/usr/bin/env python
# this program simulates the 'einstein from noise' problem
# it will add noise to a base image n times. The base image
# is randomly translated by up to <dxmax> pixels. Each image is
# aligned to ref and averaged together. Outputs are generated
# at #particles specified by svpt
# <ref> <base> <basecoef> <dxmax> <# ptcl 2 gen> [posonly] [saveraw] [label=] [verbose] [saveallraw]

from EMAN import *
from sys import argv,stdout
from math import floor
import random

ref=EMData()
fsp=(argv[1]+',0').split(',')
ref.readImage(fsp[0],int(fsp[1]))
ref.normalize()

base=EMData()
base.readImage(argv[2],0)
base.edgeNormalize()

basecoef=float(argv[3])

dxmax=int(argv[4])

n=int(argv[5])
svpt=[25,100,250,1000,2000,4000,8000,16000,32000,64000]

posonly=0
saveraw=0
label=""
verbose=0
dbg=0
for i in argv[6:]:
	j=i.split('=')
	if i=="posonly" : posonly=1
	elif i=="saveraw" : saveraw=1
	elif i=="saveallraw" : saveraw=2
	elif i=="verbose" : verbose=1
	elif i=="debug" : dbg=1
	elif j[0]=="label" : label=j[1]
	else : print "unknown option ",i

avg=ref.copy(0,0)
avg.zero()
bad=0
for i in range(1,n+1):
	if (not verbose and i%100==0) : 
		print "    %d\r"%i,
		stdout.flush()
	a=base.copy(0,0)
	a.zero(1.0)
	base2=base.copy(0,0)
	base2*=basecoef
	if (dxmax>0) :
		base2.setTAlign(random.randint(-dxmax,dxmax),random.randint(-dxmax,dxmax),0)
		orig=(base2.Dx(),base2.Dy())
		base2.rotateAndTranslate()
	a+=base2
	a.normalize()
	if ((i<=10 and saveraw==1) or saveraw==2) : a.writeImage("noisy"+label+".hdf",-1)

	if (dbg) :
		b=a.calcCCF(ref,1)
		b.display()
	a.transAlign(ref,0,0,int(floor(dxmax*1.5+1)))
	if verbose : print i,")",a.Dx(),"\t",a.Dy(),"\t",-orig[0],"\t",-orig[1],"\t",
	a.rotateAndTranslate()
#	a.writeImage("rand.hed",-1)
	d=a.dot(ref)
	if verbose : print d
	if (d<0) : bad+=1
	if (d>0 or not posonly) : avg+=a
	if (i in svpt) :
		sv=avg.copy(0,0)
		sv.normalize()
		sv.setNImg(i)
		sv.writeImage("avg"+label+".hdf",-1)

if (not i in svpt) :
	sv=avg.copy(0,0)
	sv.normalize()
	sv.setNImg(i)
	sv.writeImage("avg"+label+".hdf",-1)

print bad," were negative"
