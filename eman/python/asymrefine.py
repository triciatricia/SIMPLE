#!/usr/bin/env python

# $Id: asymrefine.py,v 1.1 2006/09/01 13:53:35 wjiang Exp $

# by Wen Jiang <jiang12@purdue.edu>, 2006-1-17


import os, sys, math, time
try:
	from optparse import OptionParser
except:
	from optik import OptionParser
import EMAN

def main():
	(options, rawimage) = parse_command_line()

	pid = EMAN.LOGbegin(sys.argv)
	EMAN.LOGInfile(pid, rawimage)

	imagenum = EMAN.fileCount(rawimage)[0]
	for iter in range(options.iters):
		projfile = "proj.%d.hdf" % (iter+1)
		cmplstfile = "cmp.%d.lst" % (iter+1)
		ortlstfile = "ort.%d.lst" % (iter+1)
		mapfile = "threed.%da.mrc" % (iter)
		mapfile2 = "threed.%da.mrc" % (iter+1)
		if options.eotest:
			mapfile2e = "threed.%da.e.mrc" % (iter+1)
			mapfile2o = "threed.%da.o.mrc" % (iter+1)
			subsetlste = "ort.%d.e.lst"  % (iter+1)
			subsetlsto = "ort.%d.o.lst"  % (iter+1)
			fscfile = "fsc.%d.txt" % (iter+1)
		else:
			mapfile2e = None
			mapfile2o = None
			subsetlste = None
			subsetlsto = None
			fscfile = None

		if not os.path.exists(mapfile):
			print "ERROR: cannot find 3D map \"%s\"" % (mapfile)
			sys.exit()
		else:
			d = EMAN.EMData()
			d.readImage(rawimage,0,1)	# read header
			rnx = d.xSize()
			rny = d.ySize()
			d.readImage(mapfile,-1,1)	# read header
			mnx = d.xSize()
			mny = d.ySize()
			mnz = d.zSize()
			if rnx!=mnx or rny!=mny:
				print "ERROR: raw images (%s) sizes (%dx%d) are different from the 3D map (%s) sizes (%dx%dx%d)" % 	(rawimage, rnx, rny, mapfile, mnx, mny, mnz)
				sys.exit()
		
		if not os.path.exists(cmplstfile):
			runpar_file = "runpar.%d.ortcen.txt" % (iter+1)
			n = imagenum/options.batchsize
			if imagenum%n: n+=1
			if n<options.cpus: 
				n=options.cpus
				options.batchsize=imagenum/n+1
				if options.batchsize==1: 
					n = imagenum
					options.batchsize=1
			
			num_tries = 0
			max_tries = 3
			while not os.path.exists(ortlstfile) and num_tries < max_tries:
				runparfp = open(runpar_file, "w")
				num_tries += 1
				todo_num = 0
				sublstfiles = []
				cmpsublstfiles = []
				for i in range(n):
					cmplstfile_tmp = "cmp.%d.%d.lst" % (iter+1, i)
					ortlstfile_tmp = "ort.%d.%d.lst" % (iter+1, i)
					startNum = i * options.batchsize
					endNum = (i+1) * options.batchsize
					if startNum>=imagenum: break
					if endNum>imagenum: endNum=imagenum
					sublstfiles.append(ortlstfile_tmp)
					cmpsublstfiles.append(cmplstfile_tmp)
					if os.path.exists(ortlstfile_tmp):	continue
					else: todo_num += 1
					
					cmd  = "symrelax.py %s %s " % (rawimage, mapfile)
					if options.sffile: cmd += "--sf=%s " % ( options.sffile )
					if options.phasecorrected: cmd += "--phasecorrected "
					cmd += "--verbose=%d " % (options.verbose )
					cmd += "--mask=%d " % (options.mask)
					cmd += "--startSym=%s " % (options.startSym)
					cmd += "--endSym=%s " % (options.endSym)
					cmd += "--first=%d --last=%d " % (startNum, endNum)
					cmd += "--shrink=%d " % (options.shrink)
					cmd += "--ortlstfile=%s " % (ortlstfile_tmp)
					cmd += "--score=%s " % (options.scorefunc)
					if options.saveprojection:
						cmd += "--projection=%s " % (projfile)
						cmd += "--cmplstfile=%s " % (cmplstfile_tmp)					
					if i: cmd += "--nocmdlog "
						
					if i == 0: print cmd
					
					runparfp.write("%s\n" % (cmd))
				runparfp.close()
				if todo_num:
					cmd = "runpar proc=%d,%d file=%s" % (options.cpus, options.cpus, runpar_file)
					print cmd
					os.system(cmd)
			
				#now merge all sublst file
				# first test if all jobs are done properly
				done = 1
				for lstfile_tmp in sublstfiles:
					if not os.path.exists(lstfile_tmp): done = 0
				
				if done:
					EMAN.merge_lstfiles(sublstfiles, ortlstfile, delete_lstfiles = 1)
					# pool the cmplstfiles
					if options.saveprojection:
						EMAN.merge_lstfiles(cmpsublstfiles, cmplstfile, delete_lstfiles = 1)

			if not os.path.exists(ortlstfile) or (os.path.exists(ortlstfile) and os.path.getsize(ortlstfile)<=5):
				print "ERROR: raw image new orientation results lst file \"%s\" is not generated properly" % (ortlstfile)
				sys.exit()
	
		if not os.path.exists(mapfile2):
			reconstruction_by_make3d(ortlstfile, mapfile2, options=options, mapfile2e=mapfile2e, mapfile2o=mapfile2o, fscfile=fscfile)
			if not (os.path.exists(mapfile2) and os.path.getsize(mapfile2)):
				print "ERROR: 3D map \"%s\" is not generated properly" % (mapfile2)
				sys.exit()
		
	EMAN.LOGend()

