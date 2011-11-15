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
	
class ssebuilder(ModelessDialog):
	name = "ssebuilder ui"
#	buttons = ("Add","Delete","Build","Close")
	buttons = ("Build","Close")
	title = "SSE Builder"
	direman=os.environ["HOME"]
	hellp = "%s/EMAN/doc/sseb_help.html"%(direman)
	help = hellp

#        def pdbpath(self, pdb):
#                info=pdb.openedAs
#                return info[0]

	def fileselector(self):
		##generate list of open files
		names=airsIO.getPDBNames()
		self.fileButton.setitems(names)
		
	def addtoatomlist(self):
		i=0
		self.selectedAtoms=[]
		while i < self.lenselected:
			self.selectedAtoms.append(chimera.selection.currentAtoms()[i].serialNumber)
			i=i+1
		self.selectedAtoms.sort()
	
		chain=self.chainid.get()
		sse=self.var.get()
		atoms=self.selectedAtoms

		self.chainlist.append(chain)
		self.sselist.append(sse)
		self.atomlist.append(atoms)
		
		text=[sse, chain, atoms]
		self.displayinfo.append(text)
		self.combobox.component("scrolledlist").setlist(self.displayinfo)
		
	def removefromatomlist(self):
		currentitem=self.combobox.get()
		j=0
		while j< len(self.displayinfo):
			print self.displayinfo[j]
			if self.displayinfo[j]==eval(currentitem):
				removeindex=j
			j=j+1
		del self.displayinfo[removeindex]
		self.combobox.component("scrolledlist").setlist(self.displayinfo)
		
	def displayselected(self):
		showitem=eval(self.combobox.get())
		h=0
		while h < len(self.selectionlist):
			i=0
			selection=self.selectionlist[h]
			compareselection=[]
			while i < len(selection):
				compareselection.append(selection[i].serialNumber)
				i=i+1
			compareselection.sort()
			if compareselection==showitem[2]:
				chimera.selection.setCurrent(selection)
			h=h+1
			
	def fillInUI(self, parent):
		self.chainlist=[]
		self.atomlist=[]
		self.sselist=[]
		self.displayinfo=[]
		self.selectionlist=[]

		self.frame0=Tkinter.Frame(parent)
#		self.frame0.grid(column=0,row=0, columnspan=1, sticky=EW)
		
	        nb = Pmw.NoteBook(self.frame0)
