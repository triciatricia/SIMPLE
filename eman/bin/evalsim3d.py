#!/usr/bin/env python
###	evalsim3d.py	Steven Ludtke	12/2002
### This program will do a refinement using the new basis based techniques
###

#N evalsim3d.py
#F A simple script that generates projections of a map and uses glmatrix to visually make a similarity comparison
#T X
#1
#P <model>	3D model to evaluate
#P [ang=<da>]	Angular spacing when generating projections
#P [sym=<sym>]	Symmetry specification
#P [shrink=<n>]	For speed, may affect accuracy of results
#D This program allows those with a good sense of geometry to visually compare the similarity
#d of the various projections of a 3D model.

import os
import sys
import random
import time
import string
from os import system
from os import unlink
from sys import argv

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
	print "evalsym3d.py <model> [ang=<da>] [sym=<sym>]"
	sys.exit(1)

ang=9
sym='c1'
shrink=1

for i in argv[2:] :
#	s=i.split('=')
	s=string.split(i,'=')
	if (s[0]=='ang') : ang=float(s[1])
	elif (s[0]=="sym") : sym=s[1]
	elif (s[0]=="shrink") : shrink=int(s[1])
	else: error(ERR_EXIT,"Unknown argument "+i)

LOGbegin(argv)

system("project3d %s sym=%s prop=%1.3f out=simcmp.hed"%(argv[1],sym,ang))
system("classesbymra simcmp.hed simcmp.hed matrix shrink=%d"%shrink)
system("mx2img matrix.dat matrix.mrc")
system("matrixembed matrix.mrc self.loc euler=simcmp.hed")
system("glmatrix self.loc matrix=matrix.mrc images=simcmp.hed")

LOGend()

