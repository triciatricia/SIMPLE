###################
# Memory.py		Steve Ludtke	05/27/03
#
# This implements model 'memories', pretty much the same thing idea 'keyframes',
# but they tend not to be applied as a whole. That is, subsets of the parameters
# will typically be used by the Animator module

import os
import Tkinter
import Tix
import Pmw
import Animator
from pprint import pprint
from time import time
#try:
import ModelParms_chimera
ModelParms=ModelParms_chimera
#except: print "Chimera Not found"
from math import sqrt


try:
	import chimera
	from chimera.baseDialog import ModelessDialog
except:
	print "Chimera not found"
	ModelessDialog=Tkinter.Window

ANIMTIME=1.0
NGLOB=4

class MemoryDialog(ModelessDialog):
	name = "Memory ui"
	buttons = ("Snapshot","Close")
	title = "Model Parameter Memories"
#    help = ("ExtensionUI.html", ExtensionUI)

	def fillInUI(self, parent):
		"This defines the user interface for the animation module"
		self.nmod=0
		self.buts=[]	# list of all current memory specific buttons
		self.nmem=0

#		self.frame1=Tkinter.Frame(parent)
		self.frame1P=Tix.ScrolledWindow(parent,scrollbar="auto")
		self.frame1=self.frame1P.window
		self.frame1P.grid(column=0,row=0,sticky="nsew")

		parent.rowconfigure(0,weight=1)
		parent.columnconfigure(0,weight=1)

		# make sure we update when the list of models is changed
		ModelParms.updateModList(self.refreshModels)
		self.refreshModels()

		parent.after(1000,self.timer,None)


	def Snapshot(self):
		try : self.snapdialog.activate()
		except :
			self.snapdialog = Pmw.PromptDialog(None,title = 'Snapshot Size',label_text = 'Snapshot Size (x,y)',
				entryfield_labelpos = 'n',defaultbutton = 0,buttons = ('OK', 'Cancel'),command = self.SnapshotGo)

	def SnapshotGo(self,str):
		self.snapdialog.withdraw()
		try:
			sz=self.snapdialog.get().split(',')
			if (len(sz)!=2 or int(sz[0])<10 or int(sz[1])<10) : return
		except: return
		ModelParms.setFrameSize(int(sz[0]),int(sz[1]))
		for mem in range(self.nmem):
			for s in ModelParms.models.values():
				s.motion={}
				for p in s.aniparms.keys(activeonly=1):
					if (s.aniparms[p]!=s.memories[mem][p]) :
						s.aniparms[p]=s.memories[mem][p]
			image=ModelParms.renderFrame()
			image.save("emanframe.%02d.jpg"%mem, format='JPEG',quality=80)


	def refreshModels(self):
		"Updates the list of models/memories"
		for i in self.buts: i.destroy()
			
		w=Tkinter.Button(self.frame1,anchor="w",text="New",command=self.storeMem)
		w.grid(row=0,column=0,sticky="w")
		self.buts.append(w)

		if (len(ModelParms.models)==0): return

		# buttons for recalling all memory parameters
		for i in range(self.nmem):
			w=Tkinter.Button(self.frame1,anchor="w",padx=2,pady=1,font="Helvetica 9",text=str(i),command=lambda self=self,ds=None,mem=i:self.restoreMem(set=ds,mem=mem))
			w.grid(row=1,column=i+1)
			w.bind("<Button-3>",lambda event,self=self,ds=None,mem=i:self.storeMem(set=ds,mem=mem,event=event))
			self.buts.append(w)

		row=1
		for m in ModelParms.models.values():
			w=Tkinter.Label(self.frame1,text=m.aniparms.name(),font="Helvetica 9 bold")
			w.grid(row=row,column=0,sticky="w")
			self.buts.append(w)
			row+=1

			for p in m.aniparms.keys(activeonly=1):
				w=Tkinter.Label(self.frame1,text="   "+m.aniparms.keylabel(p),font="Helvetica 9")
				w.grid(row=row,column=0,sticky="w")
				self.buts.append(w)
				for i in range(self.nmem):
