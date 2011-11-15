#!/usr/bin/env python

# This program will split a lst file into even and odd halves

from sys import argv,exit

if len(argv)<2 : 
	print "eolst.py <lst file>"
	exit(1)
fsp=argv[1]
infile=open(fsp,"r")
l=infile.readline()
if l[:4]!="#LST" :
	print "Input must be a LST file"
	exit(1)

oute=open(fsp[:-4]+".even"+fsp[-4:],"w")
outo=open(fsp[:-4]+".odd"+fsp[-4:],"w")

l=infile.readline()
oute.write("#LST\n"+l)
outo.write("#LST\n"+l)

while(1):
	l=infile.readline()
	if len(l)==0: break
	n=int(l.split()[0])
	if n%2==0 : oute.write(l)
	else : outo.write(l)

infile.close()
oute.close()
outo.close()
