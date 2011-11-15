#!/usr/bin/env python
# This script will convert surface data represented as greyscale to volume data
# ie - for AFM or other surface microscopies

import os
import sys
import random
import time
import string
import EMAN
from sys import argv

ERR_EXIT=1
ERR_CRIT=2
ERR_WARN=3
ERR_INFO=4
def error(type,msg):
	if (type==ERR_CRIT) : print "Critical Error: ",msg
	if (type==ERR_WARN) : print "Warning: ",msg
	if (type==ERR_INFO) : print msg
	if (type==ERR_EXIT) :
		print "Fatal Error: ",msg
		sys.exit(1)

if (len(argv)<2) :
	print "atmtomrc <infile> <outfile> [apix=<A/pixel>]  [aden=<A/density unit] [origin=<x>,<y>] [size=<w>,<h>] [fill]"
	sys.exit(1)

apix=1
aden=1
origin=[0,0]
size=[-1,-1,-1]
fill=0

for i in argv[3:] :
	s=string.split(i,'=')
	if (s[0]=="apix") : apix=float(s[1])
	elif (s[0]=="aden") : aden=float(s[1])
	elif (s[0]=="origin") : origin=[int(s[1].split(',')[0]),int(s[1].split(',')[1])]
	elif (s[0]=="size") : size=[int(s[1].split(',')[0]),int(s[1].split(',')[1]),-1]
	elif (s[0]=="fill") : fill=1
	else: error(ERR_EXIT,"Unknown argument "+i)

input=EMAN.EMData()
if (input.readImage(argv[1],0)) : error(ERR_EXIT,"Cannot read input file")

if (size[0]==-1) : size=[input.xSize()-origin[0],input.ySize()-origin[1],-1]
if (size[0]<0 or size[1]<0) : error(ERR_EXIT,"Image region specification incorrect")
size[2]=int((input.Max()-input.Min())*aden/(apix))+1

print "Output map is %d x %d x %d"%(size[0],size[1],size[2])

print size
output=EMAN.EMData()
output.setSize(size[0],size[1],size[2])
output.zero()
min=input.Min();

for y in range(origin[1],origin[1]+size[1]):
	for x in range(origin[0],origin[0]+size[0]):
		z=int((input.valueAt(x,y)-min)*aden/(apix))
		if (fill) :
			for zz in range(0,z): output.setValueAt(x,y,zz,1)
		else :output.setValueAt(x,y,z,1)

output.update()
output.writeImage(argv[2])
