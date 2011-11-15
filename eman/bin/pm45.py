#!/usr/bin/env python
# pm45.py  Steve Ludtke   08/23/2005
#
# This program is designed to, in conjunction with refine2d.py, process pairs
# of particles collected at +45 and -45 degree tilt. Reference free classification
# is performed (refine2d.py) on one of the tilts, then particles from a single
# class are processed by this program from the other image to produce a set
# of particles used with make3d.

# pm45.py <in cls file> <in opp tilt raw imgs> <out stack>

from sys import argv
from pprint import pprint
from EMAN import *
from math import *

# read the cls file
fin=file(argv[1],"r")
lns=fin.readlines()[1:]
fin.close()
l2=lns[0]
lns=lns[1:]

# parse the lines from the cls file [angle,ptcl #,dx,dy,flip]
lns=[[float(i.split(',')[1]),int(i.split()[0]),float(i.split(',')[2]),float(i.split(',')[3]),int(i.split(',')[4])] for i in lns]

# For now we don't use flipped images, this should be easily fixed
# with a little thought about the geometry of the system
lns=[i for i in lns if i[4]==0]

# sort by angle
lns.sort()

# try to do some centering
lst=[]
for i in lns:
	b=EMData()
	b.readImage(argv[2],i[1])
	lst.append(b)
avg=lst[0].copy(0)
avg.makeAverage(lst)
avg.filter(1,10,1)
#avg.display()

# This is the 'top' view, ie - from the current directory, not the opposite tilt
i2=EMData()
i2.readImage(l2.split()[1],int(l2.split()[0]))
i2.setRAlign(0,0,0)
i2.setTAlign(0,0,0)
i2.setNImg(4)	# 4 is arbitrary
# Remove this for now due to vertical artifacts
#i2.writeImage(argv[3],-1)


# write the output stack
for i in lns:
	b=EMData()
	b.readImage(argv[2],i[1])
	b.transAlign(avg,0,1,avg.xSize()/8)
	b.rotateAndTranslate()
#	b.filter(-5,20,1)
	b.setRAlign(pi/2,i[0],0)
	b.setTAlign(0,0,0)
	b.setNImg(1)
	b.writeImage(argv[3],-1)

print len(lns)," images written to ",argv[3]

