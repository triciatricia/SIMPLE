#!/usr/bin/env python
###	makeinitialmodel.py	Steven Ludtke	3/2005
### This program guides a user through making an initial model (3D)
###

#N makeinitialmodel.py
#F Interactively allows the user to make an initial model for iterative reconstruction
#T X
#1
#D Interactive prompts, no documentation.

import os
import sys
import time
import string
from os import system
from os import unlink
from sys import argv
import EMAN
try: import readline
except: pass
import random
from math import *

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

print """********** makeinitialmodel.py ************

Hello. This program will assist you in constructing a variety of mathematical
3D models for use as initial models or other purposes. I will ask you a
series of questions which will allow me to construct a model for you.

Enter the dimensions of the volume you wish to create in pixels as x y z (eg, 64 64 64):
"""
dim=[]
while len(dim)!=3:
	try:
		dim=[int(i) for i in raw_input("x y z > ").split()]
	except:
		print "Please enter 3 space separated numbers"
		
print "\nA/pixel for the generated map ?"
apix=float(raw_input("A/pix > "))

print "\nDo you wish to create a random (r) or specified (s) model ?"
rors=""
while len(rors)==0 or (not rors[0] in "rs") :
	rors=raw_input("r/s > ")

blobs=[]
	
if rors[0]=="r" :
	print "\nHow many random Gaussian blobs should I generate ?"
	nblobs=int(raw_input("nblobs > "))
	
	print "\nHow large (radius in A) should each blob be ?"
	blobsize=float(raw_input("blobsize (A) > "))
	
	print "\nRoughly how large (radius in A) would you like the distribution to be ?"
	distsize=float(raw_input("distsize (A) > "))

	for i in range(nblobs):
		v=(1.0e6,1.0e6,1.0e6)
		while v[0]**2+v[1]**2+v[2]**2>distsize**2: 
			v=(random.uniform(-distsize,distsize),random.uniform(-distsize,distsize),random.uniform(-distsize,distsize))
		blobs.append([hypot(v[0],v[1]),360.0*atan2(v[1],v[0])/pi,v[2],blobsize,blobsize,blobsize])
	
elif rors[0]=="s" :
	print """\nI will allow you to enter a series of random Gaussian blobs. You can specify the position and
dimensions of each. Blob positions are specified in cylindrical coordinates. Specify 
r (the distance from the z axis), theta (angle in degrees from the x axis in the x-y plane), and z.
All values are specified in Angstroms or Degrees."""
#	print "\nWhat symmetry would you like applied to the final model, just leave this blank for no symmetry."
#	sym=raw_input("symmetry > ")
	
	print "\nEnter blob parameters. Enter an empty line when done\n"
	while 1:
		try:
			ng=[float(i) for i in raw_input("r theta z dx dy dz > ").split()]
		except:
			break
		if len(ng)!=6 : break
#		ng[1]=ng[1]*180.0/pi
		
		blobs.append(ng)
		
LOGbegin(argv)

# nowe we build the model
model=EMAN.EMData()
model.setSize(dim[0],dim[1],dim[2])
model.zero()

# loop over all gaussians
for i in blobs:
	i[0]/=apix
	i[2]/=apix
	j=(cos(i[1]*pi/180.0)*i[0]+dim[0]/2,sin(i[1]*pi/180.0)*i[0]+dim[1]/2,i[2]+dim[2]/2)
	i[3]/=apix
	i[4]/=apix
	i[5]/=apix
	# now loop over the necessary voxels
	print j,i
	for z in range(int(max(j[2]-i[5]*3.0,0.0)),int(min(j[2]+i[5]*3.0,dim[2]-1))):
		for y in range(int(max(j[1]-i[4]*3.0,0.0)),int(min(j[1]+i[4]*3.0,dim[1]-1))):
			for x in range(int(max(j[0]-i[3]*3.0,0.0)),int(min(j[0]+i[3]*3.0,dim[0]-1))):
				r=((x-j[0])/i[3])**2+((y-j[1])/i[4])**2+((z-j[2])/i[5])**2
				model.setValueAt(x,y,z,exp(-r)+model.valueAt(x,y,z))

model.writeImage("model.mrc",-1)

LOGend()

print "\n\nDone. Output in model.mrc"
