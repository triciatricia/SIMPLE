#!/usr/bin/env python

import sys
from random import *
import EMAN
from math import *
from Numeric import *
from sys import argv

def getrandomangle(maxrange):
	maxrange=maxrange
	angle=(random()*maxrange)/pi
	return angle

def stats(scores):
	score=array(scores)
	mean=average(score)
	b=score-mean
	sigma=sqrt(dot(b,b)/len(score))
	return mean, sigma

if (len(argv)!=5) :
	print "Usage: ccf.py <target> <probe> <threshold> <fh transform>"
	sys.exit(1)

target=EMAN.EMData()
target.readImage(argv[1],-1)
if (target.xSize()!=target.ySize() or target.ySize()!=target.zSize() or target.xSize()%2==1 or target.ySize()%2==1 or target.zSize()%2==1) :
	sys.exit(1)

probe=EMAN.EMData()
probe.readImage(argv[2],-1)
if (probe.xSize()!=probe.ySize() or probe.ySize()!=probe.zSize() or probe.xSize()%2==1 or probe.ySize()%2==1 or probe.zSize()%2==1) :
	sys.exit(1)

ref=target.copy(0,0)

threshold=float(argv[3])

# generate random rot/trans parameter array
transforms = []
maxsize=int(target.xSize()/4)
minsize=int(-1*target.xSize()/4)

#for transform in transforms:
score=[]
counter=0
#for transform in transforms:
sigmaarray=[]
meanarray=[]
while 1:
	probe2=probe.copy(0,0)
	alt= getrandomangle(180)
	az= getrandomangle(360)
	phi= getrandomangle(360)
	dx= randint(minsize,maxsize)
	dy= randint(minsize,maxsize)
	dz= randint(minsize,maxsize)
	probe2.setRAlign(alt,az,phi)
	probe2.setTAlign(dx,dy,dz)
	probe2.rotateAndTranslate()
	
	probe2thresh = probe2.copy()
	probe2thresh.realFilter(0,threshold)
	
	probe2bin = probe2.copy()
	probe2bin.realFilter(2,threshold)
	refmasked = ref.copy()
	refmasked.mult(probe2bin)
	
#	filename="file-%d.mrc"%(counter)
#	probe2.writeImage(filename)
	tempscore= probe2thresh.lcmp(refmasked,1)[0]
	test=str(tempscore)
	if test != 'nan':
		counter=counter+1
		score.append( tempscore )
		mean,sigma=stats(score)
		sigmaarray.append(sigma)
		meanarray.append(mean)
		print "%d completed (%f, %f, %f )"%(counter, tempscore, mean, sigma)
		if counter >10:
			sigmaM, sigmaS=stats(sigmaarray[-30:])
			meanM, meanS=stats(meanarray[-30:])
			if meanS/meanM < 0.005 and sigmaS/sigmaM<.005:
				break
	
# compute score mean/sigma
mean,sigma=stats(score)
print "Average of %d random fits: %f" %(counter, mean)
print "Sigma of %d random fits: %f" %(counter, sigma)

fhT=argv[4]
fhTransform=fhT.split(',')

probe2=probe.copy(0,0)
probe2.setRAlign(float(fhTransform[0])/pi,float(fhTransform[1])/pi,float(fhTransform[2])/pi)
probe2.setTAlign(0,0,0)
probe2.rotateAndTranslate()
probe2.setRAlign(0,0,0)
probe2.setTAlign(float(fhTransform[3]),float(fhTransform[4]),float(fhTransform[5]))
probe2.rotateAndTranslate()

probe2thresh = probe2.copy()
probe2thresh.realFilter(0,threshold)

probe2bin = probe2.copy()
probe2bin.realFilter(2,threshold)
refmasked = ref.copy()
refmasked.mult(probe2bin)
fhScore=probe2thresh.lcmp(refmasked,1)[0]
print "Foldhunter score: %f"%(fhScore)

Zscore=abs(fhScore-mean)/sigma
print "Z-score of fit: %f"%(Zscore)
