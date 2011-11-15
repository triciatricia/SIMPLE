#!/usr/bin/env python
# This little script will read .hed (imagic) or .lst format image
# files and give info about the CTF parameters of the contained images
import os

# check for a lst file
infile=open("start.hed","r")
first=infile.read(4)
heds=[]
if (first=="#LST") :
	# if lst file, then extract the unique filenames
	lines=infile.readlines()
	for l in lines:
		ll=l.split()
		if (len(ll)<2 or ll[1] in heds): continue
		heds.append(ll[1])
else :
	heds=["start.hed"]
infile.close()

# now we read the actual file headers and make a list of unique
# CTF parameter strings. The CTF string is the key in a dictionary
# with an integer, which is a count
ctfs={}
for h in heds:
	infile=open(h,"r")
	d=infile.read()
	infile.close()

	for i in range(len(d)/1024):
		txt=d[1024*i+116:1024*i+196]	# the title from the imagic header
		ctf=txt[3:]
		count=ctfs.get(ctf,0)
		ctfs[ctf]=count+1

# print some results
for k in ctfs.keys():
	s=k.split()
	print "%6d images  df=%1.2f  B=%1.1f"%(int(ctfs[k]),float(s[0]),float(s[1]))
