#!/usr/bin/env python
###	foldhunter.py	Matthew Baker 06/2003

#N foldhunter.py
#F Python script for quickly running foldhunterP in chimera
#T LM
#1
#P <target>	Input mrc file
#P <probe>	Input pdb/mrc file
#P <res=>	resolution
#P <apix=>	a/pix
#D Runs foldhunter

import os
import sys
import string
import EMAN
import commands
import math
import re
import shutil
from math import *
from sys import argv

apix=1.0
res=8
thresh=0
binerize=0
norm=0
centerpdb=1
shrink=2
depth=1
pixels=10
keep=20
pdb=0
angle=0
rad=0
frags=[]
chains=[]
refchain=0
restrictRange="none"
userda1=0
userda2=0

if (len(argv)<2) :
	print "Usage:\nfoldhunter.py <target mrc file> <probe file> <res=> <apix=>\n"
	print "Expert options <thresh=> <binerize=> <shrink=> <depth=> <pixels> <keep=> <angle=> <rad=> <frag='[(x,y),(A,B)]'> <refinechain=> <nocenter> <norm>"
	sys.exit(1)

target=EMAN.EMData()
target.readImage(argv[1],-1)
target_size=target.xSize()
temp_target=argv[1]
shutil.copy(temp_target, 'target.mrc')

probe=argv[2]
p=probe.split('.')
probeName=str(p[0])
probeExt=str(p[-1])

for i in argv[3:] :
        s=i.split('=')
        if (s[0]=='res') : 
		res=float(s[1])
        elif (s[0]=='apix') : 
		apix=float(s[1])
	elif (s[0]=='thresh') : 
		thresh=float(s[1])
	elif (s[0]=='binarize') : 
		binerize=float(s[1])
	elif (s[0]=='shrink') : 
		shrink=int(s[1])
	elif (s[0]=='depth') : 
		depth=int(s[1])
	elif (s[0]=='pixels') : 
		pixels=int(s[1])
	elif (s[0]=='keep') : 
		keep=int(s[1])
	elif (s[0]=='nocenter') : 
		centerpdb=0
	elif (s[0]=='angle'):
		angle=float(s[1])
	elif (s[0]=='rad') :
		rad=float(s[1])
	elif (s[0]=='frag') :
		frags.append(eval(s[1]))
	elif (s[0]=='refinechain'):
		refchain=str(s[1])
	elif (s[0]=='norm') : 
		norm=1
        elif (s[0]=='restrict'):
		restrictRange=str(s[1])	
	elif (s[0]=='userda1') :
		userda1=float(s[1])
	elif (s[0]=='userda2') :
		userda2=float(s[1])
	else:
                print("Unknown argument "+i)
                exit(1)
		
checksize=target_size%shrink
if (checksize!=0):
	target_size=int(target_size+checksize)
	cmd0="proc3d target.mrc target.mrc clip=%d,%d,%d"%(target_size,target_size,target_size)
	os.system(cmd0)


########Transform PDB file and generate MRC file
if (probeExt=='pdb' or probeExt=='ent'):
	if (centerpdb==1):
		shutil.copy(probe, 'probe.pdb')
		print("Centering PDB file")
		cmd1="procpdb.py probe.pdb probe.pdb centeratoms"
		os.system(cmd1)

	cmd2="pdb2mrc probe.pdb probe.mrc apix=%f res=%f box=%d"%(apix, res, target_size)
	os.system(cmd2)
	cmd3="proc3d probe.mrc probe.mrc norm"
	os.system(cmd3)
else:
	shutil.copy(probe, 'probe.mrc')

########Filter and Scale MRC files
if (thresh!=0 & binerize==0):
	print("Tresholding target map")
	cmd4="proc3d target.mrc target.mrc rfilt=0,%f"%(thresh)
	os.system(cmd4)
if (binerize!=0):
	print("Binerizing target map")
	cmd5="proc3d target target.mrc rfilt=2,%f"%(binerize)
	os.system(cmd5)

print("Shrinking maps")
cmd6="proc3d target.mrc target-shrink.mrc shrink=%f"%(shrink)
os.system(cmd6)
cmd7="proc3d probe.mrc probe-shrink.mrc shrink=%f"%(shrink)
os.system(cmd7)

########Run foldhunterP
print("Running foldhunterP with shrunk maps")
if userda1==0:
	da=((180*res)/(math.pi*(target_size/(2*shrink))))/1.5
