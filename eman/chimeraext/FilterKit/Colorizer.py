import os
import Tix
from pprint import pprint
from time import time
import math
import VolumeViewer
import colorsys
import SimpleSession
#from PIL import Image
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

def SaveSessionC(trigger,x,file):
	""" This is used to save parameters to a file. This should happen without intervention of any other
	EMANimator modules"""

	### this dumps memories
	file.write("import FilterKit,FilterKit.Colorizer\nFilterKit.Colorizer.gui()\nimport SimpleSession\nimport chimera\nfrom chimera import selection\n")
	file.write("def COLCB(arg):\n")
	for m in single.listmodels:
		if hasattr(m,"coloropts") :
			file.write(" m=SimpleSession.modelMap[(%s,0)][0]\n"%m.id)
			file.write(" m.coloropts=%s\n"%str(m.coloropts))
			if (m.coloropts[0]=="radial") : file.write(" m.colorizer=FilterKit.Colorizer.single.colorizeradial\n")
			elif (m.coloropts[0]=="radialc") : file.write(" m.colorizer=FilterKit.Colorizer.single.colorizeradialc\n")
			elif (m.coloropts[0]=="mapc") : file.write(" m.colorizer=FilterKit.Colorizer.single.colorizemap\n")
	file.write(" pass\n")

	file.write("SimpleSession.registerAfterModelsCB(COLCB, 0)\n")

def hsvatorgba(color):
	cc=apply(colorsys.hsv_to_rgb,color[:3])
	return (cc[0],cc[1],cc[2],color[3])

def rgbatohsva(color):
	cc=apply(colorsys.rgb_to_hsv,color[:3])
	return (cc[0],cc[1],cc[2],color[3])

class Colorline(Tix.Canvas) :

	def __init__(self,parent):
		self.height=300
		Tix.Canvas.__init__(self,parent,scrollregion=(0,-10,50,self.height+20),width=50,height=self.height+20)
		self.outline=self.create_rectangle(2,-1,15,self.height)
		self.colors=[]
		for i in range(self.height):
			self.colors.append(self.create_line(3,i,15,i))
		self.labels=[self.create_text(18,0,text=" ",fill="black",anchor="w"),self.create_text(18,self.height,text=" ",fill="black",anchor="w")]

	def setColorRange(self,vrange,cranges):
		self.vrange=vrange
		self.cranges=cranges
		self.update()

	def update(self):
		vrange=self.vrange
		cranges=self.cranges
		self.itemconfigure(self.labels[0],text="%1.2f"%vrange[0])
		self.itemconfigure(self.labels[1],text="%1.2f"%vrange[1])
		for i in range(self.height):
			v=vrange[0]+i/float(self.height)*(vrange[1]-vrange[0])

			if (len(cranges)==0) : color=(1.0,1.0,1.0)
			elif (v<=cranges[0][0]) : color=cranges[0][1]
			elif (v>=cranges[-1][0]) : color=cranges[-1][1]
			else :
				for cr in cranges:
					if (v<cr[0]) :
						cur=cr
						break
					last=cr
				p=(v-last[0])/(cur[0]-last[0])
				color=(p*cur[1][0]+(1.0-p)*last[1][0],p*cur[1][1]+(1.0-p)*last[1][1],p*cur[1][2]+(1.0-p)*last[1][2])
				color=apply(colorsys.hsv_to_rgb,color)
			color="#%02x%02x%02x"%(int(color[0]*255.0),int(color[1]*255.0),int(color[2]*255.0))
			self.itemconfigure(self.colors[i],fill=color)


class ColorizerDialog(ModelessDialog):
	name = "Colorizing filters"
	buttons = ("Apply","Close")
	title = "Colorizer"
