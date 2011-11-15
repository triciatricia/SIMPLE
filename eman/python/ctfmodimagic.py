#!/usr/bin/env python

# This program will modify ctf parameters in an image file

from sys import argv
from EMAN import *
import os

a=EMData()

n=fileCount(argv[1])[0]
fin=file("start.hed","rb")
fout=file("start.new.hed","w+b")
a=fin.read()
fin.seek(0)

for i in range(n):
	h=fin.read(1024)
	v=[float(j) for j in h[118:190].strip('\0').split()]
	v[1]=75.0
	v=["%1.2f"%j for j in v]
	n=" ".join(v)+"\0\0\0\0\0\0\0\0"
	fout.write(a[i*1024:i*1024+118])
	fout.write(n)
	fout.write(a[i*1024+118+len(n):(i+1)*1024])
	print n

fin.close()
fout.close()
os.rename("start.hed","start.old.hed")
os.rename("start.new.hed","start.hed")
