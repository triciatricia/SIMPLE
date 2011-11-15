#!/usr/bin/env python
### This program will try to iteratively classify and align a set of 2D particle images without any 3D reconstruction

#N refine2d.py
#F This is a program for iterative MSA-based particle classification and averaging
#T H
#1
#P [--iter=<i>]	Number of iterations. 10 is almost always sufficient. For less noisy data 3-4 may be enough.
#P [--ninitcls=<n>]	Number of classes to generate (though some may be discarded). Typically < #ptcl/10
#P [--finalsep=<n2>]	In the final iteration, each class will be subdivided into n2 subclasses, producing n*n2 classes
#P [--nbasis=<b>]	Number of basis vectors to use in SVD. Default is usually fine.
#P [--proc=<p>]	Number of processors to use (EMAN standard classification routine)
#P [--ctfcw=<sffile>]	Perform full CTF amplitude correction when making final class-averages. Only used in the final iteration.
#P [--minptcl=<m>]	Minimum number of particles in a class to keep.
#P [--aliref=<ref img>]	If specified, the first image will be used as an alignment reference for the first class-average to help 'anchor' the set
#U refine2d.py --iter=8 --ninitcls=50 --proc=4 particles.hed
#D This program will generate very high quality 2-D class averages based on a SVD/MSA iterative
#E classification scheme. It is not typically involved in the 3-D reconstruction process other
#E than perhaps to generate an initial model, due to resolution and noise bias issues, but for
#E 2-D analysis, it performs extrememly well.
#D This program produces a large number of intermediate/output files. It is suggested that you run
#E it in an empty directory. The main output files are : iter.final.*
#D Many 'tricky' things can be done with the results of refine2d.py. Check the FAQ on the EMAN wiki
#E for tips on how to use this for dynamics analysis, particle separation, etc.


from EMAN import *
try:
	from optparse import OptionParser
except:
	from optik import OptionParser
from math import *
from os import system as system2
from random import random
import os
import sys
import string
from linecache import getline

def system(s):
	print s
	system2(s)

def LOGbegin(ARGV):
	out=open(".emanlog","a")
	b=string.split(ARGV[0],'/')
	ARGV[0]=b[len(b)-1]
	out.write("%d\t%d\t1\t%d\t%s\n"%(os.getpid(),time.time(),os.getppid(),string.join(ARGV," ")))
	out.close()

def LOGend():
	out=open(".emanlog","a")
	out.write("%d\t%d\t2\t-\t\n"%(os.getpid(),time.time()))
	out.close()


def sysprint(a):
	print a
	system(a)

def main():
	progname = os.path.basename(sys.argv[0])
	usage = """Usage: %prog [options] <particle_stack>
	
"""

	parser = OptionParser(usage=usage,version=EMANVERSION)

	parser.add_option("--iter", type="int",help="Number of refinement iterations",default=10)
