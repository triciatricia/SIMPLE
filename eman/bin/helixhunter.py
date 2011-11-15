#!/usr/bin/env python
###     helixhunter.py     Matthew Baker 06/2003

#N helixhunter.py
#F Python script for quickly running helixhunter in chimera
#T LM
#1
#P <target>     Input mrc file
#P <apix>       anstroms/pixel
#D Generates pdb helices from target mrc using helixhunter

import os
import sys
import string
import EMAN
import commands
import math
import re
import shutil
from math import *
from sys import argv

da=5
blfilt=0
norm=0
percen=.3
sigma1=0
sigma2=0
iter=0
width=0
coeff=0

if (len(argv)<3) :
        print "Usage:\helixhunter.py <input mrc file> <apix>\n"
	print "Expert options <percen=> <coeff> <blfilt=s1,s2,i,w> <norm>"
        sys.exit(1)

temp_target=EMAN.EMData()
temp_target.readImage(argv[1],-1)

target=argv[1]
shutil.copy(target, 'hh.mrc')
a=target.split('.')
name=str(a[0])
apix=float(argv[2])

for i in argv[3:] :
        s=i.split('=')
        if (s[0]=='percen') :
                percen=float(s[1])
        elif (s[0]=='coeff') :
                coeff=1
        elif (s[0]=='blfilt') :
                p=s[1].split(',')
		sigma1=float(p[0])
		sigma2=float(p[1])
		iteration=int(p[2])
		width=float(p[3])
        elif (s[0]=='norm') :
                norm=1

size=[0,0,0]
size[0]=temp_target.xSize()
size[1]=temp_target.ySize()
size[2]=temp_target.zSize()
if (size[0]!=size[1]!=size[2]):
	print "Resizing map"
	clip=max(size)
	cmd1="proc3d hh.mrc hh.mrc clip=%d,%d,%d,%d"%(clip, clip, clip)
	os.system(cmd1)
	
if (norm==1):
	print "Normalizing map"
	cmd2="proc3d hh.mrc hh.mrc norm"
	os.system(cmd2)
	
if (iter!=0):
	print "Filtering Map"
	cmd3="proc3d hh.mrc hh.mrc blfilt=%f,%f,%d,%f"%(sigma1,sigma2,iter,width)
	os.system(cmd3)

print "Running helixhunter2"
if (coeff==1):
	cmd4="helixhunter2 hh.mrc hh2-%s.iv %f percen=%f docylccffirst int=int-%s dejavu=%s.sse minlen=8 maxlen=50"%(name, apix, percen, name, name)
	os.system(cmd4)	
else:
	cmd4="helixhunter2 hh.mrc hh2-%s.iv %f percen=%f dejavu=hh2-%s.sse minlen=8 maxlen=50"%(name, apix, percen, name)
	os.system(cmd4)

print "Saving results as a PDB file"
cmd5="dejavu2pdb.py hh2-%s.sse hh2-%s.pdb"%(name, name)
os.system(cmd5)
