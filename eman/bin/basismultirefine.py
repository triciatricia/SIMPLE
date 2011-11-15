#!/usr/bin/env python
###	basismultirefine.py	Steven Ludtke	3/30/2002
### This program will do a refinement using the new basis based techniques
### it attempts to maintain compatibility with python 1.5
### 
### This version does multiple refinement very much like multirefine

#N basismultirefine.py
#F This is a highly experimental refinement procedure using a novel alignment/classification procedure
#T X
#1
#P <groups> 
#P <iterations>
#P [pad=<box size>] 
#P [ang=<dang>] 
#P [proc=<nproc>] 
#P [ctfcw=<file>] 
#P [ctfc=<res>] 
#P [mask=<r>] 
#P [nbasis=<n>] 
#P [xfiles=<A/pix>,<mass>,<ali to>] 
#P [3dit=<iter>] 
#P [3dit2=<iter>] 
#P [sym=<symmetry>] 
#P [hard=<maxpr>] 
#P [automask=<r>,<thr>,<shells>] 
#P [nbasiscls=<num>] 
#P [clsbylcmp] 
#P [jacobi] 
#P [phicomp] 
#P [align4[=<topphi>]] 
#P [snrmult=<val>] 
#P [keep=<% to keep>]
#D This program is still highly experimental. Contact sludtke@bcm.tmc.edu if you wish to try it.


import os
import sys
import random
import time
import string
from os import system
from os import unlink
from sys import argv
from shutil import copyfile

ERR_EXIT=1
ERR_CRIT=2
ERR_WARN=3
ERR_INFO=4
def error(type,msg):
	if (type==ERR_CRIT) : print "Critical Error: ",msg
	if (type==ERR_WARN) : print "Warning: ",msg
	if (type==ERR_INFO) : print msg
	if (type==ERR_EXIT) :
		print "Fatal Error: ",msg
		sys.exit(1)

def tempfile():
	fsp='.'
	while (os.access(fsp,os.F_OK)) :
		fsp="temp"+str(random.randrange(9999))
	return fsp

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
	

#### MAIN

if (len(argv)<2) :
	print "basismultirefine.py <groups> <iterations> pad=<box size> [ang=<dang>] [proc=<nproc>] [ctfcw=<file>] [ctfc=<res>] [mask=<r>] [nbasis=<n>] [xfiles=<res>,<mass>,<ali to>] [3dit=<iter>] [3dit2=<iter>] [sym=<symmetry>] [hard=<maxpr>] [automask=<r>,<thr>,<shells>] [nbasiscls=<num>] [clsbylcmp] [jacobi] [stage=<n>] [phicomp] [align4[=<topphi>]] [snrmult=<val>] [keep=<% to keep>]"
	sys.exit(1)

groups=int(argv[1])
iterations=int(argv[2])
if (iterations<1) :
	error(ERR_EXIT,"# iterations must be >0")

ctfc=-1
refmask=0
automask=[]
processors=1
ang=10
mask=-1
xfiles=[]
tdit=0
tdit2=0
sym="c1"
hard=25
lcmp=" "
phicomp=" "
nbasis=-1
nbasiscls=-1
pad=-1
maxtrans=-1
jacobi=""
align4=-1.0
snrmult=1.0
keep=100
stage=0

for i in argv[3:] :
#	s=i.split('=')
	s=string.split(i,'=')
	if (s[0]=='ang') : ang=float(s[1])
	elif (s[0]=="proc") : processors=int(s[1])
	elif (s[0]=="ctfcw") : ctfc=s[1]
	elif (s[0]=='ctfc') : ctfc=float(s[1])
	elif (s[0]=='mask') : mask=int(s[1])
	elif (s[0]=='nbasis') : nbasis=int(s[1])
	elif (s[0]=='nbasiscls') : nbasiscls=int(s[1])
	elif (s[0]=='xfiles') : xfiles=string.split(s[1],',')
	elif (s[0]=='maxtrans') : maxtrans=int(s[1])
	elif (s[0]=='3dit') : tdit=int(s[1])
	elif (s[0]=='3dit2') : tdit2=int(s[1])
	elif (s[0]=='snrmult') : snrmult=float(s[1])
	elif (s[0]=='pad') : pad=int(s[1])
	elif (s[0]=='sym') : sym=s[1]
	elif (s[0]=='hard') : hard=float(s[1])
	elif (s[0]=='jacobi') : jacobi="jacobi"
	elif (s[0]=='clsbylcmp') : lcmp="clsbylcmp"
	elif (s[0]=='phicomp') : phicomp="phicomp"
	elif (s[0]=='stage') : stage=float(s[1])
	elif (s[0]=='keep') : keep=float(s[1])
	elif (s[0]=='align4') :
		if (len(s)==2) : align4=float(s[1])
		else : align4=0
		if (align4<0) : error(ERR_EXIT,"0 <= align4 <360")
	elif (s[0]=='automask') : 
		automask=string.split(s[1],',')
		refmask=1
	else: error(ERR_EXIT,"Unknown argument "+i)

