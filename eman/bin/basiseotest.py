#!/usr/bin/env python
###	basiseotest.py	Steven Ludtke	2/2002
### it attempts to maintain compatibility with python 1.5

#N basiseotest.py
#F This is the basisrefine equivalent to eotest
#T X
#1
#P [pad=<box size>] 
#P [proc=<nproc>] 
#P [ctfcw=<file>] 
#P [ctfc=<res>] 
#P [mask=<r>] 
#P [3dit=<iter>] 
#P [3dit2=<iter>] 
#P [sym=<symmetry>] 
#P [hard=<maxpr>] 
#P [automask=<r>,<thr>,<shells>]
#D This program is still highly experimental. Contact sludtke@bcm.tmc.edu if you wish to try it.

import os
import sys
import random
import time
import string
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
	print "svdeotest.py pad=<box size> [proc=<nproc>] [ctfcw=<file>] [ctfc=<res>] [mask=<r>] [3dit=<iter>] [3dit2=<iter>] [sym=<symmetry>] [hard=<maxpr>] [automask=<r>,<thr>,<shells>] "
	sys.exit(1)

ctfc=-1
refmask=0
automask=[]
processors=1
mask=-1
xfiles=[]
tdit=0
tdit2=0
sym="c1"
hard=25
pad=-1

for i in argv[1:] :
#	s=i.split('=')
	s=string.split(i,'=')
	if (s[0]=="proc") : processors=int(s[1])
	elif (s[0]=="ctfcw") : ctfc=s[1]
	elif (s[0]=='ctfc') : ctfc=float(s[1])
	elif (s[0]=='mask') : mask=int(s[1])
	elif (s[0]=='xfiles') : xfiles=string.split(s[1],',')
	elif (s[0]=='3dit') : tdit=int(s[1])
	elif (s[0]=='3dit2') : tdit2=int(s[1])
	elif (s[0]=='pad') : pad=int(s[1])
	elif (s[0]=='sym') : sym=s[1]
	elif (s[0]=='hard') : hard=float(s[1])
	elif (s[0]=='automask') : 
		automask=string.split(s[1],',')
		refmask=1
	else: error(ERR_EXIT,"Unknown argument "+i)

if (pad<1) : error(ERR_EXIT,"Warning: suggest setting a pad= value")

LOGbegin(argv)

logfile=open("refine.log","w")
logfile.write("Begin eotest at "+time.ctime(time.clock())+"\n")
logfile.close()

# average particles with ctf correction
for curit in range(1,9999):
	if (not os.access("classes.%d.hed"%curit,os.F_OK)): break
curit=curit-1

try:
	unlink("classes.%de.hed"%curit)
	unlink("classes.%de.img"%curit)
	unlink("classes.%do.hed"%curit)
	unlink("classes.%do.img"%curit)
except: pass
if (refmask) : rm="refmask"
else: rm=""

for ncls in range(9999):
	if (not os.access("cls%04d.lst"%ncls,os.F_OK)): break

for eo in ["even","odd"]:
	tf=tempfile()
	out=open(tf,"w")
	for i in range(ncls):
		if (type(ctfc)==type('')) : 
			out.write("ctfavg %s %s sffile=%s copyeuler ref0 %s copyrefs %s\n"%("cls%04d.lst"%i,"classes.%d%s.hed"%(curit,eo[0]),ctfc,rm,eo))
		else :
			out.write("ctfavg %s %s res=%f copyeuler %s ref0 copyrefs %s\n"%("cls%04d.lst"%i,"classes.%d%s.hed"%(curit,eo[0]),ctfc,rm,eo))
	out.close()
	system("echo class averages `date` >>refine.log")
	system("runpar proc="+str(processors)+" file="+tf)
	system("head -10  "+tf+" >>refine.log");
	os.unlink(tf)
	
	# make a 3D model
	system("echo make3d `date` >>refine.log")
	system("make3d classes.%d.hed out=threed.%d%s.mrc hard=%f sym=%s pad=%d"%(curit,curit,eo[0],hard,sym,pad))
	system("proc3d threed.%d%s.mrc threed.%d%s.mrc norm mask=%d"%(curit,eo[0],curit,eo[0],mask))
	
	#clean up 3d model
	system("echo clean3d `date` >>refine.log")
	if (tdit>0 or tdit2>0) :
		system("clean3d classes.%d%s.hed threed.%d%s.mrc proc=%d 3dit=%d 3dit2=%d sym=%s"%(curit,eo[0],curit,eo[0],processors,tdit,tdit2,sym))
	
	# mask and x-files
	if (len(xfiles)>=2) : system("volume threed.%d%s.mrc %f set=%f"%(curit,eo[0],float(xfiles[0]),float(xfiles[1])))
	if (len(automask)==3 and len(xfiles)>=2) : system("proc3d threed.%d%s.mrc threed.%d%s.mrc automask2=%d,%1.3f,%d"%(curit,eo[0],curit,eo[0],int(automask[0]),float(automask[1]),int(automask[2])))
	if (len(xfiles)>=2):
		system("proc3d threed.%d%s.mrc x%s.%d.mrc clip=%d,%d,%d"%(curit,eo[0],eo[0],curit,mask*2,mask*2,mask*2))
		system("volume x%s.%d.mrc %f set=%f"%(eo[0],curit,float(xfiles[0]),float(xfiles[1])))

#end of main loop

LOGend()

