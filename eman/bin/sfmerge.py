#!/usr/bin/env python

#N sfmerge.py
#F Combines a structure factor from CTFIT with a simulated curve for use in CTF correction
#T X
#1
#P <ctfit file>	File produced by CTFIT
#P <high res file>	2 column text file containing high resolution structure factor
#P <cutoff S>	Spatial frequency at which the transition should occur
#P <output>	Output filespec
#U sfmerge.py out.txt high.txt .04 sim.sf
#D This program will combine a structure factor file generated by CTFIT
#E with the 'save 1 column' command (save column 11), with a 2 column
#E structure factor file at high resolution. This requires that
#E the data sets have been fit so the calculated structure factor matches
#E well at low spatial frequencies. If you wish to actually use this program,
#E you should probably contact sludtke@bcm.tmc.edu first.

#D note the ctfit file contains amplitudes, the high res sf file 
#E contains intensities, and the output contains intensities

# sfmerge.py <ctfit file> <high res sf> <cutoff S> <output>

import os
import sys
import string
from sys import argv

if (len(argv)<5):
	print "sfmerge.py <ctfit file> <high res sf> <cutoff S> <output>"
	sys.exit(1)

ssplit=float(argv[3])

fin=file(argv[1],"r")
lines=fin.readlines()
fin.close()

# read ctfit file and calculate min value at each s
vals=[]
for i in lines:
	s=string.split(i)
	if (float(s[0])>=ssplit) : break
	s=map ((lambda x: float(x)),s)
	vals.append([s[0],min(s[1:])**2])

# read appropriate part of high res sf file	
vals2=[]
fin=file(argv[2],"r")
lines=fin.readlines()
fin.close()
for i in lines:
	s=string.split(i)
	if (float(s[0])<=ssplit) : continue
	vals2.append([float(s[0]),float(s[1])])

# rescale 1st half
scale=vals2[0][1]/vals[len(vals)-1][1]
vals=map((lambda x: [x[0],x[1]*scale]),vals)

out=file(argv[4],"w")
for i in vals:
	if i[1]!=float("nan") : out.write("%1.5f\t%1.5f\n"%(i[0],i[1]))
	
for i in vals2:
	if i[1]!=float("nan") : out.write("%1.5f\t%1.5f\n"%(i[0],i[1]))
	
