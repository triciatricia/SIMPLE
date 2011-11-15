import os
import sys
import Pmw
import Tkinter
from Tkinter import *
import tkMessageBox
import chimera
import VolumeViewer
import airsIO

try:
	import chimera
	from chimera.baseDialog import ModelessDialog
except:
	print "Chimera not found"
	ModelessDialog=Tkinter.Window

class filters(ModelessDialog):
	name = "bfc ui"
	buttons = ("Close")
	title = "filters"
	direman=os.environ["HOME"]
	hellp = "%s/EMAN/doc/blfilt_help.html"%(direman)
	help = hellp

	def fileselector(self):
		##generate list of open volume files
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
		self.frame3=Tkinter.Frame(parent, bd=2, relief=GROOVE)
		self.frame3.grid(column=0,row=3, sticky=EW)
		
		Label(self.frame0, text='file:').grid(row=0, column=0, sticky=W)
		self.infile=StringVar()
		self.fileButton=Pmw.OptionMenu(self.frame0,labelpos=W, menubutton_textvariable=self.infile)
		self.fileButton.grid(row=0, column=1, sticky=W)
		self.fileselector()
		
		Label(self.frame1, text='Bilateral Filter').grid(row=0, sticky=W)
		Label(self.frame1, text='sigma1').grid(row=1, sticky=W)
		sigma1=StringVar()
		self.sigma1 = Entry(self.frame1, textvariable=sigma1, width = 8)
		sigma1.set("0")
		self.sigma1.grid(row=1, column=1, sticky=W)
		
		Label(self.frame1, text='sigma2').grid(row=2, sticky=W)
		sigma2=StringVar()
		self.sigma2 = Entry(self.frame1, textvariable=sigma2, width = 8)
		sigma2.set("0")		
		self.sigma2.grid(row=2, column=1, sticky=W)
		
		Label(self.frame1, text='iter').grid(row=3, sticky=W)
		iteration=StringVar()
		self.iteration = Entry(self.frame1, textvariable=iteration, width = 8)
		iteration.set("0")
		self.iteration.grid(row=3, column=1, sticky=W)		
		
		Label(self.frame1, text='width').grid(row=4, sticky=W)		
		wid=StringVar()
		self.wid = Entry(self.frame1, textvariable=wid, width = 8)
		wid.set("0")
		self.wid.grid(row=4, column=1, sticky=W)
		Button(self.frame1,text='Filter', command=self.bf).grid(row=5, column=0, sticky=W)

		Label(self.frame2, text='High/Low Pass Filter').grid(row=0, sticky=W)
		Label(self.frame2, text='apix').grid(row=1, sticky=W)
		apix=StringVar()
		self.apix = Entry(self.frame2, textvariable=apix, width = 8)
		apix.set("1")
		self.apix.grid(row=1, column=1, sticky=W)
		
		Label(self.frame2, text='radius').grid(row=2, sticky=W)
		filterRadius=StringVar()
		self.filterRadius = Entry(self.frame2, textvariable=filterRadius, width = 8)
		filterRadius.set("1")
		self.filterRadius.grid(row=2, column=1, sticky=W)
		Button(self.frame2,text='High Pass', command=self.hp).grid(row=3, column=0, sticky=W)
		Button(self.frame2,text='Low Pass', command=self.lp).grid(row=3, column=1, sticky=W)
		
		Label(self.frame3, text='Median Filter').grid(row=0, sticky=W)
		Label(self.frame3, text='width').grid(row=1, sticky=W)		
		Mwid=StringVar()
		self.Mwid = Entry(self.frame3, textvariable=Mwid, width = 8)
		Mwid.set("3")
		self.Mwid.grid(row=1, column=1, sticky=W)
		Button(self.frame3,text='Filter', command=self.median).grid(row=2, column=0, sticky=W)
		
	def hp(self):
	    	filename = airsIO.cleanFileName(str(self.infile.get()))
		filepath=airsIO.getPath(filename)
		apix= str(self.apix.get())
		filterRadius=str(self.filterRadius.get())

		outfile="hp-%s"%(filename.strip())
		cmd0='proc3d %s %s hp=%s,%s'%(filepath,outfile,apix, filterRadius)
		print cmd0
		os.system(cmd0)
		
		chimera.openModels.open(outfile)
				
	def lp(self):
	    	filename = airsIO.cleanFileName(str(self.infile.get()))
		filepath=airsIO.getPath(filename)
		apix= str(self.apix.get())
		filterRadius=str(self.filterRadius.get())


		outfile="lp-%s"%(filename.strip())
		cmd0='proc3d %s %s lp=%s,%s'%(filepath,outfile,apix, filterRadius)
		print cmd0
		os.system(cmd0)
		
		chimera.openModels.open(outfile)

	def bf(self):
		filename = airsIO.cleanFileName(str(self.infile.get()))
		filepath=airsIO.getPath(filename)
       		sigma1= str(self.sigma1.get())
		sigma2=str(self.sigma2.get())
		iteration=int(self.iteration.get())
		width=str(self.wid.get())
	
		outfile="bf-%s"%(filename.strip())
		cmd0='proc3d %s %s blfilt=%s,%s,%d,%s'%(filepath,outfile,sigma1,sigma2,iteration,width)
		print cmd0
		os.system(cmd0)
		
		chimera.openModels.open(outfile)

	def median(self):
	    	filename = airsIO.cleanFileName(str(self.infile.get()))
		filepath=airsIO.getPath(filename)
		width=str(self.Mwid.get())

		outfile="median-%s"%(filename.strip())
		cmd0='proc3d %s %s rfilt=20,%s'%(filepath,outfile,width)
		print cmd0
		os.system(cmd0)
		
		chimera.openModels.open(outfile)

try:
	chimera.dialogs.register(filters.name, filters)
except: pass

dialog = None

def gui():
	"""This is a Chimera specfic function to support instantiation of the dialog"""
	global dialog
	if not dialog:
		dialog = filters()
	dialog.enter()

def Refresh(self, *triggerArgs, **kw):
	if ('model list change' in triggerArgs[-1].reasons) :
                dialog.fileselector()

triggerOpenModels = chimera.triggers.addHandler('OpenModels', Refresh, None)
		
		
		
		
