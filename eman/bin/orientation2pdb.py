#!/usr/bin/env python

import math, sys
from math import cos, sin
import EMAN
import getopt

Usage = "%s: <input image file> <output PDB file> [--radius=<number>] [--tree=<input tree file>] [--treemem=<output file name>]" % (sys.argv[0])

verbose = 0
tree = ""
treemem = ""
r = 100.0

if len(sys.argv) <3: 
	print Usage
	sys.exit(1)
elif len(sys.argv) > 3:
	try:
		optlist, junks = getopt.getopt(sys.argv[3:], 'v', ['radius=','tree=','treemem=','verbose'])
	except getopt.GetoptError:
		# print help information and exit:
		print Usage
		sys.exit(2)
	if len(junks):
		for o in junks:
			print "Error: option '"+o+"' is not supported"
			print Usage
			sys.exit(3)
	for o, a in optlist:
		if o in ("-v", "--verbose"):
			verbose = verbose + 1
		if o in ("", "--radius"):
			r=float(a)
		if o in ("", "--tree"):
			tree=a
		if o in ("", "--treemem"):
			treemem=a

indices = []
members = {}
if tree:
	for l in open(tree,"r"):
		indices.append(int(l.split()[0]))
		if treemem:
			mem = l.split()[1:]
			members[indices[-1]] = []
			for m in mem: members[indices[-1]].append(int(m))
else:
	indices = range(EMAN.fileCount(sys.argv[1])[0])

img = EMAN.EMData()

pdb = open(sys.argv[2],"w")

for  i in indices:
	img.readImage(sys.argv[1],i,nodata=1)
	
	alt=img.alt()
	az=img.az()
	phi=img.phi()
	x=r*sin(alt)*cos(az)
	y=r*sin(alt)*sin(az)
	z=r*cos(alt)

	pdb.write("ATOM  %5d  CA  ALA A%4d    %8.3f%8.3f%8.3f%6.2f%6.2f%8s\n" % (i,i,x,y,z,1.0,0.0," "))
	
	if treemem: 
		fname = "%s.%d.pdb" % (treemem, i)
		mpdb = open(fname,"w")
		for m in members[i]:
			img.readImage(sys.argv[1],m,nodata=1)
	
			alt=img.alt()
			az=img.az()
			phi=img.phi()
			x=r*sin(alt)*cos(az)
			y=r*sin(alt)*sin(az)
			z=r*cos(alt)

			mpdb.write("ATOM  %5d  CA  ALA A%4d    %8.3f%8.3f%8.3f%6.2f%6.2f%8s\n" % (m,m,x,y,z,1.0,0.0," "))
		mpdb.close()
		
		
	