def reconstruction_by_make3d(imagefile, mapfile, options, mapfile2e, mapfile2o, fscfile):
	cmd_prefix = EMAN.pre_mpirun(mpilib = options.mpi, mpi_nodefile = options.mpi_nodefile, single_job_per_node = 1)
	cmd_3drec = "%s `which make3d` %s hard=90 lowmem sym=%s mode=2 apix=%g pad=%d usecenter iter=1" % \
			(cmd_prefix, imagefile, options.endSym, options.apix, options.pad)
	if options.sffile: 
		cmd_3drec += " wiener3d=%s" % ( options.sffile )
		if not options.phasecorrected: cmd_3drec += " flipphase"
	cmd = "%s out=%s" % (cmd_3drec, mapfile)
	if options.eotest and mapfile2e and mapfile2o:
		cmd += "\n%s subset=0/2 out=%s" % (cmd_3drec, mapfile2e)
		cmd += "\n%s subset=1/2 out=%s" % (cmd_3drec, mapfile2o)
	print cmd
	if options.mpi:
		os.system(cmd)
	else:
		runpar_file = "runpar.make3d"
		runparfp = open(runpar_file,"w")
		runparfp.write("%s\n" % (cmd))
		runparfp.close()
		cmd = "runpar proc=%d,%d file=%s nofs" % (options.cpus, options.cpus, runpar_file)
		print cmd
		os.system(cmd)
	if not (os.path.exists(mapfile) and os.path.getsize(mapfile)):
		print "ERROR: 3D map \"%s\" is not generated properly" % (mapfile)
		sys.exit()
	if mapfile2e and mapfile2o and os.path.exists(mapfile2e) and os.path.exists(mapfile2o):
		cmd = "proc3d %s %s fsc=%s" % (mapfile2e,mapfile2o,fscfile)
		print cmd
		os.system(cmd)
	EMAN.post_mpirun(mpilib = options.mpi)

def parse_command_line():
	usage="Usage: %prog <raw image filename> [options]"
	parser = OptionParser(usage=usage)
	parser.add_option("--mask",dest="mask",type="int",help="mask radius. default to half image size", default=0)
	parser.add_option("--pad",dest="pad",type="int",help="padded to this size during 3D reconstruction. default to no padding", default=0)
	parser.add_option("--cpus",dest="cpus",type="int",help="number of CPUs. default to 1", default=1)
	parser.add_option("--iters",dest="iters",type="int",help="number of iterations. default to 1", default=1)
	parser.add_option("--shrink",dest="shrink",type="float",help="shrink factor, can only be 1.5 or >1 integer", default=1)
	parser.add_option("--apix",dest="apix",type="float",help="angstrom/pixel for the image", default=0)
	parser.add_option("--verbose",dest="verbose",type="int",help="verbose level [0-2]. default to 1", default=1)
	parser.add_option("--sf",dest="sffile",type="string",help="structural factor ile name", default="")
	parser.add_option("--phasecorrected",dest="phasecorrected",action="store_true",help="if the particle images already phase flipped. default to 0", default=0)
	parser.add_option("--startSym",dest="startSym",type="string",help="starting symmetry, default to icos", default="icos")
	parser.add_option("--endSym",dest="endSym",type="string",help="ending symmetry, default to c1", default="c1")
	parser.add_option("--score",metavar="['ncccmp', 'lcmp', 'pcmp', 'fsccmp', 'wfsccmp']",dest="scorefunc",type="choice",choices=['ncccmp', 'lcmp', 'pcmp', 'fsccmp', 'wfsccmp'], help="scoring function to use. default to \"fsccmp\"", default="fsccmp")
	parser.add_option("--eotest",dest="eotest",action="store_true",help="do split data reconstruction, disabled by default", default=0)
	parser.add_option("--saveprojection",dest="saveprojection",action="store_true",help="save projections for comparision, disabled by default", default=0)
	parser.add_option("--batchsize",dest="batchsize",type="int",help="number of particles per runpar job for CCML search. default to 50",default=50)
	parser.add_option("--mpi",dest="mpi",type="choice",choices=["none","mpich1","mpich2","lam"],help='which mpi program is used for the 3D reconstruction program. choices are: ["none","mpich1","mpich2","lam"]. default to "none"', default="none")
	parser.add_option("--mpi_nodefile",dest="mpi_nodefile",type="string",help="which file has the node list for mpi jobs", default="")

	(options, rawimage)=parser.parse_args()

	if len(rawimage) !=1:
		parser.print_help()
		sys.exit(-1)
	
	if options.sffile and not os.path.exists(options.sffile):
		print "ERROR: sffile \"%s\" does not exist" % (options.sffile)
		sys.exit()

	if options.mask<=0 or options.apix<=0 or options.pad!=0:
		d = EMAN.EMData()
		d.readImage(rawimage[0], 0)	# header only
		if options.mask<=0:
			imagesize = d.xSize();
			options.mask=imagesize/2
		if options.apix<=0:
			options.apix=d.getCTF()[10]
		if options.pad <=0:
			options.pad = d.ySize()
	
	if options.mpi == "none": options.mpi = ""
	if options.mpi_nodefile and not os.path.exists(options.mpi_nodefile):
		print "--mpi_nodefile=%s does not exists" % (options.mpi_nodefile)
		sys.exit(-2)

	return (options, rawimage[0])
	
if __name__== "__main__":
	main()

