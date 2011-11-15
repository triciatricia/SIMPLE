#!/usr/bin/env python
###	sheethunter2.py	Matthew Baker 09/2003

#N sheethunter2.py
#F Beta sheet identification
#T LM
#1
#P <target>	Input mrc file or quantized mrc file in PDB format
#P <nseg=>	number of segments to create in segment3d
#P <thr=>	threshold for segment 3d
#P <apix=>	a/pix
#P <dist=>	distance
#P <angle=>	angle
#D Runs foldhunter

import os
import sys
import string
import commands
import math
import EMAN
from math import *
from sys import argv
from Numeric import array
from Numeric import dot


def cross_product(a,b):
    """Cross product of two 3-d vectors. from http://www-hep.colorado.edu/~fperez/python/python-c/weave_examples.html
    """
    cross = [0]*3
    cross[0] = a[1]*b[2]-a[2]*b[1]
    cross[1] = a[2]*b[0]-a[0]*b[2]
    cross[2] = a[0]*b[1]-a[1]*b[0]
    return array(cross)


thr=0
seg=100
apix=1
dist=5.5
angMax=30
removeHelix=0

if (len(argv)<2) :
	print "Usage:\nsheethunter2.py <input mrc file> <seg=> <thr=> <apix=> <dist=> <angle=> <hh=> \n"
	sys.exit(1)

target=argv[1]
t=target.split('.')
targetName=str(t[0])
targetExt=str(t[-1])

for a in argv[2:] :
        s=a.split('=')
        if (s[0]=='apix') :
		apix=float(s[1])
	elif (s[0]=='seg') :
		seg=int(s[1])
	elif (s[0]=='thr') :
		thr=float(s[1])
	elif (s[0]=='dist') :
		dist=float(s[1])
	elif (s[0]=='angle'):
		angMax=float(s[1])
	elif (s[0]=='hh'):
		removeHelix=1
		hh=str(s[1])
        else:
                print("Unknown argument "+a)
                exit(1)

##read input data
if (targetExt=="mrc"):
	targetMRC=EMAN.EMData()
	targetMRC.readImage(argv[1],-1)
	target_xsize=targetMRC.xSize()
	target_ysize=targetMRC.ySize()
	target_zsize=targetMRC.zSize()
	print("Segment3D")
	pdbOut="seg-%s.pdb"%(targetName)
	cmd0="segment3d %s seg-%s nseg=%d thr=%f pdb=%s"%(target, target, seg, thr, pdbOut)
	os.system(cmd0)
	file1=open(pdbOut, "r")
else:
	file1=open(target, "r")
lines1=file1.readlines()
file1.close()

##read in coordinates of points
xIn=[]
yIn=[]
zIn=[]
atomNumber=[]
coords=[]
counter=0
for line in lines1:
	isatom=str(line[0:6].strip())
	if (isatom=="ATOM"):
#		coord=(0,0,0)
		xIn.append(float(line[30:38].strip()))
		yIn.append(float(line[38:46].strip()))
		zIn.append(float(line[46:54].strip()))
		atomNumber.append(int(line[6:11].strip()))
		coord=(xIn[-1],yIn[-1],zIn[-1])
#		print coord
		coords.append(coord)
		counter=counter+1

print " "
##Get helical info
helixCount=0
helixCoords=[]
if removeHelix==1:
	xH=[]
	yH=[]
	zH=[]
	fileH=open(hh, "r")
	linesH=fileH.readlines()
	fileH.close()
	for line in linesH:
		isatom=str(line[0:6].strip())
		if (isatom=="ATOM"):
#			helixCoord=(0, 0, 0)
			xH.append(float(line[30:38].strip()))
			yH.append(float(line[38:46].strip()))
			zH.append(float(line[46:54].strip()))
			helixCoord=(xH[-1],yH[-1],zH[-1])
			helixCoords.append(helixCoord)
#			print helixCoords
			helixCount=helixCount+1

xArray=[]
yArray=[]
zArray=[]
filtout=0
counterFilt=0
linesS=[]
pointsS=[]
filtersheet=0
filtered=open("filtered-sheet.pdb","w")
while filtersheet < counter:
	l=lines1[filtersheet]
	if coords[filtersheet] in helixCoords:
#		print "spam"
		filtersheet=filtersheet+1
	else:
		pointsS.append(atomNumber[filtersheet])
		xArray.append(xIn[filtersheet])
		yArray.append(zIn[filtersheet])
		zArray.append(yIn[filtersheet])
		filtered.write(l)
		linesS.append(l)
		counterFilt=counterFilt+1
		filtersheet=filtersheet+1

