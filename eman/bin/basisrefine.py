#!/usr/bin/env python
###	basisrefine.py	Steven Ludtke	2/2002
### This program will do a refinement using the new basis based techniques
### it attempts to maintain compatibility with python 1.5

#N basisrefine.py
#F This is a highly experimental refinement procedure using a novel alignment/classification procedure
#T X
#1
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
#P [clsbylcmp=<filt r>] 
#P [jacobi] 
#P [phicomp] 
#P [align4[=<topphi>]] 
#P [snrmult=<val>] 
#P [setsf=<lp>[,<hp>[,<sffile>]]
#P [geodc]
#P [keep=<% to keep>]
#D This program is still highly experimental. Contact sludtke@bcm.tmc.edu if you wish to try it.

import os
import sys
import random
import time
import string
import EMAN
from os import system
from os import unlink
from sys import argv

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
	print "basisrefine.py <iterations> pad=<box size> mask=<r> [ang=<dang>] [proc=<nproc>] [ctfcw=<file>] [ctfc=<res>] [nbasis=<n>] [xfiles=<A/pix>,<mass>,<ali to>] [3dit=<iter>] [3dit2=<iter>] [sym=<symmetry>] [hard=<maxpr>] [automask=<r>,<thr>,<shells>] [nbasiscls=<num>] [clsbylcmp=<filt r>] [jacobi] [phicomp] [align4[=<topphi>]] [snrmult=<val>] [keep=<% to keep>]"
	sys.exit(1)

iterations=int(argv[1])
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
lcmptoo=" "
nbasis=-1
nbasiscls=-1
pad=-1
maxtrans=-1
jacobi=""
align4=-1.0
snrmult=1.0
keep=100
dcmp=0
setsflp=0
setsfhp=0
setsffile=None

for i in argv[2:] :
#	s=i.split('=')
	s=string.split(i,'=')
	if (s[0]=='ang') : ang=float(s[1])
	elif (s[0]=="proc") : processors=int(s[1])
	elif (s[0]=="ctfcw") : 
		ctfc=s[1]
		if (setsffile==None) : setsffile=s[1]
	elif (s[0]=='ctfc') : ctfc=float(s[1])
	elif (s[0]=='mask') : mask=int(s[1])
	elif (s[0]=='nbasis') : nbasis=int(s[1])
	elif (s[0]=='nbasiscls') : nbasiscls=int(s[1])
	elif (s[0]=='xfiles') : xfiles=string.split(s[1],',')
	elif (s[0]=='maxtrans') : maxtrans=int(s[1])
	elif (s[0]=='3dit') : tdit=int(s[1])
	elif (s[0]=='3dit2') : tdit2=int(s[1])
	elif (s[0]=='lcmptoo') : 
		if (len(s)>1) : lcmptoo="lcmptoo="+s[1]
		else: lcmptoo="lcmptoo"
	elif (s[0]=='snrmult') : snrmult=float(s[1])
	elif (s[0]=='pad') : pad=int(s[1])
	elif (s[0]=='sym') : sym=s[1]
	elif (s[0]=='hard') : hard=float(s[1])
	elif (s[0]=='jacobi') : jacobi="jacobi"
	elif (s[0]=='clsbylcmp') : 
		lcmp="clsbylcmp"
		if (float(s[1])>0): lcmp="clsbylcmp=%s"%s[1]
	elif (s[0]=='phicomp') : phicomp="phicomp"
	elif (s[0]=='setsf') :
		t=s[1].split(',')
		setsflp=float(t[0])
		if (len(t)>1) : setsfhp=float(t[1])
		if (len(t)>2) : setsffile=t[2]
	elif (s[0]=='keep') : keep=float(s[1])
	elif (s[0]=='geodc') : dcmp=1
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
if (pad<1) : error(ERR_EXIT,"Warning: suggest setting a pad= value")
if (mask<2) : error(ERR_EXIT,"mask=<r> is a required parameter")
if (keep<1) : error (ERR_EXIT,"Keep values <1 are not allowed, 1-100 only")


LOGbegin(argv)

curit=1
while (curit<iterations) :
	if (not os.access("threed."+str(curit)+"a.mrc",os.F_OK)): break
	curit=curit+1
	
print "Starting at iteration ",str(curit),":"