#					if (m.aniparms.keytype(p)=="color") :
					w=Tkinter.Button(self.frame1,padx=2,pady=1,font="Helvetica 6",text="  ",command=lambda self=self,ds=m,parm=p,mem=i:self.restoreMem(set=ds,parm=parm,mem=mem))
					w.grid(row=row,column=i+1)
					w.bind("<Button-3>",lambda event,self=self,ds=m,parm=p,mem=i:self.storeMem(set=ds,parm=parm,mem=mem,event=event))
					self.buts.append(w)
				row+=1

		w=Tkinter.Label(self.frame1,text="Global Ort",font="Helvetica 9 bold")
		w.grid(row=row,column=0,sticky="w")
		self.buts.append(w)

		for i in range(NGLOB):
			w=Tkinter.Button(self.frame1,anchor="w",padx=2,pady=1,font="Helvetica 9",text=str(i),command=lambda self=self,mem=i:self.restoreGlob(n=mem))
			w.grid(row=row,column=i+1)
			w.bind("<Button-3>",lambda event,self=self,mem=i:self.storeGlob(n=mem,event=event))
			self.buts.append(w)

	def storeMem(self,set=None,parm=None,mem=-1,event=None):
		"This will store the current location/orientation of 1 or all particles in a memory"
		if (set!=None):
			if (parm==None) :
				for p in set.aniparms.keys():
					set.memories[mem][p]=set.aniparms[p]
			else:
				set.memories[mem][parm]=set.aniparms[parm]
		else:
			if (mem<0) :
				for m in ModelParms.models.values():
					m.memories.append({})
				mem=self.nmem
				self.nmem+=1

			for s in ModelParms.models.values():
				while (len(s.memories)<=mem): s.memories.append({})		# make sure there's enough space
				for p in s.aniparms.keys():
					s.memories[mem][p]=s.aniparms[p]

		print "new memory %d %d"%(mem,self.nmem)
		self.refreshModels()
#		if (event!=None) : event.widget.flash()

	def restoreMem(self,set=None,parm=None,mem=-1):
		"""This will restore the current location/orientation of 1 or all particles from a memory.
		Actually, it doesn't restore the values, but sets up a little real-time animation
		which will end up at the memory value ANIMTIME seconds later."""
		if (set!=None):											# restore a specific model
			if (parm==None):
				set.motion={}
				for p in set.aniparms.keys(activeonly=1):		# all parameters for the model
					if (set.animparms[p]!=set.memories[mem][p]) :
						set.motion[p]=[set.animparms[p],set.memories[mem][p],time()]
			else:
				if (set.aniparms[parm]!=set.memories[mem][parm]) :
					set.motion={parm:[set.aniparms[parm],set.memories[mem][parm],time()]}
		else:
			for s in ModelParms.models.values():
				s.motion={}
				for p in s.aniparms.keys(activeonly=1):
					if (s.aniparms[p]!=s.memories[mem][p]) :
						s.motion[p]=[s.aniparms[p],s.memories[mem][p],time()]

	def storeGlob(self,n=0,event=None):
		"""This will store the current location/orientation of the first displayed object in
		a persistent local file."""
		for m in ModelParms.models.values():
			try:
				value=m.aniparms["xform"]
				break
			except:
				pass
		
		try:
			a=file("chimeraglobs.txt","r")
			l=[i.strip() for i in a.readlines()]
			a.close()
		except:
			l=["" for i in range(NGLOB)]
		
		l[n]=str(value.mx)[1:-1]+",%f"%ModelParms.models["CAM"].aniparms["zoom"]
		
		a=file("chimeraglobs.txt","w")
		for i in l: a.write(i+"\n")
		a.close()
		
		self.refreshModels()
