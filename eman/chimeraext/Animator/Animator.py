import os
import sys
import Tix
from pprint import pprint
from time import time
import Modules
import Memory
import SimpleSession
import chimera.printer as cp
from PIL import Image
from CGLtk.color import ColorWell
try:
	import ModelParms_chimera
	import chimera
	from chimera.baseDialog import ModelessDialog
	ModelParms=ModelParms_chimera
except:
	print "Chimera Not found"
	ModelessDialog=Tix.Window


modlist=[Modules.AniMotion,Modules.AniSpin,Modules.AniShowHide,Modules.AniSequence]

class Timeline(Tix.Canvas) :

	def __init__(self,parent):
		self.width=400
		self.actorlist=[]
		self.modules=[]
		self.target=None
		self.timemark=None
		self.curtime=0
		Tix.Canvas.__init__(self,parent,scrollregion=(-100,0,self.width,100),width=self.width+104,height=100)

	def setActors(self,actorlist):
		"""This takes a list of strings defining the names of all actors in the set"""
		self.actorlist=actorlist
		self.update()

	def setDTime(self,t):
		self.curtime=t
		if (self.timemark==None) : self.update()
		self.coords(self.timemark,self.curtime*self.width/self.maxtime,0,self.curtime*self.width/self.maxtime,1000)

	def setModlist(self,mods):
		"""This will allow the Timeline to display information from an existing list of
		modules. These modules must conform to the module definition in Modules.py."""
		self.modules=mods
		self.update()

	def update(self):
		"""Complete refresh of the display"""
		self.maxtime=10.0
		for m in self.modules:
			self.maxtime=max(self.maxtime,m.parms["start"][0]+m.parms["duration"][0])

		self.delete("all")

		self.timemark=self.create_line(self.curtime*self.width/self.maxtime,0,self.curtime*self.width/self.maxtime,100)
		self.tag_bind(self.timemark,"<B1-Motion>",self.timeMove)

		cy=0
		for a in self.actorlist:
			cy+=14
			mcy=0
			ranges=[]
			used=0
			r=None
			for m in self.modules:
				lcy=0
				if (a[1:] in m.actors) :
					if used==0 : self.create_line(0,cy+3,0,cy-1,self.width,cy-1,self.width,cy+3)
					used=1
					ranges.append([m.parms["start"][0],m.parms["start"][0]+m.parms["duration"][0]])
					for r in ranges[:-1]:
						if (not(ranges[-1][0]>=r[1] or ranges[-1][1]<=r[0])) :
							lcy=r[2]+4
							break

					r=self.create_rectangle(ranges[-1][0]*self.width/self.maxtime,cy+lcy-4,
						ranges[-1][1]*self.width/self.maxtime,cy+lcy+3,fill=m.color)
					self.tag_bind(r,"<Button-1>",lambda e,x=m,y=r:self.modDown(e,x,y))
					self.tag_bind(r,"<B1-Motion>",lambda e,x=m:self.modMove(e,x))
					self.tag_bind(r,"<ButtonRelease-1>",lambda e,x=m:self.modUp(e,x))
					ranges[-1].append(lcy)
					mcy=max(mcy,lcy)
			if used:
				self.create_text(-2,cy,anchor="e",text=a[0])
				cy+=max(0,mcy-4)
			else: cy-=14


		self.config(scrollregion=(-100,0,self.width,cy+14))
		self.config(width=self.width+104)
		self.config(height=cy+14)

	def timeMove(self,e):
		if (e.x<100) : return
		self.target.renderAt((e.x-100)*self.maxtime/self.width,1)
		self.setDTime((e.x-100)*self.maxtime/self.width)

	def modDown(self,e,module,rect):
		self.mouseDown=[e.x,e.x,rect]

	def modUp(self,e,module):
		module.parms["start"][0]+=(e.x-self.mouseDown[1])*self.maxtime/self.width
		if (module.parms["start"][0]<0) :  module.parms["start"][0]=0
		if (self.target!=None) : self.target.inspect(module)
		self.update()

	def modMove(self,e,module):
		self.move(self.mouseDown[2],e.x-self.mouseDown[0],0)
		self.mouseDown[0]=e.x

	def updateItem(self,mod):
		pass


class AnimatorDialog(ModelessDialog):
	name = "Animator ui"
	buttons = ("Close")
	title = "Animator"
