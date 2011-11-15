import os
import sys
import string
import commands
import math
import re
import shutil
from math import *
from sys import argv
import Pmw
import Tkinter
from Tkinter import *
import tkMessageBox

try:
	import chimera
	from chimera.baseDialog import ModelessDialog
except:
	print "Chimera not found"
	ModelessDialog=Tkinter.Window

class helix(ModelessDialog):
	name = "helix ui"
	buttons = ("Close")
	title = "helix"
	
	def fillInUI(self, parent):
		##setup frames for inputs
		self.frame0=Tkinter.Frame(parent, bd=2, relief=GROOVE)
		self.frame0.grid(column=0,row=0, sticky=EW)
		self.frame1=Tkinter.Frame(parent, bd=2, relief=GROOVE)
		self.frame1.grid(column=0,row=1, sticky=EW)
		self.frame3=Tkinter.Frame(parent, bd=2, relief=GROOVE)
		self.frame3.grid(column=0,row=3, sticky=EW)
		self.frame4=Tkinter.Frame(self.frame3, bd=2, relief=FLAT)
		self.frame4.grid(column=0,row=0, sticky=EW)
		self.frame5=Tkinter.Frame(self.frame3, bd=2, relief=FLAT)
		self.frame5.grid(column=1,row=0, sticky=EW)
		self.frame6=Tkinter.Frame(parent, bd=2, relief=GROOVE)
		self.frame6.grid(column=0,row=4, sticky=EW)
		self.frame7=Tkinter.Frame(parent, bd=2, relief=GROOVE)
		self.frame7.grid(column=0,row=5, sticky=EW)
		self.frame8=Tkinter.Frame(self.frame1, bd=2, relief=FLAT)
		self.frame8.grid(column=0,row=0, sticky=EW)
		self.frame9=Tkinter.Frame(self.frame1, bd=2, relief=FLAT)
		self.frame9.grid(column=1,row=0, sticky=EW)		
		
		Label(self.frame0, text='input file:').grid(row=0, column=0, sticky=EW)
		self.infile = Entry(self.frame0, width = 20)
		self.infile.grid(row=0, column=0, sticky=EW)
		Button(self.frame0, text="Open", command=self.openFile).grid(row=0, column=2, sticky=EW)
		
		self.listHelices=[]
		Label(self.frame8, text='Chains').grid(column=0, row=0, sticky=W)
		self.chains = Pmw.ScrolledListBox(self.frame8, listbox_selectmode=MULTIPLE, items=self.listHelices, selectioncommand=self.viewHelices, dblclickcommand=self.editHelix, usehullsize=1, hull_width=50, hull_height=100)
		self.chains.grid(row=1, column=0, sticky=EW)
		Button(self.frame9, text="Show", command=self.showHelix).grid(row=0, column=0, sticky=EW)
		Button(self.frame9, text="Hide", command=self.hideHelix).grid(row=1, column=0, sticky=EW)
		Button(self.frame9, text="Add", command=self.addHelix).grid(row=0, column=1, sticky=EW)
		Button(self.frame9, text="Delete", command=self.deleteHelix).grid(row=1, column=1, sticky=EW)
				
		transx=StringVar()
		transy=StringVar()
		transz=StringVar()
		rotx=StringVar()
		roty=StringVar()
		rotz=StringVar()
		
		Label(self.frame4, text='Translation').grid(row=0, sticky=W)
		self.Xtrans=Scale(self.frame4, length=200, orient=HORIZONTAL, from_=-1000, to=1000, variable=transx, label='X', digits=2, resolution=0, tickinterval=1000)
		self.Xtrans.grid(row=1, column=0, sticky=EW)
		self.Ytrans=Scale(self.frame4, length=200, orient=HORIZONTAL, from_=-1000, to=1000, variable=transy, label='Y', digits=2, resolution=0, tickinterval=1000)
		self.Ytrans.grid(row=2, column=0, sticky=EW)		
		self.Ztrans=Scale(self.frame4, length=200, orient=HORIZONTAL, from_=-1000, to=1000, variable=transz, label='Z', digits=2, resolution=0, tickinterval=1000)
		self.Ztrans.grid(row=3, column=0, sticky=EW)		
		
		Label(self.frame5, text='Rotation').grid(row=0, sticky=W)
		self.Xrot=Scale(self.frame5, length=200, orient=HORIZONTAL, from_=-360, to=360, variable=rotx, label='X', digits=2, resolution=0, tickinterval=360)
		self.Xrot.grid(row=1, column=0, sticky=EW)
		self.Yrot=Scale(self.frame5, length=200, orient=HORIZONTAL, from_=-360, to=360, variable=roty, label='Y', digits=2, resolution=0, tickinterval=360)
		self.Yrot.grid(row=2, column=0, sticky=EW)		
		self.Zrot=Scale(self.frame5, length=200, orient=HORIZONTAL, from_=-360, to=360, variable=rotz, label='Z', digits=2, resolution=0, tickinterval=360)
		self.Zrot.grid(row=3, column=0, sticky=EW)			
		
		Label(self.frame6, text='Length').grid(row=0, column=0, sticky=EW)
		self.length = Entry(self.frame6, width = 8)
		self.length.grid(row=0, column=1, sticky=EW)
		Button(self.frame6, text="+", command=self.plus).grid(row=0, column=2, sticky=EW)
		Button(self.frame6, text="-", command=self.minus).grid(row=0, column=3, sticky=EW)
		
		Button(self.frame7, text="Write PDB", command=self.writePDB).grid(row=0, column=0, sticky=EW)
		Button(self.frame7, text="Write DejaVu", command=self.writeDejavu).grid(row=0, column=1, sticky=EW)
		
	def openFile(self):
		pattern=re.compile(r"ALPHA\s'(?P<chain>[\w]+)'\s'(?P<startres>[\w]+)'\s'(?P<stopres>[\w]+)'\s(?P<reslength>[\d]+)\s(?P<x1>[\d.,-]+)\s(?P<y1>[\d.,-]+)\s(?P<z1>[\d.,-]+)\s(?P<x2>[\d.,-]+)\s(?P<y2>[\d.,-]+)\s(?P<z2>[\d.,-]+)")

		self.x1=[]
		self.x2=[]
		self.y1=[]
		self.y2=[]
		self.z1=[]
		self.z2=[]
		self.length=[]

		infile=open(self.infile,'r')
		for line in infile.readlines():
			result = pattern.search(line)
			if result==None:
				print "searching..."
			else:
				print "helix found"
				self.x1.string.atof(append(result.group('x1')))
				self.y1.string.atof(append(result.group('y1')))
				self.z1.string.atof(append(result.group('z1')))
				self.x2.string.atof(append(result.group('x2')))
				self.y2.string.atof(append(result.group('y2')))
				self.z2.string.atof(append(result.group('z2')))
				self.length.string.atof(append(result.group('reslength')))
		infile.close()



	def viewHelices(self):
		#####Generates PDB file
		if (self.selectHelices==0):
			chains=len(self.x1)
		else:
			chains=len(self.selectHelices)
		i=0
		j=0
		p=0
		q=0
		r=0
		atom=0
		chainid=[]
		
		outfile=open(temp.pdb,"w")
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

			print "phi   : %f"%phi
			print "theta : %f"%theta
			print "length: %d\n"%intlength

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
				Nxcoord=string.atof(x1[i])+x4
				Nycoord=string.atof(y1[i])+y4
				Nzcoord=string.atof(z1[i])+z4	
				
				x5=(mx[0]*CAxorigin+mx[3]*CAyorigin+mx[6]*CAzorigin)
				y5=(mx[1]*CAxorigin+mx[4]*CAyorigin+mx[7]*CAzorigin)
				z5=(mx[2]*CAxorigin+mx[5]*CAyorigin+mx[8]*CAzorigin)
				CAxcoord=string.atof(x1[i])+x5
				CAycoord=string.atof(y1[i])+y5
				CAzcoord=string.atof(z1[i])+z5
				
				x6=(mx[0]*Cxorigin+mx[3]*Cyorigin+mx[6]*Czorigin)
				y6=(mx[1]*Cxorigin+mx[4]*Cyorigin+mx[7]*Czorigin)
				z6=(mx[2]*Cxorigin+mx[5]*Cyorigin+mx[8]*Czorigin)	
				Cxcoord=string.atof(x1[i])+x6
				Cycoord=string.atof(y1[i])+y6
				Czcoord=string.atof(z1[i])+z6
		
				x7=(mx[0]*Oxorigin+mx[3]*Oyorigin+mx[6]*Ozorigin)
				y7=(mx[1]*Oxorigin+mx[4]*Oyorigin+mx[7]*Ozorigin)
				z7=(mx[2]*Oxorigin+mx[5]*Oyorigin+mx[8]*Ozorigin)
				Oxcoord=string.atof(x1[i])+x7
				Oycoord=string.atof(y1[i])+y7
				Ozcoord=string.atof(z1[i])+z7	

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
		chimera.openModels.open(bestResult)
		
	def plus(self):
		
		return
	def minus(self):
		return
	def viewHelices(self):
		return
	def editHelix(self):
		return
	def addHelix(self):
		self.length=10
		j=0
		p=0
		q=0
		r=0
		outfile=open(temp.pdb,"w")
		while j<= self.length:
			Nxcoord=math.cos((100*j*math.pi)/180)*2.5
			Nycoord=math.sin((100*j*math.pi)/180)*2.5
			Nzcoord=j*1.54
			CAxcoord=math.cos(((35+(100*j))*math.pi)/180)*2.5
			CAycoord=math.sin(((35+(100*j))*math.pi)/180)*2.5
			CAzcoord=(j*1.54)+.87
			Cxcoord=math.cos(((81+(100*j))*math.pi)/180)*2.5
			Cycoord=math.sin(((81+(100*j))*math.pi)/180)*2.5
			Czcoord=(j*1.54)+1.85
			Oxcoord=math.cos(((81+(100*j))*math.pi)/180)*2.5
			Oycoord=math.sin(((81+(100*j))*math.pi)/180)*2.5
			Ozcoord=(j*1.54)+3.09

			p=j*4+1
			q=j*4+2
			r=j*4+3
			s=j*4+4
			j=j+1
	
			outfile.write("ATOM  %5d   N  GLY A%4d    %8.3f%8.3f%8.3f  1.00     0      S_00  0 \n"%(p,j,Nxcoord,Nycoord,Nzcoord))
			outfile.write("ATOM  %5d  CA  GLY A%4d    %8.3f%8.3f%8.3f  1.00     0      S_00  0 \n"%(q,j,CAxcoord,CAycoord,CAzcoord))
			outfile.write("ATOM  %5d   C  GLY A%4d    %8.3f%8.3f%8.3f  1.00     0      S_00  0 \n"%(r,j,Cxcoord,Cycoord,Czcoord))
			outfile.write("ATOM  %5d   O  GLY A%4d    %8.3f%8.3f%8.3f  1.00     0      S_00  0 \n"%(s,j,Oxcoord,Oycoord,Ozcoord))
	
		outfile.close()
		return

	def deleteHelix(self):
		return
	def showHelix(self):
		return
	def hideHelix(self):
		return
	def transformHelix(self):
		return
	def writePDB(self):
		return
	def writeDejavu(self):
		return		
try:
	chimera.dialogs.register(helix.name, helix)
except: pass

dialog = None

def gui():
	"""This is a Chimera specfic function to support instantiation of the dialog"""
	global dialog
	if not dialog:
		dialog = helix()
	dialog.enter()

#def Refresh(self, *triggerArgs, **kw):
#	if ('model list change' in triggerArgs[-1].reasons) : 
#		dialog.targetSelector()
#		dialog.probeSelector()
#		dialog.resultSelector()

#triggerOpenModels = chimera.triggers.addHandler('OpenModels', Refresh, None)

		
