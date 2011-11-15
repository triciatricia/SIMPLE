#!/usr/bin/env python
###	ssehunter3.py	Matthew Baker 4/2005
###     Uses skeleton, correlation and angles
#N ssehunter3.py
#F secondary structure identification

import os
import sys
import string
import commands
import math
import EMAN
from math import *
from sys import argv
import Numeric
import MLab
#import Pycluster

def cross_product(a,b):
    """Cross product of two 3-d vectors. from http://www-hep.colorado.edu/~fperez/python/python-c/weave_examples.html
    """
    cross = [0]*3
    cross[0] = a[1]*b[2]-a[2]*b[1]
    cross[1] = a[2]*b[0]-a[0]*b[2]
    cross[2] = a[0]*b[1]-a[1]*b[0]
    return Numeric.array(cross)


if (len(argv)<5) :
	print "Usage:\nssehunter3.py <input mrc> <apix> <res> <threshold>\n"
	print "OPTIONS"
	print "coeff=<intermediate correlation file> atoms=<pseudoatoms file> coeffwt=<0-1>, skeletonwt=<0-1>, pseudoatomwt=<0-1>"
	sys.exit(1)

target=argv[1]
t=target.split('.')
targetName=str(t[0])
targetExt=str(t[-1])

apix=float(argv[2])
res=float(argv[3])
thr=float(argv[4])

helixsize=3
sheetsize=4
atoms="none"
coeff="none"
coeffwt=1.0
skeletonwt=1.0
pseudoatomwt=1.0

for a in argv[5:] :
        s=a.split('=')
	print s[0], s[1]
	if (s[0]=='atoms'):
		atoms=str(s[1])			
        elif (s[0]=='coeff'):
		coeff=str(s[1])	
        elif (s[0]=='coeffwt'):
		coeffwt=float(s[1])
	elif (s[0]=='skeletonwt'):
		skeletonwt=float(s[1])	        
	elif (s[0]=='pseudoatomwt'):
		pseudoatomwt=float(s[1])	
	else:
                print("Unknown argument "+a)
                sys.exit()

if coeffwt >1 or coeffwt<0 or skeletonwt>1 or skeletonwt<0 or pseudoatomwt>1 or pseudoatomwt<0:
	print "All wieghts must be between 0 and 1"
	sys.exit() 

###################################read input data

targetMRC=EMAN.EMData()
targetMRC.readImage(argv[1],-1)
mapMean=targetMRC.Mean()
mapSigma=targetMRC.Sigma()
target_xsize=targetMRC.xSize()
target_ysize=targetMRC.ySize()
target_zsize=targetMRC.zSize()
if thr==0:
	thr=mapMean+4*mapSigma
	print "Calculating threshold"
print "Map Information"
print "   mean:      %f"%(mapMean)
print "   sigma:     %f"%(mapSigma)
print "   threshold: %f"%(thr)
print "   dimensions:%d,%d,%d"%(target_xsize,target_ysize,target_zsize)
if (target_xsize!=target_ysize!=target_zsize) or (target_xsize%2==1):
	print "The density map must be even and cubic. Terminating SSEHunter."
	sys.exit()
##################################################################



##################################get psuedoatoms
if (atoms=="none"):
	atoms="seg-%s.pdb"%(targetName)
	cmd0="pseudoatom.py %s %s %f %f %f"%(target, atoms, apix, res, thr)
	os.system(cmd0)

file1=open(atoms, "r")
lines1=file1.readlines()
file1.close()

x=[]
y=[]
z=[]
atomNumber=[]
atomCount=0

for line in lines1:
	isatom=str(line[0:6].strip())
	if (isatom=="ATOM"):
		TempX=(float(line[30:38].strip()))/apix
		TempY=(float(line[38:46].strip()))/apix
		TempZ=(float(line[46:54].strip()))/apix
		x.append(TempX)
		y.append(TempY)
		z.append(TempZ)
		atomNumber.append(int(line[6:11].strip()))
		atomCount=atomCount+1
##################################################################




########################### Generate coeff values

