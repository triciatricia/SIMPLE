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
	
class pdb2mrc(ModelessDialog):
	name = "pdb2mrc ui"
	buttons = ("Apply","Close")
	title = "PDB to MRC"
	direman=os.environ["HOME"]
	hellp = "%s/EMAN/doc/pdb2mrc_help.html"%(direman)
	help = hellp

	def fileSelector(self):
		##generate list of open files
		names=airsIO.getPDBNames()
		self.fileButton.setitems(names)


	def fillInUI(self, parent):
		##setup frames for inputs
		self.frame0=Tkinter.Frame(parent, bd=2, relief=GROOVE)
		self.frame0.grid(column=0,row=0, sticky=EW)

		##Target Selection
		Label(self.frame0, text='input file:     ').grid(row=0, sticky=W)
		self.target=StringVar()
		self.fileButton=Pmw.OptionMenu(self.frame0,labelpos=W, menubutton_textvariable=self.target)
		self.fileButton.grid(row=0, column=1, sticky=W)
		self.fileSelector()
		
		##Target Selection
		Label(self.frame0, text='output file:   ').grid(row=1, sticky=W)
		self.outfile = Entry(self.frame0, width = 15)
		self.outfile.grid(row=1, column=1, sticky=W)
		
		##parameters
		Label(self.frame0, text='angstrom/pixel:').grid(row=2, column=0, sticky=W)
		Label(self.frame0, text='resolution:    ').grid(row=3, column=0, sticky=W)
		Label(self.frame0, text='map size (pix):').grid(row=4, column=0, sticky=W)
		self.apix = Entry(self.frame0, width = 6)
		self.apix.grid(row=2, column=1, sticky=W)
		self.res = Entry(self.frame0, width = 6)
		self.res.grid(row=3, column=1, sticky=W)
		self.boxsize = Entry(self.frame0, width = 6)
		self.boxsize.grid(row=4, column=1, sticky=W)
		self.centeratoms=IntVar()
		ca = Checkbutton(self.frame0, text="centeratoms", variable=self.centeratoms).grid(row=5, sticky=W)	
		
	def Apply(self):
		target=airsIO.cleanFileName(str(self.target.get()))
		targetPath=airsIO.getPath(target)
		
		output=str(self.outfile.get())
		apix=float(self.apix.get())
		res= float(self.res.get())
		mapsize= float(self.boxsize.get())
		centerFLAG=self.centeratoms.get()
		
		if centerFLAG==1:
			cmd0="pdb2mrc %s %s apix=%f res=%f box=%f centeratoms"%(targetPath,output,apix,res,mapsize)
		
		else:
			cmd0="pdb2mrc %s %s apix=%f res=%f box=%f"%(targetPath,output,apix,res,mapsize)
		
		print cmd0
		os.system(cmd0)
		
		chimera.openModels.open(output)

try:
	chimera.dialogs.register(pdb2mrc.name, pdb2mrc)
except: pass

dialog = None

def gui():
	"""This is a Chimera specfic function to support instantiation of the dialog"""
	global dialog
	if not dialog:
		dialog = pdb2mrc()
	dialog.enter()

def Refresh(self, *triggerArgs, **kw):
	if ('model list change' in triggerArgs[-1].reasons) :
		dialog.fileSelector()
triggerOpenModels = chimera.triggers.addHandler('OpenModels', Refresh, None)

		
		
		
		
		
		
		
		
		