#	parser.add_option("--ncls","-N", type="int",help="Number of final classes to produce",default=40)
	parser.add_option("--nosvd", dest="nosvd", action="store_true", default=False, help="Use straight k-means for classification instead of SVD based vectorization")
	parser.add_option("--ninitcls","-I", type="int",help="Number of initial classes for alignment iterations",default=10)
	parser.add_option("--finalsep","-F", type="int",help="number of additional class subsplits in final iteration",default=0)
	parser.add_option("--proc","-P", type="int",help="Processors to use",default=1)
	parser.add_option("--minptcl", type="int",help="Minimum number of particles in a final class-average",default=6)
	parser.add_option("--ctfcw","-C", type="string",help="Structure factor file for full CTF correction",default=None)
	parser.add_option("--nbasis","-B", type="int",help="Number of basis vectors to use in classification, default 12",default=12)
	parser.add_option("--nofinalsort",dest="nofinalsort", action="store_true", default=False, help="Do not sort the final class-averages (this can be very slow)")
	parser.add_option("--aliref",type="string",help="The first image from the specified file will be used as an alignment reference to help anchor the orientation of the final averages",default=None)
	parser.add_option("--refbias",type="string",help="The first image in this file will be multiplied by each class-average prior to MSA calculation. This image can be used to upweight the significance of certain regions of averages when used with aliref",default=None)
	parser.add_option("--logptcl",dest="logptcl", action="store_true", default=False, help="Makes a logfile containing the identity of the class-average for each particle")
	parser.add_option("--debug",dest="debug", action="store_true", default=False, help="debuging output")
	
	(options, args) = parser.parse_args()
	if len(args)<1 : parser.error("Input stack required")
	
	LOGbegin(sys.argv)
	
	nptcl=fileCount(args[0])[0]
	print "Analyzing %d particles"%nptcl
	if (nptcl<10) : 
		print("Input file %s must contain at least 10 particles" % args[0])
		sys.exit(1)
	
	if options.refbias : 
		rb=EMData()
		rb.readImage(options.refbias)
		options.refbias,rb=rb,options.refbias
	
	if options.aliref : 
		ar=EMData()
		ar.readImage(options.aliref)
		options.aliref=ar
	
	# initial reference-free classification
	system("rm tmp.snrc.*")
	system("proc2d %s tmp.snrc.hed last=1999"%args[0])
	system("startnrclasses tmp.snrc.hed %d nobad proc=%d"%(min(nptcl/10,200),max(1,options.proc)))
	
	# Sort the averages in order of the number of particles in each
	avgs=readImages("classes.nr.hed",-1,-1)
	avgs=seriesalign3(avgs,options.aliref)

	
	try:
		os.unlink("iter.0.hed")
		os.unlink("iter.0.img")
	except: pass
	for i in avgs: 
		i.clearCTF()
		i.writeImage("iter.0.hed",-1)
	
	for i in range(1,options.iter):
		if options.debug : print "DBUG A ",i
		system("rm cls*lst")
		system("proc2d iter.%d.hed cls mraprep"%(i-1))

		# While this does classify, we're really using this to get the 
		# best alignment for each particle
		fsp="tmp.%d"%int(random()*999999)
		out=file(fsp,"w")
		if nptcl/50<options.proc : denom=options.proc
		else: denom=options.proc*(floor(nptcl/(50*options.proc)))
		if options.refbias and i>1 :
			out.write("classesbymra %s tmp.hed split refine fscmp frac=%d/%d\n"%(args[0],0,denom))
			for k in range(1,denom): out.write("classesbymra %s tmp.hed split refine fscmp frac=%d/%d quiet\n"%(args[0],k,denom))
		else:
			out.write("classesbymra %s iter.%d.hed split refine fscmp frac=%d/%d\n"%(args[0],i-1,0,denom))
			for k in range(1,denom): out.write("classesbymra %s iter.%d.hed split refine fscmp frac=%d/%d quiet\n"%(args[0],i-1,k,denom))
		out.close()
		if options.debug : print "DBUG B"
		system("runpar file=%s proc=%d"%(fsp,options.proc))
		os.unlink(fsp)
#			os.unlink(fsp)
#		else:
#			system("classesbymra %s iter.%d.hed split refine phase"%(args[0],i-1))
		
		system("tar cf cls.%0d.tar cls*lst"%i)

		if options.debug : print "DBUG C"
		fsp=os.listdir(".")
		try:
			os.unlink("ptcl.hed")
			os.unlink("ptcl.img")
		except:
			pass
			
		# write the aligned particles to ptcl.hed
		olf=file("ptcl2orig.lst","w")
		olf.write("#LST\n")
		for f in fsp:
			if f[:3]=="cls" and f[-4:]==".lst":
				ii=file(f,"r").readlines()[1:]
				ii=[(int(k.split()[0]),k.split()[1]) for k in ii]
				print f,len(ii)-1
				a=EMData()
				for im in range(1,len(ii)):
					olf.write("%d\t%s\n"%(ii[im][0],ii[im][1]))
