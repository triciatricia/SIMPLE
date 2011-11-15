#!/usr/bin/env python 

# $Id: classesbymraScoreMerge.py,v 1.6 2007/03/29 18:42:06 wjiang Exp $

# by Wen Jiang <jiang12@purdue.edu>, 2006-8-14


import os, sys, glob, bisect
import EMAN
try:
	from optparse import OptionParser
except:
	from optik import OptionParser
try:
	import psyco
	psyco.full()
except ImportError:
	pass

def main():
	(options, input_lstfiles) = parse_command_line()
	ptcls = readLstFiles(input_lstfiles, nBest = options.nBest)
	
	if options.ortLstFile:
		ptcls_list = []
		for p in ptcls:
			ptcls_list += ptcls[p].items()
		ptcls_list.sort()

		fp = open(options.ortLstFile, 'w')
		fp.write("#LST\n")
		for p in ptcls_list:
			fp.write("%d\t%s\teuler=%g,%g,%g\tcenter=%g,%g\n" % (p.imageIndex, p.imageFile, p.euler[0], p.euler[1], p.euler[2], p.center[0], p.center[1]))
		fp.close()
		cmd = "images2lst.py %s %s" % (options.ortLstFile, options.ortLstFile)
		os.system(cmd)
	
	if options.saveClsLst:
		nProj = EMAN.fileCount(options.projFile)[0]
		clses = [ 1 ]* nProj
		for i in range(len(clses)): clses[i] = []

		for p in ptcls:
			solutions = ptcls[p].items()
			for pi in solutions: 
				clses[pi.refid].append(pi)
		import math
		#digits = int(math.log10(nProj)+1)
		digits = 4
		for cls in range(len(clses)):
			ptcls_list = clses[cls]
			ptcls_list.sort()

			clsfn = "%d" % (cls)
			clsfn = "%s%s.lst" % (options.clsFileTag, clsfn.zfill(digits))
			fp = open(clsfn,'w')
			fp.write("#LST\n")
			fp.write("%d\t%s\n" % (cls, options.projFile))
			for p in ptcls_list:
				fp.write("%d\t%s\t%s\n" % (p.imageIndex, p.imageFile, p.clsinfo))
			fp.close()
			
			if options.eotest:
				clsfn = "%d" % (cls)
				clsfn_even = "%s%s.even.lst" % (options.clsFileTag, clsfn.zfill(digits))
				clsfn_odd = "%s%s.odd.lst" % (options.clsFileTag, clsfn.zfill(digits))
				fp_even = open(clsfn_even,'w')
				fp_even.write("#LST\n")
				fp_even.write("%d\t%s\n" % (cls, options.projFile))
				fp_odd = open(clsfn_odd,'w')
				fp_odd.write("#LST\n")
				fp_odd.write("%d\t%s\n" % (cls, options.projFile))
				for p in ptcls_list:
					if p.imageIndex%2:
						fp_odd.write("%d\t%s\t%s\n" % (p.imageIndex, p.imageFile, p.clsinfo))
					else:
						fp_even.write("%d\t%s\t%s\n" % (p.imageIndex, p.imageFile, p.clsinfo))
				fp_even.close()
				fp_odd.close()
			
			#cmd = "images2lst.py %s %s" % (clsfn, clsfn)
			#os.system(cmd)
			

