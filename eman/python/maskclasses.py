#!/usr/bin/env python
# This program will read 'classes.hed' and take the portions of the 
# even numbered images (projections) that are exactly 0 (masked) and mask out
# corresponding areas of the odd-numbered images (class-averages)

from EMAN import *

x=EMData()
m=EMData()
y=EMData()

n=fileCount("classes.hed")

for i in range(0,n[0],2):
	x.readImage("classes.hed",i)
	y.readImage("classes.hed",i+1)
	x.writeImage("z.hed",i)
	x.realFilter(6)
	m=y*x
	m.writeImage("z.hed",i+1)
