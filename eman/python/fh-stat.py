#!/usr/bin/env python

import sys
from random import *
import EMAN
from math import *
from Numeric import *
from sys import argv

converge_history_len = 50
converge_history_sigma = 0.01


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

if (len(argv)!=6):
	print "Usage: %s <target> <probe> <threshold target> <threshold probe> <fh transform>" % ( argv[0] )
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

threshold_target=float(argv[3])
threshold_probe=float(argv[4])

bbox_target = target.get_bounding_box(threshold_target)

# generate random rot/trans parameter array
transforms = []
maxsize=int( target.xSize()/2)
minsize=int(-target.xSize()/2)

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
	
	bbox_probe = probe2.get_bounding_box(threshold_probe)
	xlen_probe = bbox_probe[3] - bbox_probe[0]
	ylen_probe = bbox_probe[4] - bbox_probe[1]
	zlen_probe = bbox_probe[5] - bbox_probe[2]
	
	if (bbox_probe[0] +xlen_probe/2<bbox_target[0] or bbox_probe[1] +ylen_probe/2<bbox_target[1] or bbox_probe[2] +zlen_probe/2<bbox_target[2] or \
	   bbox_probe[3]>bbox_target[3]+xlen_probe/2 or bbox_probe[4]>bbox_target[4]+ylen_probe/2 or bbox_probe[5]>bbox_target[5]+zlen_probe/2) :
		continue

	probe2thresh = probe2.copy()
	probe2thresh.realFilter(0,threshold_probe)
	
	probe2bin = probe2.copy()
	probe2bin.realFilter(2,threshold_probe)
	refmasked = ref.copy()
	refmasked.mult(probe2bin)
	
#	filename="file-%d.mrc"%(counter)
#	probe2.writeImage(filename)
	tempscore= probe2thresh.ncccmp(refmasked)
	test=str(tempscore)
	if test != 'nan':
		counter=counter+1
		score.append( tempscore )
		mean,sigma=stats(score)
		sigmaarray.append(sigma)
		meanarray.append(mean)
		print "%d completed (%f, %f, %f )"%(counter, tempscore, mean, sigma)
		if counter > converge_history_len:
			sigmaM, sigmaS=stats(sigmaarray[-converge_history_len:])
			meanM, meanS=stats(meanarray[-converge_history_len:])
			if meanS/meanM < converge_history_sigma and sigmaS/sigmaM < converge_history_sigma:
				break
	
# compute score mean/sigma
mean,sigma=stats(score)
print "Average of %d random fits: %f" %(counter, mean)
print "Sigma of %d random fits: %f" %(counter, sigma)

fhT=argv[5]
fhTransform=fhT.split(',')

probe2=probe.copy(0,0)
probe2.setRAlign(float(fhTransform[0])/pi,float(fhTransform[1])/pi,float(fhTransform[2])/pi)
probe2.setTAlign(0,0,0)
probe2.rotateAndTranslate()
probe2.setRAlign(0,0,0)
probe2.setTAlign(float(fhTransform[3]),float(fhTransform[4]),float(fhTransform[5]))
probe2.rotateAndTranslate()

probe2thresh = probe2.copy()
probe2thresh.realFilter(0,threshold_probe)

probe2bin = probe2.copy()
probe2bin.realFilter(2,threshold_probe)
refmasked = ref.copy()
refmasked.mult(probe2bin)
fhScore=probe2thresh.ncccmp(refmasked)
print "Foldhunter score: %f"%(fhScore)

Zscore=abs(fhScore-mean)/sigma
print "Z-score of fit: %f"%(Zscore)
