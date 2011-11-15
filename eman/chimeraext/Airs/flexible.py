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
import re
from MMTK.Proteins import Protein
from MMTK.PDB import *
from MMTK import *
from MMTK.ForceFields import DeformationForceField
from MMTK.FourierBasis import FourierBasis, estimateCutoff
from MMTK.NormalModes import NormalModes, SubspaceNormalModes
import airsIO

try:
	import chimera
	from chimera.baseDialog import ModelessDialog
	import VolumeViewer
except:
	print "Chimera not found"
	ModelessDialog=Tkinter.Window
	
class flexible(ModelessDialog):
	name = "Flexible Foldhunter ui"
	buttons = ("Close")
	title = "Flexible Foldhunter"


	def fileselector(self):
		##generate list of open files
		names=airsIO.getPDBNames()
		self.fileButton.setitems(names)

	def targetSelector(self):
		##generate list of open volume files
		targetnames=airsIO.getVolumeNames()  
		self.targetButton.setitems(targetnames)

	def modelist(self):
		self.list=[]
		self.numberofmodes=max(8, self.universe.numberOfAtoms()/30)
		for item in range(self.numberofmodes):
			self.list.append(item)	

	def modeSelector(self):
		self.modeButton1.setitems(self.list)	
		self.modeButton2.setitems(self.list)
		self.modeButton3.setitems(self.list)	
		self.modeButton4.setitems(self.list)
		
	def fillInUI(self, parent):

		self.frame0=Tkinter.Frame(parent, bd=2, relief=GROOVE)
		self.frame0.grid(column=0,row=0, columnspan=2, sticky=EW)
		self.frame1=Tkinter.Frame(parent, bd=2, relief=GROOVE)
		self.frame1.grid(column=0,row=1, sticky=EW)
		self.frame2=Tkinter.Frame(parent, bd=2, relief=GROOVE)
		self.frame2.grid(column=0,row=2, sticky=EW)
		
####Frame for Calculating modes
		Label(self.frame0, text='PDB file:').grid(row=0, column=0, sticky=W)
		self.infile=StringVar()
		self.fileButton=Pmw.OptionMenu(self.frame0,labelpos=W, menubutton_textvariable=self.infile)
		self.fileButton.grid(row=0, column=1, sticky=E)
		self.fileselector()
		Button(self.frame0,text='Calculate modes', command=self.calculatemodes).grid(row=0, column=2, sticky=W)
		
####Frame for Applying modes		
		self.mode1=StringVar()
		self.modeButton1=Pmw.OptionMenu(self.frame1,label_text='Mode 1: ',labelpos=W, menubutton_textvariable=self.mode1)
		self.mode1.set('None')
		self.modeButton1.grid(row=1, column=0, sticky=W)
		
		self.mode2=StringVar()
		self.modeButton2=Pmw.OptionMenu(self.frame1,label_text='Mode 2: ',labelpos=W, menubutton_textvariable=self.mode2)
		self.mode2.set('None')
		self.modeButton2.grid(row=2, column=0, sticky=W)
		
		self.mode3=StringVar()
		self.modeButton3=Pmw.OptionMenu(self.frame1,label_text='Mode 3: ',labelpos=W, menubutton_textvariable=self.mode3)
		self.mode3.set('None')
		self.modeButton3.grid(row=3, column=0, sticky=W)
		
		self.mode4=StringVar()
		self.modeButton4=Pmw.OptionMenu(self.frame1,label_text='Mode 4: ',labelpos=W, menubutton_textvariable=self.mode4)
		self.mode4.set('None')
		self.modeButton4.grid(row=4, column=0, sticky=W)
		
		Label(self.frame1, text='Amplitude').grid(row=0, column=1, sticky=EW)
		
		amp1=StringVar()
		self.amp1=Scale(self.frame1, length=200, orient=HORIZONTAL, from_=-5000, to=5000, variable=amp1, digits=2, resolution=0, tickinterval=5000)
		self.amp1.grid(row=1, column=1, sticky=EW)
		amp2=StringVar()
		self.amp2=Scale(self.frame1, length=200, orient=HORIZONTAL, from_=-5000, to=5000, variable=amp2, digits=2, resolution=0, tickinterval=5000)
		self.amp2.grid(row=2, column=1, sticky=EW)
		amp3=StringVar()
		self.amp3=Scale(self.frame1, length=200, orient=HORIZONTAL, from_=-5000, to=5000, variable=amp3, digits=2, resolution=0, tickinterval=5000)
		self.amp3.grid(row=3, column=1, sticky=EW)
		amp4=StringVar()
		self.amp4=Scale(self.frame1, length=200, orient=HORIZONTAL, from_=-5000, to=5000, variable=amp4, digits=2, resolution=0, tickinterval=5000)
		self.amp4.grid(row=4, column=1, sticky=EW)

                w1=StringVar()
                w2=StringVar()
                w3=StringVar()
                w4=StringVar()
                Label(self.frame1, text='Weight (0-1)').grid(row=0, column=2, sticky=EW)
                self.weight1 = Entry(self.frame1, textvariable=w1, width = 5)
                self.weight1.grid(row=1, column=2, sticky=W)
                self.weight2 = Entry(self.frame1, textvariable=w2, width = 5)
                self.weight2.grid(row=2, column=2, sticky=W)
                self.weight3 = Entry(self.frame1, textvariable=w3, width = 5)
                self.weight3.grid(row=3, column=2, sticky=W)
                self.weight4 = Entry(self.frame1, textvariable=w4, width = 5)
                self.weight4.grid(row=4, column=2, sticky=W)
                w1.set('1')
                w2.set('1')
                w3.set('1')
                w4.set('1')

		Button(self.frame1,text='Update', command=self.UpdateMode).grid(row=5, column=0, sticky=W)
		