def parse_command_line():
	usage="%prog <input lst file 1> <input lst file 2> ... <input lst file n> [options]"
	
	parser = OptionParser(usage=usage)
	parser.add_option("--nBest",dest="nBest",type="int",help="number of best scores to use. default to 1", default=1)
	parser.add_option("--saveClsLst",dest="saveClsLst",action="store_true", help="if save the cls*.lst file for class averaging. disabled by default", default=0)
	parser.add_option("--clsFileTag",dest="clsFileTag",type="string", help="tag string to name cls files as \"tag*.lst\" instead of default \"cls*.lst\"", default="cls")
	parser.add_option("--eotest",dest="eotest",action="store_true",help="also save even/odd cls*.lst files for eotest, disabled by default", default=0)
	parser.add_option("--projFile",dest="projFile",type="string",help="projection file used for the classes", default="")
	parser.add_option("--ortLstFile",dest="ortLstFile",type="string",help="file name used to save the best scored orientations to a list file. default to \"\"", default="")
	
	(options, args)=parser.parse_args()
	if len(args)<1: 
		print "Error: At least one input image is required\n"
		parser.print_help()
		sys.exit(-1)
	
	if not options.saveClsLst and not options.ortLstFile:
		print "Error: at last one of the options [\"saveClsLst\", \"ortLstFile\"] shoudl be used\n"
		parser.print_help()
		sys.exit(1)
 	
	if options.projFile and not options.saveClsLst:
		print "Warning: option \"projFile\" is useless with option \"saveClsLst\"\n"

	if options.saveClsLst and not options.projFile:
		print "Error: option \"projFile\" is required when option \"saveClsLst\" is used\n"
		parser.print_help()
		sys.exit(1)

	input_lstfiles = []
	for f in args: input_lstfiles += glob.glob(f)
		
	return (options, input_lstfiles)


class  Particle:
	def __init__(self, imageFile=None, imageIndex=None, euler=None, center=None, refid=None, socre=None, clsinfo = None):
		self.imageFile = imageFile
		self.imageIndex = imageIndex
		self.euler = euler
		self.center = center
		self.refid = refid
		self.score = socre
		self.clsinfo = clsinfo
		self.hashVal = hash((os.path.abspath(self.imageFile),self.imageIndex)) # to speedup computation for big image lists
	def __hash__(self):
		return self.hashVal
	def __cmp__(self, other):
		same_imagefile = cmp(os.path.abspath(self.imageFile), os.path.abspath(other.imageFile))
		if same_imagefile: return same_imagefile
		same_imagefile = cmp(self.imageIndex, other.imageIndex)
		if same_imagefile: return same_imagefile
		return -1 * cmp(self.score, other.score)	# swap order so that larger scores are placed in the beginning
		
class FixedLenQueue:
	def __init__(self, maxLen=1):
		self.maxLen = maxLen
		self.queue = [] 
	def push(self, item):	# 0 - smallest, -1 - largest
		if not self.queue: self.queue.append(item)
		elif self.maxLen==1:
			if item < self.queue[0]: self.queue[0] = item
		elif item<self.queue[-1] or len(self.queue)<self.maxLen:
			bisect.insort_left(self.queue, item)
			if len(self.queue)>self.maxLen: self.queue.pop() # remove the worse one at the end
	def items(self):
		return self.queue
	
def readLstFiles(filenames, nBest = 1):
	import fileinput

	ptcls = {}
	count = 0
	for l in fileinput.input(filenames):
		if l[0]=="#": continue
		count += 1
		print "%d\r" % (count),
		
		euler = None
		center = None
		refid = None
		score = None
		clsinfo = None

		tkns = l.split()
		if len(tkns) >=5:
			imageFile = tkns[1]
			imageIndex = int(tkns[0])
			for t in tkns[2:]:
				if t.startswith("euler="):
					angs = t[6:].split(',')
					if len(angs)!=3: 
						raise ValueError("Wrong format for \"%s\"" % (t))
					else:
						euler = (float(angs[0]), float(angs[1]), float(angs[2]))
				elif t.startswith("center="):
					centers = t[7:].split(',')
					if len(centers)!=2: 
						raise ValueError("Wrong format for \"%s\"" % (t))
					else:
						center = (float(centers[0]), float(centers[1]))
				elif t.startswith("refid="):
					refid = t[6:]
					refid = int(refid)
				elif t.startswith("score="):
					score = t[6:]
					score = float(score)
				elif t.startswith("clsinfo="):
					clsinfo = t[8:]
			#print imageFile, imageIndex, euler, center, refid, score
			p = Particle(imageFile, imageIndex, euler, center, refid, score, clsinfo)
			if not ptcls.has_key(p.hashVal): ptcls[p.hashVal] = FixedLenQueue(maxLen = nBest)
			ptcls[p.hashVal].push(p)
		else:
			raise ValueError("Wrong format for line \"%s\"" % (l))
	
	print
	return ptcls

if __name__=="__main__":
	main()
