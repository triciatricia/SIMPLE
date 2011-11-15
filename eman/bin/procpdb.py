#!/usr/bin/env python
###	procpdb.py	Steven Ludtke	2/2002

#N procpdb.py
#F This program is for performing simple operations on PDB files
#T LM
#1
#P <infile>	Input file
#P [<outfile>]	Output file
#P [rot=<alt,az,phi>]	Rotation in EMAN convention
#P [trans=<dx,dy,dz>]	Translate (before rotation)
#P [posttrans=<dx,dy,dz>]	Post-translation
#P [centeratoms]	Center based on the mean atom position
#P [centerelec]	Center based on the center of electron charge
#P [centermass]	Center based on the center of mass
#P [animorph=<n>,<apix>,<vecfile>]	This will use a morph vector file (segment3d) to morph atom positions
#P [apix=<A/pix>]	multiply trans by apix
#P [split]	Split file at TER records. Results imperfect.
#P [include=[helix,sheet,other]]
#P [chains=<chainltr>]	eg - "ABO", for extracting a portion of a complex
#D Simple program for manipulating PDB files in the EMAN convention

import os
import sys
import random
import time
import string
from os import system
from os import unlink
from sys import argv
from math import *

def LOGbegin(ARGV):
	out=open(".emanlog","a")
	b=string.split(ARGV[0],'/')
	ARGV[0]=b[len(b)-1]
	out.write("%d\t%d\t1\t%d\t%s\n"%(os.getpid(),time.time(),os.getppid(),string.join(ARGV," ")))
	out.close()

def LOGend():
	out=open(".emanlog","a")
	out.write("%d\t%d\t2\t-\t\n"%(os.getpid(),time.time()))
	out.close()

#           1         2         3         4         5         6         7
# 01234567890123456789012345678901234567890123456789012345678901234567890123456789
# ATOM      1  N   ASP L   1      57.169  62.936   7.756  1.00 30.65      1ACY 129
# HEADER    COMPLEX(ANTIBODY/HIV-1 FRAGMENT)        10-FEB-94   1ACY      1ACY   2

# Note the unusual entries 'A' for ambiguous, treated as Nitrogen and 'w' for Water
atomdefs={'H':(1.0,1.00794),'C':(6.0,12.0107),'A':(7.0,14.00674),'N':(7.0,14.00674),'O':(8.0,15.9994),'P':(15.0,30.973761),
	'S':(16.0,32.066),'W':(18.0,1.00794*2.0+15.9994),'AU':(79.0,196.96655) }

#### MAIN

rot=(0,0,0)
cen=(0,0,0)		#center of rotation
trans=(0,0,0)
ptrans=(0,0,0)
center=0
apix=1
spl=0
animorph=None
chains=None
savetypes=["helix","sheet","other"]

if (len(argv)<2) :
	print "Usage:\nprocpdb.py <input>\nprocpdb.py <input> <output> [rot=<alt,az,phi>] [trans=<dx,dy,dz>] [centeratoms] [centerelec] [centermass] [apix=<A/pixel>]\n"
	sys.exit(1)

for i in argv[3:] :
	s=i.split('=')
	if (s[0]=='rot') :
		p=s[1].split(',')
		rot=(float(p[0])/57.29578,float(p[1])/57.29578,float(p[2])/57.29578)
	elif (s[0]=='trans'):
		p=s[1].split(',')
		trans=(float(p[0]),float(p[1]),float(p[2]))
	elif (s[0]=='posttrans'):
		p=s[1].split(',')
		ptrans=(float(p[0]),float(p[1]),float(p[2]))
	elif (s[0]=="chains") : chains=s[1]
	elif (s[0]=="centeratoms") : center=1
	elif (s[0]=="centerelec") : center=2
	elif (s[0]=="centermass") : center=3
	elif (s[0]=="animorph") : animorph=s[1].split(",")
	elif (s[0]=="split") : spl=1
	elif (s[0]=="apix") : apix=float(s[1])
	elif (s[0]=="include") :
		savetypes=s[1].split(',')
	else:
		print("Unknown argument "+i)
		exit(1)

if (len(argv)>2) : LOGbegin(argv)

inp=open(argv[1],'r')
lines=inp.readlines()
inp.close()

