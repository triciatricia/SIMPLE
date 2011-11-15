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
	
class cmm2pdb(ModelessDialog):
	name = "cmm2pdb ui"
	buttons = ("Generate","Close")
	title = "CMM2PDB"
	direman=os.environ["HOME"]
	hellp = "%s/EMAN/doc/sseb_help.html"%(direman)
	help = hellp

	def fileselector(self):
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
		target=str(self.infile.get())
		t=target.split()
		targetPath=str(t[-1])
		outfile="cmm-marker.pdb"
		cmd1="cmm2pdb.py %s %s"%(targetPath,outfile)
		print cmd1
		os.system(cmd1)
		chimera.openModels.open(outfile)


try:
	chimera.dialogs.register(cmm2pdb.name, cmm2pdb)
except: pass

dialog = None

def gui():
	"""This is a Chimera specfic function to support instantiation of the dialog"""
	global dialog
	if not dialog:
		dialog = cmm2pdb()
	dialog.enter()
def Refresh(self, *triggerArgs, **kw):
	if ('model list change' in triggerArgs[-1].reasons) : dialog.fileselector()

triggerOpenModels = chimera.triggers.addHandler('OpenModels', Refresh, None)