if (nbasis<1):
	print "nbasis not specified, defaulting to 20"
	nbasis=20
if (nbasiscls<1): nbasiscls=nbasis
if (pad<1) : error(ERR_WARN,"Warning: suggest setting a pad= value")
if (keep<1) : error (ERR_EXIT,"Keep values <1 are not allowed, 1-100 only")

LOGbegin(argv)

curit=1
while (curit<iterations) :
	if (not os.access("0/threed."+str(curit)+"a.mrc",os.F_OK)): break
	curit=curit+1
	
print "Starting at iteration ",str(curit),":"

logfile=open("refine.log","w")
logfile.write("Begin multirefine at "+time.ctime(time.clock())+"\n")
logfile.close()

if (type(ctfc)==type('')) : 
	for i in range(groups):
		copyfile(ctfc,"%0d/%s"%(i,ctfc));

while (curit<=iterations):
	if (stage<=1) :
		for grp in range(groups):
			log=open("%0d/particle.log"%grp,"a")
			log.write("V\t%d\t%d\n"%(curit,time.time()))
			log.close()

		# read micrograph file list
		inp=open("start.list","r")
		files=inp.readlines()
		if (len(files)<1): error(ERR_EXIT,"Need at least 1 file in start.list")
	
		# project3d, generate for each group, then join groups into 1 file
		try:
			unlink("proj.hed")
			unlink("proj.img")
		except: pass
		for grp in range(groups):
			try:
				unlink("%0d/proj.hed"%grp)
				unlink("%0d/proj.img"%grp)
			except: pass
				
			tf=tempfile()
			out=open(tf,"w")
			for i in range(processors):
				out.write("cd %d; project3d threed.%da.mrc prop=%f sym=%s frac=%d/%d %s logit=%d\n"%(grp,curit-1,ang,sym,i,processors,phicomp,curit))
			out.close()
			system("echo project3d %d `date` >>refine.log"%grp)
			os.chdir(str(grp))
			system("runpar proc="+str(processors)+" file="+tf)
			system("head -10  "+tf+" >>refine.log");
			os.chdir("..")
			unlink(tf);
			system("proc2d %d/proj.hed proj.hed"%grp)
	
		# alignment if requested
		if (align4>=0) :
			system("project3d 0/threed.%da.mrc 4point=%f out=ref4.hed sym=%s"%(curit-1,align4,sym))
			system("svdcmp ref4.hed ref4.basis.hed mask=%d jacobi"%(mask))
			system("basisfilter proj.hed ref4.basis.hed nbasis=4 poweralign precen saveali=proj.hed verbose=2")

	if (stage<=2):
		# apply CTF to projections
		tf=tempfile()
		out=open(tf,"w")
		for i in range(len(files)):
			try:
				unlink("proj.%02d.hed"%i)
				unlink("proj.%02d.img"%i)
			except: pass
			out.write("applyctf proj.hed proj.%02d.hed parmimg=%s applyctf\n"%(i,string.strip(files[i])));
		out.close()
		system("echo applyctf `date` >>refine.log")
		system("runpar proc="+str(processors)+" file="+tf)
		system("head -10  "+tf+" >>refine.log");
		os.unlink(tf)
		
	if (stage<=3) :
		# svd on modified projections
		tf=tempfile()
		out=open(tf,"w")
		for i in range(len(files)):
			try:
				unlink("basis.%02d.hed"%i)
				unlink("basis.%02d.img"%i)
			except: pass
			out.write("svdcmp proj.%02d.hed basis.%02d.hed mask=%d %s\n"%(i,i,mask,jacobi));
		out.close()
		system("echo svdcmp `date` >>refine.log")
		system("runpar proc="+str(processors)+" file="+tf)
		system("head -10  "+tf+" >>refine.log");
		os.unlink(tf)
		
		
	if (stage<=4) :
		# align and classify particles the 'groups' option will split into different groups
		splitfile=processors/len(files)
		if (splitfile<1) : splitfile=3
		else: splitfile=3*splitfile
		
		for grp in range(groups):
			system("rm %0d/cls*lst"%grp)
			system("cd %0d; proc2d proj.hed cls mraprep"%grp)
	
		tf=tempfile()
		out=open(tf,"w")
		for i in range(len(files)):
			for j in range(splitfile):
				if (i==0 and j==0) : quiet=""
				else : quiet="quiet"
				out.write("basisfilter %s %s frac=%d/%d nbasis=%d nbasiscls=%d %s classify=%s poweralign=%d saveali=%s verbose=1 logit=%d mask=%d groups=%d %s\n"%\
	(string.strip(files[i]),"basis.%02d.hed"%i,j,splitfile,nbasis,nbasiscls,lcmp,"proj.%02d.hed"%i,maxtrans,"align.%02d.hed"%i,curit,mask,groups,quiet))
		out.close()
		system("echo classify `date` >>refine.log")
		system("head -10  "+tf+" >>refine.log");
		system("runpar proc="+str(processors)+" file="+tf)
		os.unlink(tf)
	
	if (stage<=5) :
		# if keep specified, apply a filter using particle.log
		# and regenerate the cls* files
		if (keep!=100) :
			for grp in range(groups):
				system("cd %0d; basisclsregen.py %d ALL keep=%1.1f"%(grp,curit,keep))
		
	if (stage<=6) :
		# average particles with ctf correction
		for grp in range(groups):
			os.chdir(str(grp))
			for ncls in range(9999):
				if (not os.access("cls%04d.lst"%ncls,os.F_OK)): break
		
			try:
				unlink("classes.%d.hed"%curit)
				unlink("classes.%d.img"%curit)
			except: pass
			tf=tempfile()
			out=open(tf,"w")
			if (refmask) : rm="refmask"
			else: rm="mask=%d"%mask
	
			for i in range(ncls):
				if (type(ctfc)==type('')) : 
					out.write("ctfavg %s %s sffile=%s copyeuler ref0 %s copyrefs snrmult=%f\n"%("cls%04d.lst"%i,"classes.%d.hed"%curit,ctfc,rm,snrmult))
				else :
					out.write("ctfavg %s %s res=%f copyeuler %s ref0 copyrefs snrmult=%f\n"%("cls%04d.lst"%i,"classes.%d.hed"%curit,ctfc,rm,snrmult))
			out.close()
			system("echo class averages `date` >>refine.log")
			system("runpar proc="+str(processors)+" file="+tf)
			system("head -10  "+tf+" >>refine.log");
			os.unlink(tf)
			os.chdir("..")
		
	if (stage<=7) :
		# make a 3D model
		for grp in range(groups):
			os.chdir(str(grp))
			system("echo make3d `date` >>refine.log")
			system("make3d classes.%d.hed out=threed.%d.mrc hard=%f sym=%s pad=%d mask=%d"%(curit,curit,hard,sym,pad,mask))
			system("proc3d threed.%d.mrc threed.%d.mrc norm mask=%d"%(curit,curit,mask))
			os.chdir("..")
		
	if (stage<=8) :
		for grp in range(groups):
			#clean up 3d model
			os.chdir(str(grp))
			system("echo clean3d `date` >>refine.log")
			if (tdit>0 or tdit2>0) :
				system("clean3d classes.%d.hed threed.%d.mrc proc=%d 3dit=%d 3dit2=%d sym=%s"%(curit,curit,processors,tdit,tdit2,sym))
		
			# mask and x-files
			system("cp threed.%d.mrc threed.%da.mrc"%(curit,curit))
			if (len(xfiles)>=2) : system("volume threed.%da.mrc %f set=%f"%(curit,float(xfiles[0]),float(xfiles[1])))
			if (len(automask)==3 and len(xfiles)>=2) : system("proc3d threed.%da.mrc threed.%da.mrc automask2=%d,%1.3f,%d"%(curit,curit,int(automask[0]),float(automask[1]),int(automask[2])))
			if (len(xfiles)>=2):
				system("proc3d threed.%da.mrc x.%d.mrc clip=%d,%d,%d"%(curit,curit,mask*2,mask*2,mask*2))
				if (len(xfiles)>2 and int(xfiles[2])<curit) :
					system("align3d x.%d.mrc x.%d.mrc x.%d.mrc"%(int(xfiles[2]),curit,curit))
				system("volume x.%d.mrc %f set=%f"%(curit,float(xfiles[0]),float(xfiles[1])))
	
			os.chdir("..")
	
	#end of main loop
	stage=0
	curit=curit+1

LOGend()