####Frame for Docking
		Label(self.frame2, text='Density Map: ').grid(row=0, column=0, sticky=W)
		self.target=StringVar()
		self.targetButton=Pmw.OptionMenu(self.frame2,labelpos=W, menubutton_textvariable=self.target)
		self.targetButton.grid(row=0, column=1, sticky=W)
		self.targetSelector()

		Label(self.frame2, text='angstrom/pixel:').grid(row=1, column=0, sticky=W)
		Label(self.frame2, text='resolution:').grid(row=1, column=2, sticky=W)
		self.apix = Entry(self.frame2, width = 6)
		self.apix.grid(row=1, column=1, sticky=W)
		self.res = Entry(self.frame2, width = 6)
		self.res.grid(row=1, column=3, sticky=W)
		
		Label(self.frame2, text='Translation limit:').grid(row=2, column=0, sticky=W)
		Label(self.frame2, text='Angle limit:').grid(row=2, column=2, sticky=W)
		self.trans = Entry(self.frame2, width = 6)
		self.trans.grid(row=2, column=1, sticky=W)
		self.angle = Entry(self.frame2, width = 6)
		self.angle.grid(row=2, column=3, sticky=W)
		
		Button(self.frame2,text='Dock it!', command=self.Dock).grid(row=3, sticky=EW)
		
	def calculatemodes(self):
		# Construct system
		inputfile=str(self.infile.get())
		inputPath=airsIO.getPath(inputfile)

		self.universe = InfiniteUniverse(DeformationForceField())
		self.universe.protein = Protein(inputPath, model='calpha')
		self.modelist()
		nbasis = max(8, self.universe.numberOfAtoms()/30)
		cutoff, nbasis = estimateCutoff(self.universe, nbasis)
		print "Calculating %d low-frequency modes for %s." %(nbasis,self.infile.get())
		if cutoff is None:
			#Do full normal mode calculation
			self.modes = NormalModes(self.universe)
		else:
			# Do subspace mode calculation with Fourier basis
			subspace = FourierBasis(self.universe, cutoff)
			self.modes = SubspaceNormalModes(self.universe, subspace)
		self.modeSelector()
		
	def UpdateMode (self):
		configuration = self.universe.configuration()
		factor1 = float(self.amp1.get())
                mode1=self.mode1.get()
                w1 = float(self.weight1.get())

                factor2 = float(self.amp2.get())
                mode2=self.mode2.get()
                w2 = float(self.weight2.get())

                factor3 = float(self.amp3.get())
                mode3=self.mode3.get()
                w3 = float(self.weight3.get())

                factor4 = float(self.amp4.get())
                mode4=self.mode4.get()
                w4 = float(self.weight4.get())
		
		if mode1 !='None':
			configuration = configuration+factor1*self.modes[int(mode1)]*w1
		if mode2 !='None':
			configuration = configuration+factor2*self.modes[int(mode2)]*w2
		if mode3 !='None':
			configuration = configuration+factor3*self.modes[int(mode3)]*w3
		if mode4 !='None':
			configuration = configuration+factor4*self.modes[int(mode4)]*w4
			
		#configuration = configuration+factor*self.modes[mode]
		self.universe.setConfiguration(configuration)
		self.outfile="mode-%s"%(self.infile.get())
		result_pdb = PDBOutputFile(self.outfile)
		result_pdb.write(self.universe)
		result_pdb.close()
		chimera.openModels.open(self.outfile)
		
		if mode4 !='None':
			configuration = configuration-factor4*self.modes[int(mode4)]/w4
		if mode3 !='None':
			configuration = configuration-factor3*self.modes[int(mode3)]/w3
		if mode2 !='None':
			configuration = configuration-factor2*self.modes[int(mode2)]/w2
		if mode1 !='None':
			configuration = configuration-factor1*self.modes[int(mode1)]/w1
			
		#configuration = configuration+(-1*factor*self.modes[mode])
		self.universe.setConfiguration(configuration)

	def Dock (self):
		apix=float(self.apix.get())
		res=float(self.res.get())
		angle=float(self.angle.get())
		trans=float(self.trans.get())
		
		target=airsIO.cleanFileName(str(self.target.get()))
		targetPath=airsIO.getPath(target)
		t=os.path.splitext(target)
		targetName=str(t[0])
		
		mapInfo=airsIO.getMapInfo(target)
		mapSize=mapInfo[0][0]
			
		probePDB=self.outfile
		cmdCenter="procpdb.py %s probe.pdb centeratoms"%(probePDB)
		os.system(cmdCenter)
		cmdMRC="pdb2mrc probe.pdb probe.mrc apix=%f res=%f box=%f"%(apix, res, mapSize)
		os.system(cmdMRC)
		self.outFit="fh-mode-%s"%(targetName)
		
		cmdDock="foldhunterP %s probe.mrc fh-mode.mrc log=log-mode-fit.txt da=1 startangle=0,0,0 range=%f sphere_region=0,0,0,%f"%(targetPath, angle, trans)
		print cmdDock
		os.system(cmdDock)
		
		file=open("log-mode-fit.txt", "r")
		lines=file.readlines()
		file.close()
		fh = {}
		pattern=re.compile(r"Solution\s(?P<solnum>\d+)\:\trotation\s=\s\(\s(?P<rotx>-?\d+(\.\d+)?(e.\d+)?)\s,\s(?P<rotz1>-?\d+(\.\d+)?(e.\d+)?)\s,\s(?P<rotz2>-?\d+(\.\d+)?(e.\d+)?)\s\)\ttranslation\s=\s\(\s(?P<dx>-?\d+(\.\d+)?(e.\d+)?)\s,\s(?P<dy>-?\d+(\.\d+)?(e.\d+)?)\s,\s(?P<dz>-?\d+(\.\d+)?(e.\d+)?)\s\)")
		for line in lines:
			ps=pattern.search(line)
			if ps:
				fh[int(ps.group('solnum'))]=[float(ps.group('rotx')),float(ps.group('rotz1')),float(ps.group('rotz2')),float(ps.group('dx')),float(ps.group('dy')),float(ps.group('dz'))]
 		outRefinePDB="flex-fh-%s.pdb"%(targetName)
		cmd1="procpdb.py %s r.pdb rot=%f,%f,%f"%(self.outfile,fh[0][0],fh[0][1],fh[0][2])
		os.system(cmd1)
		cmd2="procpdb.py r.pdb %s apix=%f trans=%f,%f,%f"%(outRefinePDB,apix,fh[0][3],fh[0][4],fh[0][5])
		os.system(cmd2)
		chimera.openModels.open(outRefinePDB)

try:
	chimera.dialogs.register(flexible.name, flexible)
except: pass

dialog = None

def gui():
	"""This is a Chimera specfic function to support instantiation of the dialog"""
	global dialog
	if not dialog:
		dialog = flexible()
	dialog.enter()
def Refresh(self, *triggerArgs, **kw):
	if ('model list change' in triggerArgs[-1].reasons) : 	
		dialog.targetSelector()
		#dialog.modeSelector()
		dialog.fileselector()
		#dialog.modelist()
triggerOpenModels = chimera.triggers.addHandler('OpenModels', Refresh, None)
