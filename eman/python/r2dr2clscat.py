#!/usr/bin/env python
# This is a rather tricky program. When you run refine2d.py, each of the final
# class-averages has a 'Name' identifying which cls file it came from. If you then 
# run a multirefine (or somesuch) on the final class-averages from the refine2d
# you can use this script to extract the original particles that were used to
# build the class-averages in a cls file in the final multirefine, but it must 
# be run from the directory where refine2d was run

# r2dr2clscat.py multi/1/cls0000.lst multi/r1/start.hed all.hed

# if the 3rd argument is omitted, then particles copied will be 2-d aligned
# particles from ptcl.hed. 3rd argument allows you to use the original unaligned particles
 
from EMAN import *
from sys import argv

nimg=fileCount(argv[1])[0]

m=EMData()
for i in range(1,nimg):
	m.readImage(argv[1],i)
	print "%s\t%s"%(argv[1],m.Name())
	if len(argv)<4 : os.system("proc2d %s %s"%(m.Name(),argv[2]))
	else :
		ncpy=fileCount(m.Name())
		lst=file("m.Name()","r").readlines()
		for j in lst[1:]:
			m.readImage(argv[3],int(j.split()[0]))