if (coeffwt != 0.0):

	if (coeff=="none") :
		cmdhh="helixhunter2 %s %s.iv %f da=5 docylccffirst int=int-%s"%(target, targetName, apix, targetName)
		os.system(cmdhh)
		coeff="int-%s-coeff.mrc"%(targetName)

	hhMrc=EMAN.EMData()
	hhMrc.readImage(coeff,-1)
	coeffArray=[]
	avghhvalue=0.0
	hc=0
	maxValue=0.0
	while hc < atomCount:
		hhvalue=float(hhMrc.valueAtInterp(x[hc],y[hc],z[hc]))
		if hhvalue > maxValue:
			maxValue=hhvalue
		avghhvalue=hhvalue+avghhvalue
		coeffArray.append(hhvalue)
		hc=hc+1
	avghhvalue=avghhvalue/atomCount
	print "Correlation threshold: %f"%(avghhvalue)
	print "Correlation Maximum:   %f"%(maxValue)
	
else:
	coeffArray=[]
	coeffArray=[0]*atomcount
##################################################################




########################### Generate skeletons
if skeletonwt==0.0:
	skeletonArray=[]
	skeletonArray=[0]*atomcount  
else:
	outfile="%s-score.pdb"%(targetName)
	cmd1="skeleton 6 %s %s %f  %f %f %f %s"%(target, atoms, apix, thr, helixsize, sheetsize, outfile)
	print cmd1
	os.system(cmd1)

	file2=open(outfile)
	lines2=file2.readlines()

	skeletonArray=[]
	for line in lines2:
		isatom=str(line[0:6].strip())
		if (isatom=="ATOM"):
			skeletonArray.append(float(line[60:66].strip()))	                                                                                                                 
##################################################################




########################### psuedoatom geometry calculations
if pseudoatomwt == 0.0:
	pseudoatomArray=[]
	pseudoatomArray=[0]*atomcount 

