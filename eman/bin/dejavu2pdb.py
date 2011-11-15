#!/usr/bin/env python
###	dejavu2pdb	Matthew Baker 06/2003

#N dejavu2pdb
#F This program generates a pdb backbone for dejaVu helices
#T LM
#1
#P <infile>	Input dejavu file
#P <outfile>	Output pdb file
#D This program generates a pdb backbone for dejaVu helices

import os
import sys
import re
import string
import math
from sys import argv
from math import *
from EMAN import *
import Numeric

def cross_product(a,b):
    """Cross product of two 3-d vectors. from http://www-hep.colorado.edu/~fperez/python/python-c/weave_examples.html
    """
    cross = [0]*3
    cross[0] = a[1]*b[2]-a[2]*b[1]
    cross[1] = a[2]*b[0]-a[0]*b[2]
    cross[2] = a[0]*b[1]-a[1]*b[0]
    return Numeric.array(cross)

def normalize(a):
    try:
        r2 = math.sqrt(a[0]*a[0]+a[1]*a[1]+a[2]*a[2])
        return [a[0]/r2, a[1]/r2, a[2]/r2]
    except:
        return a

apix=1
coordshift=0
vrmlFLAG=0

if (len(argv)<3) :
	print "Usage:\ndejavu2pdb.py <input dejavu file> <output file>\n"
	print "Options: vrml, apix=<float>, coordshift=<float>, helixColor=<float,float,float>, sheetColor=<float,float,float>"
	sys.exit(1)

for a in argv[3:] :
	print a
	if a =='vrml':
		vrmlFLAG=1
	else:
	        s=a.split('=')
        	if (s[0]=='apix') :
			apix=float(s[1])
	        if (s[0]=='coordshift') :
			coordshift=float(s[1])
        	if (s[0]=='helixColor') :
			helixArray=str(s[1])
			helixColor=helixArray.split(",")
			helixRed=str(helixColor[0])
			helixGreen=str(helixColor[1])
			helixBlue=str(helixColor[2])

#	        if (s[0]=='sheetColor') :
#			sheetArray=str(s[1])
#			sheetColor=sheetArray.split(",")
#			sheetRed,sheetGreen,sheetBlue=str(sheetColor[0]),str(sheetColor[1]),str(sheetColor[2])				
        	else:
                	print("Unknown argument "+a)
                	exit(1)

####Find helix in dejavu(sse) file
pattern=re.compile(r"ALPHA\s'(?P<chain>[\w]+)'\s'(?P<startres>[\w]+)'\s'(?P<stopres>[\w]+)'\s(?P<reslength>[\d]+)\s(?P<x1>[\d.,-]+)\s(?P<y1>[\d.,-]+)\s(?P<z1>[\d.,-]+)\s(?P<x2>[\d.,-]+)\s(?P<y2>[\d.,-]+)\s(?P<z2>[\d.,-]+)")

chain=0
chainid=[]
x1=[]
x2=[]
y1=[]
y2=[]
z1=[]
z2=[]
outfile=open(argv[2],"w")
infile=open(argv[1],'r')
starthelix=1
for line in infile.readlines():
	result = pattern.search(line)
	if result==None:
		print "searching..."
	else:
		print "helix found"
		x1.append(result.group('x1'))
		y1.append(result.group('y1'))
		z1.append(result.group('z1'))
		x2.append(result.group('x2'))
		y2.append(result.group('y2'))
		z2.append(result.group('z2'))
		headerLine="HELIX  %3d %3d GLY %s    1  GLY %s %4d  1                               %5d\n"%(starthelix,starthelix,string.letters[starthelix-1],string.letters[starthelix-1],int(result.group('reslength')),int(result.group('reslength')))
		outfile.write(headerLine)
		starthelix=starthelix+1
infile.close()

#####Generates PDB file
chain=len(x1)
i=0
j=0
p=0
q=0
r=0
atom=0

if vrmlFLAG==1:
	outPre=(argv[2].split('.'))[0]
	outWrlFile="%s.wrl"%(outPre)
	outWrl=open(outWrlFile, "w")
	outWrl.write("#VRML V2.0 utf8\n")


