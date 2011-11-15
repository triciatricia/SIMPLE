#!/bin/env python

# Dumps a FP file as ascii
# fpdump.py <fp file> <# elem>

from sys import argv
from struct import *

fin=file(argv[1],"r")

h=fin.read(128)
fsp,nptcl,nbasis=unpack("120s2i",h)
try: nd=int(argv[2])
except: nd=nbasis
if nd>nbasis: nd=nbasis

data=[]
for i in range(nd):
	data.append(unpack("%sf"%nptcl,fin.read(nptcl*4)))

for i in range(nptcl):
	print "%d"%i,
	for j in range(nd):
		print "\t%f"%data[j][i],
	print

