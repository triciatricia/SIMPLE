#!/usr/bin/env python
###	helix.py	Matthew Baker 06/2003

#N helix.py
#F This program generates a Ca trace of dejaVu helices
#T LM
#1
#P <infile>	Input dejavu file
#P [<outfile>]	Output pdb file
#D This program generates a Ca trace of dejaVu helices

import os
import sys
import re
import string
import math
from sys import argv
from math import *

if (len(argv)!=3) :
	print "Usage:\nhelix.py <length> <output>\n"
	sys.exit(1)

#####this is where the the PDB file is generated
chain=argv[1]
j=0
p=0
q=0
r=0

Nxcoord=0
Nycoord=0
Nzcoord=0

outfile=open(argv[2],"w")
while j<= string.atof(chain):
	Nxcoord=math.cos((100*j*math.pi)/180)*1.6
	Nycoord=math.sin((100*j*math.pi)/180)*1.6
	Nzcoord=j*1.52
	
	print j, Nxcoord, Nycoord, Nzcoord

#	CAxcoord=Nxcoord+1.2
#	CAycoord=Nycoord-.27
#	CAzcoord=Nzcoord+.77
#	Cxcoord=Nxcoord+1.28
#	Cycoord=Nycoord+.73
#	Czcoord=Nzcoord+1.9
#	Oxcoord=Nxcoord+1.76
#	Oycoord=Nycoord+.41
#	Ozcoord=Nzcoord+2.99
	
	CAxcoord=math.cos(((28+(100*j))*math.pi)/180)*2.3
	CAycoord=math.sin(((28+(100*j))*math.pi)/180)*2.3
	CAzcoord=(j*1.54)+.83
	Cxcoord=math.cos(((61+(100*j))*math.pi)/180)*2.0
	Cycoord=math.sin(((61+(100*j))*math.pi)/180)*2.0
	Czcoord=(j*1.54)+1.7
	Oxcoord=math.cos(((61+(100*j))*math.pi)/180)*2.0
	Oycoord=math.sin(((61+(100*j))*math.pi)/180)*2.0
	Ozcoord=(j*1.54)+3.09
	p=j*4+1
	q=j*4+2
	r=j*4+3
	s=j*4+4
	j=j+1
	
	outfile.write("ATOM  %5d   N  GLY A%4d    %8.3f%8.3f%8.3f  1.00     0      S_00  0 \n"%(p,j,Nxcoord,Nycoord,Nzcoord))
	outfile.write("ATOM  %5d  CA  GLY A%4d    %8.3f%8.3f%8.3f  1.00     0      S_00  0 \n"%(q,j,CAxcoord,CAycoord,CAzcoord))
	outfile.write("ATOM  %5d   C  GLY A%4d    %8.3f%8.3f%8.3f  1.00     0      S_00  0 \n"%(r,j,Cxcoord,Cycoord,Czcoord))
	outfile.write("ATOM  %5d   O  GLY A%4d    %8.3f%8.3f%8.3f  1.00     0      S_00  0 \n"%(s,j,Oxcoord,Oycoord,Ozcoord))
#	outfile.write("ATOM  %5d   O  GLY A%4d    %8.3f%8.3f%8.3f  1.00     0      S_00  0 \n"%(s,j,0,0,Ozcoord))

outfile.close()
