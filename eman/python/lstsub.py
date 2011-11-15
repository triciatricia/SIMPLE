#!/usr/bin/env python

# This program will copy a set of images referenced in a lst file
# as proc2d <in> <out> would. However, it will replace the name of the
# image file in the lst file with the 3rd argument

# lstsub.py infile.lst outfile.hed altref.hed

from sys import argv
from sys import exit
from EMAN import *

a=EMData()

if len(argv)<4 : 
	print "Usage:\nlstsub.py infile.lst outfile.hed altref.hed\n\nThis will copy the images from the LST file 'infile' to 'outfile', but rather than use the image file name referenced in 'infile', it will substitute 'altref'."
	exit(1)


l=file(argv[1],"r").readlines()
for i in l[1:]:
	try: a.readImage(argv[3],int(i.split()[0]))
	except:
		print "Bad line: ",i
		continue
	a.writeImage(argv[2],-1)
