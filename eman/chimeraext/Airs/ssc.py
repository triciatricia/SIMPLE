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


class ssc(ModelessDialog):
	name = "ssc ui"
	buttons = ("Apply","Close")
	title = "Secondary Structure Element Hunter"
	direman=os.environ["HOME"]
	hellp = "%s/EMAN/doc/hh3c_help.html"%(direman)
	help = hellp

	def targetSelector(self):
		##generate list of open volume files
		self.targets=[]
		self.targets=map(lambda x:x.name,chimera.openModels.list())
		self.targetButton.setitems(self.targets)

	def hhSelector(self):
		##generate list of open volume files
		self.hhselector=[]
		self.hhnames=[]
		self.hhnames.append("None")
		from VolumeViewer import Volume
                self.hhselector=[m for m in chimera.openModels.list()
				 if isinstance(m, Volume)]
                for volume in self.hhselector:
                        self.hhnames.append(volume.name)           
		self.intButton.setitems(self.hhnames)
				
	def fillInUI(self, parent):
		##setup frames for inputs
		self.frame0=Tkinter.Frame(parent, bd=2, relief=GROOVE)
		self.frame0.grid(column=0,row=0, sticky=EW)
		self.frame12=Tkinter.Frame(parent, bd=2, relief=GROOVE)
		self.frame12.grid(column=0,row=1, sticky=EW)
		self.frame1=Tkinter.Frame(self.frame12, bd=2, relief=FLAT)
		self.frame1.grid(column=0,row=0, sticky=EW)
		self.frame3=Tkinter.Frame(parent, bd=2, relief=GROOVE)
		self.frame3.grid(column=0,row=2, sticky=EW)		
		self.frame4=Tkinter.Frame(parent, bd=2, relief=GROOVE)
		self.frame4.grid(column=0,row=3, sticky=EW)	
		
		##Target Selection
		Label(self.frame0, text='target file:').grid(row=0, column=0, sticky=W)
		self.target=StringVar()
		self.targetButton=Pmw.OptionMenu(self.frame0,labelpos=W, menubutton_textvariable=self.target)
		self.targetButton.grid(row=0, column=1, sticky=W)
		self.targetSelector()
		Label(self.frame0, text='coefficient file:').grid(row=1, column=0, sticky=W)
		self.intfile=StringVar()
		self.intButton=Pmw.OptionMenu(self.frame0,labelpos=W, menubutton_textvariable=self.intfile)
		self.intButton.grid(row=1, column=1, sticky=W)
		self.hhSelector()
				
		##Required parameters
		Label(self.frame1, text='Required Parameters').grid(row=0, column=0, sticky=W)
		apix=StringVar()
		Label(self.frame1, text='angstrom/pixel').grid(row=1, column=0, sticky=W)
		self.apix = Entry(self.frame1, width = 6, textvariable=apix)
		self.apix.grid(row=1, column=1, sticky=W)
		apix.set("1")
		res=StringVar()
		Label(self.frame1, text='resolution').grid(row=1, column=3, sticky=W)
		self.res = Entry(self.frame1, width = 6, textvariable=res)
		self.res.grid(row=1, column=4, sticky=W)
		res.set("6")
		thr=StringVar()
		Label(self.frame1, text='threshold').grid(row=2, column=0, sticky=W)
		self.thr = Entry(self.frame1, width = 6, textvariable=thr)
		self.thr.grid(row=2, column=1, sticky=W)
		thr.set("1")
		
		##optional parameters
		Label(self.frame3, text='SSE output options').grid(row=0, column=0, sticky=W)
		
		self.autoassign=IntVar()
		a = Checkbutton(self.frame3, text="Auto assign", variable=self.autoassign).grid(row=1, column=0, sticky=W)
		self.percen=IntVar()
		h = Checkbutton(self.frame3, text="Assign by Percent", variable=self.percen).grid(row=1, column=1, sticky=W)
		
		Hvalue=StringVar()
		Label(self.frame3, text='Helix').grid(row=2, column=0, sticky=W)
		self.Hvalue = Entry(self.frame3, width = 6, textvariable=Hvalue)
		self.Hvalue.grid(row=2, column=1, sticky=W)
		Hvalue.set("2")
		Bvalue=StringVar()
		Label(self.frame3, text='Sheet').grid(row=2, column=2, sticky=W)
		self.Bvalue = Entry(self.frame3, width = 6, textvariable=Bvalue)
		self.Bvalue.grid(row=2, column=3, sticky=W)
		Bvalue.set("-2")

	def Apply(self):
		target=str(self.target.get())
		targetPath=airsIO.getPath(target)
		t=os.path.splitext(target)
		targetNAME=str(t[0])
		
		hhint=str(self.intfile.get())
		if hhint != "None":
			hhinfile=airsIO.getPath(hhint)	
		auto=int(self.autoassign.get())
		percen=int(self.percen.get())
		
		apix=float(self.apix.get())
		res=float(self.res.get())
		Hvalue=float(self.Hvalue.get())
		Bvalue=float(self.Bvalue.get())
		thr=float(self.thr.get())

		logfile="log_%s_%f_%f.txt"%(targetNAME,Hvalue,Bvalue)

		if hhint=="None":
			if percen==1:
				cmd0="ssehunter2.py %s %f %f thr=%f helixcutoff=%f sheetcutoff=%f percen > %s"%(targetPath,apix,res,thr,Hvalue,Bvalue,logfile)
			else:
				cmd0="ssehunter2.py %s %f %f thr=%f helixcutoff=%f sheetcutoff=%f > %s"%(targetPath,apix,res,thr,Hvalue,Bvalue,logfile)
		else:
			if  percen==1:
				cmd0="ssehunter2.py %s %f %f thr=%f helixcutoff=%f sheetcutoff=%f hh=%s percen >%s"%(targetPath,apix,res,thr,Hvalue,Bvalue,hhinfile,logfile)
			else:
				cmd0="ssehunter2.py %s %f %f thr=%f helixcutoff=%f sheetcutoff=%f hh=%s >%s"%(targetPath,apix,res,thr,Hvalue,Bvalue,hhinfile,logfile)
				
		print cmd0
		os.system(cmd0)

		hfile="helix.pdb"
		bfile="sheet.pdb"
		scorefile="score-%s.pdb"%(targetNAME)
		chimera.openModels.open(scorefile)
		
		if auto==1 or percen==1:
			chimera.openModels.open(hfile)
			chimera.openModels.open(bfile)


try:
	chimera.dialogs.register(ssc.name, ssc)
except: pass

dialog = None

def gui():
	"""This is a Chimera specfic function to support instantiation of the dialog"""
	global dialog
	if not dialog:
		dialog = ssc()
	dialog.enter()

def Refresh(self, *triggerArgs, **kw):
	if ('model list change' in triggerArgs[-1].reasons) :
		dialog.targetSelector()
		dialog.hhSelector()
triggerOpenModels = chimera.triggers.addHandler('OpenModels', Refresh, None)
