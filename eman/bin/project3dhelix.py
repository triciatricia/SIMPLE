#!/usr/bin/env python
###	project3dhelix.py	Steven Ludtke	9/2003
### This program will make axial and near-axial projections of 3D volumes
### (not necessarily cubic ones)

#N project3dhelix.py
#F This program will make axial and near-axial projections of 3D volumes
#T X
#1
#P <3d model>	Input model
#P ang=<ang step>	Step in degrees between projections
#P [siderange=<angmax>]	Maximum azimuthal angle, defined by vertical subunit spacing and pitch
#P [tilt=<ang>]	Maximum axis tilt
#P [out=<outfile>]	Output filespec
#P [as1]	Set # particles to 1 in each projection image
#D Not documented yet

import os
import sys
import random
import time
import string
import math
from os import system
from os import unlink
from sys import argv
import EMAN

def LOGbegin(ARGV):
	out=open(".emanlog","a")
	b=string.split(ARGV[0],'/')
	ARGV[0]=b[len(b)-1]
	out.write("%d\t%d\t1\t%d\t%s\n"%(os.getpid(),time.time(),os.getppid(),string.join(ARGV," ")))
	out.close()

def LOGend():
	out=open(".emanlog","a")
	out.write("%d\t%d\t2\t-\t\n"%(os.getpid(),time.time()))
	out.close()


#### MAIN

if (len(argv)<2) :
	print "project3dhelix.py <3d map> ang=<angular sep> [siderange=<angmax>] [tilt=<ang>] [out=<output>]"
	sys.exit(1)

pi=math.pi
ang=1.0
siderange=360.0
tilt=0.0
out="proj.hed"
as1=-1

for i in argv[2:] :
#	s=i.split('=')
	s=string.split(i,'=')
	if (s[0]=="ang") : ang=float(s[1])
	elif (s[0]=="siderange") : siderange=float(s[1])
	elif (s[0]=="tilt") : tilt=float(s[1])
	elif (s[0]=="out") : out=s[1]
	elif (s[0]=="as1") : as1=1
	else:
		print "Unknown argument ",i
		sys.exit(1)

LOGbegin(argv)
vol=EMAN.EMData()
if (vol.readImage(argv[1])) :
	print "Cannot read input ",argv[1]
	sys.exit(1)

try:
	os.unlink(out[:-4]+".hed")
	os.unlink(out[:-4]+".img")
except:
	pass

# tilt now becomes an integer in units of 'ang'
if (tilt==0.0) : tilt=1
else : tilt=int(2+math.floor(tilt/ang-.5))

n=0
for alti in range(tilt):
	alt=pi/2.0-alti*ang*pi/180.0
	if (alti==0) : azr=int(siderange/ang)	# /2 ?
	else : azr=int(siderange/ang)
	for azi in range(azr):
		az=azi*ang*pi/180.0
		print "%d\t%f\t%f"%(n,alt*180.0/pi,az*180.0/pi)
		p=vol.project3d(alt,az,0,-5)
		p.setRAlign(alt,az,0)
		p.setNImg(as1)
		p.writeImage(out,-1)
		n+=1

LOGend()
