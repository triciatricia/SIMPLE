#!/usr/bin/env python

# This program reads out most of the MRC header and writes a modified version back
# doesn't take any parameters, just a list of filenames to operate on

from struct import pack,unpack
from sys import argv

# Header items
#  0 - nx,ny,nz
#  3 - mode
#  4 - nxstart,nystart,nzstart
#  7 - mx,my,mz
# 10 - xlen,ylen,zlen
# 13 - alpha,beta,gamma
# 16 - mapc,mapr,maps
# 19 - amin,amax,amean
# 22 - ispg,nsymbt
MRCN=["nx","ny","nz","mode","nxstart","nystart","nzstart","mx","my","mz","xlen","ylen","zlen",
	"alpha","beta","gamma","mapc","mapr","maps","amin","amax","amean","ispg","nsymbt"]
MRCH="iiiiiiiiiiffffffiiifffii"

# for each file, do:
for i in argv[1:]:
	# read and upack the header
	f=open(i,"r+")
	s=f.read(len(MRCH)*4)
	hed=list(unpack(MRCH,s))

	# display the current header
	print "\nCurrent header (%s):"%i
	for j,n in enumerate(MRCN): print n,hed[j]

	# change any desired values
	hed[4]=int(hed[0]/2)
	hed[5]=int(hed[1]/2)
	hed[6]=int(hed[2]/2)

	# write the new header
	s=pack(MRCH,*hed)
	f.seek(0)
	f.write(s)
	f.close()