filtered.close()
print pointsS

print " "
if removeHelix==1:
	x=xArray
	y=yArray
	z=zArray
	counter=counterFilt

## find triangles
i=0
j=0
distance=[0]*counter
rawDistance=[0]*counter
neighborhood=[]
while (i < counter):
	x1=x[i]
	y1=y[i]
	z1=z[i]
	distance[i]=[0]*counter
	rawDistance[i]=[0]*counter
	while (j < counter):
		x2=x[j]
		y2=y[j]
		z2=z[j]
		distance[i][j]=(j,math.sqrt((x1-x2)**2+(y1-y2)**2+(z1-z2)**2))
		rawDistance[i][j]=(j,math.sqrt((x1-x2)**2+(y1-y2)**2+(z1-z2)**2))
		j=j+1
	j=0
	i=i+1
k=0
while k < counter:
	distance[k].sort(lambda a, b: cmp(a[1],b[1]))
	neighbors=[]
	k2=0
	while k2 <counter:
		neighbors.append(distance[k2])
		k2=k2+1
	neighborhood.append(neighbors)
	k=k+1

#Calculate cross product
m=0
nxp=[]
dpTriangle=0
while (m < counter):
	triangle=180
	tri=1
	origin=distance[m][0][0]
	point1=distance[m][1][0]
	v1=(x[point1]-x[origin],y[point1]-y[origin],z[point1]-z[origin])
	lengthV1=math.sqrt(v1[0]**2+v1[1]**2+v1[2]**2)
	v1n=(v1[0]/lengthV1,v1[1]/lengthV1,v1[2]/lengthV1)
	while (triangle>120):
		tri=tri+1
		point2=distance[m][tri][0]
#		print point2
		v2=(x[point2]-x[origin],y[point2]-y[origin],z[point2]-z[origin])
		lengthV2=math.sqrt(v2[0]**2+v2[1]**2+v2[2]**2)
		v2n=(v2[0]/lengthV2,v2[1]/lengthV2,v2[2]/lengthV2)
		dpTriangle=dot(v1n,v2n)
		if dpTriangle > 1:
			dpTriangle=1
		if dpTriangle <-1:
			dpTriangle=-1
		triangle=math.acos(dpTriangle)*(180/math.pi)
#	print m, distance[m][tri], triangle
	xp=cross_product(v1,v2)
	length=math.sqrt(xp[0]**2+xp[1]**2+xp[2]**2)
	txp=(xp[0]/length, xp[1]/length, xp[2]/length)
	nxp.append(txp)
	m=m+1

##check to see if point is a sheet
n=0
valuemap=[]
avgValueArray=[]
angle=0
trip=0
tripArray=[]
clusterArray=[]
while (n<counter):
	avgnum=0
	anglesum=0
	q=0
	cluster=[]
	temp=(n,0)
	while (q<counter):
		if (rawDistance[n][q][1]<=dist):
			dp=dot(nxp[n],nxp[q])
			if dp > 1:
				dp=1
			if dp <-1:
				dp=-1
			angle=math.acos(dp)*(180/math.pi)
			if angle>90:
				angle=180-angle
			anglesum=anglesum+angle
			avgnum=avgnum+1
			print "point %d vs point %d : %f"%(pointsS[n], pointsS[q], angle)
			if angle<((angMax+15)):
				cluster.append(q)
		q=q+1
	temp=(n,cluster)
	clusterArray.append(temp)
	if avgnum<2:
		avgValue=anglesum
	else:
		avgValue=anglesum/(avgnum-1)
	if avgValue<1:
		avgValue=89
	avgValueArray.append(avgValue)
	print "point %d average: %f"%(pointsS[n],avgValue)
	trip=(int(x[n]),int(y[n]),int(z[n]))
#	quad=(trip,avgValue)
#	quad=(int(x[n]),int(y[n]),int(z[n]),rescaleAvgValue)
	tripArray.append(trip)
#	valuemap.append(quad)
	n=n+1
	q=0
#print clusterArray
lnS=0
lnH=0
outPdbHelix=open("helixX.pdb","w")
outFile="sheet-%f-%f.pdb"%(angMax,dist)
outPdbSheet=open(outFile,"w")

for line in linesS:
	if (avgValueArray[lnS] < angMax):
		outPdbSheet.write(line)
	lnS=lnS+1
outPdbSheet.close()

for line in linesH:
	outPdbHelix.write(line)
	lnH=lnH+1

outPdbHelix.close()