#    help = ("ExtensionUI.html", ExtensionUI)

	def fillInUI(self, parent):
		"This defines the user interface for the animation module"

		self.playmode=""
		self.playtime=0
		self.inspmod=None

		self.frame1=Tix.Frame(parent,relief="sunken",borderwidth=3)
		self.frame1.grid(column=0,row=0,columnspan=2)
		self.f1buts=[]
		self.refreshModules()

		self.frame2=Tix.Frame(parent)
		self.frame2.grid(column=0,row=1,sticky="ns")

#		self.modelselW=Tix.ScrolledListBox(self.frame2,command=self.refreshModules)
		self.modelselW=Tix.ScrolledListBox(self.frame2)
		self.modelselW.listbox.configure(selectmode="multiple",exportselection=0)
		self.modelselW.grid(row=0,column=0,sticky="ns",columnspan=2)

		w=Tix.Button(self.frame2,text="All",command=self.selall)
		w.grid(row=1,column=0)

		w=Tix.Button(self.frame2,text="None",command=self.selnone)
		w.grid(row=1,column=1)

		self.frame3=Tix.Frame(parent,relief="sunken",borderwidth=3)
		self.frame3.grid(column=1,row=1,sticky="nsew")
		self.f3buts=[]

		parent.rowconfigure(0,weight=0)
		parent.rowconfigure(1,weight=0)
		parent.rowconfigure(2,weight=1)
		parent.rowconfigure(3,weight=0)
		parent.columnconfigure(1,weight=1)

		self.modtype=Tix.Label(self.frame3,text=" ",font="Helvetica 14 bold")
		self.modtype.grid(row=0,column=0,columnspan=3)

		self.normW=Tix.Button(self.frame3,text="Guess",command=self.findtime)
		self.normW.grid(row=1,column=2,sticky="ew",padx=3,pady=3)

		self.start=Tix.DoubleVar()
		self.startW=Tix.Control(self.frame3,autorepeat="true",integer="false",label="Start Time (sec):",min="0",step=".1",variable=self.start)
		self.startW.grid(row=1,column=0,sticky="ew",padx=3,pady=3)

		self.duration=Tix.DoubleVar()
		self.durationW=Tix.Control(self.frame3,autorepeat="true",integer="false",label="Duration:",min="0",step=".1",variable=self.duration)
		self.durationW.grid(row=1,column=1,sticky="ew",padx=3,pady=3)
		self.duration.set(1.0)

		self.deleteW=Tix.Button(self.frame3,text="Delete",state="disabled",command=self.deleteInspect)
		self.deleteW.grid(row=10,column=0,sticky="sw")

		self.applyW=Tix.Button(self.frame3,text="Apply",state="disabled",command=self.applyInspect)
		self.applyW.grid(row=10,column=1,sticky="s")

		self.cancelW=Tix.Button(self.frame3,text="Cancel",state="disabled",command=self.cancelInspect)
		self.cancelW.grid(row=10,column=2,sticky="s")

		self.frame3.rowconfigure(10,weight=1)

