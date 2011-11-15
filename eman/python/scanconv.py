#!/usr/bin/env python
# This program will read scanner .tif images and convert them to single-image
# spider files, correcting for a flip problem

from EMAN import *
from sys import argv

im=EMData()
for fsp in argv[1:]:
	im.readImage(fsp)
	im.realFilter(104)
	im.vFlip()
	im.writeImage(fsp[:-4]+".spi",0,EMData.SINGLE_SPIDER)
	
