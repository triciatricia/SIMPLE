#!/usr/bin/env python
###	createcmm.py	Matthew Baker 12/2004

#N pdb2cmm.py
#F extract coordinate poisitions and create a cmm file from a PDB file

import os
import sys
import string
import commands
import math
from math import *
from sys import argv

if (len(argv)!=5) :
	print "Usage:\npdb2cmm.py <input pdb> <output> <format (pdb or cmm)> <selection (atom serial numbers, SSE, HELIX, SHEET)> \n"
	sys.exit(1)

target=argv[1]
output=argv[2]
format=argv[3]
atoms=argv[4]
atomarray=[]
atomarray=string.split(atoms,',')


x=[]
y=[]
z=[]
atomNumber=[]
atomCount=0

##read lines in from PDB file
file1=open(target, "r")
lines1=file1.readlines()
file1.close()

Xarray=[]
Yarray=[]
Zarray=[]
if atoms=="SSE" or atoms=="HELIX" or atoms=="SHEET":
	if atoms=="SSE":
		check1="HELIX"
		check2="SHEET"
	else:
		check1=atoms
		check2=atoms
	atomarray=[]
	for line in lines1:
		sse=str(line[0:6].strip())
		if sse==check1 or sse==check2:
			searchatom1=int(line[22:26].strip())
			searchatom2=int(line[34:37].strip())
			print "Finding Ca atom in residues %d and %d in %s"%(searchatom1, searchatom2, sse)
			for caline in lines1:
				if str(caline[0:6].strip())=="ATOM" and str(caline[12:16].strip())=="CA" and (int(caline[22:26].strip())==searchatom1 or int(caline[22:26].strip())==searchatom2):
					atomarray.append(str(caline[7:11].strip()))
	
#print atomarray

###find atom
for line in lines1:
	isatom=str(line[0:6].strip())
	if (isatom=="ATOM"):
		if str(line[7:11].strip()) in atomarray:
			#print str(line[7:11].strip())
			Xarray.append(float(line[30:38].strip()))
			Yarray.append(float(line[38:46].strip()))
			Zarray.append(float(line[46:54].strip()))

counter=0
outfile=open(output,"w")
if format == 'cmm':
	firstline="<marker_set name=\"marker set for %s\">\n"%(target)
	outfile.write(firstline)
	#print len(atomarray), len(Xarray), len(Yarray), len(Zarray)
	while counter < len(atomarray):
		#print counter
		nextline="<marker id=\"%d\" x=\"%f\" y=\"%f\" z=\"%f\"  radius=\"2\"/>\n"%(counter+1,Xarray[counter],Yarray[counter],Zarray[counter])
		outfile.write(nextline)
		counter=counter+1

	counter2=0
	while counter2 < (len(atomarray)-1):
		nextline="<link id1=\"%d\" id2=\"%d\" r=\"1\" g=\"0\" b=\"0\" radius=\"1\"/>\n"%(counter2+1,counter2+2)
		outfile.write(nextline)
		counter2=counter2+1

	lastline="</marker_set>\n"
	outfile.write(lastline)
else:
	for line in pdblines:
		outfile.write(line)

print "Booth is an ASS"
