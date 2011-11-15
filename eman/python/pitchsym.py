#!/usr/bin/env python
# pitchsym.py	Steve Ludtke  3/8/04
# This program will enforce and optimize a defined helical symmetry
# ie - it will take an object which obeys some sort of helical repeat
# and an approximate set of helical repeat parameters, optimize the
# parameters for maximum map variation, and output a symmetrized map
# specify input file, output file and pitch in terms of and angle and
# a number of pixels along z. ie 10/6 implies that translating the map
# 6 pixels with a 10 degree rotation should produce an identical map

from EMAN import *
from sys import argv
import sys
from math import *
from sys import stdout,stderr
import random

# this actually applies the symmetry
def symmetrize(model,pitch):
	sum=model.copy(0,0)
	sum.zero()
	n=int(model.zSize()/pitch[1])
	for s in range(-n,n):
		cop=model.copy(0,0)
		cop.setRAlign(0,s*pitch[0]*pi/180.0,0)
		cop.setTAlign(0,0,s*pitch[1])
		cop.rotateAndTranslate()
		sum+=cop
	sum/=(n*2.0)
	return sum

tst=EMData()
tst.readImage(argv[1],-1)
pitch=None
optimize=0

for i in argv[3:] :
	s=i.split("=")
	if (s[0]=="pitch") : pitch=s[1].split('/')
	elif (s[0]=="optimize") : optimize=1
	else :
		print("Unknown argument "+i)
		sys.exit(1)

print("Dataset is %dx%dx%d"%(tst.xSize(),tst.ySize(),tst.zSize()))

pitch[0]=float(pitch[0])
pitch[1]=float(pitch[1])

best=(symmetrize(tst,pitch).Sigma(),pitch)

scas=(.2,.1,.05,.02,.01)
if (optimize) :
	for s in range(5):
		sca=scas[s]

		for itsca in range(-4,5):
			tsca=1.0+sca*itsca/4.0
			tpitch=(pitch[0]*tsca,pitch[1]*tsca)
			sym=symmetrize(tst,tpitch)
			if (sym.Sigma()>best[0]) : best=(sym.Sigma(),tpitch)
		pitch=best[1]
		print "S ",best

		for h in range(-4,5):
			dh=h*sca*pitch[1]/4.0
			tpitch=(pitch[0],pitch[1]+dh)
			sym=symmetrize(tst,tpitch)
			if (sym.Sigma()>best[0]) : best=(sym.Sigma(),tpitch)
		pitch=best[1]
		print "H ",best


"""tpitch=pitch
dpitch=[4.0,1.0]
best=(1.0e30,tpitch)

while (dpitch[0]>.01) :
	sum=symmetrize(tst,tpitch)
	if (sum.Sigma()<best[0]) :
		best=(sum.Sigma(),tpitch)
		dpitch=(dpitch[0]*1.1,dpitch[1]*1.1)
		print best
	else:
		dpitch=(dpitch[0]*.9,dpitch[1]*.9)
		print "Scale: ",dpitch
	tpitch=[random.gauss(best[1][0],dpitch[0]),random.gauss(best[1][1],dpitch[1])]

print "\nDone !\n",pitch," -> ",best
"""


sum=symmetrize(tst,pitch)
sum.writeImage(argv[2])