#		self.frame4=Tix.Frame(parent,relief="sunken",borderwidth=2)
		self.frame4P=Tix.ScrolledWindow(parent,relief="sunken",scrollbar="auto")
		self.frame4=self.frame4P.window
		self.frame4P.grid(column=0,row=2,columnspan=2,sticky="nsew")

		self.timeline=Timeline(self.frame4)
		self.timeline.setModlist(ModelParms.modules)
		self.timeline.target=self
		self.timeline.grid(row=0,column=0,sticky="nsew")
		self.frame4.rowconfigure(0,weight=1)
		self.frame4.columnconfigure(0,weight=1)

		self.frame5=Tix.Frame(parent)
		self.frame5.grid(column=0,row=3,columnspan=2,sticky="w")

		w=Tix.Button(self.frame5,text="Play",command=self.animPlay)
		w.grid(row=0,column=0,sticky="nsew")

		w=Tix.Button(self.frame5,text="Pause",command=self.animPause)
		w.grid(row=0,column=1,sticky="nsew")

		w=Tix.Button(self.frame5,text="Stop",command=self.animStop)
		w.grid(row=0,column=2,sticky="nsew")

		self.dxster=Tix.IntVar()
		self.dxsterW=Tix.Control(self.frame5,autorepeat="true",integer="true",label="DX",step="1",variable=self.dxster)
		self.dxsterW.grid(row=1,column=0,sticky="nsew")
		
		w=Tix.Button(self.frame5,text="Analglyph",command=self.stereoRecord)
		w.grid(row=1,column=1,sticky="nsew")
		
		w=Tix.Button(self.frame5,text="Record",command=self.animRecord)
		w.grid(row=1,column=2,sticky="nsew")

		self.framerate=Tix.DoubleVar()
		self.framerateW=Tix.Control(self.frame5,autorepeat="true",integer="false",label="Frame Rate (fps)",min=".1",step="1",variable=self.framerate)
		self.framerateW.grid(row=0,column=4,sticky="nsew")
		self.framerate.set(20.0)

		self.bitrate=Tix.DoubleVar()
		self.bitrateW=Tix.Control(self.frame5,autorepeat="true",integer="false",label="Bitrate (MB/min)",min=".1",step="1",variable=self.bitrate)
		self.bitrateW.grid(row=1,column=4,sticky="nsew")
		self.bitrate.set(10.0)

		self.animsize=Tix.LabelEntry(self.frame5,label="Size (x,y)")
		self.animsize.grid(row=0,column=5,sticky="nsew")
		self.animsize.entry.insert(0,"640,480")

		self.delimg=Tix.IntVar()
		self.delimgW=Tix.Checkbutton(self.frame5,text="Del Images",variable=self.delimg)
		self.delimgW.grid(row=1,column=5,sticky="nsew")

		self.animpath=Tix.LabelEntry(self.frame5,label="Path")
		self.animpath.grid(row=2,column=0,columnspan=5,sticky="nsew")
		self.animpath.entry.insert(0,"")
		
		self.movieformat=Tix.StringVar()
		self.movieformatW=Tix.OptionMenu(self.frame5,variable=self.movieformat)
		self.movieformatW.add_command("mpeg2",label="mpeg2 (builtin)")
		self.movieformatW.add_command("mpeg4",label="mpeg4")
		self.movieformatW.add_command("msmpeg4",label="msmpeg4")
		self.movieformatW.grid(row=2,column=5,sticky="nsew")
		
		self.frame5.columnconfigure(4,weight=1)
		self.frame5.columnconfigure(5,weight=1)

		# make sure we update when the list of models is changed
		ModelParms.updateModList(self.refreshModels)
		self.refreshModels()

		# just to get the timer events started
#		self.frame1.after(1000,self.timer,None)
		# chimera-specific 'timer' event
		self.framehandler=chimera.triggers.addHandler('post-frame',self.timer,None)
		self.framehandler=chimera.triggers.addHandler('new frame',self.pretimer,None)

	def refreshModels(self):
		"""Updates ScrolledListbox to contain a list of possible models to operate on"""
		self.modelselW.listbox.delete(0,Tix.END)

		self.actors=[]

		for model in ModelParms.models.items():
			for parm in model[1].aniparms.keys():
				self.actors.append(("%s :%s"%(model[1].aniparms.keylabel(parm),model[0]),model[0],parm))

		self.timeline.setActors(self.actors)

		if (self.inspmod==None) : return

		self.actorsel=[]

		for model in ModelParms.models.items():
			for parm in model[1].aniparms.keys():
				ptype=model[1].aniparms.keytype(parm)
				if (ptype in self.inspmod.types()) or (ptype[:6]=="choice" and "choice" in self.inspmod.types()):
					self.modelselW.listbox.insert(Tix.END,"%s: %s"%(model[0],model[1].aniparms.keylabel(parm)))
					self.actorsel.append((model[0],parm))


	def refreshModules(self):
		"""Updates the list of available Modules"""

		for i in self.f1buts : i.destroy()
		self.f1buts=[]

		n=0
		for modc in modlist:
			b=Tix.Button(self.frame1,anchor="w",text=modc.name,background=modc.color,command=lambda self=self,mod=modc:self.newModule(mod))
			b.pack(side="left",fill="both")
#			b.grid(row=n/3,column=n%3)
			self.f1buts.append(b)
			n+=1

	def stereoRecord(self):
		"Enter record mode"
		self.rendertoggle=0
		if (self.playmode=="") :
			for m in ModelParms.modules:
				m.activeplay=0
			self.playmode="srecord"
			self.rectime=0
			self.recframe=0