#    help = ("ExtensionUI.html", ExtensionUI)

	def fillInUI(self, parent):
		"This defines the user interface for the Colorizer"

		self.frame1=Tix.Frame(parent,borderwidth=3)
		self.frame1.grid(column=0,row=0,padx=3,pady=3)

		self.modelselW=Tix.ScrolledListBox(self.frame1,browsecmd=self.modelSelect)
		self.modelselW.listbox.configure(selectmode="BROWSE",exportselection=0)
		self.modelselW.grid(row=0,column=0,sticky="nsew")

		self.frame2=Tix.Frame(parent)
		self.frame2.grid(column=0,row=1,sticky="nsew",padx=3,pady=3)

		self.modeselW=Tix.Select(self.frame2,label="Colorize Mode",labelside="top",command=self.newmode,radio="true",orientation="vertical")
		self.modeselW.add("nocolor",text="No Color")
		self.modeselW.add("radial",text="Radial Spherical")
		self.modeselW.add("radialc",text="Radial Cylindrical")
		self.modeselW.add("mapc",text="Color by Map")
		self.modeselW.grid(row=0,column=0,sticky="nsew")

		self.frame3=Tix.Frame(parent,relief="sunken",borderwidth=3)
		self.frame3.grid(column=0,row=2,sticky="nsew",padx=3,pady=3)

		self.colorlineW=Colorline(self.frame3)
		self.colorlineW.grid(row=0,column=2,sticky="ns",rowspan=10,padx=5)

		self.colorpoints=[]
		for i in range(0,10):
			a=Tix.LabelEntry(self.frame3,label="r=",labelside="left")
			a.entry.insert(0,"")
			a.grid(row=i,column=0,sticky="e")

			b=ColorWell.ColorWell(self.frame3,color=(1.0,1.0,1.0))
			b.grid(row=i,column=1,sticky="w")

			self.colorpoints.append((a,b))

		self.mapselW=Tix.Control(self.frame3,integer="true",min=0,max=99,label="Map #:")
		self.mapselW.grid(column=0,row=11)

		parent.rowconfigure(0,weight=1)
		parent.rowconfigure(1,weight=0)
		parent.columnconfigure(0,weight=1)

		triggerOpenModels = chimera.triggers.addHandler('OpenModels', self.maybeRefresh, None)
		self.refresh()

	def maybeRefresh(self, *triggerArgs, **kw):
		if ('model list change' in triggerArgs[-1].reasons) : self.refresh()

	def refresh(self):
		"Refresh the list of models display"
		self.modelselW.listbox.delete(0,Tix.END)
		self.listmodels=[]

		for m in chimera.openModels.list():
			from _surface import Surface_Model
                        if isinstance(m, Surface_Model):
				self.modelselW.listbox.insert(Tix.END,"%s. %s"%(m.id,m.name))
				self.listmodels.append(m)

	def newmode(self,mode,state):
		if (state==0) : return

	def modelSelect(self) :
		m=self.listmodels[int(self.modelselW.listbox.curselection()[0])]
		try:
#			print "sel ",m.coloropts
			self.modeselW.invoke(m.coloropts[0])
			for i in range(len(m.coloropts[1])):
				p=m.coloropts[1][i]
				self.colorpoints[i][0].entry.delete(0, Tix.END)
				self.colorpoints[i][0].entry.insert(0,p[0])
				self.colorpoints[i][1].showColor(hsvatorgba(p[1]))
			for i in range(len(m.coloropts[1]),10):
				self.colorpoints[i][0].entry.delete(0, Tix.END)
				self.colorpoints[i][1].showColor((1.0,1.0,1.0,1.0))
			self.colorlineW.setColorRange((m.coloropts[1][0][0],m.coloropts[1][-1][0]),m.coloropts[1])
			self.mapselW.configure(value=m.coloropts[2])
		except:
			m.coloropts=["nocolor",[]]
			self.modeselW.invoke("nocolor")

	def Apply(self):
		m=self.listmodels[int(self.modelselW.listbox.curselection()[0])]
		points=[]
		for i in range(10):
			v1=self.colorpoints[i][0].entry.get()
			v2=rgbatohsva(self.colorpoints[i][1].rgba)
			try:
				points.append((float(v1),v2))
			except: pass
		points.sort()
		m.coloropts=[self.modeselW.cget("value"),points,int(self.mapselW.cget("value"))]

		if (m.coloropts[0]=="nocolor") :
			try: delattr(m,"colorizer")
			except: pass
		elif (m.coloropts[0]=="radial") : m.colorizer=self.colorizeradial
		elif (m.coloropts[0]=="radialc") : m.colorizer=self.colorizeradialc
		elif (m.coloropts[0]=="mapc") : m.colorizer=self.colorizemap

		self.modelSelect()
		m.surface.surfaces[0].show(m.surface.surfaces[0].model,None)

	def colorizeradial(self,m,varray,tarray,rgba):
		sqrt=math.sqrt
		cranges=m.model.coloropts[1]
		print m.matrix.shape
		if (len(cranges)==0) : return
		clist=[]
		for p in varray:
			v=sqrt(p[0]**2+p[1]**2+p[2]**2)
			if (v<=cranges[0][0]) : color=cranges[0][1]
			elif (v>=cranges[-1][0]) : color=cranges[-1][1]
			else :
				for cr in cranges:
					if (v<cr[0]) :
						cur=cr
						break
					last=cr
				p=(v-last[0])/(cur[0]-last[0])
				color=(p*cur[1][0]+(1.0-p)*last[1][0],p*cur[1][1]+(1.0-p)*last[1][1],
					p*cur[1][2]+(1.0-p)*last[1][2],p*cur[1][3]+(1.0-p)*last[1][3])
			clist.append(hsvatorgba(color))
