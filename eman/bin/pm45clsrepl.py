#!/usr/bin/env python
# pm45clsrepl.py  Steve Ludtke   02/12/2006
#
# This will take the intermediate cls files from refine2d.py and
# make a stack of class-averages corresponding to each particles

# pm45clsrepl.py <output>

from sys import argv
from pprint import pprint
from EMAN import *
from math import *

if len(argv)<2 : print """Usage: pm45clsrepl.py <output>

This program will take class-averages produced by refine2d.py and map them back
to individual particles. For example:
refine2d start.hed --iter=5 ...
rm -rf cls*lst
tar xvf cls.4.tar
pm45clsrepl.py start.repl.hed

This will produce start.repl.hed, containing an image for each particle in start.hed where
the particle has been replaced by the best-matching class-average in the same orientation.
This program was designed for use with pm45.py, eg - for +45 degree -45 degree tilt pair
analysis, though it could be equally useful in many other situations"""

# read all cls files
alns=[]
for j in range(10000):
	try: fin=file("cls%04d.lst"%j,"r")
	except: break
	lns=fin.readlines()[1:]
	fin.close()
	l2=lns[0]
	lns=lns[1:]
	alns+=[[int(i.split()[0]),int(l2.split()[0]),float(i.split(',')[1]),float(i.split(',')[2]),float(i.split(',')[3]),int(i.split(',')[4])] for i in lns]

alns.sort()
reffsp=l2.split()[1]
for i in alns: print i

# write the output stack
for i in alns:
	b=EMData()
	b.readImage(reffsp,i[1])
	if (i[5]) : b.hFlip()
	b.setRAlign(-i[2],0,0)
	b.rotateAndTranslate()
	b.setTAlign(-i[3],-i[4],0)
	b.setNImg(1)
	b.rotateAndTranslate()
	b.writeImage(argv[1],-1)

