#!/usr/bin/env python
import os
import sys
import string
import commands
import EMAN
from sys import argv

if (len(argv)!=4) :
	print "Usage:\nchimerart.py <input 3D mrc file> <output 3D mrc file> <alt,az,phi,dx,dy,dz>\n"
	sys.exit(1)



for a in argv[3:] :
	s=a.split(',')
	alt=float(s[0])*3.14/180
	az=float(s[1])*3.14/180
	phi=float(s[2])*3.14/180
	dx=float(s[3])
	dy=float(s[4])
	dz=float(s[5])

print alt,az,phi,dx,dy,dz

map1=EMAN.EMData()
map1.readImage(argv[1],-1)

oldx=map1.xSize()
oldy=map1.ySize()
oldz=map1.zSize()

newx=int(oldx+2*dx)
newy=int(oldy+2*dy)
newz=int(oldz+2*dz)
print int(-dx),int(-dy),int(-dz),newx,newy,newz
map2=map1.clip(int(-dx),int(-dy),int(-dz),newx,newy,newz)

map2.setRAlign(alt,az,phi)
map2.rotateAndTranslate()
map2.update()
#map2.setTAlign(dx,dy,dz)
#map2.rotateAndTranslate()
#map2.update()
map2.writeImage(argv[2])

#map2.readMRCArea(argv[2],oldx/2+dx,oldy/2+dy,oldz/2+dz,oldx,oldy,oldz)
#map2.update()
#map2.writeImage(argv[2])

