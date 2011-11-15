import os
import sys
import commands
import math
from math import *
from sys import argv
import Tkinter
from Tkinter import *
import tkMessageBox
import Pmw
import chimera
import airsIO

from MMTK.Proteins import Protein
from MMTK.PDB import *
from MMTK import *
from MMTK.ForceFields import DeformationForceField
from MMTK.FourierBasis import FourierBasis, estimateCutoff
from MMTK.NormalModes import NormalModes, SubspaceNormalModes
try:
	import chimera
	from chimera.baseDialog import ModelessDialog
	import VolumeViewer
except:
	print "Chimera not found"
	ModelessDialog=Tkinter.Window
	
class modeviewer(ModelessDialog):
	name = "modeviewer ui"
	buttons = ("View","Close")
	title = "ModeViewer"
	direman=os.environ["HOME"]
	hellp = "%s/EMAN/doc/modev_help.html"%(direman)
	help = hellp


	def fileselector(self):
		##generate list of open files
		names=airsIO.getPDBNames()
		self.fileButton.setitems(names)
		
	def modelist(self):
		self.list=[]
		self.numberofmodes=max(10, self.universe.numberOfAtoms()/5)
		for item in range(self.numberofmodes):
			self.list.append(item)	

	def modeSelector(self):
		self.modeButton.setitems(self.list)	
		
	def fillInUI(self, parent):

		self.frame0=Tkinter.Frame(parent, bd=2, relief=GROOVE)
		self.frame0.grid(column=0,row=0, columnspan=2, sticky=EW)
		self.frame1=Tkinter.Frame(parent, bd=2, relief=GROOVE)
		self.frame1.grid(column=0,row=1, sticky=EW)
		self.frame2=Tkinter.Frame(parent, bd=2, relief=FLAT)
		self.frame2.grid(column=1,row=1, sticky=EW)
		
		Label(self.frame0, text='PDB file:').grid(row=0, column=0, sticky=W)
		self.infile=StringVar()
		self.fileButton=Pmw.OptionMenu(self.frame0,labelpos=W, menubutton_textvariable=self.infile)
		self.fileButton.grid(row=0, column=1, sticky=E)
		self.fileselector()
		Button(self.frame0,text='Calculate modes', command=self.calculatemodes).grid(row=0, column=2, sticky=W)
		
		self.mode=StringVar()
		self.modeButton=Pmw.OptionMenu(self.frame1,label_text='Mode: ',labelpos=W, menubutton_textvariable=self.mode)
		self.mode.set('None')
		self.modeButton.grid(row=0, column=0, sticky=W)

		Label(self.frame2, text='Amplitude').grid(row=0, column=0, sticky=W)
		self.amp = Entry(self.frame2, width = 5)
		self.amp.grid(row=0, column=1, sticky=W)

	def calculatemodes(self):
		# Construct system
		inputfile=str(self.infile.get())
		inputPath=airsIO.getPath(inputfile)

		self.universe = InfiniteUniverse(DeformationForceField())
		self.universe.protein = Protein(inputPath, model='calpha')
		self.modelist()

		nbasis = self.numberofmodes
		cutoff, nbasis = estimateCutoff(self.universe, nbasis)
		print "Calculating %d low-frequency modes for %s." %(nbasis,input)

		if cutoff is None:
			#Do full normal mode calculation
			self.modes = NormalModes(self.universe)
		else:
			# Do subspace mode calculation with Fourier basis
			subspace = FourierBasis(self.universe, cutoff)
			self.modes = SubspaceNormalModes(self.universe, subspace)
		self.modeSelector()
	def View(self):
		factor = float(self.amp.get())
		mode=int(self.mode.get())
	
		#universe.writeToFile(outfile,conf,'pdb')
		
		configuration = self.universe.configuration()

		configuration = configuration+factor*self.modes[mode]
		self.universe.setConfiguration(configuration)
		
		target=self.infile.get()
		outfile="mode-%s"%(target)
		result_pdb = PDBOutputFile(outfile)
		result_pdb.write(self.universe)
		result_pdb.close()

		chimera.openModels.open(outfile)
		configuration = configuration+(-1*factor*self.modes[mode])
		self.universe.setConfiguration(configuration)
try:
	chimera.dialogs.register(modeviewer.name, modeviewer)
except: pass

dialog = None

def gui():
	"""This is a Chimera specfic function to support instantiation of the dialog"""
	global dialog
	if not dialog:
		dialog = modeviewer()
	dialog.enter()

def Refresh(self, *triggerArgs, **kw):
	if ('model list change' in triggerArgs[-1].reasons) : 
                dialog.fileselector()
                #dialog.modelist()
        	#dialog.modeSelector()
triggerOpenModels = chimera.triggers.addHandler('OpenModels', Refresh, None)
