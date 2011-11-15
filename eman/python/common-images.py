#!/usr/bin/env python

# $Id: common-images.py,v 1.9 2006/11/29 01:45:19 wjiang Exp $

# by Wen Jiang <jiang12@purdue.edu>, 2006-1-17

import os, sys, sets, math
import EMAN
try:
	from optparse import OptionParser
except:
	from optik import OptionParser

def main():
	
	(options, input_imagefiles, output_lstfile) = parse_command_line()
	
	Particle.sym = options.sym
	Particle.max_ang_diff = options.max_ang_diff * math.pi/180.0
	Particle.max_cen_diff = options.max_cen_diff
		
	image_lists = []
	
	for f in input_imagefiles:	# build the image sets
		tmp_image_list = EMAN.image2list(f)
		
		# first check and remove duplicate images
		seen = sets.Set()
		tmp_image_list2 = []
		for i, img in enumerate(tmp_image_list): 
			imgid = "%s-%d" % (os.path.abspath(img[0]), img[1])
			if imgid in seen:
				print "%s: particle %d/%d (%s %d) is a duplicate image, ignored" % (f, i, len(tmp_image_list), img[0], img[1])
			else:
				seen.add(imgid)
				tmp_image_list2.append(img)
		
		image_list = sets.Set()
		for i, img in enumerate(tmp_image_list2): 
			p = Particle(img)
			image_list.add(p)
		print "%s: %d images" % (f, len(image_list))
		image_lists.append( image_list )

	all_images = image_lists[0]
	print "Begining with %d images in %s" % (len(all_images), input_imagefiles[0])
	for i in range(1,len(image_lists)):
		image_list = image_lists[i]
		if options.mode == "common":	# all_images & imageset
			all_images = intersection(all_images, image_list)
			print "%d common images after processing %d images in %s" % ( len(all_images), len(image_list), input_imagefiles[i] )
		elif options.mode == "union":
			all_images = union(all_images, image_list)	# all_images | imageset
			print "%d images after merging %d images in %s" % ( len(all_images), len(image_list), input_imagefiles[i] )
		elif options.mode == "diff":
			all_images = difference(all_images,image_list)	# all_images-imageset
			print "%d different images after processing %d images in %s" % ( len(all_images), len(image_list), input_imagefiles[i] )
		elif options.mode == "symdiff":
			all_images = symmetric_difference(all_images,image_list)	# all_images ^ imageset
			print "%d different images after processing %d images in %s" % ( len(all_images), len(image_list), input_imagefiles[i] )
	
	all_images=list(all_images)
	all_images.sort()
	
	all_images_output_list = [i.image for i in  all_images]
			
	if len(all_images_output_list):
		print "%d images saved to %s" % ( len(all_images_output_list), output_lstfile )
		EMAN.imagelist2lstfile(all_images_output_list, output_lstfile)
	else:
		print "No image left after the image sets operation"
			
def parse_command_line():
	usage="Usage: %prog <input image file 1> <input image file 2> ... <input image file n> <output lst file> [options]"
	
	parser = OptionParser(usage=usage)
	
	parser.add_option("--max_ang_diff",dest="max_ang_diff",type="float",help="maximal orientation difference allowed (in degrees), default to -1 to ignore angular difference", default=-1)
	parser.add_option("--max_cen_diff",dest="max_cen_diff",type="float",help="maximal center difference allowed (in pixels), default to -1 to ignore center difference", default=-1)
	parser.add_option("--sym",dest="sym",type="string",help="symmetry to use when computing orientation difference, default to c1", default="c1")
	parser.add_option("--mode",metavar="['common', 'union', 'diff', 'symdiff']",dest="mode",type="choice",choices=['common', 'union', 'diff', 'symdiff'], help="image set operation mode. default to \"common\"", default="common")
	
	(options, args)=parser.parse_args()

	if len(args)<3: 
		print "At least two input images and one output image are required"
		parser.print_help()
		sys.exit(-1)
	
	input_imagefiles = args[0:-1]
	output_lstfile = args[-1]
	
	return (options, input_imagefiles, output_lstfile)

class Particle:
	sym = "c1"
	max_ang_diff = -1	# in radian, won't be checked if <0
	max_cen_diff = -1	# in pixel, won't be checked if <0
	
	def __init__(self, image):
		self.image = image
		self.hashval = hash((os.path.abspath(self.image[0]),self.image[1])) # to speedup computation for big image lists
	
	def __hash__(self):
		return self.hashval

	def __eq__(self, other):
		if self.hashval != other.hashval: return 0

		same_ang = 1
		if self.__class__.max_ang_diff>=0:
			angdiff = self.ang_difference(other)
			if angdiff > self.__class__.max_ang_diff:
				print "%s:%d vs %s:%d - orientation diff too large (%g > %g degree)" % \
					(self.image[0],self.image[1],other.image[0],other.image[1], \
					angdiff*180./math.pi, self.__class__.max_ang_diff*180./math.pi)
				return 0

		if self.__class__.max_cen_diff>=0:
			dx = self.image[5] - other.image[5]
			dy = self.image[6] - other.image[6]
			if dx * dx + dy * dy >  self.__class__.max_cen_diff * self.__class__.max_cen_diff:
				print "%s:%d vs %s:%d - center diff too large (dx=%g dy=%g d=%g > %g pixel)" % \
					(self.image[0],self.image[1],other.image[0],other.image[1], \
					dx, dy, math.sqrt(dx*dx+dy*dy), self.__class__.max_cen_diff)
				return 0
		
		return 1
		
	def __cmp__(self, other):
		same_imagefile = cmp(os.path.abspath(self.image[0]), os.path.abspath(other.image[0]))
		if same_imagefile: return same_imagefile
		else: return cmp(self.image[1], other.image[1])
	
	def ang_difference(self, other):
		euler1 = EMAN.Euler(self.image[2], self.image[3], self.image[4])
		euler2 = EMAN.Euler(other.image[2], other.image[3], other.image[4])
		if self.__class__.sym=="c1": diff = euler1.diff(euler2) 
		else:
			euler2.setSym(self.__class__.sym)
			num_sym = euler2.getMaxSymEl()
			diff = 4 * math.pi
			for s in range(num_sym):
				tmp_euler = euler2.SymN(s)
				tmp_diff = euler1.diff(tmp_euler, 0) # 0 will consider all 3 angles, otherwise only the first 2 angles are considered
				if tmp_diff < diff: 
					diff = tmp_diff
		return diff

# these functions follow terminology used in standard lib sets 
def intersection(images1, images2):
	""" images1 & images2 """
	ret = sets.Set()
	for img in images1:
		if img in images2: ret.add(img)
	return ret
	
def union(images1, images2):
	""" images1 | images2 """
	more = sets.Set()
	for img in images2:
		if img not in images1: more.add(img)
	return images1.union(more)

def difference(images1, images2):
	""" images1 - images2 """
	ret = sets.Set()
	for img in images1:
		if img not in images2: ret.add(img)
	return ret

def symmetric_difference(images1, images2):
	""" images1 ^ images2, not in images1 and not in images2 """
	ret = sets.Set()
	for img in images1:
		if img not in images2: ret.add(img)
	for img in images2:
		if img not in images1: ret.add(img)
	return ret

if __name__== "__main__":
	main()
