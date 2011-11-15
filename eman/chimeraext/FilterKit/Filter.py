import os
import Tix
from pprint import pprint
from time import time
import Modules
import Memory
import SimpleSession
from PIL import Image
from CGLtk.color import ColorWell
try:
	import EMAN
except:
	print "EMAN python library missing"

try:
	import chimera
	from chimera.baseDialog import ModelessDialog
except:
	print "Chimera Not found"
	ModelessDialog=Tix.Window

class SimplePlot(Tix.Canvas) :

	def __init__(self,parent):
		Tix.Canvas.__init__(self,parent,scrollregion=(-50,-50,400,200),width=450,height=250)

def glpfilt(image):
	return 0

def ghpfilt(image):
	return 0

def atlpfilt(image):
	return 0

filterlist=[("Gaussian Lowpass",glpfilt),("Gaussian Highpass",ghpfilt),("Arctan Lowpass",atlpfilt)]

class FilterDialog(ModelessDialog):
	name = "EMAN Filter UI"
	buttons = ("Close")
	title = "Filter"
#    help = ("ExtensionUI.html", ExtensionUI)

	def fillInUI(self, parent):
		"This defines the user interface for the interactive filtration module"

		self.frame1=Tix.Frame(parent,relief="sunken",borderwidth=3)
		self.frame1.grid(column=0,row=0,columnspan=2)
		self.f1buts=[]
		self.refreshModules()

		self.plot=SimplePlot(self.frame1)
		self.plot.grid(row=0,column=0,sticky="nsew")
		self.frame1.rowconfigure(0,weight=1)
		self.frame1.columnconfigure(0,weight=1)

		self.frame2=Tix.Frame(parent)
		self.frame2.grid(column=0,row=1,sticky="ns")

		self.filtselW=[]
		self.filtsel=[]
		self.filtvalW=[]
		self.filtval=[]
		for i in range(len(filterlist)):
			self.filtsel.append(Tix.IntVar())
			self.filtselW.append(Tix.CheckButton(self.frame2,text=filterlist[i][0],variable=self.filtsel[i],command=self.refresh))
			self.filtselW[i].grid(row=0, column=i,sticky="e")
			self.filtval.append(Tix.DoubleVar())
			self.filtvalW.append(Tix.Control(self.frame2,autorepeat="true",integer="false",label="Parm",min="0",step="1",variable=self.filtval[i])
			self.filtvalW.grid(row=0, column=4)
			self.viltvalW.set(15.0)

		parent.rowconfigure(0,weight=1)
		parent.rowconfigure(1,weight=0)
		parent.columnconfigure(0,weight=1)

	def refresh(self):
		"Refresh the plot display"
		return 0

try:
	chimera.dialogs.register(FilterDialog.name, FilterDialog)
except: pass



single = None

def gui():
	global single
	if not single:
		single = FilterDialog()
	single.enter()

