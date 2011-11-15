#!/usr/bin/env python

# morphpdb2mrc.py  08/29/2004   Steven Ludtke
# This will use density morphing techniques to gradually morph the
# atomic coordinates in a PDB file to match an electron density.
# The PDB shouldn't be TOO different than the density map

from EMAN import *

from math import *
from os import system
import os
import sys
import string
import time

try:
	from optparse import OptionParser
except:
	from optik import OptionParser

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
	usage = """Usage: %prog [options] input.pdb input.mrc
	
"""

	parser = OptionParser(usage=usage,version=EMANVERSION)

	parser.add_option("--apix", "-A", type="float", help="A/voxel", default=1.0)
	parser.add_option("--res", "-R", type="float", help="Resolution in A, equivalent to Gaussian lowpass with 1/e width at 1/res",default=2.8)
	parser.add_option("--iter","-I", type="int",help="Number of iterations to run",default=4)
	parser.add_option("--nseg","-N", type="int",help="Number of segments for morph mapping",default=24)
	parser.add_option("--sym","-S",type="string",help="Symmetry operator for initial segmentation",default="c1")
	parser.add_option("--thr", "-T", type="float", help="Isosurface threshold for original map",default=-1.0)
	parser.add_option("--e2","-E",action="store_true",help="Indiciates availability of EMAN2 programs",default=False)
	
	(options, args) = parser.parse_args()
	if len(args)<2 : parser.error("Input and output files required")
	
	v1=EMData()
	v1.readImage(args[1],0,1)
	dim=(v1.xSize(),v1.ySize(),v1.zSize())
	box=max(dim)
		
	LOGbegin(sys.argv)
	
	system("cp %s morph.00.pdb"%args[0])
#	print "Segment original map"
#	sysprint("segment3d %s morph.orig.seg.mrc nseg=%d thr=%0.4f vector=morph.orig.vec.txt apix=%0.3f sym=%s >>morph.out"%(args[1],options.nseg,options.thr,options.apix,options.sym))
	
		
	for it in range(options.iter):
		print "pdb2mrc iteration ",it
		if (options.e2) : sysprint("e2pdb2mrc.py --apix=%0.3f --res=%0.3f --box=%0d morph.%02d.pdb morph.%02d.mrc >>morph.out"%(options.apix,options.res,box,it,it))
		else : 
			sysprint("pdb2mrc morph.%02d.pdb morph.%02d.mrc apix=%0.2f res=%0.2f box=%0d >>morph.out"%(it,it,options.apix,options.apix*2.0,box))
			sysprint("proc3d morph.%02d.mrc morph.%02d.mrc apix=%0.2f lp=%0.2f >>morph.out"%(it,it,options.apix,sqrt(options.res**2-(options.apix*2.0)**2)))
					
		print "segment3d A"
		sysprint("segment3d morph.%02d.mrc morph.tmp.seg.mrc nseg=%d thr=-1.0 vector=morph.%02d.vec.txt apix=%0.3f sym=%s >>morph.out"%(it,options.nseg,it+1,options.apix,options.sym))
		
		print "segment3d B"
		sysprint("segment3d %s morph.tmp.seg.mrc maxit=2 thr=%0.3f vector=morph.%02d.vec2.txt apix=%0.3f morph=morph.%02d.vec.txt chimeraout=morph.%02d.cmm sym=%s>>morph.out"%(args[1],options.thr,it+1,options.apix,it+1,it+1,options.sym))

		print "morph PDB"
		sysprint("procpdb.py morph.%02d.pdb tmp.pdb animorph=3,%0.3f,morph.%02d.vec2.txt >>morph.out"%(it,options.apix,it+1))
		
		sysprint("mv tmp.01.pdb morph.%02d.pdb"%(it+1))
		
	it=options.iter
	if (options.e2) : sysprint("e2pdb2mrc.py --apix=%0.3f --res=%0.3f --box=%0d morph.%02d.pdb morph.%02d.mrc >>morph.out"%(options.apix,options.res,box,it,it))
	else : 
		sysprint("pdb2mrc morph.%02d.pdb morph.%02d.mrc apix=%0.2f res=%0.2f box=%0d >>morph.out"%(it,it,options.apix,options.apix*2.0,box))
		sysprint("proc3d morph.%02d.mrc morph.%02d.mrc apix=%0.2f lp=%0.2f >>morph.out"%(it,it,options.apix,sqrt(options.res**2-(options.apix*2.0)**2)))
	
	
	
if __name__ == "__main__":
    main()
