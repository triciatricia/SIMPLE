#!/usr/bin/env python

import os
import sys
import string
import EMAN
from sys import argv


if (len(argv)<3) :
        print "Usage: PDBorigin.py <PDB> <MRC>"
        sys.exit(1)

trans=0
if (len(argv)>3):
	opts=argv[3].split('=')
	if opts[0]=="trans":
		trans=float(opts[1])

target=EMAN.EMData()
target.readImage(argv[2],-1)

dx=target.getXorigin()+trans
dy=target.getYorigin()+trans
dz=target.getZorigin()+trans
print dz,dy,dz



cmd0="procpdb.py %s trans-%s trans=%f,%f,%f"%(argv[1],argv[1],dx,dy,dz)
os.system(cmd0)
