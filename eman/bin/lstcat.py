#!/usr/bin/env python
###	lstcat.py	Steven Ludtke	4/2002

#N lstcat.py
#F Generates a 'lst' file from a set of input image stacks
#T LM
#1
#P <output>	Output file, MUST BE SPECIFIED FIRST
#P <input>...	Input file(s), may be images of any type
#U lstcat.py start.lst orig.1.hed orig.2.hed orig.3.hed
#D This is a simple program which will generate a 'lst' file which
#E concatenates a set of image files. A 'lst' file is a text file
#E containing pointers to images in other files. This allows you
#E to generate files with subsets of other files without making
#E an actual copy of the data. This mechanism is used by 'refine'
#E in generating the 'cls' files, for example. The 'lst' files are
#E text files that can be edited by the user. EMAN will treat them
#E as if they actually contained the referenced images.

### usage 'lstcat <output> <input1> <input2> ...'

import os
import sys
import random
import time
import string
from os import system
from os import unlink
from sys import argv

print "NOTE: in most cases, running lstfast.py on your LST files is a good idea"

out=open(argv[1],"w")
out.write("#LST\n")

for i in argv[2:] :
	l=os.popen("iminfo %s"%i,"r")
	lns=l.readlines()
	l.close()
	ptcls=int((string.split(lns[2]))[2])
	
	for j in range(ptcls):
		out.write("%d\t%s\n"%(int(j),i))
	
out.close()