else:
### all to all distance calculations
	i=0
	j=0
	distance=[0]*atomCount
	pseudoatomArray=[]

	while i < atomCount:
		x1=x[i]
		y1=y[i]
		z1=z[i]
		distance[i]=[0]*atomCount
		while (j < atomCount):
			x2=x[j]
			y2=y[j]
			z2=z[j]
			distance[i][j]=(math.sqrt((x1-x2)**2+(y1-y2)**2+(z1-z2)**2))*apix
			j=j+1
		j=0
		i=i+1


	### set bounding box
	k=0
	kernelwidth=int(round(5/apix))
	pixels=[]
	while (k < atomCount):
		tempPixel=[]
		pixelCoords=[]
		intX=int(x[k])
		intY=int(y[k])
		intZ=int(z[k])
		for addX in range(-1*kernelwidth, kernelwidth, 1):
			tempX=int((addX+intX))
			for addY in range(-1*kernelwidth, kernelwidth, 1):
				tempY=int((addY+intY))
				for addZ in range(-1*kernelwidth, kernelwidth, 1):
					tempZ=int((addZ+intZ))
					if targetMRC.valueAt(tempX,tempY,tempZ) > thr:
						tempPixel=[tempX,tempY,tempZ]
						if tempPixel not in pixelCoords:
							pixelCoords.append(tempPixel)
		pixels.append(pixelCoords)
		k=k+1



	### Check 2nd moments to see if globular
	axisMatrix=[]
	index1=0
	neighborhood=[]
	pointcloud=[]
	betadistance=8.25
	while index1 < atomCount:
		NumPoints1=Numeric.array(pixels[index1],'d')
		NumPoints1_mean=Numeric.sum(NumPoints1)/len(NumPoints1)
		NumPoints2=NumPoints1-NumPoints1_mean

		points1=Numeric.sum(map(Numeric.innerproduct,NumPoints2,NumPoints2))
		h = Numeric.sum(map(Numeric.outerproduct,NumPoints2,NumPoints2))
		[u1,x1,v1]=MLab.svd(h)
		if x1==[0,0,0]:
			print index1,
			print "is bad"
			xmod=x1
		else:
			xmod=x1/max(x1)
		if xmod[2]==0:
			aspectratio=0

		else:
			aspectratio=xmod[1]/xmod[2]
		axisMatrix.append(aspectratio)


	### checks for nearest atoms and nearest helical atoms
		index2=0
		mindistance1=99998
		mindistance2=99999
		helixneighbor1=0
		helixneighbor2=0
		mindistance3=99998
		mindistance4=99999
		neighbor3=0
		neighbor4=0
		cloud=[]
		while index2 < atomCount:
			if distance[index1][index2]<=betadistance and atomNumber[index1]!=atomNumber[index2]:
				cloud.append(atomNumber[index2])
			if distance[index1][index2] <= mindistance2 and distance[index1][index2]>0.1 and coeffArray[index2]>=avghhvalue:
				if distance[index1][index2] <= mindistance1:
					mindistance2=mindistance1
					mindistance1=distance[index1][index2]
					helixneighbor2=helixneighbor1
					helixneighbor1=atomNumber[index2]
				else:
					mindistance2=distance[index1][index2]
					helixneighbor2=atomNumber[index2]

			if distance[index1][index2] <= mindistance4 and distance[index1][index2]>0.1:
				if distance[index1][index2] <= mindistance3:
					mindistance4=mindistance3
					mindistance3=distance[index1][index2]
					neighbor4=neighbor3
					neighbor3=atomNumber[index2]
				else:
					mindistance4=distance[index1][index2]
					neighbor4=atomNumber[index2]
			index2=index2+1
		neighbors=(helixneighbor1,helixneighbor2,mindistance1,mindistance2,neighbor3, neighbor4)
		pointcloud.append(cloud)
		neighborhood.append(neighbors)
		index1=index1+1	


	sheetlist=[]
	generallist=[]
	helixlist=[]
	index3=0
	while index3 < atomCount:
	### check generic angles
		origin=index3
		p1=neighborhood[index3][4]-1
		v1=(x[p1]-x[origin],y[p1]-y[origin],z[p1]-z[origin])
		lengthV1=math.sqrt(v1[0]**2+v1[1]**2+v1[2]**2)
		v1n=(v1[0]/lengthV1,v1[1]/lengthV1,v1[2]/lengthV1)

		p2=neighborhood[index3][5]-1
		v2=(x[p2]-x[origin],y[p2]-y[origin],z[p2]-z[origin])
		lengthV2=math.sqrt(v2[0]**2+v2[1]**2+v2[2]**2)
		v2n=(v2[0]/lengthV2,v2[1]/lengthV2,v2[2]/lengthV2)

		dp=Numeric.dot(v1n,v2n)
		if dp > 1:
			dp=1
		if dp<-1:
			dp=-1
		genericAngle=math.acos(dp)*(180/math.pi)
		if genericAngle>90:
			genericAngle=180-genericAngle

	### checks helix angles
		origin=index3
		p1=neighborhood[index3][0]-1
		v1=(x[p1]-x[origin],y[p1]-y[origin],z[p1]-z[origin])
		lengthV1=math.sqrt(v1[0]**2+v1[1]**2+v1[2]**2)
		v1n=(v1[0]/lengthV1,v1[1]/lengthV1,v1[2]/lengthV1)

		p2=neighborhood[index3][1]-1
		v2=(x[p2]-x[origin],y[p2]-y[origin],z[p2]-z[origin])
		lengthV2=math.sqrt(v2[0]**2+v2[1]**2+v2[2]**2)
		v2n=(v2[0]/lengthV2,v2[1]/lengthV2,v2[2]/lengthV2)

		dp=Numeric.dot(v1n,v2n)
		if dp > 1:
			dp=1
		if dp<-1:
			dp=-1
		helixAngle=math.acos(dp)*(180/math.pi)
		if helixAngle>90:
			helixAngle=180-helixAngle

	###checks sheet angles

		cloud=pointcloud[index3]
		arrayofxp=[]
		for firstpoint in cloud:
			point1=firstpoint-1
			pv1=(x[point1]-x[origin],y[point1]-y[origin],z[point1]-z[origin])
			lengthPV1=math.sqrt(pv1[0]**2+pv1[1]**2+pv1[2]**2)
			#print firstpoint, point1, pv1, lengthPV1
			pv1n=(pv1[0]/lengthPV1,pv1[1]/lengthPV1,pv1[2]/lengthPV1)

			for secondpoint in cloud:
				point2=secondpoint-1
				if point2 != point1 and point2 != origin:
					pv2=(x[point2]-x[origin],y[point2]-y[origin],z[point2]-z[origin])
					lengthPV2=math.sqrt(pv2[0]**2+pv2[1]**2+pv2[2]**2)
					pv2n=(pv2[0]/lengthPV2,pv2[1]/lengthPV2,pv2[2]/lengthPV2)
					xp=cross_product(pv1,pv2)

					lengthxp=math.sqrt(xp[0]**2+xp[1]**2+xp[2]**2)
					if lengthxp>0:
						xpn=(xp[0]/lengthxp, xp[1]/lengthxp, xp[2]/lengthxp)
					else:
						xpn=(xp[0], xp[1], xp[2])
					arrayofxp.append(xpn)
		dpxpcounter=0
		dpxpsum=0
		if len(arrayofxp) >=2:
			for dpxp1 in arrayofxp:
				for dpxp2 in arrayofxp:
					if dpxp1 != dpxp2:
						dpxp=Numeric.dot(dpxp1,dpxp2)
						if dpxp > 1:
							dpxpAngle=0
						elif dpxp<-1:
							dpxpAngle=180
						else:
							dpxpAngle=math.acos(dpxp)*(180/math.pi)
 						if dpxpAngle>90:
							dpxpAngle=180-dpxpAngle

						dpxpcounter=dpxpcounter+1
						dpxpsum=dpxpsum+dpxpAngle
			if dpxpsum==0 and dpxpcounter==0:
				betaAngle=0
			else: 
				betaAngle=dpxpsum/dpxpcounter
		else:
			betaAngle=90	
		generallist.append(genericAngle)
		sheetlist.append(betaAngle)
		helixlist.append(helixAngle)
		aspectratio=axisMatrix[index3]
		pascore=0
		print "%d: axis: %f, neighbor angle: %f, helix angle: %f, sheet angle: %f,  number of neighbors: %d"%(atomNumber[index3], aspectratio, genericAngle, helixAngle, betaAngle, len(cloud))
		if aspectratio <=2:
			pascore=pascore+1
		if aspectratio >=3:
			pascore=pascore-1
		if genericAngle <=40:
			pascore=pascore+1
		if genericAngle >=50:
			pascore=pascore-1		
		if helixAngle <=45 and mindistance1<12:
			pascore=pascore+0.5
		if helixAngle <=45 and mindistance2<12:
			pascore=pascore+0.5
		if betaAngle >=30 and betaAngle !=90:
			pascore=pascore-1
		if len(cloud) <= 3:
			pascore=pascore+1
		if len(cloud) > 3:
			pascore=pascore-1
		pseudoatomArray.append(float(pascore/4.0))	

		index3=index3+1
##################################################################



############################Scoring algorithm
index4=0
scorefile="score-%s.pdb"%(targetName)
outscore=open(scorefile,"w")

while index4 < atomCount:
	score=0
	temp_neighbors=neighborhood[index4]
	
	print "Atom Number: %s   "%(atomNumber[index4])
	
	print "      Correlation:       %s"%(coeffArray[index4]),
	if coeffArray[index4] >= (0.9*avghhvalue):
		tmpscore=(coeffArray[index4]/maxValue)
		score=score+tmpscore*coeffwt
		print " (+%f)"%(tmpscore)
	else:
		tmpscore=(coeffArray[index4]-avghhvalue)/avghhvalue
		score=score+tmpscore*coeffwt
		print " (%f)"%(tmpscore)	
	
	print "      Skeleton:  %s"%(skeletonArray[index4])
	score=score+skeletonArray[index4]*skeletonwt

	
	print "      Pseudoatom geometry:      %s"%(pseudoatomArray[index4])
	score=score+pseudoatomArray[index4]*pseudoatomwt

	
	print "    Score: %f"%(score) 
	
	outscore.write(lines1[index4][:60]+"%6.2f"%(score)+lines1[index4][66:])
	index4=index4+1
outscore.close()
##################################################################