#			try:
			w,h=self.animsize.entry.get().split(',')
#			except :
#				w=640
#				h=480
			ModelParms.setFrameSize(int(w)+self.dxster.get(),int(h))
			self.renderAt(0)	# hack to get around ati driver problem
	
	def animRecord(self):
		"Enter record mode"
		if (self.playmode=="") :
			for m in ModelParms.modules:
				m.activeplay=0
			self.playmode="record"
			self.rectime=0
			self.recframe=0
#			try:
			w,h=self.animsize.entry.get().split(',')
#			except :
#				w=640
#				h=480
			ModelParms.setFrameSize(int(w),int(h))
			self.rendertoggle=0
			self.renderAt(0)	# hack to get around ati driver problem

	def animPlay(self):
		"Enter real-time play mode."
		self.rendertoggle=0
		if (self.playmode=="") :
			for m in ModelParms.modules:
				m.activeplay=0
			self.playmode="play"
			self.playtime=time()
		elif (self.playmode=="pause") :
			self.playmode="play"
			self.playtime=time()-self.playtime

	def animPause(self):
		"If real-time playing, enter 'pause' mode"
		if (self.playmode=="play") :
			self.playmode="pause"
			self.playtime=time()-self.playtime


	def animStop(self):
		"Stop real-time playing"
		self.playmode=""

	def selall(self):
		"select all models in module inspector"
		self.modelselW.listbox.selection_set(0,"end")

	def selnone(self):
		"deselect all models in module inspector"
		self.modelselW.listbox.selection_clear(0,"end")

	def pretimer(self,arg,arg2=None,frameno=None):
		if (self.playmode=="record") :
			if (self.renderAt(self.rectime)) : self.rendertoggle=1
		if (self.playmode=="srecord") :
			if (self.renderAt(self.rectime)) : self.rendertoggle=1
	
	def timer(self,arg,arg2=None,frameno=None):
		
		if (self.playmode=="play") :
			if (self.renderAt(time()-self.playtime)) :
				self.playmode=""
		if (self.playmode=="srecord") :
			if self.rendertoggle==1 : 
				self.rendertoggle=0
				self.playmode=""
			self.rectime+=1.0/self.framerate.get()
			
			ap=self.animpath.entry.get()
			
			chimera.viewer.camera.setMode("stereo left eye", chimera.viewer)
			image=ModelParms.renderFrame()
			image2=image.crop((0,0,image.size[0]-self.dxster.get(),image.size[1]))
			image2.save(ap+"emfl.%05d.jpg"%self.recframe, format='JPEG',quality=90)

			chimera.viewer.camera.setMode("stereo right eye", chimera.viewer)
			image=ModelParms.renderFrame()
			image2=image.crop((self.dxster.get(),0,image.size[0],image.size[1]))
			image2.save(ap+"emfr.%05d.jpg"%self.recframe, format='JPEG',quality=90)

			os.system("composite -stereo %semfr.%05d.jpg %semfl.%05d.jpg %semanframe.%05d.jpg"%(ap,self.recframe,ap,self.recframe,ap,self.recframe))
			
#			image.save("frame.%05d.png"%self.recframe, format='PNG')
			self.recframe+=1
			if (self.playmode=="") :
				w,h=self.animsize.entry.get().split(',')
				com="mencoder mf://emanframe.\*.jpg -mf fps=%f:w=%d:h=%d -o /dev/null -ovc lavc -lavcopts vcodec=mpeg4:vhq:v4mv:vqmin=2:vbitrate=%d:vpass=1"%(float(self.framerate.get()),int(w),int(h),self.bitrate.get()*133.3333)
				print com
				os.system(com)
				com="mencoder mf://emanframe.\*.jpg -mf fps=%f:w=%d:h=%d -o video.avi -ovc lavc -lavcopts vcodec=mpeg4:vhq:v4mv:vqmin=2:vbitrate=%d:vpass=2"%(float(self.framerate.get()),int(w),int(h),self.bitrate.get()*133.3333)
				print com
				os.system(com)
				if (self.delimg.get()) : 
					os.system("rm emanframe.?????.jpg")
					os.system("rm emf?.?????.jpg")
		if (self.playmode=="record") :
			if self.rendertoggle==1 : 
				self.rendertoggle=0
				self.playmode=""
			self.rectime+=1.0/self.framerate.get()
			image=ModelParms.renderFrame()
			try: image[0].save("emanframe.%05d.jpg"%self.recframe, format='JPEG',quality=90)
			except: image.save("emanframe.%05d.jpg"%self.recframe, format='JPEG',quality=90)
