#!/usr/bin/env python
import os
import sys
import string
import EMAN
from math import *
from sys import argv
import commands

def Update_map(Max_location,rangemin,rangemax):
	location=Max_location
	rmin=int(round(rangemin/2))
	rmax=int(round(rangemax/2))+1
	maxdistance=sqrt(3*rmin**2)
#	print rmin, rmax
#	print location, 
#	target.setValueAt(location[0],location[1],location[2], 0.0)
	for x in (range(rmin,rmax)):
		for y in (range(rmin,rmax)):
			for z in (range(rmin,rmax)):
				temp_value=target.valueAt(location[0]+x,location[1]+y,location[2]+z)
				distance=sqrt(x**2+y**2+z**2)
				if x==0 and y==0 and z==0:
					pixel_value=0.0
				else:
					#pixel_value=temp_value/((abs(x)+abs(y)+abs(z))/((x**2+y**2+z**2)**.5))
					#pixel_value=temp_value/(9/(abs(x)+abs(y)+abs(z)))
					pixel_value=temp_value*(distance/maxdistance)
#				print x,y,z,temp_value, pixel_value
				target.setValueAt(location[0]+x,location[1]+y,location[2]+z, pixel_value)
				target.update()

if (len(argv)!=6) :
	print "Usage: pseudoatom.py <map> <output> <apix> <res> <threshold>"
	sys.exit(1)

target=EMAN.EMData()
target.readImage(argv[1],-1)

apix=float(argv[3])
res=float(argv[4])
threshold=float(argv[5])

rangemin=-1*res/apix
rangemax=res/apix
print rangemin, rangemax

mapsize=target.xSize()
#offset=-1*mapsize*0.5*apix
offset=0
Max_value=target.Max()
Max_location=target.MinLoc()

outfile=argv[2]
out=open(outfile,"w")

i=1
chain="A"
while Max_value >= threshold:
	Max_location=target.MinLoc()
	out.write("ATOM  %5d  C   GLY %s%4d    %8.3f%8.3f%8.3f  1.00     0      S_00  0 \n"%(i,chain,i,offset+Max_location[0]*apix,offset+Max_location[1]*apix,offset+Max_location[2]*apix))
	Update_map(Max_location, rangemin,rangemax)
	
	Max_value=target.Max()
	i=i+1
out.close()
