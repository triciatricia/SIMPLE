#!/usr/bin/env python
import sys
import EMAN

if len(sys.argv)!=4:
	print "Usage: %s <input box file> <scale> <output box file>" % (sys.argv[0])
	sys.exit()

boxin = EMAN.readEMANBoxfile(sys.argv[1])
boxout = EMAN.scaleBoxes(boxin, int(sys.argv[2]))
EMAN.writeEMANBoxfile(sys.argv[3], boxout)

