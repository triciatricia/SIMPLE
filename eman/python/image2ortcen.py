#!/usr/bin/env python
import sys, os
from math import pi
import EMAN

if len(sys.argv) != 3:
	print "%s: convert image orientation and center (in EMAN convention) stored in the image headers into a text file in MRC/IMIRS format/convention" % (sys.argv[0])
	print "Usage: %s <input image file> <output ortcen file>" % (sys.argv[0])
	sys.exit(1)

imagefile = sys.argv[1]
output_ortcen_file = sys.argv[2]

imgnum, imgtype = EMAN.fileCount(imagefile)

img = EMAN.EMData()
img.readImage(imagefile, 0, 1)	# read Header only
imagesize = img.xSize()

imagefile_prefix = os.path.splitext(output_ortcen_file)[0]

outFile = open(output_ortcen_file, "w")
	
e5fto2f = EMAN.Euler(1.0172219678978513677, pi, -pi/2)	# rotation from 2fold to 5fold

for i in range(imgnum):
	print "Working on image %d/%d\r" % (i, imgnum) , 
	img.readImage(imagefile, i, 1)
	e = img.getEuler()
	
	e2 = e * e5fto2f;	# use 2-fold view instead of 5-fold view as orientation origin
	alt = e2.thetaMRC()*180./pi
	az = e2.phiMRC()*180./pi
	phi = e2.omegaMRC()*180./pi
	
	cx  = img.get_center_x()
	cy  = img.get_center_y()

	tnffile = "%s-%d.tnf" % (imagefile_prefix, i)
	
	outFile.write("%s\n" % (os.path.abspath(tnffile)))
	outFile.write(" %d, %.4f, %.4f, %.4f, %.4f, %.4f, 0.0\n" % (0, alt, az, phi, cy, cx))

print 