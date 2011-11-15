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
from Numeric import transpose

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
angMax=75
removeHelix=0
runhh=0
inthh="none"
filternumber=1.5
hhthr=.3
traget_size=0
finaltrans=0

if (len(argv)<3) :
	print "Usage:\nhelixhunterX.py <input mrc/pdb file> <apix>\n"
	print "If input is an mrc, segment3d is run first. Avaliable options: <seg=> <thr=>\n"
	print "If no interemdiate coeff file is given, a correlation map will be calculated (slow) and helices identified at 0.3.  The user can speicfy the intermediate correlation map and threshold with: <hh=int hh file> <hhthr=>\n"
	print "Advance options for filtering out false positives: <dist=> <angle=> <filternumber=>\n"
	sys.exit(1)

target=argv[1]
t=target.split('.')
targetName=str(t[0])
targetExt=str(t[-1])

apix=float(argv[2])
dist=7/apix
if dist!=math.ceil(dist):
	if dist%math.floor(dist) <=0.5:
		dist=math.floor(dist)+0.5
	else:
		dist=math.ceil(dist)

print dist
for a in argv[3:] :
        s=a.split('=')
	if (s[0]=='seg') :
		seg=int(s[1])
	elif (s[0]=='trans'):
		finaltrans=float(s[1])
	elif (s[0]=='thr') :
		thr=float(s[1])
	elif (s[0]=='dist') :
		dist=float(s[1])
	elif (s[0]=='angle'):
		angMax=float(s[1])
	elif (s[0]=='filternumber'):
		filternumber=float(s[1])
	elif (s[0]=='hhthr'):
		hhthr=float(s[1])
	elif (s[0]=='hh'):
		inthh=str(s[1])
        else:
                print("Unknown argument "+a)
                exit(1)

print inthh
###################################read input data
if (inthh=="none"):
	print inthh
	cmdhh="helixhunter2 %s %s.iv %f percen=%f docylccffirst int=int-%s"%(target, targetName, apix, hhthr, targetName)
	os.system(cmdhh)
	inthh="int-%s-coeff.mrc"%(targetName)

if (targetExt=="mrc"):
	targetMRC=EMAN.EMData()
	targetMRC.readImage(argv[1],-1)
	target_xsize=targetMRC.xSize()
	target_ysize=targetMRC.ySize()
	target_zsize=targetMRC.zSize()
	print("Segment3D")
	pdbOut="seg-%s.pdb"%(targetName)
	cmd0="segment3d %s seg-%s nseg=%d thr=%f apix=%f pdb=%s"%(target, target, seg, thr, apix, pdbOut)
	os.system(cmd0)
	file1=open(pdbOut, "r")
else:
	file1=open(target, "r")
lines1=file1.readlines()
file1.close()

#################################read in coordinates of points
x=[]
y=[]
z=[]
atomNumber=[]
counter=0

for line in lines1:
	isatom=str(line[0:6].strip())
	if (isatom=="ATOM"):
		x.append(float(line[30:38].strip()))
		y.append(float(line[38:46].strip()))
		z.append(float(line[46:54].strip()))
		atomNumber.append(int(line[6:11].strip()))
		counter=counter+1

hhMrc=EMAN.EMData()
hhMrc.readImage(inthh,-1)

###########################FILTERS Ca POINTS BASED ON HELIXHUNTER INT RESULTS
helixCounter=0
xHArray=[]
yHArray=[]
zHArray=[]
linesH=[]

hc=0
helixH=open("filtered-h2.pdb","w")
while hc < counter:
	xh=x[hc]/apix
	yh=y[hc]/apix
	zh=z[hc]/apix
	coord=(xh,yh,zh)
	l=lines1[hc]
	hhvalue=hhMrc.valueAtInterp(xh,yh,zh)
	if hhvalue >= hhthr:
		helixH.write(l)
		linesH.append(l)
		xHArray.append(xh)
		yHArray.append(yh)
		zHArray.append(zh)
		helixCounter=helixCounter+1
	hc=hc+1
helixH.close()
helixH2=open("filtered-h2.pdb", "r")
lines2=helixH2.readlines()
helixH2.close()

################################### find triplet of points
i=0
j=0
distance=[0]*helixCounter
neighborhood=[]
while (i < helixCounter):
	x1=xHArray[i]
	y1=yHArray[i]
	z1=zHArray[i]
	distance[i]=[0]*helixCounter
	while (j < helixCounter):
		x2=xHArray[j]
		y2=yHArray[j]
		z2=zHArray[j]
		distance[i][j]=(j,math.sqrt((x1-x2)**2+(y1-y2)**2+(z1-z2)**2))
		j=j+1
	j=0
	i=i+1


