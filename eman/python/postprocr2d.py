#!/usr/bin/env python
from EMAN import *
fin=open("ptclassign.txt","r")
ln=fin.readlines()
ln=[i.split() for i in ln]
for i in ln:
	a=EMData()
	a.readImage("ptcl.hed",int(i[0]))
	a.writeImage("z.hed",-1)
	a.readImage("iter.final.hed",int(i[1]))
	a.writeImage("z.hed",-1)
	print i[0]
