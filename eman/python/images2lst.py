#!/usr/bin/env python

import os, sys
from math import pi
import EMAN
try:
	from optparse import OptionParser
except:
	from optik import OptionParser

def main():
	
	(options, input_imagefiles, output_lstfile) = parse_command_line()

	lstfiles = {}
	imagefiles = {}
	alllines = []
	if options.removeDuplicates:
		import sets
		seenImages = sets.Set()

	for imagefile in input_imagefiles:
		if os.path.exists(imagefile):
			imgnum, imgtype = EMAN.fileCount(imagefile)
			if not imgnum:
				print "WARNING: file \"%s\" is empty" % (imagefile)
				continue
			else:
				print "%s: %d images" % (imagefile, imgnum)
	
			if imgtype == "lst":
				fp = open(imagefile,'r')
				lines= fp.readlines()
				if lines[0].startswith("#LST"): line0 = 1
				elif lines[0].startswith("#LSX"): line0 = 3
				if len(lines)>line0:
					for l in lines[line0:]:
						tokens = l.split(None, 2)
						realimg, realindex = follow_lst_link(tokens[1], int(tokens[0]), lstfiles, imagefiles)
						if len(tokens)>2 : 
							line = "%d\t%s\t%s" % (realindex, realimg, tokens[2])
						else: 
							line = "%d\t%s\n" % (realindex, realimg)
							
						if options.removeDuplicates and isDuplicate(seenImages, realimg, realindex):
							print "%s: particle %d is a duplicate image, ignored" %                 \
							      (realimg, realindex)
						else:
							alllines += [line]

				else:
					print "WARNING: lst file \"%s\" is empty" % (imagefile)
				fp.close()
			else:
				d = EMAN.EMData()
				for i in range(imgnum):
					d.readImage(imagefile,i,1)
					line="%d\t%s\t%g\t%g\t%g\t%g\t%g\n" % (i,imagefile,d.alt()*180./pi, d.az()*180./pi, d.phi()*180./pi, d.get_center_x(), d.get_center_y())

					if options.removeDuplicates and isDuplicate(seenImages, imagefile, i):
						print "%s: particle %d is a duplicate image, ignored" %                 \
								(imagefile, i)
					else:
						alllines += [line]
		else:
			print "WARNING: file \"%s\" does not exists" % (imagefile)
	
	if len(alllines):
		maxlen = 0;
		for l in alllines:
			if len(l)>maxlen: maxlen = len(l)
		
		lstfp = open(output_lstfile,"w")
		lstfp.write("#LSX\n#If you edit this file, you MUST rerun lstfast.py on it before using it!\n# %d\n"% (maxlen))
		for l in alllines: 
			l=l.strip()
			lstfp.write(l+' '*(maxlen-len(l)-1)+"\n")
		lstfp.close()

def parse_command_line():
	usage="Usage: %prog <input image file> ... <input image file> <output lst file> [options]"
	parser = OptionParser(usage=usage)
	
	parser.add_option("--removeDuplicates",dest="removeDuplicates",action="store_true",	      \
					  help="if check and remove duplicated particles. disabled by default",   \
					  default=0)
	
	(options, args)=parser.parse_args()

	if len(args)<2: 
		print "At least one input images and one output image are required"
		parser.print_help()
		sys.exit(-1)
	
	input_imagefiles = args[0:-1]
	output_lstfile = args[-1]
	
	return (options, input_imagefiles, output_lstfile)

def isDuplicate(seenImages, curImageFile, curImageIndex):
	imgid = "%s-%d" % (os.path.abspath(curImageFile), curImageIndex)
	if imgid in seenImages: 
		return 1
	else:
		seenImages.add(imgid)
		return 0

def follow_lst_link(image, index, lstfiles, imagefiles):
	if not (imagefiles.has_key(image) or lstfiles.has_key(image)): # it has not seen this image before and will find out
		imgnum, imgtype = EMAN.fileCount(image)
		if imgtype == "lst":
			tmplst = []
			fp = open(image,'r')
			lines= fp.readlines()
			fp.close()
			if lines[0].startswith("#LST"): line0 = 1
			elif lines[0].startswith("#LSX"): line0 = 3
			
			for l in lines[line0:]:
				tokens = l.split()
				tmplst.append((tokens[1], int(tokens[0])))
			lstfiles[image] = tmplst
		else:
			imagefiles[image]=imgnum
	
	if imagefiles.has_key(image): 	# it has already known this image is a binary format image
		if index>=imagefiles[image]:
			print "Error: image file %s only has %d images, not enough for %d" % (image, imagefiles[image], index)
			sys.exit(-1) 
		else:
			return (image, index)
	elif lstfiles.has_key(image):	# it has already known this image is a list format image
		if index>=len(lstfiles[image]):
			print "Error: lst file %s only has images, not enough for %d" % (image, len(lstfiles[image]), index)
			sys.exit(-1) 
		else:
			return follow_lst_link(lstfiles[image][index][0], lstfiles[image][index][1], lstfiles, imagefiles)
	else:
		print "Something is wrong, need to debug this program and the image file"
		sys.exit(-1)


if __name__== "__main__":
	main()
