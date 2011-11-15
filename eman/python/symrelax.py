#!/usr/bin/env python

# $Id: symrelax.py,v 1.2 2006/11/22 00:58:52 wjiang Exp $

# by Wen Jiang <jiang12@purdue.edu>, 2006-1-17

import EMAN
import glob, re, os, sys, string
from math import pi
import Numeric, MLab
try:
	from optparse import OptionParser
except:
	from optik import OptionParser
try:
	import mpi
except:
	mpi = None
try:
	import pypar
except:
	pypar = None

def main():
	EMAN.appinit(sys.argv)
	if sys.argv[-1].startswith("usefs="): sys.argv = sys.argv[:-1]	# remove the runpar fileserver info

	(options, rawimage, refmap) = parse_command_line()

	sffile = options.sffile
	verbose = options.verbose
	shrink = options.shrink
	mask = options.mask
	first = options.first
	last = options.last
	scorefunc = options.scorefunc

	projfile = options.projection
	output_ptcls = options.update_rawimage
	cmplstfile = options.cmplstfile
	ortlstfile = options.ortlstfile
	startSym = options.startSym
	endSym = options.endSym
	
	if not options.nocmdlog:
		pid = EMAN.LOGbegin(sys.argv)
		EMAN.LOGInfile(pid, rawimage)
		EMAN.LOGInfile(pid, refmap)
		if projfile: EMAN.LOGOutfile(pid, projfile)
		if output_ptcls: EMAN.LOGOutfile(pid, output_ptcls)
		if cmplstfile: EMAN.LOGOutfile(pid, cmplstfile)
		if ortlstfile: EMAN.LOGOutfile(pid, ortlstfile)

	ptcls = []
	if not (mpi or pypar) or ((mpi and mpi.rank == 0) or (pypar and pypar.rank==0)):
		ptcls = EMAN.image2list( rawimage )
		ptcls = ptcls[first:last]

		print "Read %d particle parameters" % (len(ptcls))
		#ptcls = ptcls[0:10]
	
	if mpi and mpi.size>1: 
		ptcls = mpi.bcast(ptcls)
		print "rank=%d\t%d particles" % (mpi.rank, len(ptcls))
	elif pypar and pypar.size()>1:
		ptcls = pypar.broadcast(ptcls)
		print "rank=%d\t%d particles" % (pypar.rank(), len(ptcls))

	if sffile:
		sf = EMAN.XYData()
		sf.readFile(sffile)        
		sf.logy()
	
	if not mpi or ((mpi and mpi.rank == 0) or (pypar and pypar.rank()==0)):
		if cmplstfile and projfile:
			if output_ptcls: raw_tmp = output_ptcls
			else: raw_tmp = rawimage
			raw_tmp = rawimage
			fp = open("tmp-"+cmplstfile,'w')
			fp.write("#LST\n")
			for i in range(len(ptcls)):
				fp.write("%d\t%s\n" % (first + i, projfile))
				fp.write("%d\t%s\n" % (first + i, raw_tmp))
			fp.close()
		if (mpi and mpi.size>1 and mpi.rank == 0) or (pypar and pypar.size()>1 and pypar.rank()==0):
			total_recv = 0
			if output_ptcls: total_recv += len(ptcls)
			if projfile:     total_recv += len(ptcls)
			for r in range(total_recv):
				#print "before recv from %d" % (r)
				if mpi: 
					msg, status = mpi.recv()
				else: 
					msg = pypar.receive(r)
				#print "after recv from %d" % (r)
				#print msg, status
				d = emdata_load(msg[0])
				fname = msg[1]
				index = msg[2]
				d.writeImage(fname,index)
				print "wrtie %s %d" % (fname, index)
			if options.ortlstfile:
				solutions=[]
				for r in range(1,mpi.size):
					msg, status = mpi.recv(source = r, tag = r)
					solutions += msg
				def ptcl_cmp(x, y):
					eq = cmp(x[0], y[0])
					if not eq: return cmp(x[1],y[1])
					else: return eq
				solutions.sort(ptcl_cmp)		
	if (not mpi or (mpi and ( (mpi.size >1 and mpi.rank >0) or mpi.size==1))) or \
	   (not pypar or (pypar and ( (pypar.size() >1 and pypar.rank() >0) or pypar.size()==1))):                               
		map3d = EMAN.EMData()
		map3d.readImage(refmap,-1)
		map3d.normalize()
		if shrink>1: map3d.meanShrink(shrink)
		map3d.realFilter(0,0)	# threshold, remove negative pixels
		
		imgsize = map3d.ySize()
		
		img = EMAN.EMData()
		
		ctffilter = EMAN.EMData()
		ctffilter.setSize(imgsize+2,imgsize,1)
		ctffilter.setComplex(1);
		ctffilter.setRI(1);

		if (mpi and mpi.size>1) or (pypar and pypar.size()>1):
			ptclset = range(mpi.rank -1, len(ptcls), mpi.size-1)
		else:
			ptclset = range(0, len(ptcls))

		if mpi: print "Process %d/%d: %d/%d particles" % (mpi.rank, mpi.size, len(ptclset), len(ptcls))

		solutions = []
		for i in ptclset:
			ptcl = ptcls[i]
			e = EMAN.Euler( ptcl[2], ptcl[3], ptcl[4] )
			dx = ptcl[5] - imgsize/2
			dy = ptcl[6] - imgsize/2
			print "%d\talt,az,phi=%8g,%8g,%8g\tx,y=%8g,%8g" % (i+first, e.alt()*180/pi, e.az()*180/pi, e.phi()*180/pi, dx, dy), 

			img.readImage(ptcl[0], ptcl[1])
			img.setTAlign(-dx, -dy, 0)
			img.setRAlign(0,0,0)
			img.rotateAndTranslate()	# now img is centered
			img.applyMask(int(mask-max(abs(dx), abs(dy))), 6, 0, 0, 0)
			if img.hasCTF():
				fft=img.doFFT()
				
				ctfparm = img.getCTF()
				ctffilter.setCTF(ctfparm)
				if options.phasecorrected:
					if sffile: ctffilter.ctfMap(64, sf)	# Wiener filter with 1/CTF (no sign) correction
				else:
					if sffile: ctffilter.ctfMap(32, sf)	# Wiener filter with 1/CTF (including sign) correction
					else: ctffilter.ctfMap(2, EMAN.XYData())	# flip phase
	
				fft.mult(ctffilter)
				img2 = fft.doIFT()	# now img2 is the CTF-corrected raw image
				
				img.gimmeFFT()
				del fft
			else:
				img2 = img
				
			img2.normalize()
			if shrink>1: img2.meanShrink(shrink)
			#if sffile:
			#	snrcurve = img2.ctfCurve(9, sf)	# absolute SNR
			#else:
			#	snrcurve = img2.ctfCurve(3, EMAN.XYData())		# relative SNR

			e.setSym(startSym)
			maxscore = -1e30	# the larger the better
			scores = []
			for s in range(e.getMaxSymEl()):
				ef = e.SymN(s)
				#proj = map3d.project3d(ef.alt(), ef.az(), ef.phi(), -6)		# Wen's direct 2D accumulation projection
				proj = map3d.project3d(ef.alt(), ef.az(), ef.phi(), -1)	# Pawel's fast projection, ~3 times faster than mode -6 with 216^3
																			# don't use mode -4, it modifies its own data
				#proj2 = proj    
				proj2 = proj.matchFilter(img2)                                                                   
				proj2.applyMask(int(mask-max(abs(dx), abs(dy))), 6, 0, 0, 0)
				if scorefunc == 'ncccmp': score = proj2.ncccmp(img2)
				elif scorefunc == 'lcmp': score = -proj2.lcmp(img2)[0]
				elif scorefunc == 'pcmp': score = -proj2.pcmp(img2)	
				elif scorefunc == 'fsccmp': score = proj2.fscmp(img2, [])
				elif scorefunc == 'wfsccmp': score = proj2.fscmp(img2, snrcurve)
				if score> maxscore:
					maxscore = score
					best_proj = proj2
					best_ef = ef
					best_s=s
				scores.append(score)
				#proj2.writeImage("proj-debug.img",s)
				#print "\tsym %2d/%2d: euler=%8g,%8g,%8g\tscore=%12.7g\tbest=%2d euler=%8g,%8g,%8g score=%12.7g\n" % \
				#		   (s,60,ef.alt()*180/pi,ef.az()*180/pi,ef.phi()*180/pi,score,best_s,best_ef.alt()*180/pi,best_ef.az()*180/pi,best_ef.phi()*180/pi,maxscore)
			scores=Numeric.array(scores)
			print "\tbest=%2d euler=%8g,%8g,%8g max score=%12.7g\tmean=%12.7g\tmedian=%12.7g\tmin=%12.7g\n" % \
				   (best_s,best_ef.alt()*180/pi,best_ef.az()*180/pi,best_ef.phi()*180/pi,maxscore,MLab.mean(scores),MLab.median(scores),MLab.min(scores))
			if projfile:
				best_proj.setTAlign(dx,dy,0)
				best_proj.setRAlign(0,0,0)
				best_proj.rotateAndTranslate()

				best_proj.set_center_x(ptcl[5])
				best_proj.set_center_y(ptcl[6])
				best_proj.setRAlign(best_ef)
				#print "before proj send from %d" % (mpi.rank)
				
				if mpi and mpi.size>1: mpi.send((emdata_dump(best_proj), projfile, i+first), 0)
				elif pypar and pypar.size()>1: pypar.send((emdata_dump(best_proj), projfile, i+first), 0)
				#print "after proj send from %d" % (mpi.rank)
				else: best_proj.writeImage(projfile, i+first)
			
			img2.setTAlign(0,0,0)
			img2.setRAlign(best_ef)
			img2.setNImg(1)
			#print "before raw send from %d" % (mpi.rank)
			if output_ptcls:
				if mpi and mpi.size>1: mpi.send((emdata_dump(img2), output_ptcls, i+first), 0)
				elif pypar and pypar.size()>1: pypar.send((emdata_dump(img2), output_ptcls, i+first), 0)
				#print "after raw send from %d" % (mpi.rank)
				else: img2.writeImage(output_ptcls, i+first)
												  
			solutions.append( (ptcl[0], ptcl[1], best_ef.alt(), best_ef.az(), best_ef.phi(), ptcl[5], ptcl[6]) )
		if mpi and (mpi.size >1 and mpi.rank >0):
			mpi.send(solutions, 0, tag = mpi.rank)

	if mpi: mpi.barrier()
	elif pypar: pypar.barrier()
	if mpi: mpi.finalize()
	elif pypar: pypar.finalize()
	
	if options.cmplstfile: 
		os.rename("tmp-"+cmplstfile,cmplstfile)
	if options.ortlstfile:
		lFile = open(options.ortlstfile, "w")
		lFile.write("#LST\n")
		for i in solutions:
			lFile.write("%d\t%s\t%g\t%g\t%g\t%g\t%g\n" % (i[1], i[0], i[2]*180.0/pi, i[3]*180.0/pi, i[4]*180.0/pi, i[5], i[6]))
		lFile.close()

	if not options.nocmdlog:
		EMAN.LOGend()