#               nb.pack(expand=1, fill=Tkinter.BOTH)
		nb.pack(expand=1, fill='both', padx=5, pady=5)

                self.notebook = nb
                nb.add('page1', tab_text='SSEBuilder')
                self.pageFrame1 = nb.page('page1')
                nb.add('page2', tab_text='Options')
                self.pageFrame2 = nb.page('page2')			

		self.frame1 = Tkinter.Frame(self.pageFrame1, bd=2, relief=GROOVE)
                self.frame1.grid(column=0, row=0, sticky=EW)
                self.frame2 = Tkinter.Frame(self.pageFrame1, bd=2, relief=GROOVE)
                self.frame2.grid(column=0, row=1, sticky=EW)
		self.frame3 = Tkinter.Frame(self.pageFrame1, bd=2, relief=GROOVE)
                self.frame3.grid(column=0, row=2, sticky=EW)
		
                self.frame4 = Tkinter.Frame(self.pageFrame2, bd=2, relief=GROOVE)
                self.frame4.grid(column=0, row=0, sticky=EW)
		self.frame5 = Tkinter.Frame(self.pageFrame2, bd=2, relief=GROOVE)
                self.frame5.grid(column=0, row=1, sticky=EW)
                self.frame6 = Tkinter.Frame(self.pageFrame2, bd=2, relief=GROOVE)
                self.frame6.grid(column=0, row=2, sticky=EW)	
		
                self.frame0.pack(fill='both',expand=1)
                self.frame1.pack(fill='both',expand=1)
                self.frame2.pack(fill='both',expand=1)
                self.frame3.pack(fill='both',expand=1)
                self.frame4.pack(fill='both',expand=1)
                self.frame5.pack(fill='both',expand=1)			
		self.frame6.pack(fill='both',expand=1)
		
		Label(self.frame1, text='input file:').grid(row=0, column=0, sticky=W)
		self.infile=StringVar()
		self.fileButton=Pmw.OptionMenu(self.frame1,labelpos=W, menubutton_textvariable=self.infile)
		self.fileButton.grid(row=0, column=1, sticky=E)
		self.fileselector()
		
		self.combobox=Pmw.ComboBox(self.frame2, label_text='SSE', labelpos='wn', dropdown=0, scrolledlist_items=self.displayinfo)
		self.combobox.grid(row=0, column=0, sticky=W)

		Label(self.frame3, text='ID').grid(row=0, column=0, sticky=W)
		self.chainid = Entry(self.frame3, width = 5)
		self.chainid.grid(row=0, column=1, sticky=W)
		Button(self.frame3,text='Show', command=self.displayselected).grid(row=3, column=0, sticky=W)
		Button(self.frame3,text='Add', command=self.Add).grid(row=1, column=0, sticky=W)
		Button(self.frame3,text='Delete', command=self.Delete).grid(row=2, column=0, sticky=W)
		self.var= StringVar()
		for text in [('Helix'), ('Sheet'), ('Coil')]:
			Radiobutton(self.frame3, text=text, value=text, variable=self.var).grid(sticky=W)
		self.var.set('Coil')

		Label(self.frame4, text='Helix Color').grid(row=0, column=0, sticky=W)
		Label(self.frame4, text='Red').grid(row=1, column=0, sticky=W)
		helixRed=StringVar()
		self.helixRed = Entry(self.frame4, width = 5, textvariable=helixRed)
		helixRed.set("0")
		self.helixRed.grid(row=1, column=1, sticky=W)
		
		Label(self.frame4, text='Green').grid(row=2, column=0, sticky=W)
		helixGreen=StringVar()
		self.helixGreen = Entry(self.frame4, width = 5, textvariable=helixGreen)
		helixGreen.set("0.5")
		self.helixGreen.grid(row=2, column=1, sticky=W)

		Label(self.frame4, text='Blue').grid(row=3, column=0, sticky=W)
		helixBlue=StringVar()
		self.helixBlue = Entry(self.frame4, width = 5, textvariable=helixBlue)
		helixBlue.set("0")
		self.helixBlue.grid(row=3, column=1, sticky=W)		
		
		Label(self.frame5, text='Sheet Color').grid(row=0, column=0, sticky=W)
		Label(self.frame5, text='Red').grid(row=1, column=0, sticky=W)
		sheetRed=StringVar()
		self.sheetRed = Entry(self.frame5, width = 5, textvariable=sheetRed)
		sheetRed.set("0")
		self.sheetRed.grid(row=1, column=1, sticky=W)
		
		Label(self.frame5, text='Green').grid(row=2, column=0, sticky=W)
		sheetGreen=StringVar()
		self.sheetGreen = Entry(self.frame5, width = 5, textvariable=sheetGreen)
		sheetGreen.set("0.75")
		self.sheetGreen.grid(row=2, column=1, sticky=W)

		Label(self.frame5, text='Blue').grid(row=3, column=0, sticky=W)
		sheetBlue=StringVar()
		self.sheetBlue = Entry(self.frame5, width = 5, textvariable=sheetBlue)
		sheetBlue.set("0.75")
		self.sheetBlue.grid(row=3, column=1, sticky=W)			
		
		Label(self.frame6, text='Helix style').grid(row=0, column=0, sticky=W)		
		self.style= StringVar()
		for text in [('PDB'), ('VRML')]:
			Radiobutton(self.frame6, text=text, value=text, variable=self.style).grid(sticky=W)
		self.style.set('VRML')

	def Add(self):
		selected=chimera.selection.currentAtoms()
		self.selectionlist.append(selected)
		print selected
		self.lenselected=len(selected)
		self.addtoatomlist()

	def Delete(self):
		self.removefromatomlist()
	
	def Build(self):
		inputfile=str(self.infile.get())
		inputPre=str((inputfile.split('.'))[0])
		infile='None'
		helixColor="%s,%s,%s"%(self.helixRed.get(),self.helixGreen.get(),self.helixBlue.get())
		index=0
                filename=airsIO.getPath(inputfile)
		
