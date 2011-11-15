#!/usr/bin/env python
###	sseaxis.py	Matthew Baker 09/2003

#N sseaxis.py
#F sse medial axis

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


searchradius=1
if (len(argv)!=5) :
	print "Usage:\nsseaxis.py <input pdb file> <imput mrc file> <apix> <iterations>\n"
	sys.exit(1)

target=argv[1]
mrcfile=argv[2]
apix=float(argv[3])
iterations=int(argv[4])

file=open(target, "r")
lines=file.readlines()
file.close()

x=[]
y=[]
z=[]
xorig=[]
yorig=[]
zorig=[]
atomNumber=[]
counter=0
infile=EMAN.EMData()
infile.readImage(mrcfile,-1)

for line in lines:
	isatom=str(line[0:6].strip())
	if (isatom=="ATOM"):
		x.append(float(line[30:38].strip()))
		y.append(float(line[38:46].strip()))
		z.append(float(line[46:54].strip()))
		xorig.append(float(line[30:38].strip()))
		yorig.append(float(line[38:46].strip()))
		zorig.append(float(line[46:54].strip()))
		atomNumber.append(int(line[6:11].strip()))
		counter=counter+1

iterationcounter=0
while iterationcounter < iterations:
	xnew=[]*counter
	ynew=[]*counter
	znew=[]*counter
	i=0
	while (i < counter):
		x1=x[i]
		y1=y[i]
		z1=z[i]
		neighbor1distance=99999998.0
		neighbor2distance=99999999.0
		point1=0
		point2=0
		j=0
		while (j < counter):
			if i!=j:
				x2=x[j]
				y2=y[j]
				z2=z[j]
				distance=math.sqrt((x1-x2)**2+(y1-y2)**2+(z1-z2)**2)
				if distance > .001*apix:
					if  distance < neighbor2distance:
						if distance < neighbor1distance:
							neighbor2distance=neighbor1distance
							neighbor1distance=distance
							point2=point1
							point1=j
						else:
							neighbor2distance=distance
							point2=j
			j=j+1
		dweight=0
		d1=0
		d2=0
		while dweight<=1:
			dvalue1=infile.valueAtInterp((x1/apix)*dweight+(x[point1]/apix)*(1-dweight),(y1/apix)*dweight+(y[point1]/apix)*(1-dweight),(z1/apix)*dweight+(z[point1]/apix)*(1-dweight))
			d1=d1+dvalue1
			dvalue2=infile.valueAtInterp((x1/apix)*dweight+(x[point2]/apix)*(1-dweight),(y1/apix)*dweight+(y[point2]/apix)*(1-dweight),(z1/apix)*dweight+(z[point2]/apix)*(1-dweight))
			d2=d2+dvalue2
			dweight=dweight+.1
		if d1 and d2 >= 1:
			weight1=d1/(d1+d2)
			weight2=d2/(d1+d2)
		else:
			weight1=.5
			weight2=.5
		weight1=0.5
		weight2=0.5
		xmid=(weight1*x[point1])+(weight2*x[point2])
		ymid=(weight1*y[point1])+(weight2*y[point2])
		zmid=(weight1*z[point1])+(weight2*z[point2])
		maxvalue=infile.valueAtInterp(xmid/apix,ymid/apix,zmid/apix)
		dx=-1*searchradius
		while dx <=searchradius:
			xcoord=xmid/apix+dx
			dy=-1*searchradius
			while dy <=searchradius:
				ycoord=ymid/apix+dy
				dz=-1*searchradius
				while dz <=searchradius:
					zcoord=zmid/apix+dz
					coordvalue=infile.valueAtInterp(xcoord,ycoord,zcoord)
#					print atomNumber[i], xcoord,ycoord,zcoord, maxvalue, coordvalue
					if coordvalue >= maxvalue:
						Xmax=xmid+dx
						Ymax=ymid+dy
						Zmax=zmid+dz
						maxvalue=coordvalue		
					dz=dz+.25
				dy=dy+.25
			dx=dx+.25
		Xmax=xmid
		Ymax=ymid
		Zmax=zmid
		xnew.append(Xmax)
		ynew.append(Ymax)
		znew.append(Zmax)
		d=math.sqrt((xnew[i]-xorig[i])**2+(ynew[i]-yorig[i])**2+(znew[i]-zorig[i])**2)
		print atomNumber[i], atomNumber[point1], atomNumber[point2], weight1, weight2, neighbor1distance, neighbor2distance, d
		i=i+1
	x=xnew
	y=ynew
	z=znew
	iterationcounter=iterationcounter+1
	
	outfile="medial-%s"%(target)
	out=open(outfile,"w")
	index=0
	for i in lines:
		out.write(i[:30]+" %7.2f %7.2f %7.2f"%(x[index],y[index],z[index])+i[54:])
		index=index+1
	out.close()
