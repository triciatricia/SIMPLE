import os
import sys
import string
#import EMAN
import commands
import math
import re
import shutil
from math import *
from sys import argv
import Tkinter
from Tkinter import *
import tkMessageBox
import Pmw
import airsIO

try:
	import chimera
	from chimera.baseDialog import ModelessDialog
	import VolumeViewer
except:
	print "Chimera not found"
	ModelessDialog=Tkinter.Window
	
class pdb2cmm(ModelessDialog):
	name = "pdb2cmm ui"
	buttons = ("Generate","Close")
	title = "PDB2CMM"
	direman=os.environ["HOME"]
	hellp = "%s/EMAN/doc/sseb_help.html"%(direman)
	help = hellp

	def fileselector(self):
		##generate list of open files
		names=airsIO.getPDBNames()
		self.fileButton.setitems(names)
			
	def fillInUI(self, parent):

				
		self.frame0=Tkinter.Frame(parent, bd=2, relief=GROOVE)
		self.frame0.grid(column=0,row=0, columnspan=2, sticky=EW)				
		
		Label(self.frame0, text='input file:').grid(row=0, column=0, sticky=W)
		self.infile=StringVar()
		self.fileButton=Pmw.OptionMenu(self.frame0,labelpos=W, menubutton_textvariable=self.infile)
		self.fileButton.grid(row=0, column=1, sticky=E)
		self.fileselector()

	def Generate(self):
		target=airsIO.cleanFileName(str(self.infile.get()))
		targetPath=airsIO.getPath(target)
		t=os.path.splitext(target)
		targetPRE=str(t[0])
		
		self.selectionlist=[]
		atoms=""
		selected=chimera.selection.currentAtoms()
		for i in selected:
			atoms=atoms+str(i.serialNumber)+","
		print atoms
		outfile="%s.cmm"%(targetPRE)
		cmd1="pdb2cmm.py %s %s cmm %s"%(targetPath,outfile,atoms[0:-1].strip())
		print cmd1
		os.system(cmd1)
		chimera.openModels.open(outfile)


try:
	chimera.dialogs.register(pdb2cmm.name, pdb2cmm)
except: pass

dialog = None

def gui():
	"""This is a Chimera specfic function to support instantiation of the dialog"""
	global dialog
	if not dialog:
		dialog = pdb2cmm()
	dialog.enter()
def Refresh(self, *triggerArgs, **kw):
	if ('model list change' in triggerArgs[-1].reasons) : dialog.fileselector()

triggerOpenModels = chimera.triggers.addHandler('OpenModels', Refresh, None)