#					a.readImage(ii[im][1],ii[im][0])
					a.readImage(f,im)
					a.edgeNormalize()
					a.rotateAndTranslate()
					a.writeImage("ptcl.hed",-1)
		olf.close()

		if options.debug : print "DBUG D"
		# now classify
		if (not options.nosvd) :
			# we make our basis set using SVD on the averages
			ncc=fileCount("iter.%d.hed"%(i-1))[0]
			if options.nbasis>=ncc : nb=ncc-1
			else: nb=options.nbasis
			if options.refbias:
				try :
					os.unlink("tmp.hed")
					os.unlink("tmp.img")
				except: pass
				im=EMData()
				for c in range(ncc):
					im.readImage("iter.%d.hed"%(i-1),c)
					im*=options.refbias
					im.writeImage("tmp.hed",c)
				
				system("svdcmp tmp.hed basis.%d.hed n=%d"%(i,nb))
			else :system("svdcmp iter.%d.hed basis.%d.hed n=%d"%(i-1,i,nb))

			if options.debug : print "DBUG E"
			# Now make a 'fp' file containing the vectorization
			# of each aligned particle image
			if options.refbias : system("basisfilter ptcl.hed basis.%d.hed footprint=ptcl.fp bias=%s"%(i,rb))
			else : system("basisfilter ptcl.hed basis.%d.hed footprint=ptcl.fp"%(i))

			if options.debug : print "DBUG F"
			# Now classify the particles (k-means) based on their
			# footprints
			system("classes ptcl.fp %d maxiter=25"%(options.ninitcls))

			if options.debug : print "DBUG G"
			# now make the class-averages
			try:
				os.unlink("iter.%d.hed"%i)
				os.unlink("iter.%d.img"%i)
			except: pass
			for c in range(options.ninitcls):
				fpath="cls%04d.lst"%c
				if options.ctfcw!=None and i==options.iter-1: system("ctfavg2 %s iter.%d.ctfc.hed ctfcw=%s nolog comment=%s"%(fpath,i,options.ctfcw,fpath))
				#else : 
				system("proc2d cls%04d.lst iter.%d.hed average comment=%s"%(c,i,fpath))
		else:
			# non SVD based classification. Doesn't work as well
			system("classifykmeans.py stack=ptcl.hed classes=%d average=iter.%d nosingle"%(options.ninitcls,i))
			
		if options.debug : print "DBUG H"
		# now realign and sort the averages
		avgs=readImages("iter.%d.hed"%i,-1,-1)
		avgs=[ii for ii in avgs if ii.NImg()>=options.minptcl]	# remove classes with too few particles
		avgs=seriesalign3(avgs,options.aliref)
		try:
			os.unlink("iter.%d.hed"%i)
			os.unlink("iter.%d.img"%i)
		except: pass

		for im in avgs: 
#			if i<options.iter-2 : im.cmCenter()
			im.cmCenter()
			im.clearCTF()
			im.writeImage("iter.%d.hed"%i,-1)

	# final separation
	try:
		os.unlink("iter.final.hed")
		os.unlink("iter.final.img")
	except: pass
	
	if options.debug : print "DBUG I"
	# subclassify each class into ninitcls groups
	if (options.finalsep>1) :
		plog=[]
		ofs=0
		for i in range(options.ninitcls):
			try: os.mkdir("cls%04d"%i)
			except: pass
			os.chdir("cls%04d"%i)
			sdir="cls%04d"%i
			
			if (not options.nosvd) :
				if options.debug : print "DBUG J"
				# Now make a 'fp' file containing the vectorization
				# of each aligned particle image
				system("basisfilter ../cls%04d.lst ../basis.%d.hed footprint=ptcl.fp"%(i,options.iter-1))
				
				if options.debug : print "DBUG K"
				# Now classify the particles (k-means) based on their
				# footprints
				system("classes ptcl.fp %d"%(options.finalsep))
			
				if options.debug : print "DBUG L"
				# now make the class-averages
				for c in range(options.finalsep):
					if options.logptcl :
						try: f1=open("cls%04d.lst"%c,"r")
						except: 
							ofs+=options.finalsep-c 
							print "missing cls%04d.lst in cls%04d"%(c,i)
							break
						f1l=f1.readlines()
						f1.close()
						for l in f1l[1:] :
							l2=getline("../cls%04d.lst"%i,2+int(l.split()[0]))
							if not l2 or len(l2)<2 :
								print "Error on (%d) %s"%(i,l2)
							plog.append((int(l2.split()[0]),i*options.finalsep+c-ofs))
					fpath="cls%04d.lst"%c
					if options.ctfcw!=None : system("ctfavg2 %s ../iter.final.ctfc.hed ctfcw=%s nolog comment=%s"%(fpath,options.ctfcw,sdir+"/"+fpath))
					system("proc2d cls%04d.lst ../iter.final.hed average comment=%s"%(c,sdir+"/"+fpath))
			else:
				system("classifykmeans.py stack=../cls%04d.lst classes=%d average=../iter.final nosingle"%(i,options.finalsep))
				
			os.chdir("..")
		if options.debug : print "DBUG M"
		if options.logptcl:
			plog.sort()
			out=open("ptclassign.txt","w")
			for i in plog:
				out.write("%d\t%d\n"%(i[0],i[1]))
			out.close()
	else:
		system("cp iter.%d.hed iter.final.hed"%(options.iter-1))
		system("cp iter.%d.img iter.final.img"%(options.iter-1))
		if options.ctfcw!=None : 
			system("cp iter.%d.ctfc.hed iter.final.ctfc.hed"%(options.iter-1))
			system("cp iter.%d.ctfc.img iter.final.ctfc.img"%(options.iter-1))
			
	
	if options.debug : print "DBUG N"
	avgs=readImages("iter.final.hed",-1,-1)
	avgs=[ii for ii in avgs if ii.NImg()>=options.minptcl]	# remove classes with too few particles
	if not options.nofinalsort : avgs=seriesalign3(avgs,options.aliref)
	if options.debug : print "DBUG O"
	for im in avgs: 
		im.cmCenter()
		im.clearCTF()
		im.writeImage("iter.final.sort.hed",-1)

	if options.ctfcw!=None :
		avgs=readImages("iter.final.ctfc.hed",-1,-1)
		avgs=[ii for ii in avgs if ii.NImg()>=options.minptcl]	# remove classes with too few particles
		if not options.nofinalsort : avgs=seriesalign3(avgs,options.aliref)
		for im in avgs: 
			im.cmCenter()
			im.clearCTF()
			im.writeImage("iter.final.ctfc.sort.hed",-1)

		
	if options.debug : print "DBUG P"
	LOGend()

