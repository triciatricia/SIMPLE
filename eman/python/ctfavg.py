#!/usr/bin/env python

# This program will average CTF intensities for a set of defocuses

from sys import argv
from EMAN import *

#defocuses=[i/10.0 for i in range(15,22)]
defocuses=[i/10.0 for i in range(15,34)]
#defocuses=[1.5,1.7,1.9,2.1,2.3,2.5,2.7,2.9,3.1]
#defocuses=[1.5]

apix=4.0
acont=0.2

a=EMData()
a.setSize(256,256,1)

av=None
for d in defocuses:
	a.setCTF([-d,200.0,1.0,acont,0,0,0,0,200,2,apix])
	c = a.ctfCurve(0,None)	# 0 will average amplitudes
#	c = a.ctfCurve(8,None)	# intensities, but need structure factor
	c=[i*i for i in c]
	if not av : av=c
	else :
		for i,j in enumerate(c) : av[i]+=j

for i,j in enumerate(av):
	print i/(apix*256.0*5.0),(j/len(defocuses))
#	print i/(apix*256.0*5.0),1.0/(j/len(defocuses))	# plots the reciprocal of the intensity

