import os
import sys
import string
import commands
import re
import shutil
import math
from math import *
from sys import argv
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


class foldhunter(ModelessDialog):
	name = "fhc ui"
	buttons = ("Apply","Close")
	title = "Foldhunter"
	direman=os.environ["HOME"]
	hellp = "%s/EMAN/doc/fh_help.html"%(direman)
	help = hellp

	def targetSelector(self):
		names=airsIO.getVolumeNames()        
		self.targetButton.setitems(names)

	def probeSelector(self):
		##generate list of open volume files
		probes=airsIO.getAllNames()
		self.probeButton.setitems(probes)

	def refineSelector(self):
		##generate list of open volume files
		refines=airsIO.getAllNames()
		refines.insert(0,"Unselected")
		self.maskButton.setitems(refines)	

	def openResults(self):
		if (self.result.get()=='None'):
			return
		else:
			currentModel=str(self.result.get())
			chimera.openModels.open(currentModel)
			
	def transformPDB(self, inPDB, outPDB, apix, mapSize, mapOrigin, dAlt, dAz, dPhi, dx, dy, dz):
		cmdt1="procpdb.py %s %s rot=%f,%f,%f"%(inPDB, outPDB, dAlt,dAz,dPhi)
		os.system(cmdt1)
		cmdt2="procpdb.py %s %s apix=%f trans=%f,%f,%f"%(outPDB,outPDB,apix,dx,dy,dz)
		os.system(cmdt2)
		if self.mapOri.get()==1:
			print apix, mapSize, mapOrigin[0], (0.5*apix+mapSize)
			Ox=mapOrigin[0]+(0.5*apix*mapSize)
			Oy=mapOrigin[1]+(0.5*apix*mapSize)
			Oz=mapOrigin[2]+(0.5*apix*mapSize)
			cmdt3="procpdb.py %s %s trans=%f,%f,%f"%(outPDB,outPDB,Ox,Oy,Oz)
			os.system(cmdt3)
	
		chimera.openModels.open(outPDB)

        ##LSNB: Lavu Sridhar Note Book 20050903

        ##LSNB: Lavu Sridhar Note Book 20050903

	def fillInUI(self, parent):
		##setup frames for inputs
		self.frame0=Tkinter.Frame(parent, bd=2, relief=GROOVE)
		self.frame0.grid(column=0,row=0, sticky=EW)

                #LSNB: begin modifications            

                #LSNB: commented out following:
		
		# self.frame1=Tkinter.Frame(self.frame0, relief=GROOVE)
		# self.frame1.grid(column=0,row=0, sticky=EW)
		# self.frame2=Tkinter.Frame(parent, bd=2, relief=GROOVE)
		# self.frame2.grid(column=1,row=0, sticky=EW)
		# self.frame3=Tkinter.Frame(parent, bd=2, relief=GROOVE)
		# self.frame3.grid(column=1,row=1, sticky=EW)
		# self.frame4=Tkinter.Frame(parent, bd=2, relief=GROOVE)
		# self.frame4.grid(column=0,row=1, sticky=EW)
		# self.frame5=Tkinter.Frame(parent, bd=2, relief=GROOVE)
		# self.frame5.grid(column=0,row=2, sticky=EW)

                #LSNB: add note book frame            
                nb = Pmw.NoteBook(self.frame0)
                nb.pack(expand=1, fill=Tkinter.BOTH)
                self.notebook = nb
                nb.add('page1', tab_text='Input')
                self.pageFrame1 = nb.page('page1')
                nb.add('page2', tab_text='Options')
                self.pageFrame2 = nb.page('page2')
                nb.add('page3', tab_text='Peak Search')
                self.pageFrame3 = nb.page('page3')
                nb.add('page4', tab_text='Refine/Mask')
                self.pageFrame4 = nb.page('page4')

                #LSNB: split page 1 into 2 frames
                self.frame1 = Tkinter.Frame(self.pageFrame1, bd=2, relief=GROOVE)
                self.frame1.grid(column=0, row=0, sticky=EW)
                self.frame2 = Tkinter.Frame(self.pageFrame1, bd=2, relief=GROOVE)
                self.frame2.grid(column=0, row=1, sticky=EW)

                #LSNB: add frame on each of other pages
                self.frame3 = Tkinter.Frame(self.pageFrame2, bd=2, relief=GROOVE)
                self.frame3.grid(column=0, row=0, sticky=EW)
                self.frame4 = Tkinter.Frame(self.pageFrame3, bd=2, relief=GROOVE)
                self.frame4.grid(column=0, row=0, sticky=EW)
                self.frame5 = Tkinter.Frame(self.pageFrame4, bd=2, relief=GROOVE)
                self.frame5.grid(column=0, row=0, sticky=EW)

                #LSNB: allow for expansion
                self.frame0.pack(fill='both',expand=1)
                self.frame1.pack(fill='both',expand=1)
                self.frame2.pack(fill='both',expand=1)
                self.frame3.pack(fill='both',expand=1)
                self.frame4.pack(fill='both',expand=1)
                self.frame5.pack(fill='both',expand=1)

                #LSNB: end modifications            

		##Target Selection
		Label(self.frame1, text='Input Files:').grid(row=0, sticky=W)
		Label(self.frame1, text='target file:').grid(row=1, column=0, sticky=W)
		self.target=StringVar()
		self.targetButton=Pmw.OptionMenu(self.frame1,labelpos=W, menubutton_textvariable=self.target)
		self.targetButton.grid(row=1, column=1, sticky=W)
		self.targetSelector()
		
		##Probe Selection
		Label(self.frame1, text='probe file:').grid(row=2, column=0, sticky=W)
		self.probe=StringVar()
		self.probeButton=Pmw.OptionMenu(self.frame1,labelpos=W, menubutton_textvariable=self.probe)
		self.probeButton.grid(row=2, column=1, sticky=W)
		self.probeSelector()
		
		##Required parameters
		Label(self.frame2, text='Required parameters').grid(row=0, sticky=W)
		Label(self.frame2, text='angstrom/pixel:').grid(row=1, column=0, sticky=W)
		Label(self.frame2, text='resolution:').grid(row=2, column=0, sticky=W)
		self.apix = Entry(self.frame2, width = 6)
		self.apix.grid(row=1, column=1, sticky=W)
		self.res = Entry(self.frame2, width = 6)
		self.res.grid(row=2, column=1, sticky=W)
		self.mapOri=IntVar()
		s = Checkbutton(self.frame2, text="Density map origin", variable=self.mapOri).grid(row=3, column=0, sticky=W)
		
		##Options and Filters
		Label(self.frame3, text='Options ').grid(row=0, sticky=W)
		Label(self.frame3, text='shrink: ').grid(row=1, column=0, sticky=W)
		Label(self.frame3, text='filters:').grid(row=3, column=0, sticky=W)
		Label(self.frame3, text='solutions:').grid(row=2, column=0, sticky=W)
		
		shrink=StringVar()
		self.shrink = Entry(self.frame3, width = 4, textvariable=shrink)
		shrink.set("2")
		self.shrink.grid(row=1, column=1, sticky=W)
		self.filter=StringVar()
		keep=StringVar()
		self.keep = Entry(self.frame3, width = 4, textvariable=keep)
		keep.set("20")
		self.keep.grid(row=2, column=1, sticky=W)
		self.filter.set('None')
		options=['None', 'Binary', 'Threshold', 'Normalize', 'Laplacian']
		self.filterButton=Pmw.OptionMenu(self.frame3,labelpos=W, menubutton_textvariable=self.filter, items=options)
		self.filterButton.grid(row=3, column=1, sticky=W)
		self.filterValue=Entry(self.frame3, width=4)
		self.filterValue.grid(row=3, column=2, sticky=W)
		self.smart=IntVar()
		s = Checkbutton(self.frame3, text="SMART", variable=self.smart).grid(row=4, column=0, sticky=W)

		##Heirarchical Search
		self.hs=IntVar()
		h = Checkbutton(self.frame4, text="Peak Search", variable=self.hs).grid(row=0, sticky=W)
		Label(self.frame4, text='number of peaks:').grid(row=1, column=0, sticky=W)
		Label(self.frame4, text='exclusion radius:').grid(row=2, column=0, sticky=W)
		Label(self.frame4, text=' ').grid(row=4, column=0, sticky=W)
		depth=StringVar()
		self.depth = Entry(self.frame4, width = 4, textvariable=depth)
		depth.set("1")
		self.depth.grid(row=1, column=1, sticky=W)
		pixel=StringVar()
		self.pixel = Entry(self.frame4, width = 4, textvariable=pixel)
		pixel.set("1")
		self.pixel.grid(row=2, column=1, sticky=W)
		self.result=StringVar()
		self.resultButton=Pmw.OptionMenu(self.frame4,label_text='results',labelpos=W, menubutton_textvariable=self.result)
		self.result.set('None')
		self.resultButton.grid(row=3, column=0, sticky=W)
		Button(self.frame4,text='Open', command=self.openResults).grid(row=3, column=1, sticky=W)

		##Refinement Search
		self.rs=IntVar()
		r = Checkbutton(self.frame5, text="Refinement", variable=self.rs).grid(row=0, sticky=W)
		self.refine=StringVar()
		Label(self.frame5, text="Refine selection on:").grid(row=1, sticky=W)
		Entry(self.frame5, width = 20, textvariable=self.probe).grid(row=1, column=1, sticky=W)
						
		self.mask=StringVar()
		self.maskButton=Pmw.OptionMenu(self.frame5,label_text='mask: ',labelpos=W, menubutton_textvariable=self.mask)
		self.mask.set('Unselected')
		self.maskButton.grid(row=2, column=1, sticky=W)
		self.refineSelector()
		self.ms=IntVar()
		m = Checkbutton(self.frame5, text="Apply mask on", variable=self.ms).grid(row=2, column=0, sticky=W)
				
		Label(self.frame5, text='refine angle:   ').grid(row=3, column=0, sticky=W)
		Label(self.frame5, text='refine distance:').grid(row=4, column=0, sticky=W)
		angle=StringVar()
		self.angle = Entry(self.frame5, width = 4, textvariable=angle)
		angle.set("1")
		self.angle.grid(row=3, column=1, sticky=W)
		refdist=StringVar()
		self.refdist = Entry(self.frame5, width = 4, textvariable=refdist)
		refdist.set("1")
		self.refdist.grid(row=4, column=1, sticky=W)

	def Apply(self):
		target=airsIO.cleanFileName(str(self.target.get()))
		targetPath=airsIO.getPath(target).strip()
		shutil.copy(targetPath, 'target.mrc')
		t=target.split('.')
		targetExt=str(t[-1])
		
		refineFLAG=0
		maskFLAG=0		
		if (self.rs.get()==1):	
			refineFLAG=1
			if self.ms.get()==1:
				maskFLAG=1

        	probe=airsIO.cleanFileName(str(self.probe.get()))
		print str(self.probe.get())
		print probe
		probePath=airsIO.getPath(probe)
		print probePath
		probesplit=probe.split('.')
		probeExt=str(probesplit[-1])
		probeName=str(probesplit[0])
		print probeExt
		print probeName
		#probesplit=os.path.split(probe)
		#probeName=str(probesplit[0])

		mapinfo=airsIO.getMapInfo(target)
		mapSize=mapinfo[0][0]
		mapOrigin=mapinfo[1] 

		if probeExt=="mrc" or probeExt=="map" or probeExt=="ccp4":
			probeinfo=airsIO.getMapInfo(probe)
			tempSizeX=probeinfo[0][0]
			tempSizeY=probeinfo[0][1]
			tempSizeZ=probeinfo[0][2]
		 

		#openfiles=chimera.openModels.list()
		#mapSize=0
		#from VolumeViewer import volume_list
		#for v in volume_list():
		#	if v.data.name == volume_name.strip():
		#		mapSize = v.data.size[0]
		#		mapOrigin= v.data.origin
		#		if probeExt=="mrc":
		#			tempSizeX,tempSizeY,tempSizeZ = v.data.size
		apix=float(self.apix.get())
		res= float(self.res.get())
		shrink = int(self.shrink.get())
		keep=int(self.keep.get())

		if ((self.filter.get()=='None') or (self.filter.get()=='Normalize')): 
			value=None	
		else:
			value=float(self.filterValue.get())
		
		hs=0
		hs=int(self.hs.get())
					
		if hs==1:
			depth= int(self.depth.get())
			pixel=int(self.pixel.get())
		else:
			depth=1
			pixel=1
		########create user selection
		if (refineFLAG==1):
			selectedLength=0
			selected=chimera.selection.currentAtoms()
			selectedLength=len(selected)
			
			if (selectedLength!=0) and (probeExt=='pdb' or probeExt=='ent'):
				print "ENTERED USER SELECTION"	
				i=0
				selectedAtoms=[]
				while (i < selectedLength):
					selectedAtoms.append(chimera.selection.currentAtoms()[i].serialNumber)
					i=i+1
	
				selectedAtoms.sort()
				print selectedAtoms
				fileRefine=open(probe, "r")
				linesRefine=fileRefine.readlines()
				fileRefine.close()
				
				refinePDB=open("refine.pdb", "w")
				maskPDB=open("mask.pdb", "w")
				for lineRefine in linesRefine:
					isatom=str(lineRefine[0:6].strip())
					serialNum=str(lineRefine[6:11].strip())
					if (isatom=="ATOM"):
						serialNum=int(lineRefine[6:11].strip())
						if (serialNum in selectedAtoms):
							refinePDB.write(lineRefine)
						else :
							maskPDB.write(lineRefine)
				refinePDB.close()
				maskPDB.close()

				cmdRS0="pdb2mrc refine.pdb refine.mrc apix=%f res=%f box=%d"%(apix, res, mapSize)
				os.system(cmdRS0)
				cmdRS1="pdb2mrc mask.pdb mask.mrc apix=%f res=%f box=%d"%(apix, res, mapSize)
				os.system(cmdRS1)
				cmdRS2="proc3d refine.mrc refine.mrc norm"
				os.system(cmdRS2)

				if self.mask.get()!="Unselected":
					maskfile=str(self.mask.get())
					maskPath=airsIO.getPath(maskfile)
					maskEXT=str(maskfile[-1])
					
					if (maskExt=='pdb' or maskExt=='ent'):
						cmdRS3="pdb2mrc %s mask.mrc apix=%f res=%f box=%d"%(maskPath, apix, res, mapSize)
						os.system(cmdRS3)	
					else:
						shutil.copy(targetpath, 'mask.mrc')
					
