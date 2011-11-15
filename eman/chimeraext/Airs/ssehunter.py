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
	
class ssehunter(ModelessDialog):
	name = "ssehunter ui"
	buttons = ("Apply","Close")
	title = "SSEhunter"
	direman=os.environ["HOME"]
	hellp = os.path.join(os.environ['EMANDIR'],"doc/AIRS/sse-help.htm")
	help = hellp
	
	def targetSelector(self):
		self.targetnames=airsIO.getVolumeNames()   
		self.targetButton.setitems(self.targetnames)

	def coeffSelector(self):
		coeffnames=airsIO.getVolumeNames() 
		coeffnames.append("None")
		self.coeffButton.setitems(coeffnames)		
	
	def atomSelector(self):
		##generate list of open files
		atomnames=airsIO.getPDBNames()
		atomnames.append("None")
		self.atomButton.setitems(atomnames)
		
	
	def fillInUI(self, parent):
		##setup frames for inputs
		self.frame0=Tkinter.Frame(parent, bd=2, relief=GROOVE)
		self.frame0.grid(column=0,row=0, sticky=EW)
		self.frame1=Tkinter.Frame(self.frame0, relief=GROOVE)
		self.frame1.grid(column=0,row=0, sticky=EW)
		self.frame2=Tkinter.Frame(parent, bd=2, relief=GROOVE)
		self.frame2.grid(column=0,row=1, sticky=EW)
		
		Label(self.frame1, text='MRC file:   ').grid(row=0, sticky=W)
		self.target=StringVar()
		self.targetButton=Pmw.OptionMenu(self.frame1,labelpos=W, menubutton_textvariable=self.target)
		self.targetButton.grid(row=0, column=1, sticky=W)
		self.targetSelector()
		
		Label(self.frame1, text='psuedoatoms file:').grid(row=1, sticky=W)
		self.atoms=StringVar()
		self.atomButton=Pmw.OptionMenu(self.frame1,labelpos=W, menubutton_textvariable=self.atoms)
		self.atomButton.grid(row=1, column=1, sticky=W)
		self.atomSelector()
		
		Label(self.frame1, text='correlation file:').grid(row=2, sticky=W)
		self.coeff=StringVar()
		self.coeffButton=Pmw.OptionMenu(self.frame1,labelpos=W, menubutton_textvariable=self.coeff)
		self.coeffButton.grid(row=2, column=1, sticky=W)
		self.coeffSelector()
		
		Label(self.frame2, text='angstrom/pixel:').grid(row=0, column=0, sticky=W)
		Label(self.frame2, text='resolution:    ').grid(row=1, column=0, sticky=W)
		Label(self.frame2, text='threshold:     ').grid(row=2, column=0, sticky=W)

		self.apix = Entry(self.frame2, width = 6)
		self.apix.grid(row=0, column=1, sticky=W)
		self.res = Entry(self.frame2, width = 6)
		self.res.grid(row=1, column=1, sticky=W)		
		self.thresh = Entry(self.frame2, width = 6)
		self.thresh.grid(row=2, column=1, sticky=W)		

		self.mapOri=IntVar()
		s = Checkbutton(self.frame2, text="Density map origin", variable=self.mapOri).grid(row=3, column=0, sticky=W)
		
	def Apply(self):
		target=airsIO.cleanFileName(str(self.target.get()))
		targetPath=airsIO.getPath(target)
		t=os.path.splitext(target)
		targetPRE=str(t[0])

		pseudoatoms=str(self.atoms.get())
		coeff=airsIO.cleanFileName(str(self.coeff.get()))
		apix=float(self.apix.get())
		thresh=float(self.thresh.get())
		res=float(self.res.get())
		
		mapinfo=airsIO.getMapInfo(target)
		mapSize=mapinfo[0][0]
		mapOrigin=mapinfo[1]  
		
		logfile="log-%s.txt"%(targetPRE)
		
		if coeff!="None":
			if pseudoatoms!="None":
				cmd1="ssehunter3.py %s %f %f %f coeff=%s atoms=%s > %s"%(target, apix, res, thresh, coeff, pseudoatoms, logfile)
			else:
				cmd1="ssehunter3.py %s %f %f %f coeff=%s > %s"%(target, apix, res, thresh, coeff, logfile)
		else:
			if pseudoatoms!="None":
				cmd1="ssehunter3.py %s %f %f %f atoms=%s > %s"%(target, apix, res, thresh, pseudoatoms, logfile)
			else:
				cmd1="ssehunter3.py %s %f %f %f > %s"%(target, apix, res, thresh, logfile)
		print cmd1
		os.system(cmd1)

		outfile="score-%s.pdb"%(targetPRE)
		if self.mapOri.get()==1:
			Ox=mapOrigin[0]
			Oy=mapOrigin[1]
			Oz=mapOrigin[2]			
			cmdt="procpdb.py %s %s trans=%f,%f,%f"%(outfile,outfile,Ox,Oy,Oz)
			os.system(cmdt)
		chimera.openModels.open(outfile)

try:
	chimera.dialogs.register(ssehunter.name, ssehunter)
except: pass

dialog = None

def gui():
	"""This is a Chimera specfic function to support instantiation of the dialog"""
	global dialog
	if not dialog:
		dialog = ssehunter()
	dialog.enter()

def Refresh(self, *triggerArgs, **kw):
	if ('model list change' in triggerArgs[-1].reasons) :
		dialog.atomSelector()
		dialog.targetSelector()
		dialog.coeffSelector()
triggerOpenModels = chimera.triggers.addHandler('OpenModels', Refresh, None)			