#		print rgba,m,m.group,len(varray),len(tarray),len(clist),cranges[0][1],clist[0],clist[1]
		m.group.set_vertex_colors(clist)

	def colorizeradialc(self,m,varray,tarray,rgba):
		sqrt=math.sqrt
		cranges=m.model.coloropts[1]
		if (len(cranges)==0) : return
		clist=[]
		for p in varray:
			v=sqrt(p[0]**2+p[1]**2)
			if (v<=cranges[0][0]) : color=cranges[0][1]
			elif (v>=cranges[-1][0]) : color=cranges[-1][1]
			else :
				for cr in cranges:
					if (v<cr[0]) :
						cur=cr
						break
					last=cr
				p=(v-last[0])/(cur[0]-last[0])
				color=(p*cur[1][0]+(1.0-p)*last[1][0],p*cur[1][1]+(1.0-p)*last[1][1],
					p*cur[1][2]+(1.0-p)*last[1][2],p*cur[1][3]+(1.0-p)*last[1][3])
			clist.append(hsvatorgba(color))
#		print rgba,m,m.group,len(varray),len(tarray),len(clist),cranges[0][1],clist[0],clist[1]
		m.group.set_vertex_colors(clist)

	def colorizemap(self,m,varray,tarray,rgba):
		cranges=m.model.coloropts[1]
		msurf=chimera.openModels.list()[m.model.coloropts[2]].surface.surfaces[0]
		mmx=msurf.matrix
		morigin=msurf.xyz_origin
		mstep=msurf.xyz_step
#		print morigin,mstep,mmx[50][50][50],mmx[80][50][50],-morigin[0]/mstep[0],mmx.shape
		if (len(cranges)==0) : return
		clist=[]
		for p in varray:
			ix=int(math.floor(.5+(p[0]-morigin[0])/mstep[0]))
			iy=int(math.floor(.5+(p[1]-morigin[1])/mstep[1]))
			iz=int(math.floor(.5+(p[2]-morigin[2])/mstep[2]))
			if (ix<0 or iy<0 or iz<0 or ix>=mmx.shape[2] or iy>=mmx.shape[1] or iz>=mmx.shape[0]) : v=0
			else : v=mmx[iz][iy][ix]
			if (v<=cranges[0][0]) : color=cranges[0][1]
			elif (v>=cranges[-1][0]) : color=cranges[-1][1]
			else :
				for cr in cranges:
					if (v<cr[0]) :
						cur=cr
						break
					last=cr
				p=(v-last[0])/(cur[0]-last[0])
				color=(p*cur[1][0]+(1.0-p)*last[1][0],p*cur[1][1]+(1.0-p)*last[1][1],
					p*cur[1][2]+(1.0-p)*last[1][2],p*cur[1][3]+(1.0-p)*last[1][3])
			clist.append(hsvatorgba(color))
#		print rgba,m,m.group,len(varray),len(tarray),len(clist),cranges[0][1],clist[0],clist[1]
		m.group.set_vertex_colors(clist)


try:
	chimera.dialogs.register(ColorizerDialog.name, ColorizerDialog)
except: pass
chimera.triggers.addHandler(SimpleSession.SAVE_SESSION, SaveSessionC, None)



single = None

def gui():
	global single
	if not single:
		single = ColorizerDialog()
	single.enter()

