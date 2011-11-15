import os
import sys
import shutil
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


class helixhunter(ModelessDialog):
	name = "hhc ui"
	buttons = ("Apply","Close")
	title = "helixhunter"
	direman=os.environ["HOME"]
	hellp = "%s/EMAN/doc/hh_help.html"%(direman)
	help = hellp
	
		
	def fileselector(self):
		names=airsIO.getVolumeNames()
		self.fileButton.setitems(names)
		
	def fillInUI(self, parent):
		##setup frames for inputs
		self.frame0=Tkinter.Frame(parent, bd=2, relief=GROOVE)
		self.frame0.grid(column=0,row=0, sticky=EW)
		self.frame1=Tkinter.Frame(parent, bd=2, relief=GROOVE)
		self.frame1.grid(column=0,row=1, sticky=EW)
		self.frame2=Tkinter.Frame(parent, bd=2, relief=GROOVE)
		self.frame2.grid(column=0,row=2, sticky=EW)
		
		##fileselctor window
		Label(self.frame0, text='input file:').grid(row=0, column=0, sticky=W)
		self.infile=StringVar()
		self.fileButton=Pmw.OptionMenu(self.frame0,labelpos=W, menubutton_textvariable=self.infile)
		self.fileButton.grid(row=0, column=1, sticky=W)
		self.fileselector()
		
		self.norm = IntVar()
		a = Checkbutton(self.frame2, text="normalize", variable=self.norm).grid(row=5, sticky=W)
		self.coeff = IntVar()
		b = Checkbutton(self.frame2, text="correlation", variable=self.coeff).grid(row=5, column=1, sticky=E)
		self.bf = IntVar()
		c=  Checkbutton(self.frame2, text="bilateral Filter", variable=self.bf).grid(row=6, column=0, sticky=E)

	
		Label(self.frame1, text='angstroms/pixel:').grid(row=1, sticky=W)
		Label(self.frame1, text='angular search:').grid(row=2, sticky=W)
		Label(self.frame1, text='correlation value:').grid(row=3, sticky=W)
		Label(self.frame2, text='Options').grid(row=4, sticky=W)
		Label(self.frame2, text='sigma1').grid(row=7, sticky=W)
		Label(self.frame2, text='sigma2').grid(row=8, sticky=W)
		Label(self.frame2, text='iteration').grid(row=9, sticky=W)
		Label(self.frame2, text='width').grid(row=10, sticky=W)
				

		self.apix = Entry(self.frame1, width = 8)
		da=StringVar()
		self.da = Entry(self.frame1, textvariable=da, width = 8)
		da.set("5")
		self.percen = Entry(self.frame1, width = 8)
		
		sigma1=StringVar()
		self.sigma1 = Entry(self.frame2, textvariable=sigma1, width = 8)
		sigma1.set("0")
		sigma2=StringVar()
		self.sigma2 = Entry(self.frame2, textvariable=sigma2, width = 8)
		sigma2.set("0")
		iter=StringVar()
		self.iter = Entry(self.frame2, textvariable=iter, width = 8)
		iter.set("0")
		wid=StringVar()
		self.wid = Entry(self.frame2, textvariable=wid, width = 8)
		wid.set("0")

		self.apix.grid(row=1, column=1, sticky=W)
		self.da.grid(row=2, column=1, sticky=W)
		self.percen.grid(row=3, column=1, sticky=W)
		self.sigma1.grid(row=7, column=1, sticky=W)
		self.sigma2.grid(row=8, column=1, sticky=W)
		self.iter.grid(row=9, column=1, sticky=W)
		self.wid.grid(row=10, column=1, sticky=W)
		
		return self.infile

	def Apply(self):
	    	inputfile = airsIO.cleanFileName(str(self.infile.get()))
		fullPath=airsIO.getPath(inputfile)
		shutil.copy(fullPath, 'hh.mrc')
		a=os.path.splitext(inputfile)
		name=str(a[0])
		
		apix=float(self.apix.get())
		da = float(self.da.get())
		percen = float(self.percen.get())
		
		if self.bf.get()==1:
			sigma1= float(self.sigma1.get())
			sigma2=float(self.sigma2.get())
			it=int(self.iter.get())
			width=float(self.wid.get())
		else:
			sigma1=0
			sigma2=0
			it=0
			width=0		 
		
		if (self.norm.get()==1):
			print "Normalizing map"
			cmd2="proc3d hh.mrc hh.mrc norm"
			os.system(cmd2)
	
		if (it>=1):
			print "Filtering Map"
			cmd3="proc3d hh.mrc hh.mrc blfilt=%f,%f,%d,%f"%(sigma1,sigma2,iter,width)
			os.system(cmd3)
			
		print "Running helixhunter2"
		file0="hh2-%s-%f"%(name,percen)
		if (self.coeff.get()==1):
			cmd4="helixhunter2 hh.mrc %s.iv %f percen=%f docylccffirst int=int-%s dejavu=%s.sse da=%d minlen=8 maxlen=50"%(file0, apix, percen, name, file0, da)
			os.system(cmd4)	
		else:
			cmd4="helixhunter2 hh.mrc %s.iv %f percen=%f dejavu=%s.sse minlen=8 maxlen=50 da=%d"%(file0, apix, percen, file0, da)
			os.system(cmd4)

		print "Saving results as a PDB file"

		trash=["hh.mrc"]
		airsIO.cleanTempFiles(trash)

		file1="%s.sse"%(file0)
		file2="%s.pdb"%(file0)
		
		check=os.path.exists(file1)
		if check==1:
			cmd5="dejavu2pdb.py %s %s"%(file1, file2)
			os.system(cmd5)
			chimera.openModels.open(file2)

try:
	chimera.dialogs.register(helixhunter.name, helixhunter)
except: pass

dialog = None

def gui():
	"""This is a Chimera specfic function to support instantiation of the dialog"""
	global dialog
	if not dialog:
		dialog = helixhunter()
	dialog.enter()

def Refresh(self, *triggerArgs, **kw):
	if ('model list change' in triggerArgs[-1].reasons) : dialog.fileselector()

triggerOpenModels = chimera.triggers.addHandler('OpenModels', Refresh, None)