def parse_command_line():
	usage="Usage: %prog <raw image filename> <ref 3D map> [options]"
	parser = OptionParser(usage=usage)
	parser.add_option("--mask",dest="mask",type="int",help="mask radius. default to half image size", default=0)
	parser.add_option("--verbose",dest="verbose",type="int",help="verbose level [0-2]. default to 1", default=1)
	parser.add_option("--phasecorrected",dest="phasecorrected",action="store_true",help="if the particle images already phase flipped. default to false", default=0)
	parser.add_option("--sf",dest="sffile",type="string",help="structural factor ile name", default="")
	parser.add_option("--startSym",dest="startSym",type="string",help="starting symmetry, default to icos", default="icos")
	parser.add_option("--endSym",dest="endSym",type="string",help="ending symmetry, default to c1", default="c1")
	parser.add_option("--first",dest="first",type="int",help="first image index", default=0)
	parser.add_option("--last",dest="last",type="int",help="last image index", default=0)
	parser.add_option("--shrink",dest="shrink",type="float",help="shrink factor, can only be 1.5 or >1 integer", default=1)
	parser.add_option("--score",metavar="['ncccmp', 'lcmp', 'pcmp', 'fsccmp', 'wfsccmp']",dest="scorefunc",type="choice",choices=['ncccmp', 'lcmp', 'pcmp', 'fsccmp', 'wfsccmp'], help="scoring function to use. default to \"fsccmp\"", default="fsccmp")
	parser.add_option("--projection",dest="projection",type="string",help="output projection image filename", default="")
	parser.add_option("--update_rawimage",dest="update_rawimage",type="string",help="output image file name for the updated raw images", default="")
	parser.add_option("--cmplstfile",dest="cmplstfile",type="string",help="output the lst file for comparing raw images and projections", default="")
	parser.add_option("--ortlstfile",dest="ortlstfile",type="string",help="output the lst file for the new orientation/center parameters", default="")
	parser.add_option("--nocmdlog",dest="nocmdlog",action="store_true",help="don't log command, disabled by default", default=0)

	(options, args)=parser.parse_args()

	if len(args) !=2:
		parser.print_help()
		sys.exit(-1)
	
	if options.sffile and not os.path.exists(options.sffile):
		print "ERROR: sffile \"%s\" does not exist" % (options.sffile)
		sys.exit()
	if options.cmplstfile and not options.projection:
		print "\"--projection\" options must be set for \"--cmplstfile\" to work"
		options.cmplstfile=""

	if options.mask<=0:
		d = EMAN.EMData()
		d.readImage(args[0], 0)	# header only
		imagesize = d.ySize();
		options.mask=imagesize/2
	if options.first<0 or options.last<=0 or options.first>=options.last:
		imgnum = EMAN.fileCount(args[0])
		if options.first<0: options.first=0
		if options.last<=0 or options.first>=options.last: options.first=imgnum
	
	return (options, args[0], args[1])

def emdata_dump(emdata_obj):
	rot = emdata_obj.getEuler()
	alt = rot.alt()
	az = rot.az()
	phi = rot.phi()
	return {"rotation":(alt,az,phi),"data":emdata_obj.getData() }
	#return {"data":EMAN2.Wrapper.em2numpy(emdata_obj) }

def emdata_load(obj):
	d = EMAN.EMData()
	d.setData(obj["data"])
	d.setRAlign(obj["rotation"][0], obj["rotation"][1], obj["rotation"][2]) 
	d.setNImg(1)
	return d

if __name__== "__main__":
	main()

