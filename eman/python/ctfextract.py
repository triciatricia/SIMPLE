#!/usr/bin/env python

# by Wen Jiang 2005-6-24

# $Id: ctfextract.py,v 1.2 2005/07/01 16:58:18 wjiang Exp $

import sys
try:
	from optparse import OptionParser
except:
	from optik import OptionParser

import EMAN

usage = "Usage: %prog <image 1> ... <image n> [options]"
parser = OptionParser(usage=usage)
parser.add_option("--ctfparmfile",dest="ctffile",metavar="filename",type="string", \
				  help="output file name to store the CTF parameters",default="ctfparm.txt")
parser.add_option("--sffile",dest="sffile",metavar="filename",type="string", \
				  help="structural factor file for the CTF parameters",default="")

(options, images)=parser.parse_args()

if not len(images):
	parser.print_help()
	sys.exit(1)

ctffile = options.ctffile
sffile = options.sffile
if not sffile: sffile="(null)"

fp = open(ctffile, 'a')

d = EMAN.EMData()

for m in images:
	d.readImage(m,0,1)
	ctf = d.getCTF()
	fp.write("%s\t%g,%g,%g,%g,%g,%g,%g,%g,%g,%g,%g,%s\n" % (m.split(".")[0], ctf[0], ctf[1], ctf[2], ctf[3], ctf[4], ctf[5], ctf[6], ctf[7], ctf[8], ctf[9], ctf[10], sffile))

fp.close() 
	

