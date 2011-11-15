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
	
class morph(ModelessDialog):
	name = "morph ui"
	buttons = ("Generate","Close")
	title = "morph"
	direman=os.environ["HOME"]
	hellp = "%s/EMAN/doc/sseb_help.html"%(direman)
	help = hellp

        def pdbpath(self, pdb):
                info=pdb.openedAs
                return info[0]

	def fileselector(self):
		##generate list of open files
                self.names=[] 
		self.files=chimera.openModels.list(modelTypes = [chimera.Molecule])
                if len(self.files) != 0:
                        for mol in self.files:

                               self.names.append(mol.marker_set.file_path) 
                else:
                        self.files=[]
		self.fileButton.setitems(self.names)
			
	def fillInUI(self, parent):

				
		self.frame0=Tkinter.Frame(parent, bd=2, relief=GROOVE)
		self.frame0.grid(column=0,row=0, columnspan=2, sticky=EW)				
		
		Label(self.frame0, text='CMM file1:').grid(row=0, column=0, sticky=W)
		self.infile1=StringVar()
		self.fileButton=Pmw.OptionMenu(self.frame0,labelpos=W, menubutton_textvariable=self.infile1)
		self.fileButton.grid(row=0, column=1, sticky=E)
		self.fileselector()
		
		Label(self.frame0, text='CMM file2:').grid(row=1, column=0, sticky=W)
		self.infile2=StringVar()
		self.fileButton=Pmw.OptionMenu(self.frame0,labelpos=W, menubutton_textvariable=self.infile2)
		self.fileButton.grid(row=1, column=1, sticky=E)
		self.fileselector()
		
		Label(self.frame0, text='steps').grid(row=2, column=0, sticky=W)
		self.steps = Entry(self.frame0, width = 5)
		self.steps.grid(row=2, column=1, sticky=W)

	def Generate(self):
		target1=str(self.infile1.get())
		target1PATH=airsIO.getPath(target1)
		target2=str(self.infile2.get())
		target2PATH=airsIO.getPath(target2)
	
		cmd1="cmm-morph.py %s %s %d"%(target1PATH,target2PATH,int(self.steps.get()))
		print cmd1
		os.system(cmd1)
		counter=0
		while counter < int(self.steps.get()):
			openfile="morph-%s-%s-%d.cmm"%(target1PATH,target2PATH,counter)
			chimera.openModels.open(openfile)
			counter=counter+1


try:
	chimera.dialogs.register(morph.name, morph)
except: pass

dialog = None

def gui():
	"""This is a Chimera specfic function to support instantiation of the dialog"""
	global dialog
	if not dialog:
		dialog = morph()
	dialog.enter()
def Refresh(self, *triggerArgs, **kw):
	if ('model list change' in triggerArgs[-1].reasons) : dialog.fileselector()

triggerOpenModels = chimera.triggers.addHandler('OpenModels', Refresh, None)
