#!/usr/bin/env python
# This will examine all of the particles in a particular class when classified by basis
# and generate some plots

# parms:  <iteration> <class #, range or 'ALL'>

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
quadc=""

if (len(argv)<3):
	error(ERR_EXIT,"Usage:\nsvdclsregen.py <iteration> <cls no. or ALL> [quadclass=<sffile>]")

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
	elif (s[0]=='quadclass') : quadc=s[1]
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
# B ->  0)'B',1) ptcl #,2) filespec,3) multi #,4) qual factor,5) defocus,6) class #,7) iteration,8) 2nd qual(opt)
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
	sys.exit(0)

# Loop over the classes
for i in keys:
	if (verbose>0) : print("Class %d:"%i)

	# first, we fit the quality factor as a function of defocus
	lst=ptcl[i]
	min=float(lst[0][5])
	max=min
	for j in lst:
		print "%f\t%f\t# %d"%(float(j[4]),float(j[8]),int(j[1]))
	
	if quadc!="" :
		out=[0,0,0,0]
		avlcmp=0
		avsvd=0
		avn=0
		minlc=1.0e24
		for j in lst:
			avlcmp=avlcmp+float(j[8])
			avsvd=avsvd+float(j[4])
			avn=avn+1
			if (float(j[8])<minlc) : minlc=float(j[8])

		avlcmp=(2*avlcmp/avn+minlc)/3
		avsvd=avsvd/avn

		for k in range(4):
			out[k]=open("a%d.lst"%k,"w")
			out[k].write("#LST\n")

		for j in lst:
			if float(j[8])<avlcmp : k=1
			else : k=0
			if float(j[4])>avsvd : k=k+2
			out[k].write("%s\t%s\t%1.5f\n"%(j[1],j[2],float(j[4])))

		for k in out:
			k.close()
			
		os.system("ctfavg a0.lst qual.hed sffile=%s"%quadc)
		os.system("ctfavg a1.lst qual.hed sffile=%s"%quadc)
		os.system("ctfavg a2.lst qual.hed sffile=%s"%quadc)
		os.system("ctfavg a3.lst qual.hed sffile=%s"%quadc)
		
