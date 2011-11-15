#!/usr/bin/env python
###	tomohunter.py	Matthew Baker 010/2005

#N tomohunter.py
#F tomography hunter

import os
import sys
import string
import commands
import math
import EMAN
from math import *
from sys import argv


def tomoccf(targetMRC,probeMRC):
	ccf=targetMRC.calcCCF(probeMRC)
	ccf.toCorner()
	return (ccf)

def updateCCF(bestCCF,bestALT,bestAZ,bestPHI,altrot,azrot,phirot,currentCCF,box):
	z=0
	while z < box:
		y=0
		while y < box:
			x=0
			while x < box:
				currentValue=currentCCF.valueAt(x,y,z)
				#print x,y,z, currentValue
				if  currentValue > bestCCF.valueAt(x,y,z):
					bestCCF.setValueAt(x,y,z,currentValue)
					bestALT.setValueAt(x,y,z,altrot*180/3.14)
					bestAZ.setValueAt(x,y,z,azrot*180/3.14)
					bestPHI.setValueAt(x,y,z,phirot*180/3.14)
				x=x+1
			y=y+1
		z=z+1		
	bestCCF.update()
	bestALT.update()
	bestAZ.update()
	bestPHI.update()
	return(bestCCF)
	
def ccfFFT(currentCCF, thresh, box):
	tempCCF = currentCCF.copy()
	tempCCF.doFFT()
	tempCCF.gimmeFFT()
	tempCCF.ri2ap()
	tempCCF.realFilter(2,thresh)
	mapSum=	tempCCF.Mean()*box*box*box
	return(mapSum)

def peakSearch(bestCCF,Max_location,width,box):
	xmin=Max_location[0]-width
	xmax=Max_location[0]+width
	ymin=Max_location[1]-width
	ymax=Max_location[1]+width
	zmin=Max_location[2]-width
	zmax=Max_location[2]+width
	for x in (range(xmin,xmax)):
		for y in (range(ymin,ymax)):
			for z in (range(zmin,zmax)):
				print x,y,z
				bestCCF.setValueAt(x,y,z,-10000)
	bestCCF.update()
	return(bestCCF)		

if (len(argv)<3) :
	print "Usage:\ntomohunter.py <target mrc file> <probe mrc file> \n"
	print "Options: da=<search step (default=30)>, thresh=<threshold (default=0), maxpeaks=<number of results returned in log file (default=20)>, width=<peak width (default=2)>"
	sys.exit()
	
target=argv[1]
probe=argv[2]
thresh=0
da=60
maxPeaks=20
width=2

for a in argv[3:] :
        s=a.split('=')
	if (s[0]=='da'):
		da=int(s[1])
	elif (s[0]=='thresh'):
		thresh=float(s[1])
	elif (s[0]=='maxpeaks'):
		maxPeaks=int(s[1])			
	elif (s[0]=='width'):
		width=int(s[1])
        else:
                print("Unknown argument "+a)
                exit(1)

print target, probe

targetMRC=EMAN.EMData()
targetMRC.readImage(argv[1],-1)
targetMean=targetMRC.Mean()
targetSigma=targetMRC.Sigma()
print "Target Information"
print "   mean:       %f"%(targetMean)
print "   sigma:      %f"%(targetSigma)

target_xsize=targetMRC.xSize()
target_ysize=targetMRC.ySize()
target_zsize=targetMRC.zSize()
if (target_xsize!=target_ysize!=target_zsize) or (target_xsize%2==1):
	print "The density map must be even and cubic. Terminating."
	sys.exit()
box=target_xsize

probeMRC=EMAN.EMData()
probeMRC.readImage(argv[2],-1)
probeMean=probeMRC.Mean()
probeSigma=probeMRC.Sigma()
print "Probe Information"
print "   mean:       %f"%(probeMean)
print "   sigma:      %f"%(probeSigma)


bestCCF=EMAN.EMData()
bestCCF.setSize(box,box,box)
bestCCF.zero()

bestAZ=EMAN.EMData()
bestAZ.setSize(box,box,box)
bestAZ.zero()

bestALT=EMAN.EMData()
bestALT.setSize(box,box,box)
bestALT.zero()

bestPHI=EMAN.EMData()
bestPHI.setSize(box,box,box)
bestPHI.zero()


altarray=[]
alt=0
while alt < 360:
	altarray.append(alt*3.14/180)
	alt=alt+da

azarray=[]
az=0
while az < 360:
	azarray.append(az*3.14/180)
	az=az+da

phiarray=[]
phi=0
while phi < 180:
	phiarray.append(phi*3.14/180)
	phi=phi+da

for altrot in altarray:
	for azrot in azarray:
		for phirot in phiarray:
			dMRC=EMAN.EMData()
			dMRC = probeMRC.copy()
			dMRC.setRAlign(altrot,azrot,phirot)
			dMRC.setTAlign(0,0,0)
			dMRC.rotateAndTranslate()	
			print "Trying rotation %f %f %f"%(altrot, azrot, phirot)
			currentCCF=tomoccf(targetMRC,dMRC)
			scalar=ccfFFT(currentCCF,thresh,box)/(box*box*box)
			#scalar=1
			scaledCCF=currentCCF/scalar
			bestCCF=updateCCF(bestCCF,bestALT,bestAZ,bestPHI,altrot,azrot,phirot,scaledCCF,box)

outCCF="ccf-%s"%(argv[1])
outalt="alt-%s"%(argv[1])
outaz="az-%s"%(argv[1])
outphi="phi-%s"%(argv[1])

bestCCF.writeImage(outCCF)
bestALT.writeImage(outalt)
bestAZ.writeImage(outaz)
bestPHI.writeImage(outphi)

out=open("log.txt","w")
peak=0
while peak < maxPeaks:
	Max_location=bestCCF.MinLoc()
	ALT=str(bestALT.valueAt(Max_location[0],Max_location[1],Max_location[2]))
	AZ=str(bestAZ.valueAt(Max_location[0],Max_location[1],Max_location[2]))
	PHI=str(bestPHI.valueAt(Max_location[0],Max_location[1],Max_location[2]))
	COEFF=str(bestCCF.valueAt(Max_location[0],Max_location[1],Max_location[2]))
	LOC=str((Max_location[0]-(0.5*box),Max_location[1]-(0.5*box),Max_location[2]-(0.5*box)))
	line="Peak %d trans=%s rot=(%s, %s, %s) coeff=%s\n"%(peak,LOC,ALT,AZ,PHI,COEFF)
	out.write(line)
	bestCCF=peakSearch(bestCCF,Max_location, width, box)
	peak=peak+1
out.close()
