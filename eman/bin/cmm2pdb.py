#!/usr/bin/env python
###	createcmm.py	Matthew Baker 11/2004

#N cmm2pdb.py
#F conver cmm to pdb

import os
import sys
import string
import commands
import math
from math import *
from sys import argv

if (len(argv)!=3) :
	print "Usage:\ncmm2pdb.py <input cmm> <output pdb> \n"
	sys.exit(1)

target=argv[1]


X=[]
Y=[]
Z=[]
file1=open(target, "r")
lines1=file1.readlines()
file1.close()
for line in lines1:
	if str(line[1:8].strip())=="marker":
		split1=string.split(line, ' ')
		for element in split1:
			checkelement=str(element[0:2].strip())
			if checkelement == "x=":
				split2=string.split(element,'=')
				X.append(float(split2[1][1:-2].strip()))
			if checkelement == "y=":
				split2=string.split(element,'=')
				Y.append(float(split2[1][1:-1].strip()))	
			if checkelement== "z=":
				split2=string.split(element,'=')
				Z.append(float(split2[1][1:-1].strip()))
X2=[]
chain="A"
outfile=argv[2]
out=open(outfile,"w")
counter=0
while counter < len(X):
	out.write("ATOM  %5d  C   GLY %s%4d    %8.3f%8.3f%8.3f  1.00     0      S_00  0 \n"%(counter+1,chain,counter+1,X[counter],Y[counter],Z[counter]))
	counter=counter+1

counter2=0
while counter2 < len(X)-1:
	out.write("CONECT %4d %4d\n"%(counter2+1,counter2+2))
	counter2=counter2+1

out.close()
