#!/usr/bin/env python

# morphpdb2mrc.py  08/29/2004   Steven Ludtke
# This will use density morphing techniques to gradually morph 
# one MRC file into another

from EMAN import *

try:
	from optparse import OptionParser
except:
	from optik import OptionParser
from math import *
from os import system
import os
import sys
import string

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
	usage = """Usage: %prog [options] inputstart.mrc inputend.mrc <inputend2.mrc>
	
"""

	parser = OptionParser(usage=usage,version=EMANVERSION)

	parser.add_option("--steps", type="int",help="Number of steps in the animation sequence",default=8)
	parser.add_option("--nseg","-N", type="int",help="Number of segments for morph mapping",default=24)
	parser.add_option("--sym","-S",type="string",help="Symmetry operator for initial segmentation",default="c1")
	parser.add_option("--thr", "-T", type="float", help="Isosurface threshold for original map, negative values are sigma multipliers",default=-1.0)
	
	(options, args) = parser.parse_args()
	if len(args)<2 : parser.error("Input and output files required")
	
	v1=EMData()
	v1.readImage(args[0],0,1)
	dim=(v1.xSize(),v1.ySize(),v1.zSize())
	box=max(dim)
	apix=v1.Pixel()
		
	LOGbegin(sys.argv)
	
	if (len(args)==2) :
		system("segment3d %s morph.tmp.mrc nseg=%0d thr=%0.4f vector=morph.vec1.txt sym=%s apix=%0.3f"%(args[0],options.nseg,options.thr,options.sym,apix))
		system("segment3d %s morph.tmp.mrc morph=morph.vec1.txt thr=%0.4f sym=%s apix=%0.3f vector=morph.vec2.txt chimeraout=morph.vec.cmm"%(args[1],options.thr,options.sym,apix))
		system("proc3d %s %s animorph=%0d,morph.vec2.txt"%(args[0],args[1],options.steps))
	else :
		system("segment3d %s morph.tmp.mrc nseg=%0d thr=%0.4f vector=morph.vec1.txt sym=%s apix=%0.3f"%(args[0],options.nseg,options.thr,options.sym,apix))
		system("segment3d %s morph.tmp.mrc morph=morph.vec1.txt thr=%0.4f sym=%s apix=%0.3f vector=morph.vec2.txt chimeraout=morph.vec12.cmm"%(args[1],options.thr,options.sym,apix))
		system("proc3d %s %s animorph=%0d,morph.vec2.txt"%(args[0],args[1],options.steps))
		system("segment3d %s morph.tmp.mrc nseg=%0d thr=%0.4f vector=morph.vec3.txt sym=%s apix=%0.3f"%(args[1],options.nseg,options.thr,options.sym,apix))
		system("segment3d %s morph.tmp.mrc morph=morph.vec3.txt thr=%0.4f sym=%s apix=%0.3f vector=morph.vec4.txt chimeraout=morph.vec34.cmm"%(args[2],options.thr,options.sym,apix))
		system("proc3d %s %s animorph=%0d,morph.vec2.txt,%0d"%(args[1],args[2],options.steps,options.steps))
		
		
	LOGend()
	
if __name__ == "__main__":
    main()