##############################NEIGHBOR DISTANCE AND ANGLE CALCULATOR
n=0
HelixPoints=[]
avgvaluedict={}
while (n<helixCounter):
	angleSum=0
	AngleBigSum=0
	AngleAvg=0
	q=0
	neighborCounter=0
	neighborhood=[]
	lineorigin=lines2[n]
	originpoint=int(lineorigin[6:11].strip())

	while (q<helixCounter):
		if (distance[n][q][1]<=.1):
			origin=distance[n][q][0]
		elif (distance[n][q][1]<=dist):
			neighborhood.append(distance[n][q][0])
			neighborCounter=neighborCounter+1
		q=q+1
	h1=0
	aboveX=0
	belowX=0
	while h1 < neighborCounter:
		p1=neighborhood[h1]
		v1=(xHArray[p1]-xHArray[origin],yHArray[p1]-yHArray[origin],zHArray[p1]-zHArray[origin])
		lengthV1=math.sqrt(v1[0]**2+v1[1]**2+v1[2]**2)
		v1n=(v1[0]/lengthV1,v1[1]/lengthV1,v1[2]/lengthV1)
		g=0
		p1pixelsum=0
		while g<lengthV1:
			scalefactor=g/math.floor(lengthV1)
			xinterp1=((scalefactor*xHArray[p1])+((1-scalefactor)*xHArray[origin]))
			yinterp1=((scalefactor*yHArray[p1])+((1-scalefactor)*yHArray[origin]))
			zinterp1=((scalefactor*zHArray[p1])+((1-scalefactor)*zHArray[origin]))
			p1density=float(hhMrc.valueAtInterp(xinterp1,yinterp1,zinterp1))
			p1pixelsum=p1density+p1density
			g=g+1
		origintoP1=p1pixelsum/g
		h2=0
		while h2 <neighborCounter:
			p2=neighborhood[h2]
			v2=(xHArray[p2]-xHArray[origin],yHArray[p2]-yHArray[origin],zHArray[p2]-zHArray[origin])
			lengthV2=math.sqrt(v2[0]**2+v2[1]**2+v2[2]**2)
			v2n=(v2[0]/lengthV2,v2[1]/lengthV2,v2[2]/lengthV2)
			h=0
			p2pixelsum=0
			while h<lengthV2:
				scalefactor=h/math.floor(lengthV2)
				xinterp2=((scalefactor*xHArray[p2])+((1-scalefactor)*xHArray[origin]))
				yinterp2=((scalefactor*yHArray[p2])+((1-scalefactor)*yHArray[origin]))
				zinterp2=((scalefactor*zHArray[p2])+((1-scalefactor)*zHArray[origin]))
				p2density=float(hhMrc.valueAtInterp(xinterp2,yinterp2,zinterp2))
				p2pixelsum=p2density+p2density
				h=h+1
			origintoP2=p2pixelsum/h

			dp=dot(v1n,v2n)
			if dp > 1:
				dp=1
			if dp<-1:
				dp=-1
			helixAngle=math.acos(dp)*(180/math.pi)
			if helixAngle>90:
				helixAngle=180-helixAngle
			atomcounter=0
			for line2 in lines2:
				if atomcounter==origin:
					originpoint=int(line2[6:11].strip())
				if atomcounter==neighborhood[h1]:
					neighbor1point=int(line2[6:11].strip())
				if atomcounter==neighborhood[h2]:
					neighbor2point=int(line2[6:11].strip())
				atomcounter=atomcounter+1
			print "point %d to %d (%f) vs %d to %d (%f): %f"%(originpoint,neighbor1point,origintoP1,originpoint,neighbor2point,origintoP2,helixAngle)
			if helixAngle>angMax:
				aboveX=aboveX+1
			elif helixAngle>1 and helixAngle<=angMax:
				belowX=belowX+1
			angleSum=angleSum+helixAngle
			h2=h2+1
		angleBigSum=AngleBigSum+angleSum
		h1=h1+1
	if neighborCounter==0:
		angleAvg=90
	elif neighborCounter==1:
		angleAvg=0
	else:
		angleAvg=angleBigSum/(neighborCounter*(neighborCounter-1))
	print "point %d average angle: %f :%f %f"%(originpoint,angleAvg, belowX, aboveX)
	avgvaluedict[originpoint]=angleAvg
	if ((angleAvg<=angMax and belowX>=aboveX) or (angleAvg==0)):
		HelixPoints.append(origin)
	n=n+1