#					for f in openfiles:
#        	        		        if f.name==maskfile:
#							mask=str(f.name)
#                                                       from VolumeViewer import Volume
#                                                       from chimera import Molecule
#							if isinstance(p,Volume):
#								maskpath=str(os.path.abspath(mask))
#    		   		                     	elif isinstance(p,Molecule):
#								mf=f.openedAs
#								maskpath=mf[0]
#
#
#						maskExt=str(probesplit2[-1])
#						maskName=str(probesplit2[0])
#
#						if (maskExt=='pdb' or maskExt=='ent'):
#							cmdRS3="pdb2mrc %s mask.mrc apix=%f res=%f box=%d"%(msplit, apix, res, mapSize)
#						else:
#							if os.system("copy")==1:
#								cmdRS3="copy %s mask.mrc"%(msplit)
#							else:
#								cmdRS3="cp %s mask.mrc"%(msplit)
#						os.system(cmdRS3)

				cmdRS9="proc3d mask.mrc mask.mrc norm"
				os.system(cmdRS9)
				
				if (maskFLAG!=0):
					cmdRS4="proc3d mask.mrc mask-bin.mrc bin=0.5"
					cmdRS5="proc3d mask-bin.mrc mask-inv.mrc mult=-1"
					cmdRS6="proc3d mask-inv.mrc mask-add.mrc add=1"
					cmdRS7="proc3d target.mrc target.mrc maskfile=mask-add.mrc"
					cmdRS8="proc3d target.mrc target.mrc rfilt=0,0.5"
					os.system(cmdRS4)
					os.system(cmdRS5)
					os.system(cmdRS6)
					os.system(cmdRS7)
					os.system(cmdRS8)
					tempfiles=["mask.mrc","mask-bin.mrc","mask-inv.mrc","mask-add.mrc"]
					airsIO.cleanTempFiles(tempfiles)

			else:
				shutil.copy(probePath, 'refine.mrc')	
			selected=chimera.selection.currentEmpty()
			selectedLength=0

		########Transform PDB file and generate MRC file
		if (probeExt=='pdb' or probeExt=='ent') and (refineFLAG==0):
                        print probe
			shutil.copy(probe, 'probe.pdb')
			cmd1="procpdb.py probe.pdb probe.pdb centeratoms"
			os.system(cmd1)
			cmd2="pdb2mrc probe.pdb probe.mrc apix=%f res=%f box=%d"%(apix, res, mapSize)
			os.system(cmd2)
			cmd3="proc3d probe.mrc probe.mrc norm"
			os.system(cmd3)
		elif (refineFLAG!=0):
			print "Selection transformed"
		else:
			shutil.copy(probePath, 'probe.mrc')
			if (tempSizeX!=tempSizeY!=tempSizeZ!=mapSize):
				cmd3a="proc3d probe.mrc probe.mrc clip=%d,%d,%d"%(mapSize,mapSize,mapSize)
				os.system(cmd3a)
		print "filter"		
		########Filter and Scale MRC files
		if (self.filter.get()=='Threshold'):
			print("Tresholding target map")
			cmdF1="proc3d target.mrc target.mrc rfilt=0,%f"%(value)
			os.system(cmdF1)
		if (self.filter.get()=='Binary'):
			print("Binerizing target map")
			cmdF2="proc3d target.mrc target.mrc rfilt=2,%f"%(value)
			os.system(cmdF2)
		if (self.filter.get()=='Normalize'):
			print("Normalizing target map")
			cmdF3="proc3d target.mrc target.mrc  norm"
			os.system(cmdF3)
		if (self.filter.get()=='Laplacian'):
			print("Laplacian filter")
			cmdF4="proc3d target.mrc target.mrc rfilt=80,%f"%(value)
			os.system(cmdF4)
		if (refineFLAG==0):	
			print("Shrinking maps")
			cmdST="proc3d target.mrc target-shrink.mrc shrink=%f"%(shrink)
			os.system(cmdST)
			cmdSP="proc3d probe.mrc probe-shrink.mrc shrink=%f"%(shrink)
			os.system(cmdSP)
		pattern=re.compile(r"Solution\s(?P<solnum>\d+)\:\trotation\s=\s\(\s(?P<rotx>-?\d+(\.\d+)?(e.\d+)?)\s,\s(?P<rotz1>-?\d+(\.\d+)?(e.\d+)?)\s,\s(?P<rotz2>-?\d+(\.\d+)?(e.\d+)?)\s\)\ttranslation\s=\s\(\s(?P<dx>-?\d+(\.\d+)?(e.\d+)?)\s,\s(?P<dy>-?\d+(\.\d+)?(e.\d+)?)\s,\s(?P<dz>-?\d+(\.\d+)?(e.\d+)?)\s\)")

		self.listResults=[]
		
		###############################
		####### Run foldhunterP #######
		###############################

		########SMART option
		if (self.smart.get()==1 and refineFLAG==0):
			print "RUNNING SMART FOLDHUNTER"
			logSmart="log-fh-%s.txt"%(probeName)
			outSmart="fh-smart-%s.mrc"%(probeName)
			cmdS1="foldhunterP target.mrc probe.mrc %s log=%s da=1 keep=%d "%(outSmart, logSmart, keep)
			print cmdS1
			os.system(cmdS1)
			if (probeExt=='pdb' or probeExt=='ent'):
				file0=open(logSmart, "r")
				lines0=file0.readlines()
				file0.close()
				fh0 = {}
				for line in lines0:
					ps=pattern.search(line)
					if ps:
						fh0[int(ps.group('solnum'))]=[float(ps.group('rotx')),float(ps.group('rotz1')),float(ps.group('rotz2')),float(ps.group('dx')),float(ps.group('dy')),float(ps.group('dz'))]

				fhSmart="fh-smart-%s.pdb"%(probeName)
				self.transformPDB('probe.pdb', fhSmart, apix, mapSize, mapOrigin,fh0[0][0],fh0[0][1],fh0[0][2],fh0[0][3],fh0[0][4],fh0[0][5])
 			else:
				chimera.openModels.open(outSmart)
				
		########Scale foldhunter	
		if (refineFLAG==0) and (self.smart.get()==0):
			print "RUNNING FOLDHUNTER ON SMALL MAPS"
			outShrink="fh-shrink-%s.mrc"%(probeName)
			da=((180*res)/(math.pi*(mapSize/(2*shrink))))*1.5
			if da>30:
				da=30
			cmdFHS="foldhunterP target-shrink.mrc probe-shrink.mrc %s log=log-fh-shrink.txt da=%f keep=%d"%(outShrink,da,keep)
			print cmdFHS
			os.system(cmdFHS)

			########Parse output and repeat foldhunterP
			file1=open('log-fh-shrink.txt', "r")
			lines1=file1.readlines()
			file1.close()
			fh1 = {}
			for line in lines1:
				ps=pattern.search(line)
				if ps:
					fh1[int(ps.group('solnum'))]=[float(ps.group('rotx')),float(ps.group('rotz1')),float(ps.group('rotz2')),float(ps.group('dx')),float(ps.group('dy')),float(ps.group('dz'))]
			print("RUNNING FOLDHUNTER")
			count=0
			children=0
			while ((count < depth) and (children < keep)):
				angle_range=da/2
				da2=1
				if ((angle_range >=10) and (mapSize>=80)):
					da2=2
				sphere_radius=mapSize/10

				x1=shrink*fh1[children][3]
				y1=shrink*fh1[children][4]
				z1=shrink*fh1[children][5]

				dist = []
				solution=0
				while (solution <= children):
					x2=shrink*fh1[solution][3]
					y2=shrink*fh1[solution][4]
					z2=shrink*fh1[solution][5]
					if (solution!=children):
						distance=math.sqrt((x1-x2)**2+(y1-y2)**2+(z1-z2)**2)
					else:
						distance=10000
					dist.append(distance)
					print "%d verse %d: %f"%(children,solution,dist[solution])
					solution=solution+1
				pixel_distance=min(dist)
	
				if ((pixel_distance >= pixel) or (count==0)):
					logfile="log-%s-%d.txt"%(probeName,count)
					cmdFH="foldhunterP target.mrc probe.mrc fh-%d.mrc log=%s da=%f startangle=%f,%f,%f range=%f sphere_region=%f,%f,%f,%f"%(children,logfile,da2,fh1[children][0],fh1[children][1],fh1[children][2],angle_range,x1,y1,z1,sphere_radius)
					print cmdFH
					os.system(cmdFH)
					num=count
					count=count+1
		
					########Transform PDB
					if (probeExt=='pdb' or probeExt=='ent'):
						print("Transforming PDB")
						file2=open(logfile, "r")
						lines2=file2.readlines()
						file2.close()
						fh2 = {}
						for line in lines2:
							ps=pattern.search(line)
							if ps:
								fh2[int(ps.group('solnum'))]=[float(ps.group('rotx')),float(ps.group('rotz1')),float(ps.group('rotz2')),float(ps.group('dx')),float(ps.group('dy')),float(ps.group('dz'))]
						addFile="fh-solution-%d-%s.pdb"%(num,probeName)
						self.transformPDB('probe.pdb', addFile, apix, mapSize, mapOrigin,fh2[0][0],fh2[0][1],fh2[0][2],fh2[0][3],fh2[0][4],fh2[0][5])

					else:
						addFile="fh-%d.mrc"%(children)
				children=children+1
				self.listResults.append(addFile)