else:
	da=userda1
	
if restrictRange=="none":
	cmd8="foldhunterP target-shrink.mrc probe-shrink.mrc fh-shrink.mrc log=log-fh-shrink.txt da=%f keep=%d"%(da,keep)
#	cmd8="foldhunterP target-shrink.mrc probe-shrink.mrc fh-shrink.mrc da=%f keep=%d"%(da,keep)
else:
	cmd8="foldhunterP target-shrink.mrc probe-shrink.mrc fh-shrink.mrc log=log-fh-shrink.txt da=%f keep=%d range=%s"%(da,keep,restrictRange)

os.system(cmd8)

########Parse output and repeat foldhunterP
file1=open('log-fh-shrink.txt', "r")
lines1=file1.readlines()
file1.close()
pattern=re.compile(r"Solution\s(?P<solnum>\d+)\:\trotation\s=\s\(\s(?P<rotx>-?\d+\.?\d*)\s,\s(?P<rotz1>-?\d+\.?\d*)\s,\s(?P<rotz2>-?\d+\.?\d*)\s\)\ttranslation\s=\s\(\s(?P<dx>-?\d+\.?\d*)\s,\s(?P<dy>-?\d+\.?\d*)\s,\s(?P<dz>-?\d+\.?\d*)\s\)")

fh1 = {}
for line in lines1:
	ps=pattern.search(line)
	if ps:
		fh1[int(ps.group('solnum'))]=[float(ps.group('rotx')),float(ps.group('rotz1')),float(ps.group('rotz2')),float(ps.group('dx')),float(ps.group('dy')),float(ps.group('dz'))]

print("Running foldhunterP on original maps")
count=0
children=0
while ((count < depth) and (children < keep)):
	if angle==0:
		angle_range=((180*res)/(math.pi*(target_size/2)))
		if (angle_range > 20):
			angle_range=20
	else:
		angle_range=angle
	if rad==0:
		sphere_radius=0.25*target_size
	else:
		sphere_radius=rad
		
	if userda2==0:
		da=1
	else:
		da=userda2
	x1=shrink*fh1[children][3]
	y1=shrink*fh1[children][4]
	z1=shrink*fh1[children][5]

	dist = []
	solution=0
	while (solution <= children):
		x2=shrink*fh1[solution][3]
		y2=shrink*fh1[solution][4]
		z2=shrink*fh1[solution][5]
		if (solution!=children):
			distance=math.sqrt((x1-x2)**2+(y1-y2)**2+(z1-z2)**2)
		else:
			distance=10000
		dist.append(distance)
		print "%d verse %d: %f"%(children,solution,dist[solution])
		alt=fh1[solution][0]
		az=fh1[solution][1]
		phi=fh1[solution][2]

		solution=solution+1
	pixel_distance=min(dist)
	
	if ((pixel_distance >= pixels) or (count==0)):
		logfile="log-fh-%d.txt"%(children)
		cmd9="foldhunterP target.mrc probe.mrc fh-%d.mrc log=%s da=%f startangle=%f,%f,%f range=%f sphere_region=%f,%f,%f,%f"%(children,logfile,da,alt,az,phi,angle_range,x1,y1,z1,sphere_radius)
		os.system(cmd9)
		num=count
		count=count+1
		
		########Transform PDB
		if (probeExt=='pdb' or probeExt=='ent'):
			print("Transforming PDB")
			file2=open(logfile, "r")
			lines2=file2.readlines()
			file2.close()
			fh2 = {}
			for line in lines2:
				ps=pattern.search(line)
				if ps:
					fh2[int(ps.group('solnum'))]=[float(ps.group('rotx')),float(ps.group('rotz1')),float(ps.group('rotz2')),float(ps.group('dx')),float(ps.group('dy')),float(ps.group('dz'))]

			fhOut="fh-%d-%s"%(num,probe)
			cmd10="procpdb.py probe.pdb r-%s rot=%f,%f,%f"%(probe,fh2[0][0],fh2[0][1],fh2[0][2])
			os.system(cmd10)
			cmd11="procpdb.py r-%s %s apix=%f trans=%f,%f,%f"%(probe,fhOut,apix,fh2[0][3],fh2[0][4],fh2[0][5])
			os.system(cmd11)
	children=children+1
