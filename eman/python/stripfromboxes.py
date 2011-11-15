#!/usr/bin/env python

# This script is designed to remove a subset of the boxed out particles from a set of '.box' files. It requires
# a 'LST' file containing a list of particle numbers referenced to a second LST files containing the entire
# set of input particles. The entire set of input particles must refer to a set of images with corresponding '.box'
# files which will then be modified to produce a new set of '.box' files without the particles referenced in the
# first 'LST' file.

# Typical usage:
# lstcat.py all.lst ../*hdf
# lstfast.pyt all.lst
# refine2d.py all.lst --iter=5 ...
# foreach i (cls*lst)
# proc2d $i avgs.hed average
# end
# Manually go through avgs.hed and pick 'bad' averages, then run this program on
# the corresponding cls files.


# usage:
# stripfromboxes.py <all ptcl lst> <cls file> <cls file> ...

from sys import argv
from sys import exit
import os
from pprint import pprint

fin=open(argv[1],"r")
allptcl=fin.readlines()
fin.close()
allptcl=[(i.split()[1],int(i.split()[0])) for i in allptcl if i[0]!='#']		# strips and reformats a LST file

# allbad will now contain all box references to be removed
allbad=[]
for i in argv[2:]:
	fin=open(i,"r")
	bad=fin.readlines()
	fin.close()
	bad=[allptcl[int(i.split()[0])] for i in bad if i[0]!='#']		# strips and reformats a LST file
	allbad+=bad
#pprint(allbad)

# now turn this into a dictionary split by referenced file
allbadsplit={}
for i in allbad:
	try: allbadsplit[i[0]].append(i[1])
	except: allbadsplit[i[0]]=[i[1]]

#pprint(allbadsplit)

# ok, now we go through the dictionary keys and fix each box file
totp=0
totpg=0
for i in allbadsplit.keys():
	try: fin=open(i[:-4]+".box","r")
	except:
		print "Error opening ",i[:-4]+".box"
		exit(1)
	fout=open(i[:-4]+".2.box","w")
	
	lines=fin.readlines()
	bad=allbadsplit[i]
	for j,k in enumerate(lines):
		if j not in bad : 
			fout.write(k)
			totpg+=1
	
	fin.close()
	fout.close()
	totp+=len(lines)

print "Kept %d of %d particles (%d bad)"%(totpg,totp,len(allbad))