#			bestResult=self.listResults[0]
#			chimera.openModels.open(bestResult)
			self.resultSelector()
		
		########Refinement option
		if (refineFLAG==1)and (self.smart.get()==0):
			print "RUNNING REFINEMENT"
			outRefine="fh-refine-%s.mrc"%(probeName)
			angl=float(self.angle.get())
			refdis=float(self.refdist.get())
			cmdREF1="foldhunterP target.mrc refine.mrc %s log=log-fh-refine.txt keep=%d da=1 startangle=0,0,0 range=%f sphere_region=0,0,0,%f"%(outRefine, keep, angl, refdis)
			os.system(cmdREF1)
			if (probeExt=='pdb' or probeExt=='ent'):
				fileR=open("log-fh-refine.txt", "r")
				linesR=fileR.readlines()
				fileR.close()
				fhR = {}
				for lineR in linesR:
					ps=pattern.search(lineR)
					if ps:
						fhR[int(ps.group('solnum'))]=[float(ps.group('rotx')),float(ps.group('rotz1')),float(ps.group('rotz2')),float(ps.group('dx')),float(ps.group('dy')),float(ps.group('dz'))]
 				outRefinePDB="fh-refine-%s.pdb"%(probeName)
				self.transformPDB('refine.pdb', outRefinePDB, apix, mapSize, mapOrigin,fhR[0][0],fhR[0][1],fhR[0][2],fhR[0][3],fhR[0][4],fhR[0][5])

			else:
				chimera.openModels.open(outRefine)		

		tempfiles=["target.mrc", "probe.mrc", "target-shrink.mrc", "probe-shrink.mrc", "r.pdb", "refine.mrc", "refine.pdb"] 
		airsIO.cleanTempFiles(tempfiles)
				
	def resultSelector(self):
		##generate list of open files
		if (self.hs.get()==1):
			self.resultButton.setitems(self.listResults)	
		else:
			return
				
try:
	chimera.dialogs.register(foldhunter.name, foldhunter)
except: pass

dialog = None

def gui():
	"""This is a Chimera specfic function to support instantiation of the dialog"""
	global dialog
	if not dialog:
		dialog = foldhunter()
	dialog.enter()

def Refresh(self, *triggerArgs, **kw):
	if ('model list change' in triggerArgs[-1].reasons) : 
		dialog.targetSelector()
		dialog.probeSelector()
		dialog.resultSelector()
		dialog.refineSelector()
triggerOpenModels = chimera.triggers.addHandler('OpenModels', Refresh, None)
