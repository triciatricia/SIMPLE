#!/usr/bin/env python

# This script will filter ctfparm.txt to allow specific parameters to be set


import os
from math import *

infile=file("ctfparm.txt","r")
lines=infile.readlines()
infile.close()
os.rename("ctfparm.txt","ctfparm.txt.orig")

out=file("ctfparm.txt","w")

for l in lines:
	s=[l.split()[0]]
	s+=l.split()[1].split(',')
	for i in range(1,len(s)-1):
		s[i]=float(s[i])
	out.write("%s\t%1.5f,%1.3f,%1.5f,%1.6f,%1.5f,%1.2f,%1.2f,%1.2f,%1.2f,%1.2f,%1.2f,%s\n"%(
		s[0],s[1],275.0,s[3],s[4],s[5],s[6],s[7],s[8],s[9],s[10],s[11],s[12]))
out.close()