while i<chain:
	######calulates phi and theta for each helix
	x1f = string.atof(x1[i])
	y1f = string.atof(y1[i])
	z1f = string.atof(z1[i])

	x2f = string.atof(x2[i])
	y2f = string.atof(y2[i])
	z2f = string.atof(z2[i])
	
	dx=x2f - x1f
	dy=y2f - y1f
	dz=z2f - z1f
	
	length=math.sqrt(dx*dx + dy*dy + dz*dz)
	intlength=math.ceil(length/1.54)
		
	xyplane=math.sqrt((dx*dx)+(dy*dy))

	print "helix: %d"%i
	if dy >= 0:
		phi=math.atan2(dy,dx) + math.pi/2.0
	else:
		phi = math.atan2(dy,dx) + math.pi/2.0
	new_dy = -dx * sin(phi) + dy * cos(phi)

	if new_dy <= 0: 
		theta=math.atan2(xyplane,dz)
	else:
		theta=math.atan2(xyplane,dz) + math.pi/2.0
	print dx,dy,dz
	print "phi   : %f"%phi
	print "theta : %f"%theta
	print "length: %d\n"%intlength
	
	#hlxorig = [0, 0, 1.0]
	hlxorig = [0, 1, 0.0]
	hlxvec= normalize([dx,dy,dz])
	nvect = normalize(cross_product(hlxorig, hlxvec))
	theta2cos = Numeric.innerproduct(hlxorig, hlxvec)
	print theta2cos
	if theta2cos>1.0: theta2cos = 1.0
	elif theta2cos<-1.0: theta2cos = -1.0
	theta2 = math.acos(theta2cos)
	print theta2
	helixSpin = (nvect[0], nvect[1], nvect[2], theta2)
	
	#helixEuler=Euler(phi,theta,pi)
	#print helixEuler
	#helixEuler.fromMRC(phi,theta,0.0)
	#print helixEuler
	#helixSpin=helixEuler.getByType(Euler.SPIN)
	#helixSpin=(helixEuler.n1(), helixEuler.n2(), helixEuler.n3(), helixEuler.Q()) 
	#print helixSpin
	#print helixSpin[1]
	xTrans=(x1f+x2f)/2
	yTrans=(y1f+y2f)/2
	zTrans=(z1f+z2f)/2
	
	if vrmlFLAG==1:
		helixColorLine="       emissiveColor %s %s %s\n"%(helixRed, helixGreen, helixBlue)
		outWrl.write("Group {\n")
		outWrl.write(" children [\n")
		outWrl.write(" Transform {\n")
		transformLine="  translation %f %f %f\n"%(xTrans, yTrans, zTrans)
		rotationLine="  rotation %f %f %f %f\n"%(helixSpin[0],helixSpin[1],helixSpin[2],helixSpin[3])
		outWrl.write(transformLine)
		outWrl.write(rotationLine)
		outWrl.write("  children [\n")
		#outWrl.write("    }\n")
		outWrl.write("   Shape {\n")
		outWrl.write("    appearance \n")
		outWrl.write("     Appearance {\n")
		outWrl.write("      material Material {\n")
		#outWrl.write("       emissiveColor 0.0 1.0 0.0\n")
		outWrl.write(helixColorLine)
		outWrl.write("       }\n")
		outWrl.write("     }\n")		
		outWrl.write("    geometry\n")
		outWrl.write("     Cylinder {\n")
		helixHeight=sqrt((x1f-x2f)**2+(y1f-y2f)**2+(z1f-z2f)**2)
		heightLine="      height %f\n"%(helixHeight)
		outWrl.write(heightLine)
		outWrl.write("      radius 2.5\n")
		outWrl.write("     }\n")
		outWrl.write("   }\n")
		outWrl.write("  ]\n")
		outWrl.write(" }\n")
		outWrl.write(" ]\n")
		outWrl.write("}\n")
	
	rot=[phi,theta]
	mx=[0,0,0,0,0,0,0,0,0]
 	mx[0]= cos(phi)
	mx[1]= sin(phi) 
	mx[2]= 0
	
	mx[3]= -cos(theta) * sin(phi)
	mx[4]= cos(theta) * cos(phi)
	mx[5]= sin(theta)

	mx[6]= sin(theta) * sin(phi)
	mx[7]= -sin(theta) * cos(phi)
	mx[8]= cos(theta)

	######transforms and writes out each helix as a chain
	while j< intlength:


		Nxorigin=math.cos((100*j*math.pi)/180)*2.5
		Nyorigin=math.sin((100*j*math.pi)/180)*2.5
		Nzorigin=j*1.54
		CAxorigin=math.cos(((35+(100*j))*math.pi)/180)*2.5
		CAyorigin=math.sin(((35+(100*j))*math.pi)/180)*2.5
		CAzorigin=(j*1.54)+.87
		Cxorigin=math.cos(((77+(100*j))*math.pi)/180)*2.5
		Cyorigin=math.sin(((77+(100*j))*math.pi)/180)*2.5
		Czorigin=(j*1.54)+1.85
		Oxorigin=math.cos(((81+(100*j))*math.pi)/180)*2.5
		Oyorigin=math.sin(((81+(100*j))*math.pi)/180)*2.5
		Ozorigin=(j*1.54)+3.09

		x4=(mx[0]*Nxorigin+mx[3]*Nyorigin+mx[6]*Nzorigin)
		y4=(mx[1]*Nxorigin+mx[4]*Nyorigin+mx[7]*Nzorigin)
		z4=(mx[2]*Nxorigin+mx[5]*Nyorigin+mx[8]*Nzorigin)
		Nxcoord=(string.atof(x1[i])+x4)/apix
		Nycoord=(string.atof(y1[i])+y4)/apix
		Nzcoord=(string.atof(z1[i])+z4)/apix

		x5=(mx[0]*CAxorigin+mx[3]*CAyorigin+mx[6]*CAzorigin)
		y5=(mx[1]*CAxorigin+mx[4]*CAyorigin+mx[7]*CAzorigin)
		z5=(mx[2]*CAxorigin+mx[5]*CAyorigin+mx[8]*CAzorigin)
		CAxcoord=(string.atof(x1[i])+x5)/apix
		CAycoord=(string.atof(y1[i])+y5)/apix
		CAzcoord=(string.atof(z1[i])+z5)/apix

		x6=(mx[0]*Cxorigin+mx[3]*Cyorigin+mx[6]*Czorigin)
		y6=(mx[1]*Cxorigin+mx[4]*Cyorigin+mx[7]*Czorigin)
		z6=(mx[2]*Cxorigin+mx[5]*Cyorigin+mx[8]*Czorigin)
		Cxcoord=(string.atof(x1[i])+x6)/apix
		Cycoord=(string.atof(y1[i])+y6)/apix
		Czcoord=(string.atof(z1[i])+z6)/apix

		x7=(mx[0]*Oxorigin+mx[3]*Oyorigin+mx[6]*Ozorigin)
		y7=(mx[1]*Oxorigin+mx[4]*Oyorigin+mx[7]*Ozorigin)
		z7=(mx[2]*Oxorigin+mx[5]*Oyorigin+mx[8]*Ozorigin)
		Oxcoord=(string.atof(x1[i])+x7)/apix
		Oycoord=(string.atof(y1[i])+y7)/apix
		Ozcoord=(string.atof(z1[i])+z7)/apix

		p=atom+1
		q=atom+2
		r=atom+3
		s=atom+4
		atom=r
		j=j+1

		outfile.write("ATOM  %5d  N   GLY %s%4d    %8.3f%8.3f%8.3f  1.00     0      S_00  0 \n"%(p,string.letters[i],j,Nxcoord,Nycoord,Nzcoord))
		outfile.write("ATOM  %5d CA   GLY %s%4d    %8.3f%8.3f%8.3f  1.00     0      S_00  0 \n"%(q,string.letters[i],j,CAxcoord,CAycoord,CAzcoord))
		outfile.write("ATOM  %5d  C   GLY %s%4d    %8.3f%8.3f%8.3f  1.00     0      S_00  0 \n"%(r,string.letters[i],j,Cxcoord,Cycoord,Czcoord))
		outfile.write("ATOM  %5d  O   GLY %s%4d    %8.3f%8.3f%8.3f  1.00     0      S_00  0 \n"%(s,string.letters[i],j,Oxcoord,Oycoord,Ozcoord))

	i=i+1
	j=0
	
outfile.close()
if vrmlFLAG==1:
	outWrl.close()