if len(frags):
	print "Fragment Refine"
	parts=1
	fhPDB="fh-0-%s"%(probe)
	file3=open(fhPDB, "r")
	lines3=file3.readlines()
	file3.close()
	outPDB="fragment-%d.pdb"%(parts)
	outFrag=open(outPDB, "w")
	for frag in frags:
		aalist=[]
		for sfrag in frag:
			Nend=sfrag[0]
			Cend=sfrag[1]
			aalist+=range(Nend,Cend+1)
		for line in lines3:
			isatom=str(line[0:6].strip())
			resnum=int(line[22:26].strip())
			if ((isatom=="ATOM") and (resnum in aalist)):
				outFrag.write(line)
	outFrag.close
	cmdF1="pdb2mrc fragment-%d.pdb fragment-%d.mrc apix=%f res=%f box=%d"%(parts, parts, apix, res, target_size)
	os.system(cmdF1)
	cmdF2="proc3d fragment-%d.mrc fragment-%d.mrc norm"%(parts, parts)
	os.system(cmdF2)
	logfile2="log-fragment-%d.txt"%(parts)
	cmdF3="foldhunterP target.mrc fragment-%d.mrc fh-fragment-%d.mrc log=%s da=%f startangle=0,0,0 range=%f sphere_region=0,0,0,%f"%(parts,parts,logfile2,da,angle_range,sphere_radius)
	os.system(cmdF3)
	file4=open(logfile2, "r")
	lines4=file4.readlines()
	file4.close()
	fh4 = {}
	for line in lines4:
		ps=pattern.search(line)
		if ps:
			fh4[int(ps.group('solnum'))]=[float(ps.group('rotx')),float(ps.group('rotz1')),float(ps.group('rotz2')),float(ps.group('dx')),float(ps.group('dy')),float(ps.group('dz'))]

	fhOut2="fh-fragment-%d.pdb"%(parts)
	cmdF4="procpdb.py %s r-%s rot=%f,%f,%f"%(outPDB,outPDB,fh4[0][0],fh4[0][1],fh4[0][2])
	os.system(cmdF4)
	cmdF5="procpdb.py r-%s %s apix=%f trans=%f,%f,%f"%(outPDB,fhOut2,apix,fh4[0][3],fh4[0][4],fh4[0][5])
	os.system(cmdF5)
	
	parts=parts+1
	
if (refchain!=0):
	print "Chain Refine"
	fhPDB="fh-0-%s"%(probe)
	file5=open(fhPDB, "r")
	lines5=file5.readlines()
	file5.close()
	outPDB="chain-%d.pdb"%(parts)
	outChain=open(outPDB, "w")
	for line in lines5:
		isatom=str(line[0:6].strip())
		chainid=str(line[21:22].strip())
		if ((isatom=="ATOM") and (chainid==refchain)):
				outFrag.write(line)
	outChain.close
	cmdC1="pdb2mrc chain-%s.pdb chain-%s.mrc apix=%f res=%f box=%d"%(refchain, refchain, apix, res, target_size)
	os.system(cmdC1)
	cmdC2="proc3d chain-%s.mrc chain-%s.mrc norm"%(refchain, refchain)
	os.system(cmdC2)
	logfileC="log-chain-%s.txt"%(refchain)
	cmdC3="foldhunterP target.mrc chain-%s.mrc fh-chain-%s.mrc log=%s da=%f startangle=0,0,0 range=%f sphere_region=0,0,0,%f"%(refchain,refchain,logfileC,da,angle_range,sphere_radius)
	os.system(cmdC3)
	file6=open(logfileC, "r")
	lines6=file6.readlines()
	file6.close()
	fh6 = {}
	for line in lines6:
		ps=pattern.search(line)
		if ps:
			fh6[int(ps.group('solnum'))]=[float(ps.group('rotx')),float(ps.group('rotz1')),float(ps.group('rotz2')),float(ps.group('dx')),float(ps.group('dy')),float(ps.group('dz'))]

	fhOut3="fh-chain-%d.pdb"%(parts)
	cmdC4="procpdb.py %s r-%s rot=%f,%f,%f"%(outPDB,outPDB,fh6[0][0],fh6[0][1],fh6[0][2])
	os.system(cmdC4)
	cmdC5="procpdb.py r-%s %s apix=%f trans=%f,%f,%f"%(outPDB,fhOut3,apix,fh6[0][3],fh6[0][4],fh6[0][5])
	os.system(cmdC5)