#		while index < len(self.names):
#                        if str(self.files[index].name) == inputfile:
#                                 filename=self.pdbpath(self.files[index])
#                        index=index+1
	
	
		outDejavu=open("helix.sse","w")
		outDejavu.write("!\n")
		outDejavu.write("!  ===  0dum\n")
		outDejavu.write("!\n")
		outDejavu.write("MOL   0dum\n")
		outDejavu.write("NOTE  from helixhunter3.py\n")
		outDejavu.write("PDB   1SSE\n")
		outDejavu.write("!\n")

		file=open(filename, "r")
		lines=file.readlines()
		file.close
		x=[]
		y=[]
		z=[]
		atomNumber=[]
		counter=0
		atomLine=[]

		for line in lines:
			isatom=str(line[0:6].strip())
			if (isatom=="ATOM"):
				atomLine.append(line)
				x.append(float(line[30:38].strip()))
				y.append(float(line[38:46].strip()))
				z.append(float(line[46:54].strip()))
				atomNumber.append(int(line[6:11].strip()))
				counter=counter+1
		
		k=0
		alphaAtoms=open("helix-atoms.pdb","w")
		betaAtoms=open("sheet-atoms.pdb","w")
		sheetFile="sheet-%s.wrl"%(inputPre)
		coilFile="coil-%s.wrl"%(inputPre)
		print sheetFile,coilFile
		outsheet=open(sheetFile,"w")	
		outsheet.write("#VRML V2.0 utf8\n")
		outcoil=open(coilFile,"w")
		outcoil.write("#VRML V2.0 utf8\n")	
		while k < len(self.displayinfo):
			buildlist=self.displayinfo[k]
			print buildlist
			if buildlist[0] == 'Helix':
				helixpoints=[]
				helixlength=0.0
				q=0
				while q < len(atomNumber):
					if atomNumber[q] in buildlist[2]:
						helixpoints.append(q)
						alphaAtoms.write(atomLine[q])
					q=q+1
				for point1 in helixpoints:
					for point2 in helixpoints:
						distance=math.sqrt((x[point1]-x[point2])**2+(y[point1]-y[point2])**2+(z[point1]-z[point2])**2)
						if distance >= helixlength:
							helixlength=distance
							hpoint1=[x[point1], y[point1], z[point1]]
							hpoint2=[x[point2], y[point2], z[point2]]
				intlength=int(math.ceil(helixlength/1.54))
				dejavuline="ALPHA 'A%d' '%d' '%d' %d %f %f %f %f %f %f\n"%(k,k*100,k*100+(intlength-1),intlength,hpoint1[0],hpoint1[1],hpoint1[2],hpoint2[0],hpoint2[1],hpoint2[2])
				outDejavu.write(dejavuline)	
			if buildlist[0] == 'Sheet':
				sheetpoints=[]
				templine=[0,0,0]
				q=0
				xsum=0.0
				ysum=0.0
				zsum=0.0
				
				while q < len(atomNumber):
					if atomNumber[q] in buildlist[2]:
						betaAtoms.write(atomLine[q])
						templine=[x[q], y[q], z[q]]
						xsum=xsum+x[q]
						ysum=ysum+y[q]
						zsum=zsum+z[q]
						sheetpoints.append(templine)
					q=q+1
				xOrigin=xsum/len(sheetpoints)
				yOrigin=ysum/len(sheetpoints)
				zOrigin=zsum/len(sheetpoints)
				
				points=0
				maxDistance=0.0
				while points < len(sheetpoints):
					point1=sheetpoints[points]
					x1=point1[0]
					y1=point1[1]
					z1=point1[2]
					distance=math.sqrt((x1-xOrigin)**2+(y1-yOrigin)**2+(z1-zOrigin)**2)
					if distance > maxDistance:
						maxDistance=distance				
					points=points+1
				print maxDistance
				sheetColor="            emissiveColor %s %s %s\n"%(self.sheetRed.get(), self.sheetGreen.get(), self.sheetBlue.get())
				outsheet.write("Shape {\n")
				outsheet.write("    appearance Appearance {\n")
				outsheet.write("        material Material {\n")
				#outsheet.write("            emissiveColor 0.0 1.0 1.0\n")
				outsheet.write(sheetColor)
				outsheet.write("        }\n")
				outsheet.write("    }\n")		
				outsheet.write("    geometry IndexedFaceSet {\n")
				outsheet.write("       coord Coordinate {\n")
				outsheet.write("            point [\n")
				counter=0
				
				originLine="                 %f %f %f,\n"%(xOrigin,yOrigin,zOrigin)
				outsheet.write(originLine)
				for item in sheetpoints:
					lineA="                 %f %f %f,\n"%(item[0],item[1],item[2])
					outsheet.write(lineA)
				outsheet.write("            ]\n")
				outsheet.write("        }\n")
				outsheet.write("        coordIndex [\n")
				counter1=0
				while counter1 < len(sheetpoints):
					counter2=0
					while counter2 < len(sheetpoints):
						distanceCheck=math.sqrt((sheetpoints[counter1][0]-sheetpoints[counter2][0])**2+(sheetpoints[counter1][1]-sheetpoints[counter2][1])**2+(sheetpoints[counter1][2]-sheetpoints[counter2][2])**2)								
						print buildlist[2][counter1],counter1+1,buildlist[2][counter2],counter2+1, distanceCheck
						if counter1!=counter2 and distanceCheck <=maxDistance:
							print buildlist[2][counter1],counter1,buildlist[2][counter2],counter2, distanceCheck					
							lineB="            0,%d,%d,0\n"%(counter1+1,counter2+1)
							outsheet.write(lineB)
						#counter3=0
						#while counter3<len(sheetpoints):
						#	if counter1!=counter!=counter3:
						#		lineB="            %d,%d,%d,%d,-1\n"%(counter1,counter2,counter3,counter1)
						#		outsheet.write(lineB)		
						#	counter3=counter3+1
						counter2=counter2+1
					counter1=counter1+1
				outsheet.write("        ]\n")
				outsheet.write("    }\n")
				outsheet.write("}\n")
			if buildlist[0] == 'Coil':
				coilpoints=[]
				templine=[0,0,0]
				q=0
				while q < len(atomNumber):
					if atomNumber[q] in buildlist[2]:
						templine=[x[q], y[q], z[q]]
						coilpoints.append(templine)
					q=q+1
				outcoil.write("Shape {\n")
				outcoil.write("    appearance Appearance {\n")
				outcoil.write("        material Material {\n")
				outcoil.write("            emissiveColor 1.0 0.5 0.0\n")
				outcoil.write("        }\n")
				outcoil.write("    }\n")		
				outcoil.write("    geometry IndexedLineSet {\n")
				outcoil.write("       coord Coordinate {\n")
				outcoil.write("            point [\n")
				counter=0
				for item in coilpoints:
					lineA="                 %f %f %f,\n"%(item[0],item[1],item[2])
					outcoil.write(lineA)
				counter1=0
				maxdistance=0
				endpoints=[]
				
				while counter1 < len(coilpoints):
					counter2=0
					while counter2 < len (coilpoints):
						distance=math.sqrt((coilpoints[counter1][0]-coilpoints[counter2][0])**2+(coilpoints[counter1][1]-coilpoints[counter2][1])**2+(coilpoints[counter1][2]-coilpoints[counter2][2])**2)
						if distance>maxdistance:
							maxdistance=distance		
							endpoints=[counter1,counter2]
						counter2=counter2+1
					counter1=counter1+1
				print endpoints
				counter3=0
				start=endpoints[0]
				listofdistances=[]
				sortedlistofdistances=[]
				while counter3<len(coilpoints):
					neighbordistance=math.sqrt((coilpoints[start][0]-coilpoints[counter3][0])**2+(coilpoints[start][1]-coilpoints[counter3][1])**2+(coilpoints[start][2]-coilpoints[counter3][2])**2)
					listofdistances.append(neighbordistance)
					sortedlistofdistances.append(neighbordistance)
					counter3=counter3+1
				sortedlistofdistances.sort()
				sortedlistofdistances.pop(0)
				connection=[]
				connection.append(start)
				counter4=0
				while counter4<len(sortedlistofdistances):					      
					comparedistance=sortedlistofdistances[counter4]
					print comparedistance
					print "versus"
					counter5=0
					while counter5<len(listofdistances):
						print counter5 , listofdistances[counter5]
						if comparedistance==listofdistances[counter5]:
							print counter5,
							print " is the same"
							connection.append(counter5)
						counter5=counter5+1
					counter4=counter4+1
				print 	connection
				outcoil.write("            ]\n")
				outcoil.write("        }\n")
				outcoil.write("        coordIndex [\n")
				coiltext=str(connection)
				coiltext2=coiltext[1:-1]
				lineS="            %s\n"%(coiltext2)
				outcoil.write(lineS)
				outcoil.write("        ]\n")
				outcoil.write("    }\n")
				outcoil.write("}\n")
				
				"""
				while counter4<len(coilpoints):
					counter3=0
					mindistance=999999
					while counter3<len(coilpoints):
						print excludelist, mindistance
						if counter3 not in excludelist:
							neighbordistance=math.sqrt((coilpoints[start][0]-coilpoints[counter3][0])**2+(coilpoints[start][1]-coilpoints[counter3][1])**2+(coilpoints[start][2]-coilpoints[counter3][2])**2)
							print neighbordistance
							if neighbordistance < mindistance:
								mindistance=neighbordistance
								start=counter3
								print start
					   	#start=nextpoint
						counter3=counter3+1
					excludelist.append(start)
					counter4=counter4+1
				print excludelist
				text=str(excludelist)
				"""
			k=k+1
		outcoil.close()
		outsheet.close()
		alphaAtoms.close()
		betaAtoms.close()
		chimera.openModels.open(sheetFile)		
		chimera.openModels.open(coilFile)
		outDejavu.close()
		outfile="helix-%s"%(inputfile)

		if str(self.style.get())=='VRML':
			cmdHH="dejavu2pdb.py helix.sse %s vrml helixColor=%s"%(outfile,helixColor)
			outfile="helix-%s.wrl"%(inputPre)
		else:
			cmdHH="dejavu2pdb.py helix.sse %s"%(outfile)	
		os.system(cmdHH)	
		chimera.openModels.open(outfile)

try:
	chimera.dialogs.register(ssebuilder.name, ssebuilder)
except: pass

dialog = None

def gui():
	"""This is a Chimera specfic function to support instantiation of the dialog"""
	global dialog
	if not dialog:
		dialog = ssebuilder()
	dialog.enter()
def Refresh(self, *triggerArgs, **kw):
	if ('model list change' in triggerArgs[-1].reasons) : dialog.fileselector()

triggerOpenModels = chimera.triggers.addHandler('OpenModels', Refresh, None)
