#!/usr/bin/env python
###	classifykmeans.py	Steven Ludtke	12/2003
### Program for classifying raw 2d or 3d data by kmeans

#N classifykmeans.py
#F This program will classify pre-aligned 2D or 3D images
#T X
#1
#P [stack=<input images>]	An image file containing all images to be classified
#P [list=<input images>]	A text file with a list of single image filenames
#P [classes=<#>]	Number of classes to generate. Default is 4.
#P [average=<prefix>]	Make averages of each class and save them to prefix.#.mrc
#P [clsfiles]	Generate cls* files
#P [listout=<file>]	Outputs a text file containing a list: <class> <ptcl #> <compare to mean>
#P [nosingle]	This will try to reject classes with only one member at each step
#D Simple k-means classifier for 2D or 3D images. Images must be prealigned.
#E This doesn't use MSA or any other data reduction technique. It's just a
#E simple classifier.
#D WARNING: The entire set to be classified must fit into memory

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
	print "classifykmeans.py [stack=<input images>] [list=<input images>] [classes=<#>] [average=<prefix>] [clsfiles] [listout=<file>]"
	sys.exit(1)

Ncls=4
averageout=None
listout=None
clsfiles=0
data=[]
stackname=None
nosingle=0

for i in argv[1:] :
	s=i.split('=')

	if (s[0]=="classes") : Ncls=int(s[1])
	elif (s[0]=="average") : averageout=s[1]
	elif (s[0]=="clsfiles") : clsfiles=1
	elif (s[0]=="listout") : listout=s[1]
	elif (s[0]=="nosingle") : nosingle=1
	elif (s[0]=="stack") :
		data=EMAN.readImages(s[1],-1,-1)
		stackname=s[1]
	elif (s[0]=="list") :
		fin=open(s[1],"r")
		fsp=fin.readlines()
		fin.close()
		for i in fsp:
			x=EMAN.EMData()
			x.readImage(i.strip())
			data.append(x)
	else:
		print "Unknown argument ",i
		exit(1)

if (len(data)==0) :
	print "No data to classify. Please specify stack= or list=."
	sys.exit(1)

print len(data)," images to classify."

# start with Ncls random images
centers=[]		# the average images for each class
for i in range(Ncls): centers.append(data[random.randint(0,len(data)-1)])

iter=40
npcold=[0]*Ncls

while (iter>0) :
	iter-=1

	classes=[]					# list of particle #'s in each class
	for i in range(Ncls): classes.append([])

	for i in range(len(data)):			# put each particle in a class
		best=(1.0e30,-1)
		for j in range(len(centers)):	# check for best matching center
			c=centers[j].lcmp(data[i],0)[0]
			if (c<best[0]) : best=(c,j)
		classes[best[1]].append((i,best[0]))

	# make new averages
	print "\nIteration ",40-iter
	todel=-1
	for j in range(len(centers)):
		print "%3d. %4d\t(%d)"%(j,len(classes[j]),npcold[j])
		if (len(classes[j])==0 ) :
			centers[j]=data[random.randint(0,len(data)-1)]		# reseed empty classes with random image
		elif nosingle and len(classes[j])==1:
			centers[j]=data[random.randint(0,len(data)-1)]		# reseed empty classes with random image
			todel=classes[j][0][0]		# delete the particle that was in its own class later
			iter+=1
		else :
			centers[j]=data[classes[j][0][0]].copy(0,0)
			for i in range(1,len(classes[j])):
				centers[j]+=data[classes[j][i][0]]
			centers[j].normalize()
			
	if todel!=-1 : del data[todel]
			
	npc=map(lambda x:len(x),classes)		# produces a list with the number of particles in each class
	if (npc==npcold) : break
	npcold=npc

if (averageout != None) :
	if (centers[0].zSize()>1) :
		for i in range(len(centers)):
			centers[i].writeImage(averageout+(".%04d"%i)+".mrc",0)
	else:
		for i in range(len(centers)):
			centers[i].setNImg(npc[i])
			centers[i].writeImage(averageout+".hed",-1)

if (listout!=None) :
	out=open(listout,"w")
	for j in range(len(classes)):
		for i in range(len(classes[j])):
			out.write("%d\t%d\t%1.5f\n"%(j,classes[j][i][0],classes[j][i][1]))
	out.close()

if (clsfiles!=None) :
	if (stackname) :
		os.system("rm cls????.lst")
		for j in range(len(classes)):
			out=open("cls%04d.lst"%j,"w")
			out.write("#LST")
			for i in range(len(classes[j])):
				out.write("%d\t%s\n"%(classes[j][i][0],stackname))
			out.close()
	else:
		os.system("rm cls????.????.mrc")
		for j in range(len(classes)):
			for i in range(len(classes[j])):
				data[classes[j][i][0]].writeImage("cls%04d.%04d.mrc"%(j,i))

