#!/usr/bin/env python
import EMAN
import sys
from sys import argv
import os
import math

RD=180.0/math.pi

if (len(argv)<3) :
	print "alitest.py <refs> <ptcl file> <ptcl #>"
	sys.exit(1)

refs=EMAN.readImages(argv[1],-1,-1)
ptcl=EMAN.EMData()
ptcl.readImage(argv[2],int(argv[3]))
ptcl.edgeNormalize()
ptclf=ptcl.copy(0,0);
ptclf.vFlip()

out=os.popen("triplot -","w")
#out=open("tp","w")

for i in refs:
#	i.realFilter(30)
	i.normalize()

print "begin analysis"
n=0
for i in refs:
	ali=ptcl.RTFAlign(i,ptclf,1)
	ali.refineAlign(i)
	c=1000.0*i.dot(ali)/math.sqrt(i.SumSq()*ali.SumSq())
	if (c<0) : c=0
	out.write("%f\t%f\t%f\n"%(i.alt(),i.az(),c))
	print "%d. %f\t%f\t%f"%(n,i.alt()*RD,i.az()*RD,c)
	n+=1
out.write("!\n")

n=0
for i in refs:
	ali=ptcl.RTFAlign(i,ptclf,1)
	ali.refineAlign(i)
	c=(2.0-ali.lcmp(i,1)[0])*500.0
	if (c<0) : c=0
	out.write("%f\t%f\t%f\n"%(i.alt(),i.az(),c))
	print "%d. %f\t%f\t%f"%(n,i.alt()*RD,i.az()*RD,c)
	n+=1

out.write("!\n")

n=0
for i in refs:
	ali=ptcl.RTFAlign(i,ptclf,1)
	ali.refineAlign(i)
#	ali.realFilter(30)
#	ali=ptcl

#	i.writeImage("tst.hed",n*2)
#	ali.writeImage("tst.hed",n*2+1)
#	c=(2.0-ali.pcmp(i,None))*500.0
	c=(2.0-i.pcmp(ali,None))*500.0
	if (c<0) : c=0
	out.write("%f\t%f\t%f\n"%(i.alt(),i.az(),c))
	print "%d. %f\t%f\t%f"%(n,i.alt()*RD,i.az()*RD,c)
	n+=1

out.write("!\n")

n=0
for i in refs:
	ali=ptcl.RTFAlign(i,ptclf,1)
	ali.refineAlign(i)
	c=(1.0+ali.fscmp(i,None))*500.0
	if (c<0) : c=0
	out.write("%f\t%f\t%f\n"%(i.alt(),i.az(),c))
	print "%d. %f\t%f\t%f"%(n,i.alt()*RD,i.az()*RD,c)
	n+=1



out.close()