helixlist=[]
sheetlist=[]
title=""
atoms=0
mass=0
electrons=0
# center of atoms,center of electron density,center of mass,min,max
xval=[0,0,0,None,None]
yval=[0,0,0,None,None]
zval=[0,0,0,None,None]

if (spl) :
	for i in range(len(lines)):
		if (lines[i][:4]=="ATOM" or lines[i][:6]=="HETATM") :
			start=i
			break

	sn=0
	out=None
	for i in lines[start:]:
		if i[:3]=="ter" or i[:3]=="TER" or sn==0 :
			if (out) : out.close()
			sn+=1
			out=open("%s.%d.ent"%(argv[2],sn),"w")
			for j in lines[:start]: out.write(j)
		else : out.write(i)

	sys.exit(1)

for i in lines:
	if (i[:6]=='HEADER') : title=i[10:72].strip()
	if (i[:5]=='HELIX') :
		helixlist.extend(range(int(i[21:25]),int(i[33:37])+1))
	if (i[:5]=='SHEET') :
		sheetlist.extend(range(int(i[22:26]),int(i[33:37])+1))
	if ((i[:4]=='ATOM' or i[:6]=='HETATM') and (not chains or (i[21] in chains))) :
		a=i[12:14].strip()
		res=int(i[22:26].strip())
		if (res in helixlist) :
			 if (not "helix" in savetypes) : continue
		elif (res in sheetlist) :
			if (not "sheet" in savetypes) : continue
		elif (not "other" in savetypes) : continue

		x=float(i[30:38])
		y=float(i[38:46])
		z=float(i[46:54])
		atm=(0,0)
		try:
			atm=atomdefs[a]
			mass+=atm[1]
			electrons+=atm[0]
			atoms+=1.0
		except:
			print "Unknown Atom '%s' ignored."%a

		xval[0]+=x
		yval[0]+=y
		zval[0]+=z
		xval[1]+=x*atm[0]
		yval[1]+=y*atm[0]
		zval[1]+=z*atm[0]
		xval[2]+=x*atm[1]
		yval[2]+=y*atm[1]
		zval[2]+=z*atm[1]
		if (xval[3]==None) :
			xval[3]=x
			yval[3]=y
			zval[3]=z
		xval[3]=min(xval[3],x)
		yval[3]=min(yval[3],y)
		zval[3]=min(zval[3],z)
		xval[4]=max(xval[4],x)
		yval[4]=max(yval[4],y)
		zval[4]=max(zval[4],z)

xval[0]/=atoms
yval[0]/=atoms
zval[0]/=atoms
xval[1]/=electrons
yval[1]/=electrons
zval[1]/=electrons
xval[2]/=mass
yval[2]/=mass
zval[2]/=mass

print title
print "%1.0f atoms   %1.0f electrons   mass= %1.3f kDa"%(atoms,electrons,mass/1000.0)
print "atom center = (%1.2f,%1.2f,%1.2f)"%(xval[0],yval[0],zval[0])
print "electron density center = (%1.2f,%1.2f,%1.2f)"%(xval[1],yval[1],zval[1])
print "center of mass = (%1.2f,%1.2f,%1.2f)"%(xval[2],yval[2],zval[2])
print "x range: %1.1f to %1.1f  (%1.1f)"%(xval[3],xval[4],xval[4]-xval[3])
print "y range: %1.1f to %1.1f  (%1.1f)"%(yval[3],yval[4],yval[4]-yval[3])
print "z range: %1.1f to %1.1f  (%1.1f)"%(zval[3],zval[4],zval[4]-zval[3])

#           1         2         3         4         5         6         7
# 01234567890123456789012345678901234567890123456789012345678901234567890123456789
# ATOM      1  N   ASP L   1      57.169  62.936   7.756  1.00 30.65      1ACY 129
# HEADER    COMPLEX(ANTIBODY/HIV-1 FRAGMENT)        10-FEB-94   1ACY      1ACY   2

if (center==1) : trans=(-xval[0],-yval[0],-zval[0])
elif (center==2) : trans=(-xval[1],-yval[1],-zval[1])
elif (center==3) : trans=(-xval[2],-yval[2],-zval[2])