#print HelixPoints


dm=0
distMatrix=[]
rowZero=[9999999]*len(HelixPoints)
while dm<len(HelixPoints):
	distMatrix.append(rowZero)
	dm=dm+1
PointMatrix=distMatrix

q=0
outPdbHelix=open("helix.pdb","w")
atomArray=[]
lineArray=[]
while q<len(HelixPoints):
	point=HelixPoints[q]
	lineH1=linesH[point]
	lineArray.append(lineH1)
	outPdbHelix.write(lineH1)
	xH1=float(lineH1[30:38].strip())/apix
	yH1=float(lineH1[38:46].strip())/apix
	zH1=float(lineH1[46:54].strip())/apix
	atomArray.append(int(lineH1[6:11].strip()))
	r=0
	rowMatrix=[0]*len(HelixPoints)
	while r<q:
		point2=HelixPoints[r]
		lineH2=linesH[point2]
		xH2=float(lineH2[30:38].strip())/apix
		yH2=float(lineH2[38:46].strip())/apix
		zH2=float(lineH2[46:54].strip())/apix
		H1H2Length=math.sqrt((xH1-xH2)**2+(yH1-yH2)**2+(zH1-zH2)**2)
		rowMatrix[r]=H1H2Length
		r=r+1
#	print rowMatrix
	distMatrix[q]=rowMatrix
	q=q+1
outPdbHelix.close()

TdistMatrix=transpose(distMatrix)
bigMatrix=distMatrix+TdistMatrix

s=0
while s<len(HelixPoints):
	t=0
#	print "Within %f of %d: "%(dist, atomArray[s])
	while t<len(bigMatrix[s]):
		if bigMatrix[s][t]<=dist:
			PointMatrix[s][t]=atomArray[t]
#			print atomArray[t],bigMatrix[s][t]
		else:
			PointMatrix[s][t]=0
		t=t+1
#	print PointMatrix[s]
	s=s+1
#print ClusterArray
#print PointMatrix
a=0
Helices=[]
while a<len(PointMatrix):
	b=0
	rowAtom=atomArray[a]
	while b<len(PointMatrix[a]):
		if PointMatrix[a][b]!=0:
			columnAtom=atomArray[b]
			i=0
			foundrow=-1
			foundcolumn=-1
			while i<len(Helices):
				if rowAtom in Helices[i]:
					foundrow=i
				if columnAtom in Helices[i]:
					foundcolumn=i
				i=i+1
#			print rowAtom,columnAtom,foundrow,foundcolumn
			if foundrow!=-1 and foundcolumn!=-1:
				if foundrow!=foundcolumn:
					Helices[foundrow].extend(Helices[foundcolumn])
					del Helices[foundcolumn]
			elif foundrow!=-1:
				Helices[foundrow].append(columnAtom)
			elif foundcolumn!=-1:
				Helices[foundcolumn].append(rowAtom)
			elif foundrow==-1 and foundcolumn==-1:
#				Helix=[]
				if rowAtom==columnAtom:
					pass
#					Helix=[rowAtom]
				else:
					Helix=[rowAtom,columnAtom]
					Helices.append(Helix)
		b=b+1
	a=a+1
#print Helices

finalHelices=[]
counter=0
while counter<len(Helices):
	HelixMetric=0
	counter2=0
	counter3=0
	sumHelixValuesquared=0
	sumHelixValue=0
	sumcorrelation=0
	while counter2<len(Helices[counter]):
		index=Helices[counter][counter2]
#		print index, lines1[int(index)-1]
		pointvalue=avgvaluedict[index]
		if pointvalue>=1:
			counter3=counter3+1
		sumHelixValuesquared=pointvalue*pointvalue+sumHelixValuesquared
		sumHelixValue=pointvalue+sumHelixValue
		counter4=0
		x3=float(lines1[int(index)-1][30:38].strip())/apix
		y3=float(lines1[int(index)-1][38:46].strip())/apix
		z3=float(lines1[int(index)-1][46:54].strip())/apix
		avgcorrelation=0
		while counter4<len(Helices[counter]):
			index2=Helices[counter][counter4]
			x4=float(lines1[int(index2)-1][30:38].strip())/apix
			y4=float(lines1[int(index2)-1][38:46].strip())/apix
			z4=float(lines1[int(index2)-1][46:54].strip())/apix
			x3x4Length=math.sqrt((x4-x3)**2+(y4-y3)**2+(z4-z3)**2)
			correlation=0
			if x3x4Length!=0:
				f=0
				pixelsum=0
				while f<x3x4Length:
					scalefactor=f/math.floor(x3x4Length)
					xinterp=((scalefactor*x3)+((1-scalefactor)*x4))
					yinterp=((scalefactor*y3)+((1-scalefactor)*y4))
					zinterp=((scalefactor*z3)+((1-scalefactor)*z4))
					x3x4density=float(hhMrc.valueAtInterp(xinterp,yinterp,zinterp))
					pixelsum=x3x4density+pixelsum
					f=f+1
