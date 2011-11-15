#!/usr/bin/env python

# by Wen Jiang 2005-12-9

# $Id: ctfcopy.py,v 1.1 2005/12/09 00:23:32 wjiang Exp $

import sys
import EMAN

usage = "Usage: %s <input image> <output image>" % (sys.argv[0])
if len(sys.argv) != 3: 
	print usage
	sys.exit(1)

n1 = EMAN.fileCount(sys.argv[1])[0]
n2 = EMAN.fileCount(sys.argv[2])[0]

if n1 != n2:
	print "ERROR: %d in %s != %d in %s" % (n1, sys.argv[1], n2, sys.argv[2])
	sys.exit(1)

d1 = EMAN.EMData()
d2 = EMAN.EMData()

for i in range(n1):
	d1.readImage(sys.argv[1],i,1)
	d2.readImage(sys.argv[2],i,1)
	
	if d1.hasCTF():
		ctf = d1.getCTF()
		print "%d\t%g,%g,%g,%g,%g,%g,%g,%g,%g,%g,%g" % (i, ctf[0], ctf[1], ctf[2], ctf[3], ctf[4], ctf[5], ctf[6], ctf[7], ctf[8], ctf[9], ctf[10])
		d2.setCTF( ctf )
		d2.writeImage(sys.argv[2], i, EMAN.EMData.ANY, 1)
	else:
		print "Warning: image %d in %s does not have CTF parameters !" % ( i, sys.argv[1] )
	

