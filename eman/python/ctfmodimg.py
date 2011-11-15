#!/usr/bin/env python

# This program will modify ctf parameters in an image file

from sys import argv
from EMAN import *

a=EMData()
apix=float(argv[2])

n=fileCount(argv[1])[0]

for i in range(n):
	a.readImage(argv[1],i)
	c=a.getCTF()
	c[10]=apix
	a.setCTF(c)
	a.writeImage(argv[1],i)

