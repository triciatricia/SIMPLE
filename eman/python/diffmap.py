#!/usr/bin/env python

# by Wen Jiang 2005-12-9

# $Id: diffmap.py,v 1.1 2005/12/28 20:30:39 wjiang Exp $

import sys
try:
	from optparse import OptionParser
except:
	from optik import OptionParser
import EMAN
float_min = -3.4028234663852886e+38

def main():
	(options, mapref, mapprobe, mapout) = parse_command_line()

	pid = EMAN.LOGbegin(sys.argv)
	EMAN.LOGInfile(pid, mapref)
	EMAN.LOGInfile(pid, mapprobe)
	EMAN.LOGOutfile(pid, mapout)
	
	da = EMAN.EMData()
	db = EMAN.EMData()
	
	da.readImage(mapref,-1)
	db.readImage(mapprobe,-1)
		
	if da.xSize() != db.xSize() or da.ySize() != db.ySize() or da.zSize() != db.zSize():
		print "Error: map %s size (%dx%dx%d) != map %s size (%dx%dx%d)" % ( sys.argv[1], da.xSize(), \
			da.ySize(), da.zSize(), sys.argv[2], db.xSize(), db.ySize(), db.zSize() )
		sys.exit(1)
	
	diff = difference_map(da, db, options)
	
	diff.writeImage(mapout)
	
	EMAN.LOGend()

def difference_map(mapref, mapprobe, options):
	ref2 = mapref.copy(0,0)
	probe2 = mapprobe.copy(0,0)
	if options.imask>0 or options.mask>0 or options.thresh > float_min or options.maskmap:
		if options.mask>0:
			print "Applying outside mask (rad=%d)" % (options.mask)
			ref2.applyMask(options.mask, 4)
			probe2.applyMask(options.mask, 4)
		if options.imask>0:
			print "Applying inner mask (rad=%d)" % (options.imask)
			ref2.applyMask(options.imask, 5)
			probe2.applyMask(options.imask, 5)
		if options.maskmap:
			print "Applying maskfile %s" % (options.maskfile)
			ref2.mult(options.maskmap)
			probe2.mult(options.maskmap)
		if options.thresh > float_min:
			print "Applying threshold %g" % (options.thresh)
			ref2.realFilter(0, options.thresh)
			probe2.realFilter(0, options.thresh)
	#probe2 = probe2.matchFilter(ref2)
	if options.saveintmap:
		probe2.writeImage("map_probe.mrc")
		ref2.writeImage("map_ref.mrc")
		
	a, b = probe2.normalizeTo(ref2) # ref = a * probe + b
	print "map_ref = %g * map_probe + %g" % (a, b)
	mapprobe.multConst(a)
	mapprobe.add(b)
	if options.savefittedmap: mapprobe.writeImage(options.savefittedmap)
	mapref.subtract(mapprobe)
	return mapref

def parse_command_line():
	usage = "Usage: %prog <input map a> <input map b> <output map a-b> [options]"
	parser = OptionParser(usage=usage)
	parser.add_option("--imask",dest="imask",metavar="<radius>",type="int", \
					  help="inner mask radius in pixel. default to 0", default=0)
	parser.add_option("--mask",dest="mask",metavar="<radius>",type="int", \
					  help="outside mask radius in pixel. default to 0", default=0)
	parser.add_option("--maskfile",dest="maskfile",metavar="<filename>",type="string", \
					  help="mask file", default="")
	parser.add_option("--thresh",dest="thresh",metavar="<min pixel value>",type="float", \
					  help="minimal pixel value to threshold", default=float_min)
	parser.add_option("--saveintmap",dest="saveintmap",action="store_true",
					  help="if save the intermediate maps", default=0)
	parser.add_option("--savefittedmap",dest="savefittedmap",metavar="<filename>",type="string",
					  help="save the fitted map to this file", default="")
	
	(options, maps)=parser.parse_args()

	if len(maps) !=3:
		parser.print_help()
		sys.exit(-1)
	
	if options.imask >0 and options.mask >0 and options.imask>=options.mask:
		print "Error: inner mask radius (%g) >= outside mask radius (%g)" % (options.imask, options.mask)
		sys.exit(-2)
	
	if options.maskfile:
		d = EMAN.EMData()
		d.readImage(options.maskfile,-1)
		options.maskmap = d
	else:
		options.maskmap = None
	
	return (options, maps[0], maps[1], maps[2])

if __name__== "__main__":
	main()