#					print x3, y3, z3, x4, y4, z4, xinterp, yinterp, zinterp, x3x4density
				correlation=pixelsum/f
				sumcorrelation=sumcorrelation+correlation
			counter4=counter4+1
		allpointssum=sumcorrelation/(counter4*(counter4-1))
		counter2=counter2+1
	avgallpoints=(allpointssum/counter2)/2
	if counter3==0:
		counter3=1
	avgHelixValue=sumHelixValue/counter3
	stdHelixValue=math.sqrt(math.fabs((sumHelixValuesquared-counter2*(avgHelixValue**2))/counter2))
	if stdHelixValue==0:
		HelixMetric=((90-avgHelixValue)*allpointssum)
	else:
		HelixMetric=((90-avgHelixValue)*allpointssum)/stdHelixValue

	print "Possible helix %d contains points:%s average angle:%f angle sigma:%f avgerage correlation value:%f metric:%f"%(counter,Helices[counter],avgHelixValue,stdHelixValue,allpointssum,HelixMetric)
	if HelixMetric >= filternumber:
		finalHelices.append(Helices[counter])
	counter=counter+1
print finalHelices
############CREATES DEJAVU OUTPUT AND CONVERTS TO PDB FILE####################
c=0
outDejavu=open("helix.sse","w")
outDejavu.write("!\n")
outDejavu.write("!  ===  0dum\n")
outDejavu.write("!\n")
outDejavu.write("MOL   0dum\n")
outDejavu.write("NOTE  from helixhunter3.py\n")
linePDB="PDB   %s\n"%(target)
outDejavu.write(linePDB)
outDejavu.write("!\n")
outPdbHelix2=open("helix2.pdb","w")

while c<len(finalHelices):
	d=0
	ListPoints=[]
	while d<len(finalHelices[c]):
		k=0
		while k<len(atomArray):
			Points=[]
			if finalHelices[c][d]==atomArray[k]:
				templine=lineArray[k]
				outPdbHelix2.write(templine)
				Points=[atomArray[k],float(templine[30:38].strip()),float(templine[38:46].strip()),float(templine[46:54].strip())]
				ListPoints.append(Points)
			k=k+1
		d=d+1
	j=0
	currentBig=0
	end1=0
	end2=0
	end1location=[]
	end2location=[]
	while j<len(ListPoints):
		q=0
		while q<len(ListPoints):
			HelixLength=math.sqrt((ListPoints[j][1]-ListPoints[q][1])**2+(ListPoints[j][2]-ListPoints[q][2])**2+(ListPoints[j][3]-ListPoints[q][3])**2)
#			print ListPoints[j][0], ListPoints[q][0], HelixLength
			if HelixLength>currentBig:
				currentBig=HelixLength
				end1=ListPoints[j][0]
				end1location=[ListPoints[j][1],ListPoints[j][2],ListPoints[j][3]]
				end2=ListPoints[q][0]
				end2location=[ListPoints[q][1],ListPoints[q][2],ListPoints[q][3]]
			q=q+1
		j=j+1
	HelixLength=currentBig
	print "Helix %d   Length: %f    end1: %f    end2: %f"%(c,HelixLength,end1,end2)
	intlength=int(math.ceil(HelixLength/1.54))
	if (HelixLength*apix)>8:
#	if HelixLength>=6.0:
		end1location[0]=end1location[0]+finaltrans
		end1location[1]=end1location[1]+finaltrans
		end1location[2]=end1location[2]+finaltrans
		end2location[0]=end2location[0]+finaltrans
		end2location[1]=end2location[1]+finaltrans
		end2location[2]=end2location[2]+finaltrans
		dejavuline="ALPHA 'A%d' '%d' '%d' %d %f %f %f %f %f %f\n"%(c,c*100,c*100+(intlength-1),intlength,end1location[0],end1location[1],end1location[2],end2location[0],end2location[1],end2location[2])
		outDejavu.write(dejavuline)
	c=c+1
outDejavu.close()
outPdbHelix2.close()

cmdHH="dejavu2pdb.py helix.sse hh-%s-%f-%f.pdb"%(targetName,filternumber,dist)
os.system(cmdHH)
