#!/usr/bin/env python

import os
import sys
import random
import time
import string
import EMAN
from math import *
from sys import argv

R2D=180.0/pi

ERR_EXIT=1
ERR_CRIT=2
ERR_WARN=3
ERR_INFO=4
def error(type,msg):
	if (type==ERR_CRIT) : print "Critical Error: ",msg
	if (type==ERR_WARN) : print "Warning: ",msg
	if (type==ERR_INFO) : print msg
	if (type==ERR_EXIT) :
		print "Fatal Error: ",msg
		sys.exit(1)

def coords(i,s):
	x=i%(s*s)
	z=int(floor(i/(s*s)))
	y=i-z*s*s
	return (x,y,z)

# MAIN
if (len(argv)<2) :
	print "Usage: fastfoldhunter.py <map to search> <search map or pdb> [apix=<apix>] [maxdx=<int>]]"
	print """\nNOTE: It is very important that the probe NOT be unnecessarily padded. It should
be in the smallest reasonable box. Both input images must be cubic and have
an even number of pixels in each axis."""
	sys.exit(1)

apix=1.0
maxdx=-1
init2k=-1
for i in argv[3:] :
	s=string.split(i,'=')
	if (s[0]=="apix") : apix=float(s[1])
	elif (s[0]=="maxdx") : maxdx=int(s[1])
	elif (s[0]=="init2k") : init2k=int(s[1])
	else: error(ERR_EXIT,"Unknown argument "+i)

# read the imare we're searching
target=EMAN.EMData()
target.readImage(argv[1],-1)
if (target.xSize()!=target.ySize() or target.ySize()!=target.zSize() or target.xSize()%2==1 or target.ySize()%2==1 or target.zSize()%2==1) :
	print "Target map must be cubic with even dimensions (%d x %d x %d)"%(target.xSize(),target.ySize(),target.zSize())
	sys.exit(1)

# read the probe image
probe=EMAN.EMData()
probe.readImage(argv[2],-1)
if (probe.xSize()!=probe.ySize() or probe.ySize()!=probe.zSize() or probe.xSize()%2==1 or probe.ySize()%2==1 or probe.zSize()%2==1) :
	print "Probe map must be cubic with even dimensions (%d x %d x %d)"%(probe.xSize(),probe.ySize(),probe.zSize())
	sys.exit(1)
if (probe.xSize()>=target.xSize()) :
	print "Probe map should be smaller than target map. Probe should be in the smallest reasonable even cubic box."
	sys.exit(1)

shrink=int(2**floor(log(probe.xSize())/log(2.0)-3))		# probe should be at least 8 pixels
shrink2=int(2**floor(log(target.xSize())/log(2.0)-4))	# target should be at least 16 pixels
shrink=min(shrink,shrink2)

#fsize=int(floor(2.0*target.xSize()/shrink))
#if (fsize%4!=0) : fsize-=fsize%4
fsize=int(2**ceil(log(target.xSize()/shrink)/log(2.0)))


# first stage, shrink a LOT
targets=target.copy(0,0)
targets.meanShrink(shrink)

print "Using an initial shrink of %d giving a target size of %d padded to %d\ninitial probe would be %d"%(shrink,targets.xSize(),fsize,probe.xSize()/shrink)

txs=(fsize-targets.xSize())/2
targets.edgeNormalize()
targets=targets.clip(-txs,-txs,-txs,fsize,fsize,fsize)

pxs=int((fsize-floor(probe.xSize()/shrink))/2)

# probe must be same size as image
probes=probe.copy(0,0)
probes.meanShrink(shrink)
probes.edgeNormalize()
probes=probes.clip(-pxs,-pxs,-pxs,fsize,fsize,fsize)
probesp=probes				# this maintains a reference so probes doesn't get garbage collected
probes=probes.copy(0,1)

#ang=[(0,0),(45,0),(45,90),(45,180),(45,270),(90,0),(90,60),(90,120),(90,180),(90,240),(90,300),(135,0),(135,90),(135,180),(135,270),(180,0)]

# we assemble a list of all the angles to check in the initial pass
# we desire 1 pixel accuracy in the reduced size maps (where it's fast)
dang=atan(shrink*2.0/probe.xSize())*R2D
dang=90.0/ceil(90.0/dang)
print "Angular step in coarse search=%1.2f"%dang
ang=[]
alt=0.0
while (alt<180.0):
	daz=360.0/(int(ceil(sin(alt/R2D+.00001)*20.0)))
	az=0.0
	while (az<360.0):
		phi=0.0
		while (phi<360.0):
			ang.append((alt,az,phi))
			phi+=dang
		az+=daz
	alt+=dang

print len(ang)," angles to check in intial correlation pass"
if (init2k<=0) : init2k=len(ang)

# maximum x/y/z translation if not forced
if (maxdx<=0) :
	maxdx=(target.xSize()-probe.xSize())/2
	print "maxdx in initial probe %d"%(maxdx/shrink)

# now we do the initial coarse-grained search for possible locations
n=0
loclist=[]
x0=probes.xSize()/2-maxdx/shrink
x1=probes.xSize()/2+maxdx/shrink+1
targets.writeImage("trg.mrc")
for aa in ang:
	# rotate the probe and get it ready
	probes.setRAlign(aa[0]/R2D,aa[1]/R2D,aa[2]/R2D)
	probes.rotateAndTranslate()
	probes.edgeNormalize()
#	probes.toCorner()

	# ccf and filter to find only peak values
#	ccf=targets.calcCCF(probes)
	ccf=targets.calcFLCF(probes,probe.xSize()/(shrink*2))
	sig=ccf.Sigma()
	mn=ccf.Mean()
	ccf.toCorner()
#	ccf.realFilter(91)	# peak filter (eliminate non-peaks)
	if (n==1457 or n==1837 or n==0) : probes.writeImage("pr.%d.mrc"%n)
	if (n==1457 or n==1837 or n==0) : ccf.writeImage("ccf.%d.mrc"%n)

	# find the best values and add them to our list
	for x in range(x0,x1):
		for y in range(x0,x1):
			for z in range(x0,x1):
				if (ccf.valueAt(x,y,z)>mn+sig) :
					loclist.append([-ccf.valueAt(x,y,z),(x*shrink,y*shrink,z*shrink),(aa[0],aa[1],aa[2]),n])

	# this periodically trims the list down to 100 elements
	if (n%10==0):
		loclist.sort()						# we've taken (-cor. values) so lower is better
		loclist=loclist[0:init2k]

	# status
	if (n%100==0):
		print "  %d/%d    \r"%(n,len(ang)),
		sys.stdout.flush()
	n=n+1

loclist.sort()						# we've taken - correl values so lower is better
loclist=loclist[0:init2k]

for i in loclist:
	print "%f\t%3d,%3d,%3d\t%1.2f, %1.2f, %1.2f\t%d"%(-i[0],i[1][0],i[1][1],i[1][2],i[2][0],i[2][1],i[2][2],i[3])
