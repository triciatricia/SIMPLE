#!/usr/bin/env python

import sys
import glob
import os
import EMAN
import random
try:
	from optparse import OptionParser
except:
	from optik import OptionParser

def check_files(sf,particles):
	needed_files = ["start.hed","start.img","proj.hed","proj.img"]
	if len(particles)<1:
		print "Variance must be calculated in a directory with all the cls????.lst files still intact"
		sys.exit(-1)
	if sf == None:
		print "Structure Factor File must be specified using the --structure-factor option"
		sys.exit(-1)
	needed_files.append(sf)
	for i in needed_files:
		#print i
		if os.path.exists(i): 
			pass
		else:
			print "File:  %s must exist"%(i)
			sys.exit(-1)
	return needed_files


def calc_variance(args):
	cmd = "mapvariance %s %s model_*/threed.mrc"%(args[0],args[1])
	os.system(cmd)

def get_particles():
	particles=[]
	try:
		for cls in glob.glob("cls????.lst"):
			classid = cls[3:7]
			lines = open(cls).readlines();
			for l in lines[2:]:
			#	tokens=l.split()
				particles.append((l, classid))
	except:
	 	print "Error:: This command must be run in the same directory as a previous reconstrution, with all the cls????.lst files still present"
		raise
		sys.exit(-1)
	#print particles
	return particles

# this part has been modified to use bootstrap instead of jacknife
# will sample a pool as the same size as the original dataset
def random_sample(num_maps, sf, particles):
	#subset_num = int (len(particles)*fraction)
	num_part = int(len(particles))
	num_proj = EMAN.fileCount("proj.img")[0]
	
	for i in range(num_maps):
		#print "Model %d" % (i)
		#random.shuffle(particles)
		directory = "model_%d" % (i)
		os.mkdir(directory)
		os.chdir(directory)
		for files in ["start.hed","proj.hed"]:
		#up_dir_file = "../"+file
			cmd="lstcat.py "+files+" ../"+files
			os.system(cmd)
			os.link(files, files[:-3]+"img")
		os.link("../"+sf,sf)
		for c in range(num_proj):
			clsfile="cls%04d.lst" % (c)
			fp = file(clsfile,"w")
			fp.write("#LST\n%d\tproj.hed\n" % (c) )
			fp.close()
		#for j in range(subset_num):
		for j in range(num_part):
			#p = int(particles[j][0])	
			#c = int(particles[j][1])
			partt=random.choice(particles)
			p = partt[0]
			c = int(partt[1])
			#print "Index %d/%d/%d\tParticle %d -> Class %d" % (j, subset_num, len(particles), p, c)
			clsfile="cls%04d.lst" % (c)
			fp = open(clsfile,"a")
			fp.write(p)
			fp.close()
		os.chdir("..")


def build_models(options):
	scriptfile = "buildmodel.runpar"
	sfp=file(scriptfile,"w")
	
	for m in glob.glob("model_*"):
		if os.path.exists( "%s/threed.mrc" % (m) ): continue
		#cmd="cd %s; make3d classes.hed out=threed.mrc mask=%s hard=%s sym=%s mode=%s pad=%s\n" % (m,options.mask,options.hard,options.sym,options.mode,options.pad)
		cmd="make3d %s/classes.hed out=%s/threed.mrc mask=%s hard=%s sym=%s mode=%s pad=%s\n" % (m,m,options.mask,options.hard,options.sym,options.mode,options.pad)
		print cmd
		sfp.write(cmd)
	sfp.close()

	for m in glob.glob("model_*"):
		if os.path.exists( "%s/classes.img" % (m) ): continue
		# here I set a hard value proc=16 minimum to avoid network communication problem when doing classalignall
		cmd = "cd %s; classalignall ref1 finalref saverefs keep=%s %s proc=16,%d mask=%s imask=-1 logit=1 ctfcw=%s" % (m, options.keep,options.iterations,options.cpu,options.mask,options.sf)
		#cmd = "cd %s; classalignall ref1 finalref saverefs keep=%s %s proc=16,%d mask=%s imask=-1 logit=1 phase" % (m, options.keep,options.iterations,options.cpu,options.mask)
		if options.phase:
			cmd = cmd + " phase"		
		if options.dfilt:
			cmd = cmd + " dfilt"
		if options.refine:
			cmd = cmd + " refine"
		print cmd
		os.system(cmd)

	cmd="runpar proc=%d,%d file=%s" % (options.cpu, options.cpu, scriptfile)
	print cmd
	os.system(cmd)

def parse_command_line():
	usage="Usage: %prog <Mean Reconstruction Map> <Variance Map> [options]"
	parser = OptionParser(usage=usage)
	# calculateMapVar options
	parser.add_option("--num-maps",dest="num_maps",type="int",help="Number of reconstructions to use for calculating statistics, (100 is default)",default=100)
	#parser.add_option("--fraction",dest="fraction",type="float",help="Fraction of particles from each class average to include in each reconstruction, (0.5 is default)",default=0.5)

	# make3d options
	parser.add_option("--cpu", dest="cpu", type="int", help="number of CPUs to use",default=1)
	parser.add_option("--sym", dest="sym", type="string", help="symmetry to impose in the reconstruction [Required]" )
	parser.add_option("--mask", dest="mask", type="int", help="real space mask radius in pixels [Required]")
	parser.add_option("--hard", dest="hard", type="int",help="A phase residual indicating how well the class averages must match the model to be included, (25 is default)",default=25)
	parser.add_option("--mode", dest="mode", type="int",help="Specifies the interpolation size, (2 is default)", default=2)
	parser.add_option("--pad", dest="pad", type="int",help="To reduce Fourier artifacts, the model is typically padded by ~25% [Required]")

	#classalignall options
	parser.add_option("--keep", dest="keep", type="float",help="The threshold value for keeping images. Standard deviation multiplier (0.8 is default)",default=0.8)
	parser.add_option("--iterations", dest="iterations", type="int", help="Number of iterative loops in classalign2",default=3)
	parser.add_option("--refine", dest="refine", action="store_true", default=False, help="This enables 1/2 pixel accuracy in alignment, slows alignment down quite a bit.")
	parser.add_option("--dfilt", dest="dfilt", action="store_true", default=False, help="Experimental, should not use with option phase")
	parser.add_option("--phase", dest="phase", action="store_true", default=True, help="Like phasecls in EMAN refine command")
	#common options
	parser.add_option("--structure-factor",dest="sf", type="string", help="1-D Structure Factor File (Intensity vs Spatial Frequency). Should be put in the same directory of all the cls files. [Required]")
	
	(option, args)=parser.parse_args()
	#print args
	if len(args) == 0:
		args = ['Mean.mrc','Sigma.mrc']
	elif len(args) == 1:
		args = ['Mean.mrc',args[0]]
	elif len(args) > 2:
		print "Warning :: Ignoring the following arguments "
		for a in args[2:]:
			print a
		args = [args[0], args[1]]
		
	#print args

	for key in parser.option_list[1:]:  #this omits the -h/--help option
		eval_string = "option.%s"%(key.dest)
		value = eval(eval_string)
		if value == None:
			print "The option %s must be specified on the command line"%(key)
			sys.exit(-1)
		else:
			pass
			#print "Accepting option %s :: %s "%(key,value)

	
	return (option,args)

def main():
	(options,args) =  parse_command_line()
	particles = get_particles()
	needed_files = check_files(options.sf,particles)
	random_sample(options.num_maps,options.sf,particles)
	build_models(options)
	calc_variance(args)
	

if __name__== "__main__":
	main()