logfile=open("refine.log","w")
logfile.write("Begin refine at "+time.ctime(time.clock())+"\n")
logfile.close()

while (curit<=iterations):
	log=open("particle.log","a")
	log.write("V\t%d\t%d\n"%(curit,time.time()))
	log.close()

	# read micrograph file list
	inp=open("start.list","r")
	files=inp.readlines()
	if (len(files)<1): error(ERR_EXIT,"Need at least 1 file in start.list")
	
	# project3d
	try:
		unlink("proj.hed")
		unlink("proj.img")
	except: pass
	tf=tempfile()
	out=open(tf,"w")
	for i in range(processors):
		out.write("project3d threed.%da.mrc prop=%f sym=%s frac=%d/%d %s logit=%d\n"%(curit-1,ang,sym,i,processors,phicomp,curit))
	out.close()
	system("echo project3d `date` >>refine.log")
	system("runpar proc="+str(processors)+" file="+tf)
	system("head -10  "+tf+" >>refine.log");
	unlink(tf);

	# alignment if requested
	if (align4>=0) :
		system("project3d threed.%da.mrc 4point=%f out=ref4.hed sym=%s"%(curit-1,align4,sym))
		if (dcmp==0) : system("svdcmp ref4.hed ref4.basis.hed mask=%d jacobi"%(mask))
		else : system("geodcmp ref4.hed ref4.basis.hed mask=%d"%(mask))
		system("basisfilter proj.hed ref4.basis.hed nbasis=4 poweralign precen saveali=proj.hed basis0+ verbose=2")

	# apply CTF to projections
	tf=tempfile()
	out=open(tf,"w")
	for i in range(len(files)):
		try:
			unlink("proj.%02d.hed"%i)
			unlink("proj.%02d.img"%i)
		except: pass
		if (i==0) : q=""
		else : q="quiet"
		out.write("applyctf proj.hed proj.%02d.hed parmimg=%s applyctf %s\n"%(i,string.strip(files[i]),q))
	out.close()
	system("echo applyctf `date` >>refine.log")
	system("runpar proc="+str(processors)+" file="+tf)
	system("head -10  "+tf+" >>refine.log");
	os.unlink(tf)
	
	# svd on modified projections
	tf=tempfile()
	out=open(tf,"w")
	for i in range(len(files)):
		try:
			unlink("basis.%02d.hed"%i)
			unlink("basis.%02d.img"%i)
		except: pass
		if (i==0) : q=""
		else : q="quiet"
		if (dcmp==0) : out.write("svdcmp proj.%02d.hed basis.%02d.hed mask=%d %s %s altwt\n"%(i,i,mask,jacobi,q))
		else : out.write("geodcmp proj.%02d.hed basis.%02d.hed mask=%d n=%d\n"%(i,i,mask,max(nbasis,nbasiscls)))
	out.close()
	system("echo dcmp `date` >>refine.log")
	system("runpar proc="+str(processors)+" file="+tf)
	system("head -10  "+tf+" >>refine.log");
	os.unlink(tf)
	
	system("rm cls*lst")
	system("proc2d proj.hed cls mraprep")
	
	# align and classify particles
	splitfile=processors/len(files)
	if (splitfile<1) : splitfile=3
	else: splitfile=3*splitfile
	
	tf=tempfile()
	out=open(tf,"w")
	for i in range(len(files)):
		for j in range(splitfile):
			if (i==0 and j==0) : q=""
			else : q="quiet"