if (len(argv)>2) :
	if (animorph) :
		v=open(animorph[2],"r")
		vecs=v.readlines()
		v.close()
		
		apix=float(animorph[1])
		vecs=[map(lambda y:float(y),x.split()) for x in vecs]
		for i,v in enumerate(vecs):
			vecs[i]=[apix*(v[3]),apix*(v[4]),apix*(v[5]),apix*(v[0]-v[3]),apix*(v[1]-v[4]),apix*(v[2]-v[5])]
#			vecs[i]=[apix*(v[0]+v[3])/2,apix*(v[1]+v[4])/2,apix*(v[2]+v[5])/2,apix*(v[3]-v[0]),apix*(v[4]-v[1]),apix*(v[5]-v[2])]
		
		for m in range(int(animorph[0])):
			aw=m/(float(animorph[0])-1.0)
			out=open("%s.%02d%s"%(argv[2][:-4],m,argv[2][-4:]),"w")
			for i in lines:
				if (i[:6]=='HEADER') : title=i[10:72].strip()
				if (i[:4]=='ATOM' or i[:6]=='HETATM') :
					if (not chains or (i[21] in chains)):
						res=int(i[22:26].strip())
						if (res in helixlist) :
							if (not "helix" in savetypes) : continue
						elif (res in sheetlist) :
							if (not "sheet" in savetypes) : continue
						elif (not "other" in savetypes) : continue
			
						x=float(i[30:38])
						y=float(i[38:46])
						z=float(i[46:54])
						
						dx,dy,dz,nm=0,0,0,0
#						print "-------------------"
						for v in vecs:
							w=1.0/((x-v[0])**4+(y-v[1])**4+(z-v[2])**4)
#							print w
							dx+=w*v[3]
							dy+=w*v[4]
							dz+=w*v[5]
							nm+=w
						dx/=nm
						dy/=nm
						dz/=nm
						out.write(i[:30]+" %7.2f %7.2f %7.2f"%(x+dx*aw,y+dy*aw,z+dz*aw)+i[54:])
				else : out.write(i)

			out.close()
			print "%d/%d complete"%(m,int(animorph[0]))
	else:	
		mx=[0,0,0,0,0,0,0,0,0]
		mx[0]=(cos(rot[2])*cos(rot[1])-cos(rot[0])*sin(rot[1])*sin(rot[2]))
		mx[1]=-(sin(rot[2])*cos(rot[1])+cos(rot[0])*sin(rot[1])*cos(rot[2]))
		mx[2]=sin(rot[0])*sin(rot[1])
		mx[3]=(cos(rot[2])*sin(rot[1])+cos(rot[0])*cos(rot[1])*sin(rot[2]))
		mx[4]=(-sin(rot[2])*sin(rot[1])+cos(rot[0])*cos(rot[1])*cos(rot[2]))
		mx[5]=-sin(rot[0])*cos(rot[1])
		mx[6]=sin(rot[0])*sin(rot[2])
		mx[7]=sin(rot[0])*cos(rot[2])
		mx[8]=cos(rot[0])
	
		out=open(argv[2],"w")
		for i in lines:
			if (i[:6]=='HEADER') : title=i[10:72].strip()
			if (i[:4]=='ATOM' or i[:6]=='HETATM') :
				if (not chains or (i[21] in chains)):
					res=int(i[22:26].strip())
					if (res in helixlist) :
						if (not "helix" in savetypes) : continue
					elif (res in sheetlist) :
						if (not "sheet" in savetypes) : continue
					elif (not "other" in savetypes) : continue
		
					x=float(i[30:38])+(apix*trans[0])
					y=float(i[38:46])+(apix*trans[1])
					z=float(i[46:54])+(apix*trans[2])
					x4=(mx[0]*(x+cen[0])+mx[3]*(y+cen[1])+mx[6]*(z+cen[2]))-cen[0]
					y4=(mx[1]*(x+cen[0])+mx[4]*(y+cen[1])+mx[7]*(z+cen[2]))-cen[1]
					z4=(mx[2]*(x+cen[0])+mx[5]*(y+cen[1])+mx[8]*(z+cen[2]))-cen[2]
					out.write(i[:30]+" %7.2f %7.2f %7.2f"%(x4+ptrans[0],y4+ptrans[1],z4+ptrans[2])+i[54:])
			else : out.write(i)
	
		out.close()

if (len(argv)>2) : LOGend()