#		if (event!=None) : event.widget.flash()

	def restoreGlob(self,n=0):
		"""This will restore the current location/orientation from a persistent local file.
		Actually, it doesn't restore the values, but sets up a little real-time animation
		which will end up at the memory value ANIMTIME seconds later."""
		try:
			a=file("chimeraglobs.txt","r")
			l=a.readlines()
			a.close()
		except:
			return
		
		try:
			s=l[n].split(',')
			val=ModelParms.AnimMatrix(s[:16])
			zoom=float(s[-1])
		except:
			return
		
		for s in ModelParms.models.values():
			s.motion={}
			for p in s.aniparms.keys(activeonly=1):
				if p=="xform" : 
					s.motion[p]=[s.aniparms[p],val,time()]
				
		ModelParms.models["CAM"].motion={}
		ModelParms.models["CAM"].motion["zoom"]=[ModelParms.models["CAM"].aniparms["zoom"],zoom,time()]
		
		return


	def timer(self,arg):
		for e in ModelParms.models.values():
			if (hasattr(e,'motion')) :
				for p in e.motion.keys():
					frac=(time()-e.motion[p][2])/ANIMTIME		# fraction of total time used
					frac1=1.0-frac
					if (frac>=1.0) :
						print '--->',p,e.motion[p][1]
						e.aniparms[p]=e.motion[p][1]	# set to final value
						del e.motion[p]
						continue
					vartype=e.aniparms.keytype(p)		# type of variable being animated
					if   (vartype=="float") : e.aniparms[p]=frac1*e.motion[p][0]+frac*e.motion[p][1]
					elif (vartype=="vector") :
						e.aniparms[p]=( frac1*e.motion[p][0][0]+frac*e.motion[p][1][0],
										frac1*e.motion[p][0][1]+frac*e.motion[p][1][1],
										frac1*e.motion[p][0][2]+frac*e.motion[p][1][2] )
					elif (vartype=="color") :
						e.aniparms[p]=( frac1*e.motion[p][0][0]+frac*e.motion[p][1][0],
										frac1*e.motion[p][0][1]+frac*e.motion[p][1][1],
										frac1*e.motion[p][0][2]+frac*e.motion[p][1][2],
										frac1*e.motion[p][0][3]+frac*e.motion[p][1][3] )
					elif (vartype=="int" or vartype=="string") : pass
					elif (vartype=="matrix") :
						q1=e.motion[p][0].getQuat()		# get original orientation as quaternion
						q2=e.motion[p][1].getQuat()		# get final "
						t1=e.motion[p][0].getAllPretran()	# converts posttranslation to pretranslation
						t2=e.motion[p][1].getAllPretran()

						if (q1[0]*q2[0]+q1[1]*q2[1]+q1[2]*q2[2]+q1[3]*q2[3])<0 :
							q1=(q1[0]*-1.0,q1[1]*-1.0,q1[2]*-1.0,q1[3]*-1.0)

						q=[frac1*q1[0]+frac*q2[0],		# quaternion interpolation
						   frac1*q1[1]+frac*q2[1],
						   frac1*q1[2]+frac*q2[2],
						   frac1*q1[3]+frac*q2[3]]
						n=sqrt(q[0]**2+q[1]**2+q[2]**2+q[3]**2)
						q[0]/=n
						q[1]/=n
						q[2]/=n
						q[3]/=n

						t=(frac1*t1[0]+frac*t2[0],		# with a linear shift of the rotation center
						   frac1*t1[1]+frac*t2[1],
						   frac1*t1[2]+frac*t2[2])

						mx=ModelParms.AnimMatrix()
						mx.setQuat(q)
						mx.setPretran(t)
						e.aniparms[p]=mx


				if len(e.motion)==0 : delattr(e,"motion")	# stop animating now

		self.frame1.after(20,self.timer,None)

try:
	chimera.dialogs.register(MemoryDialog.name, MemoryDialog)
except: pass

dialog = None

def gui():
	"""This is a Chimera specfic function to support instantiation of the dialog"""
	global dialog
	if not dialog:
		dialog = MemoryDialog()
	dialog.enter()
