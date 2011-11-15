#!/usr/bin/env python
###	createcmm.py	Matthew Baker 11/2004

#N cmm-morph.py
#F morph between 2 cmm files

import os
import sys
import string
import commands
import math
from math import *
from sys import argv

if (len(argv)!=4) :
	print "Usage:\ncmm-morph.py <input cmm> <input cmm> <steps> \n"
	sys.exit(1)

target1=argv[1]
target2=argv[2]
steps=int(argv[3])

X1=[]
Y1=[]
Z1=[]
file1=open(target1, "r")
lines1=file1.readlines()
file1.close()
for line in lines1:
	if str(line[1:8].strip())=="marker":
		split1=string.split(line, ' ')
		for element in split1:
			checkelement=str(element[0:2].strip())
			if checkelement == "x=":
				split2=string.split(element,'=')
				X1.append(float(split2[1][1:-2].strip()))
			if checkelement == "y=":
				split2=string.split(element,'=')
				Y1.append(float(split2[1][1:-1].strip()))	
			if checkelement== "z=":
				split2=string.split(element,'=')
				Z1.append(float(split2[1][1:-1].strip()))
X2=[]
Y2=[]
Z2=[]
file2=open(target2, "r")
lines2=file2.readlines()
file2.close()
for line in lines2:
	if str(line[1:8].strip())=="marker":
		split1=string.split(line, ' ')
		for element in split1:
			checkelement=str(element[0:2].strip())
			if checkelement == "x=":
				split2=string.split(element,'=')
				print split2
				X2.append(float(split2[1][1:-2].strip()))
			if checkelement == "y=":
				split2=string.split(element,'=')
				Y2.append(float(split2[1][1:-1].strip()))	
			if checkelement== "z=":
				split2=string.split(element,'=')
				Z2.append(float(split2[1][1:-1].strip()))	

print X1
print X2
model=0
while model < steps:
	output="morph-%s-%s-%d.cmm"%(target1,target2,model)
	outfile=open(output,"w")
	firstline="<marker_set name=\"marker set for %s\">\n"%(output)
	outfile.write(firstline)
	counter=0
	while counter < len(X1):
		newX=(float(model)/float(steps))*X1[counter] + (float(steps-model)/float(steps))*X2[counter]
		newY=(float(model)/float(steps))*Y1[counter] + (float(steps-model)/float(steps))*Y2[counter]
		newZ=(float(model)/float(steps))*Z1[counter] + (float(steps-model)/float(steps))*Z2[counter]
		#print newX,newY,newZ
		nextline="<marker id=\"%d\" x=\"%f\" y=\"%f\" z=\"%f\"  radius=\"2\"/>\n"%(counter+1,newX,newY,newZ)
		outfile.write(nextline)
		counter=counter+1
	counter2=0
	while counter2 < (len(X1)-1):
		nextline="<link id1=\"%d\" id2=\"%d\" r=\"1\" g=\"0\" b=\"0\" radius=\"1\"/>\n"%(counter2+1,counter2+2)
		outfile.write(nextline)
		counter2=counter2+1
	lastline="</marker_set>\n"
	outfile.write(lastline)
	outfile.close()
	model=model+1
