import os
import sys
import string
import commands
from sys import argv
import Pmw
import Tkinter
from Tkinter import *
import tkMessageBox
import airsIO
try:
	import chimera
	from chimera.baseDialog import ModelessDialog
	import VolumeViewer
except:
	print "Chimera not found"
	ModelessDialog=Tkinter.Window


class rt(ModelessDialog):
	name = "rt ui"
	buttons = ("Apply","CCF","Close")
	title = "Manual rotation and translation"
	direman=os.environ["HOME"]
	hellp = "%s/EMAN/doc/hh3c_help.html"%(direman)
	help = hellp
	
	def targetSelector(self):
	##generate list of open volume files
		targets=airsIO.getAllNames()
 		self.targetButton.setitems(targets)
		self.pButton.setitems(targets)
		ccftargets=airsIO.getVolumeNames()
		self.tButton.setitems(ccftargets)

	def fillInUI(self, parent):
		##setup frames for inputs
		self.frame0=Tkinter.Frame(parent, bd=2, relief=GROOVE)
		self.frame0.grid(column=0,row=0, sticky=EW)
		self.frame1=Tkinter.Frame(parent, bd=2, relief=GROOVE)
		self.frame1.grid(column=0,row=1, sticky=EW)
		self.frame2=Tkinter.Frame(parent, bd=2, relief=GROOVE)
		self.frame2.grid(column=0,row=2, sticky=EW)		

		##Target Selection
		Label(self.frame0, text='map:').grid(row=0, column=0, sticky=W)
		self.target=StringVar()
		self.targetButton=Pmw.OptionMenu(self.frame0,labelpos=W, menubutton_textvariable=self.target)
		self.targetButton.grid(row=0, column=1, sticky=W)
		#self.targetSelector()
		
		
		alt=StringVar()
		Label(self.frame1, text='alt').grid(row=0, column=0, sticky=W)
		self.alt = Entry(self.frame1, width = 10, textvariable=alt)
		self.alt.grid(row=0, column=1, sticky=W)
		
		az=StringVar()
		Label(self.frame1, text='az').grid(row=1, column=0, sticky=W)
		self.az = Entry(self.frame1, width = 10, textvariable=az)
		self.az.grid(row=1, column=1, sticky=W)
		
		phi=StringVar()
		Label(self.frame1, text='phi').grid(row=2, column=0, sticky=W)
		self.phi = Entry(self.frame1, width = 10, textvariable=phi)
		self.phi.grid(row=2, column=1, sticky=W)
		
		dx=StringVar()
		Label(self.frame1, text='dx').grid(row=0, column=2, sticky=W)
		self.dx = Entry(self.frame1, width = 10, textvariable=dx)
		self.dx.grid(row=0, column=3, sticky=W)
		
		dy=StringVar()
		Label(self.frame1, text='dy').grid(row=1, column=2, sticky=W)
		self.dy = Entry(self.frame1, width = 10, textvariable=dy)
		self.dy.grid(row=1, column=3, sticky=W)
		
		dz=StringVar()
		Label(self.frame1, text='dz').grid(row=2, column=2, sticky=W)
		self.dz = Entry(self.frame1, width = 10, textvariable=dz)
		self.dz.grid(row=2, column=3, sticky=W)
		
		Label(self.frame2, text='ccf probe').grid(row=0, column=0, sticky=W)
		self.pfile=StringVar()
		self.pButton=Pmw.OptionMenu(self.frame2,labelpos=W, menubutton_textvariable=self.pfile)
		self.pButton.grid(row=0, column=1, sticky=W)
		#self.targetSelector()
		
		Label(self.frame2, text='ccf target').grid(row=1, column=0, sticky=W)
		self.tfile=StringVar()
		self.tButton=Pmw.OptionMenu(self.frame2,labelpos=W, menubutton_textvariable=self.tfile)
		self.tButton.grid(row=1, column=1, sticky=W)
		self.targetSelector()
		
	def Apply(self):
		infile=airsIO.cleanFileName(str(self.target.get()))
		targetPath=airsIO.getPath(infile)
		alt=float(self.alt.get())
		az=float(self.az.get())
		phi=float(self.phi.get())
		dx=float(self.dx.get())
		dy=float(self.dy.get())
		dz=float(self.dz.get())
		outfile="rt-%s"%(infile.strip())
		print outfile
		if str(infile.split(".")[-1].strip())==("mrc" or "map" or "ccp4"):
			cmd0="chimerart.py %s %s %f,%f,%f,%f,%f,%f"%(targetPath, outfile, alt,az,phi,dx,dy,dz)
		elif str(infile.split(".")[-1])==("pdb" or "ent"):
			cmd0="procpdb.py %s %s rot=%f,%f,%f trans=%f,%f,%f"%(targetPath, outfile, alt,az,phi,dx,dy,dz)
		else:
			print "bad file"
		print cmd0
		os.system(cmd0)
		chimera.openModels.open(outfile)
		
	def CCF(self):
		infile=str(self.pfile.get())
		targetPath=airsIO.getPath(infile)
		ccffile=str(self.tfile.get())
		ccfPath=airsIO.getPath(ccffile)
		cmd0="ccf2.py %s %s"%(targetPath,ccfPath)
		os.system(cmd0)
		
try:
	chimera.dialogs.register(rt.name, rt)
except: pass

dialog = None

def gui():
	"""This is a Chimera specfic function to support instantiation of the dialog"""
	global dialog
	if not dialog:
		dialog = rt()
	dialog.enter()

def Refresh(self, *triggerArgs, **kw):
	if ('model list change' in triggerArgs[-1].reasons) :
		dialog.targetSelector()
triggerOpenModels = chimera.triggers.addHandler('OpenModels', Refresh, None)

		
