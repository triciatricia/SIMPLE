#!/usr/bin/env python
# ctfplot.py
# plot automatically determined CTF parameters in various ways
# requires Gnuplot python module

import sys
from sys import argv
from math import *
from string import *

points=[]
fnum=0
while (fnum<len(argv)-1):
	fnum=fnum+1
	infile=open(argv[fnum],"r")
	lines=infile.readlines()
	infile.close()
	
	i=0
	while (i<len(lines)):
		tmp=split(lines[i])
		lines[i]=[tmp[0]]
		lines[i].extend(split(tmp[1],','))
		i=i+1
	
	for i in lines:
		print "%f\t%f"%(-float(i[1]),float(i[2]))
	