#			image.save("frame.%05d.png"%self.recframe, format='PNG')
#			cp.saveImage("emanframe.%05d.jpg"%self.recframe, format='JPEG',supersample=3)
			self.recframe+=1
			if (self.playmode=="") :
				w,h=self.animsize.entry.get().split(',')
				if self.movieformat.get()=="mpeg4" :
					com="mencoder mf://emanframe.\*.jpg -mf fps=%f:w=%d:h=%d -o video.avi -ovc lavc -lavcopts vcodec=mpeg4:vhq:v4mv:vqmin=2:vbitrate=%d"%(float(self.framerate.get()),int(w),int(h),self.bitrate.get()*133.3333)
					print com
					os.system(com)
				elif self.movieformat.get()=="msmpeg4" :
					com="mencoder mf://emanframe\*.jpg -mf fps=%f:w=%d:h=%d -o /dev/null -ovc lavc -lavcopts vcodec=msmpeg4v2:vbitrate=%d:vpass=1"%(float(self.framerate.get()),int(w),int(h),self.bitrate.get()*133.3333)
					print com
					os.system(com)
					com="mencoder mf://emanframe\*.jpg -mf fps=%f:w=%d:h=%d -o video.avi -ovc lavc -lavcopts vcodec=msmpeg4v2:vbitrate=%d:vpass=2"%(float(self.framerate.get()),int(w),int(h),self.bitrate.get()*133.3333)
					print com
					os.system(com)
				elif self.movieformat.get()=="mpeg2" :
					FFMPEG_EXE = os.path.join(os.path.split(sys.executable)[0],"ffmpeg")
					com="%s -i emanframe.%%05d.jpg -r %f -aspect 1.33 -y -vcodec mpeg2video -f mpeg1video -b %f video.mp2"%(FFMPEG_EXE,float(self.framerate.get()),self.bitrate.get()*133.333)
					print com
					os.system(com)

				if (self.delimg.get()) : os.system("rm emanframe.?????.jpg")