#			out.write("basisfilter %s %s frac=%d/%d nbasis=%d nbasiscls=%d %s classify=%s poweralign=%d saveali=%s basis0+ verbose=1 logit=%d mask=%d %s\n"%\
#(string.strip(files[i]),"basis.%02d.hed"%i,j,splitfile,nbasis,nbasiscls,lcmp,"proj.%02d.hed"%i,maxtrans,"align.%02d.hed"%i,curit,mask,q))
			out.write("classesbybasis %s %s %s noisecomp mask=%d frac=%d/%d nbasis=%d logit=%d maxshift=%d %s %s verbose=1 saveali=%s savealiparm\n"%\
(string.strip(files[i]),"proj.%02d.hed"%i,"basis.%02d.hed"%i,mask,j,splitfile,nbasis,curit,maxtrans,q,lcmptoo,"align.%02d.hed"%i))
	out.close()
	system("echo classify `date` >>refine.log")
	system("head -10  "+tf+" >>refine.log");
	c="runpar proc="+str(processors)+" file="+tf
	print c
	try: os.unlink("aliparm.txt");
	except: pass
	system(c)
	os.unlink(tf)

	# Now we need to do the actual rotations/translations of the particle data
	apf=open("aliparm.txt","r")
	aliparm=apf.readlines()
	apf.close()
	for i in range(len(aliparm)):
		aliparm[i]=aliparm[i].split()
		aliparm[i][1]=int(aliparm[i][1])
		aliparm[i][3]=float(aliparm[i][3])
		aliparm[i][4]=float(aliparm[i][4])
		aliparm[i][5]=float(aliparm[i][5])

	aliparm.sort()

	d=EMAN.EMData()
	for im in aliparm:
		d.readImage(im[2],im[1])
		d.setRAlign(im[3]);
		d.setTAlign(im[4],im[5],0);
		d.rotateAndTranslate()
		d.writeImage(im[0],im[1])


	# if keep specified, apply a filter using particle.log
	# and regenerate the cls* files
	if (keep!=100) :
		system("basisclsregen.py %d ALL keep=%1.1f"%(curit,keep))
	
	# average particles with ctf correction
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
		if (i==0) : q=""
		else : q="quiet"

		if (type(ctfc)==type('')) : 
			out.write("ctfavg %s %s sffile=%s copyeuler ref0 %s copyrefs snrmult=%f %s\n"%("cls%04d.lst"%i,"classes.%d.hed"%curit,ctfc,rm,snrmult,q))
		else :
			out.write("ctfavg %s %s res=%f copyeuler %s ref0 copyrefs snrmult=%f %s\n"%("cls%04d.lst"%i,"classes.%d.hed"%curit,ctfc,rm,snrmult,q))
	out.close()
	system("echo class averages `date` >>refine.log")
	system("runpar proc="+str(processors)+" file="+tf)
	system("head -10  "+tf+" >>refine.log");
	os.unlink(tf)
	
	# make a 3D model
	system("echo make3d `date` >>refine.log")
	system("make3d classes.%d.hed out=threed.%d.mrc hard=%f sym=%s pad=%d mask=%d"%(curit,curit,hard,sym,pad,mask))
	system("proc3d threed.%d.mrc threed.%da.mrc norm mask=%d"%(curit,curit,mask))

	# setsf
	if (setsffile and setsflp) :
		c="proc3d threed.%da.mrc threed.%da.mrc setsf=%s apix=%1.4f lp=%1.4f"%(curit,curit,setsffile,xfiles[0],setsflp)
		if (setsfhp>0) : c=c+" hp=%1.4f"%setsfhp
		system(c)
	
	#clean up 3d model
	system("echo clean3d `date` >>refine.log")
	if (tdit>0 or tdit2>0) :
		system("clean3d classes.%d.hed threed.%da.mrc proc=%d 3dit=%d 3dit2=%d sym=%s"%(curit,curit,processors,tdit,tdit2,sym))
	
	# mask and x-files
#	system("cp threed.%d.mrc threed.%da.mrc"%(curit,curit))
	if (len(xfiles)>=2) : system("volume threed.%da.mrc %f set=%f"%(curit,float(xfiles[0]),float(xfiles[1])))
	if (len(automask)==3 and len(xfiles)>=2) : system("proc3d threed.%da.mrc threed.%da.mrc automask2=%d,%1.3f,%d"%(curit,curit,int(automask[0]),float(automask[1]),int(automask[2])))
	if (len(xfiles)>=2):
		system("proc3d threed.%da.mrc x.%d.mrc clip=%d,%d,%d"%(curit,curit,mask*2,mask*2,mask*2))
		if (len(xfiles)>2 and int(xfiles[2])<curit) :
			system("align3d x.%d.mrc x.%d.mrc x.%d.mrc"%(int(xfiles[2]),curit,curit))
		system("volume x.%d.mrc %f set=%f"%(curit,float(xfiles[0]),float(xfiles[1])))

	#end of main loop
	curit=curit+1

LOGend()