def seriesalign2(avgs):
	# ok, this little loop finds the mean center of mass position of all
	# aligned particles, then recenters using this mean
	orig=avgs[:]	# copy since seriesalign is destructive
	avgs2=seriesalign(avgs)
	xc,yc,nc=0,0,0
	for im in avgs2:
		im.cmCenter()
		xc+=im.Dx()
		yc+=im.Dy()
		nc+=1
	avgs2[0].setRAlign(0,0,0)
	avgs2[0].setTAlign(xc/nc,yc/nc,0)
	avgs2[0].rotateAndTranslate()	# the first image in avgs2 is the original, not a copy

	return seriesalign(orig)

def seriesalign3(avgs,ref=None):
	# ok, this little loop aligns and sorts the particles, then recenters each
	avgs2=seriesalign(avgs,ref)
	for im in avgs2:
		im.cmCenter()
		im.rotateAndTranslate()

	return avgs2

def seriesalign(avgs,ref=None) :
	avgs.sort(lambda x,y: cmp(y.NImg(),x.NImg()))
	
	# now align the averages in order by their mutual similarity
	if ref : avgsali=[ref]
	else: 
		avgsali=[avgs[0]]
		del avgs[0]
	while len(avgs)>0:
		bst=None
		bsti=-1
		bstcmp=1.0e10
		for i in range(len(avgs)):
			a1=avgs[i].copy(0)
			a1.meanShrink(2)
			a2=avgsali[-1].copy(0);
			a2.meanShrink(2)
			a3=a1.RTFAlign(a2,None,1,a2.xSize()/6)
			ali=avgs[i].copy(0)
			ali.setRAlign(a3.alt(),a3.az(),a3.phi())
			ali.setTAlign(a3.Dx()*2,a3.Dy()*2,a3.Dz()*2)
			ali.rotateAndTranslate()
			
#			ali=avgs[i].RTFAlign(avgsali[-1],None,1,avgsali[-1].xSize()/6)
			val=ali.lcmp(avgsali[-1])[0]
			if val<bstcmp :
				bstcmp=val
				bsti=i
				bst=ali
		if bst!=None : 
#			print bsti,bstcmp
			avgsali.append(bst)
			del avgs[bsti]
		else : print "Align failed"
	if ref : del avgsali[0]
	return avgsali
	
main()