#		self.frame1.after(20,self.timer,None)

	def renderAt(self,curtime,single=0) :
		"""render all modules at a given timestep
		The rules are, each module will be called at least once with firstlast set to 1
		The first call of the module if curtime is between start and stop will have firstlast -1
		The final call with firstlast 1 may occur curtime>stop
		However, a call will never be made at curtime<start"""
		self.timeline.setDTime(curtime)
		endtime=0
		for m in ModelParms.modules:
			start=m.parms["start"][0]
			stop=start+m.parms["duration"][0]
			endtime=max(endtime,stop)
			doit=0
			if (single) :
				if (curtime>=start and curtime<=stop) :
					doit=1
					firstlast=0
			elif (curtime>=start and curtime<=stop) :
				if (m.activeplay==0) :
					firstlast=-1
					m.activeplay=1
				else : firstlast=0
				doit=1
			elif (m.activeplay==1 or (m.activeplay==0 and stop<curtime)) :
				m.activeplay=-1
				doit=1
				firstlast=1
			if (doit) : m.doit(m.actors,curtime,firstlast)
		if (curtime>endtime) : return 1
		return 0

	def findtime(self):
		"""This will try to select an intelligent start time for the current module"""
		models=map(lambda x:int(x),self.modelselW.listbox.curselection())
		maxt=0
		for i in ModelParms.modules:
			ok=1
			for j in models: ok*=(j in i.models)

			if ok :
				maxt=max(maxt,i.parms["start"][0]+i.parms["duration"][0])

		self.start.set(maxt)


	def newModule(self,modcls) :
		ModelParms.modules.append(modcls(self.start.get(),self.duration.get()))
		ModelParms.modules[-1].actors=[]
		self.inspect(ModelParms.modules[-1])

	def inspect(self,module):
		# this removes the widget references in the parameters array
		if (self.inspmod!=None) :
			for p in self.inspmod.parms.values():
				if (len(p)>4) : p.pop()

		for i in self.f3buts : i.destroy()
		self.f3buts=[]

		self.inspmod=module
		if (module==None) :
			self.deleteW.config(state="disabled")
			self.applyW.config(state="disabled")
			self.cancelW.config(state="disabled")
			self.modtype.config(text=" ")
			return

		self.start.set(module.parms["start"][0])
		self.duration.set(module.parms["duration"][0])

		self.modtype.config(text=self.inspmod.name)
		maxrow=0
		for key in module.parms.keys():
			if (key=="start" or key=="duration") : continue
			v=module.parms[key]
			if (v[1]=="int") : w=Tix.Control(self.frame3,autorepeat="true",integer="true",label=v[2],value=v[0])
			elif (v[1]=="float") : w=Tix.Control(self.frame3,autorepeat="true",integer="false",label=v[2],value=v[0])
			elif (v[1]=="string" or v[1]=="vector") :
				w=Tix.LabelEntry(self.frame3,label=v[2])
				w.entry.insert(0,str(v[0]))
			elif (v[1]=="time") : w=Tix.Control(self.frame3,autorepeat="true",integer="false",label=v[2],min="0",step=".1",value=v[0])
			elif (v[1]=="memory") : w=Tix.Control(self.frame3,autorepeat="true",integer="true",label=v[2],value=v[0],min=0)
			elif (v[1]=="color") : w=ColorWell.ColorWell(self.frame3,color=v[0])
			elif (v[1][:6]=="choice") :
				w=Tix.OptionMenu(self.frame3,label=v[2],dynamicgeometry="false")
				s=v[1].split(':')[1:]
				for i in s:
					w.add_command(i)
				w.configure(value=v[0])
			else:
				w=None
				print "Unknown data type ",v[1]
			if (v[1]=="string" or v[1]=="vector") : w.grid(row=v[3][1]+1,column=v[3][0],columnspan=3-v[3][0],sticky="ew",padx=3,pady=3)
			elif (v[1]=="color") :w.grid(row=v[3][1]+1,column=v[3][0])
			else : w.grid(row=v[3][1]+1,column=v[3][0],sticky="ew",padx=3,pady=3)
			if (len(v)==4) : v.append(w)
			else : v[4]=w
			self.f3buts.append(w)
			maxrow=max(maxrow,v[3][1])

		self.refreshModels()
		for i in range(self.modelselW.listbox.size()):
			if (self.actorsel[i] in self.inspmod.actors) : self.modelselW.listbox.select_set(i)
			else : self.modelselW.listbox.select_clear(i)


		self.deleteW.config(state="normal")
		self.applyW.config(state="normal")
		self.cancelW.config(state="normal")

	def deleteInspect(self):
		if (self.inspmod==None) : return
		ModelParms.modules.remove(self.inspmod)
		self.inspect(None)
		self.timeline.update()
		return



	def applyInspect(self):
		if (self.inspmod==None) : return		# not inspecting anything, nothing to do

		if (len(self.modelselW.listbox.curselection())==0 and not (hasattr(self.inspmod,"isglobal") and self.inspmod.isglobal)) :		# if someone 'applies' with no models, delete
			ModelParms.modules.remove(self.inspmod)
			self.timeline.update()
			self.inspect(None)
			return

		p=self.inspmod.parms
		p["start"][0]=self.start.get()
		p["duration"][0]=self.duration.get()
		for i in p.keys():
			if (i=="start" or i=="duration"): continue
			if (p[i][1]=="int" or p[i][1]=="memory") : p[i][0]=int(p[i][4].cget("value"))
			elif (p[i][1]=="float" or p[i][1]=="time") : p[i][0]=float(p[i][4].cget("value"))
			elif (p[i][1]=="string") : p[i][0]=p[i][4].entry.get()
			elif (p[i][1]=="color") :
				p[i][0]=p[i][4].rgba
#				print p[i][4].rgba
			elif (p[i][1]=="vector") :
				try: p[i][0]=eval(p[i][4].entry.get())
				except: pass
			elif (p[i][1][:6]=="choice") :
				p[i][0]=p[i][4].cget("value")
		self.inspmod.actors=map(lambda x:self.actorsel[int(x)],self.modelselW.listbox.curselection())
		self.timeline.update()

	def cancelInspect(self):
		self.inspect(None)

try:
	chimera.dialogs.register(AnimatorDialog.name, AnimatorDialog)
except: pass



single = None

def gui():
	Memory.gui()
	global single
	if not single:
		single = AnimatorDialog()
	single.enter()

