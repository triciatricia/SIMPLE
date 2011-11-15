#!/usr/bin/env python

#N basisclsregen.py
#F Regenerates cls files for a particular iteration produced with 'basisrefine'
#T LC
#1
#P <iteration>	The 'basisrefine' iteration to regenerate
#P <class #>	Specify a single class number, a range or 'ALL'
#P [clsgen]		Generate 'cls' files
#P [keep=<% to keep>]	Specify percentage of particles to include (0-100)
#P [verbose]	Verbose text output
#U basisclsregen.py 2 ALL clsgen keep=90
#D This program is used to regenerate the cls*.lst files for a particular iteration
#E of 'basisrefine' by extracting information from particle.log. Note that this will
#E NOT regenerate classes from iterations run with 'refine'. This program will
#E also allow a subset of the particles to be excluded based on the quality
#E factor determined during classification/alignment. 
#D The cls files contain the individual particles in each class, which are then averaged
#E to produce classes.?.hed.
#D Note that this is a more
#E intelligent routine than the one used in 'refine'. This routine actually
#E examines how the quality factor varies with defocus and takes this into
#E account when deciding which particles to exclude.

# parms:  <iteration> <class #, range or 'ALL'> [clsgen] [keep=<% to keep>] [verbose]

import os
import sys
import string
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

# compares the quality factor in two 'B' records
# This produces descending quality factors
def cmpitmqual(it0,it1):
	d=float(it1[4])-float(it0[4])
	if (d<0) : return -1
	if (d>0) : return 1
	return 0

# compares the quality factor in two 'B' records
# This produces ascending defocus
def cmpitmdf(it0,it1):
	d=float(it0[5])-float(it1[5])
	if (d<0) : return -1
	if (d>0) : return 1
	return 0


#### MAIN

clsgen=0
keep=1.0
verbose=0

if (len(argv)<3):
	error(ERR_EXIT,"Usage:\nsvdclsregen.py <iteration> <cls no. or ALL> [clsgen] [verbose] [keep=<% to use>]")

iter=int(argv[1])
if (argv[2]=='ALL'): cls2p=[-1,-1]
else :
	i=string.split(argv[2],'-')
	if (len(i)==1): i=string.split(argv[2],",")
	if (len(i)==1): cls2p=[int(i[0]),int(i[0])]
	else: cls2p=[int(i[0]),int(i[1])]

for i in argv[3:] :
	s=string.split(i,'=')
	if (s[0]=='clsgen') : clsgen=1
	elif (s[0]=='verbose') : verbose=1
	elif (s[0]=='keep') : keep=float(s[1])/100.0
	else: error(ERR_EXIT,"Unknown argument "+i)

fin=open("particle.log","r")

# locate the start of the last instance of the requested iteration
i=0
start=-1
while (1):
	ln=fin.readline()
	if (len(ln)<1) : break
	if (ln[0]=="V" and int(string.split(ln)[1])==iter): start=fin.tell(); startln=i+1
	i=i+1

if (start<0):
	print "Iteration not found"
	sys.exit()
	
print("Iteration %d starts at line %d\n"%(iter,startln))

# go back to the beginning of the iterations
fin.seek(start)

ln="  "
ptcl={}
i=0
# pull out particles in one of the specified classes and 
# make a dict of lists, 1 list/class
# B ->  'B',ptcl #,filespec,multi #,qual factor,defocus,class #,iteration,2nd qual(opt)
while (ln[0]!="V") :
	ln=fin.readline()
	lns=string.split(ln)
	if (len(lns)<6): break
	if (lns[0]=="B"):
		cls=int(lns[6])
		if (cls2p[0]==-1 or (cls>=cls2p[0] and cls<=cls2p[1])): 
			if (ptcl.has_key(cls)): ptcl[cls].append(lns)
			else: ptcl[cls]=[lns]
	i=i+1

# sort by class numbers
keys=ptcl.keys()
keys.sort()

#for i in keys:
#	print "%d\t%d"%(i,len(ptcl[i]))

if (len(keys)==0) :
	print "No classes to process\n"
	exit(0)

# Loop over the classes
for i in keys:
	if (verbose>0) : print("Class %d:"%i)

	# first, we fit the quality factor as a function of defocus
	lst=ptcl[i]
	min=float(lst[0][5])
	max=min
	for j in lst:
		if (float(j[5])>max) : max=float(j[5])
		if (float(j[5])<min) : min=float(j[5])
	
	# If there's only one defocus, there isn't any fitting to do
	if (min==max) :
		if (verbose>0) : print("only one defocus")
		out=open("cls%04d.lst"%i,"w")
		out.write("#LST\n%d\tproj.hed\n"%i)
		lst.sort(cmpitmqual)
		for j in lst[0:int(len(lst)*keep)-1] :
			out.write("%s\t%s\t%s\n"%(j[1],j[2],j[4]))
		out.close()
		continue		

	# here's the actual fit	
	S=0
	Sx=0
	Sy=0
	Sxx=0
	Sxy=0
	for j in lst:
		x=float(j[5])
		y=float(j[4])
		Sx=Sx+x
		Sy=Sy+y
		Sxx=Sxx+x*x
		Sxy=Sxy+x*y
		S=S+1

	dlt=S*Sxx-Sx*Sx
	if (dlt==0) : dlt=.0000001
	b=(Sxx*Sy-Sx*Sxy)/dlt		# intercept
	m=(S*Sxy-Sx*Sy)/dlt			# slope

	if (verbose) : print "\tslope=%1.4f\tint=%1.4f"%(m,b)

	# Modify quality factors so they are relative with respect to the fit
	for j in lst:
		j[4]=float(j[4])-(m*float(j[5])+b)

	lst.sort(cmpitmqual)
	
	out=open("cls%04d.lst"%i,"w")
	out.write("#LST\n%d\tproj.hed\t%f\n"%(i,Sy/S))
	lst.sort(cmpitmqual)
	for j in lst[0:int(len(lst)*keep)-1] :
		out.write("%s\t%s\t%1.5f\n"%(j[1],j[2],j[4]))
	out.close()
	
