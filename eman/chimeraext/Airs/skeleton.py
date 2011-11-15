import os
import sys
import string
import commands
import Pmw
import Tkinter
from Tkinter import *
import tkMessageBox
from chimera import replyobj
import chimera
import airsIO


try:
	import chimera
	from chimera.baseDialog import ModelessDialog
	import VolumeViewer
except:
	print "Chimera not found"
	ModelessDialog=Tkinter.Window
	
class skeleton(ModelessDialog):
	name = "skeleton ui"
	buttons = ("Apply","Close")
	title = "SSE Skeleton"
	direman=os.environ["HOME"]
	hellp = os.path.join(os.environ['EMANDIR'],"doc/AIRS/sse-help.htm")
	help = hellp
	
	def targetSelector(self):
		names=airsIO.getVolumeNames()
		self.targetButton.setitems(names)
		
	def fileSelector(self):
		##generate list of open files
                self.names=[] 
		self.names.append("None")
		self.files=chimera.openModels.list(modelTypes = [chimera.Molecule])
                if len(self.files) != 0:
                        for mol in self.files:
                               self.names.append(mol.name) 
                else:
                        self.files=[]
		self.fileButton.setitems(self.names)
	
	def fillInUI(self, parent):
		##setup frames for inputs
		self.frame0=Tkinter.Frame(parent, bd=2, relief=GROOVE)
		self.frame0.grid(column=0,row=0, sticky=EW)
		self.frame1=Tkinter.Frame(self.frame0, relief=GROOVE)
		self.frame1.grid(column=0,row=0, sticky=EW)
		self.frame2=Tkinter.Frame(parent, bd=2, relief=GROOVE)
		self.frame2.grid(column=0,row=1, sticky=EW)
		
		Label(self.frame1, text='input MRC file:   ').grid(row=0, sticky=W)
		self.target=StringVar()
		self.targetButton=Pmw.OptionMenu(self.frame1,labelpos=W, menubutton_textvariable=self.target)
		self.targetButton.grid(row=0, column=1, sticky=W)
		self.targetSelector()
		
		Label(self.frame1, text='input psuedoatoms:').grid(row=1, sticky=W)
		self.atoms=StringVar()
		self.fileButton=Pmw.OptionMenu(self.frame1,labelpos=W, menubutton_textvariable=self.atoms)
		self.fileButton.grid(row=1, column=1, sticky=W)
		self.fileSelector()
		
		self.skeleton=IntVar()
		ske = Checkbutton(self.frame1, text="skeleton only", variable=self.skeleton).grid(row=2, column=0, sticky=W)
		self.sse=IntVar()
		sse = Checkbutton(self.frame1, text="sse only", variable=self.sse).grid(row=2, column=1, sticky=W)
		
		Label(self.frame2, text='angstrom/pixel:').grid(row=0, column=0, sticky=W)
		Label(self.frame2, text='resolution:    ').grid(row=1, column=0, sticky=W)
		Label(self.frame2, text='threshold:     ').grid(row=2, column=0, sticky=W)
		Label(self.frame2, text='helix size:    ').grid(row=0, column=3, sticky=W)
		Label(self.frame2, text='sheet size:    ').grid(row=1, column=3, sticky=W)
		self.apix = Entry(self.frame2, width = 6)
		self.apix.grid(row=0, column=1, sticky=W)
		self.res = Entry(self.frame2, width = 6)
		self.res.grid(row=1, column=1, sticky=W)		
		self.thresh = Entry(self.frame2, width = 6)
		self.thresh.grid(row=2, column=1, sticky=W)
		self.helixsize = Entry(self.frame2, width = 6)
		self.helixsize.grid(row=0, column=4, sticky=W)
		self.sheetsize = Entry(self.frame2, width = 6)
		self.sheetsize.grid(row=1, column=4, sticky=W)
		
		
	def Apply(self):
		target=airsIO.cleanFileName(str(self.target.get()))
		targetPath=airsIO.getPath(target)
		t=os.path.splitext(target)
		targetPRE=str(t[0])

		pseudoatoms=str(self.atoms.get())
		apix=float(self.apix.get())
		thresh=float(self.thresh.get())
		res=float(self.res.get())
		
		sseFLAG=self.sse.get()
		skeFLAG=self.skeleton.get()

		print "Generating skeletons on %s where pseudoatoms are %s. apix: %f threshold: %f resolution: %f skeletons: %d sse: %d"%(targetPath,pseudoatoms,apix,thresh,res,skeFLAG,sseFLAG)
		
		if pseudoatoms=="None":
			pseudoatoms="%s-atoms.pdb"%(targetPRE)
			cmd0="pseudoatom.py %s %s %f %f %f"%(targetPath, pseudoatoms, apix, res, thresh)
			print cmd0
			os.system(cmd0)
		else:
			pseudoatomsPath=airsIO.getPath(pseudoatoms)
			
		helixsize=float(self.helixsize.get())
		sheetsize=float(self.sheetsize.get())	

		mode=6		
		if skeFLAG==1 and sseFLAG==0:
			mode=4
		elif skeFLAG==0 and sseFLAG==1:
			mode=5
		outfile="%s-score.pdb"%(targetPRE)
		cmd1="skeleton %d %s %s %f  %f %f %f %s"%(mode,targetPath, pseudoatoms, apix, thresh, helixsize, sheetsize, outfile)
		print cmd1
		os.system(cmd1)
		
		if mode==4 or mode==6:
			helixout="%s_helix.mrc"%(targetPRE)
			chimera.openModels.open(helixout)
			sheetout="%s_sheet.mrc"%(targetPRE)
			chimera.openModels.open(sheetout)
			skeletonout="%s_skeleton.mrc"%(targetPRE)
			chimera.openModels.open(skeletonout)
		if mode==5 or mode==6:
			chimera.openModels.open(outfile)

try:
	chimera.dialogs.register(skeleton.name, skeleton)
except: pass

dialog = None

def gui():
	"""This is a Chimera specfic function to support instantiation of the dialog"""
	global dialog
	if not dialog:
		dialog = skeleton()
	dialog.enter()

def Refresh(self, *triggerArgs, **kw):
	if ('model list change' in triggerArgs[-1].reasons) :
		dialog.fileSelector()
		dialog.targetSelector()
triggerOpenModels = chimera.triggers.addHandler('OpenModels', Refresh, None)			
