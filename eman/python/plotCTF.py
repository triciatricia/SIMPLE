#!/usr/bin/env python
import os, sys 
import Numeric
try:
	from optparse import OptionParser
except:
	from optik import OptionParser
import EMAN

# $Id: plotCTF.py,v 1.2 2007/08/30 15:44:21 gtang Exp $

# by Wen Jiang <jiang12@purdue.edu>, 2006-5-26

def main():
	(options, image, output) = parse_command_line()

	pid = EMAN.LOGbegin(sys.argv)
	EMAN.LOGInfile(pid, image)
	EMAN.LOGOutfile(pid, output)

	imgnum = options.last-options.first+1
	
	d = EMAN.EMData()
	
	if options.mode == "defocus":
		defocuses = [0] * imgnum
		count = 0
		for i in range(options.first, options.last+1):
			print "\rReading image %d(%d/%d)" % (i, count+1, imgnum),
			d.readImage(image,i,1)
			defocuses[count] = d.getCTF()[0]
			count += 1
		defocuses.sort()
		fp = open(output,'w')
		for i, defocuse in enumerate(defocuses):
			fp.write("%d\t%g\n" % (i, defocuse))
		fp.close()
	elif options.mode in ["ctfamp", "ctfb", "snr"]:
		sf = EMAN.XYData()
		if options.mode == "ctfamp":
			ctfcurve_mode = 11
		elif options.mode == "ctfb":
			ctfcurve_mode = 2
		elif options.mode == "snr":
			ctfcurve_mode = 9
			sf.readFile(options.sffile)
		d.readImage(image,0,1)
		ds = 1./(d.ySize()*d.getCTF()[10]*5)	# 5 is the oversampling ratio
		ctfcurve = Numeric.array(d.ctfCurve(0, sf))
		ctfcurve *= 0
		count = 0
		for i in range(options.first, options.last+1):
			print "\rReading image %d(%d/%d)" % (i, count+1, imgnum),
			d.readImage(image,i,1)
			ctfcurve_tmp = d.ctfCurve(ctfcurve_mode, sf)
			# compute average
			ctfcurve *= float(count)/float(count+1)
			ctfcurve += Numeric.array(ctfcurve_tmp)/float(count+1)
			count += 1
		fp = open(output,'w')
		for i, ctfval in enumerate(ctfcurve):
			fp.write("%g\t%g\n" % (i*ds, ctfval))
		fp.close()
	
	EMAN.LOGend()
	
def parse_command_line():
	usage="Usage: %prog <image filename> <output filename> [options]"
	parser = OptionParser(usage=usage)
	parser.add_option("--mode",metavar="['defocus', 'snr', 'ctfb', 'ctfamp']",dest="mode",type="choice",choices=['defocus', 'snr', 'ctfb', 'ctfamp'], help="ctf mode to plot. default to \"defocus\"", default="defocus")
	parser.add_option("--sf",dest="sffile",type="string",help="structural factor file name", default="")
	parser.add_option("--first",dest="first",type="int",help="first image to use. default to 0", default=0)
	parser.add_option("--last",dest="last",type="int",help="last image to use. default to last image in the file", default=-1)
	
	(options, args) = parser.parse_args()
	if len(args) != 2:
		parser.print_help()
		sys.exit(-1)
	else:
		image = args[0]
		output = args[1]
	
	if options.mode in ['snr']:
		if not options.sffile:
			print "Error: --sf should be specified"
			sys.exit(1)
		elif not os.path.exists(options.sffile):
			print "Error: sffile %s does not exist" % (options.sffile)
			sys.exit(2)
	imgnum = EMAN.fileCount(image)[0]
	if options.last==-1: options.last=imgnum-1
	if options.first>0 or options.last>0:
		if not (0<=options.first<imgnum):
			print "Error: --first=%d is out of correct range [0, %d]" % (options.first, imgnum-1)
			sys.exit(3)
		if not (options.first<=options.last<imgnum):
			print "Error: --last=%d is out of correct range [%d, %d]" % (options.last, options.first, imgnum-1)
			sys.exit(4)

	return (options, image, output)
	
if __name__== "__main__":
	main()
