###################
# ModelParms_chimera.py		Steve Ludtke	05/27/03
#
# This implements chimera-specific portions of EMANimator. Except for a few GUI/dialog
# specific issues, all chimera dependencies are in this file. For other visualization
# back-ends, another version of this file should exist.

import chimera
import VolumeViewer
import SimpleSession
from math import sqrt,sin,cos,fabs
from PIL import Image

from chimera import Molecule, VRMLModel, LensViewer
from _volume import Volume_Model
import _surface
global Surface_Model
Surface_Model=_surface.SurfaceModel
#from _surface import Surface_Model
from VolumeViewer.volume import Volume

# This is the module-global list of visualization models,
# The types in this list are dependent on which visualization system we're in
models={}		# a dict of all models, or other parameterizable objects, the key is the id in this case

modules = []		# list of currently defined global module instances

updatecb=[]		# a list of functions to call when the list of models changes

def updateModList(callback=None):
	"""This function will interrogate the rendering environment for a list of models
	and add a ModelParms instance to each one. It will get called again whenever
	the list of models changes, a callback can be set so another event happens whenever
	the list of models changes"""
	global models
	global updatecb
	models={"CAM":chimera.viewer}
	from chimera import VRMLModel
	for m in chimera.openModels.list(): 
		if not isinstance(m,VRMLModel):
                    models[m.id]=m		# VRMLModels often share and id with another object
						
	for m in models.values():
		if (not hasattr(m,"aniparms")) : m.aniparms=ModelParms(m)
		if (not hasattr(m,"memories")) : m.memories=[]

	global updatecb
	if (callback!=None) : updatecb.append(callback)
	else:
		for i in updatecb:
			i()

fsize=(640,480)
def setFrameSize(w,h):
	"""Call this to define the size of the frame for animations"""
#	chimera.tkgui.app.graphics.config(width=int(w),height=int(h))
	global fsize
	fsize=(w,h)

def renderFrame():
	"""This will render a frame with the current parameters and return a PIL Image"""
	v = chimera.viewer
#	im = v.pilImage(fsize[0],fsize[1],supersample=1)           # ImagingCore object
#	im = v.pilImage(fsize[0],fsize[1],supersample=3,opacity=False)           # ImagingCore object
	im = v.pilImages(fsize[0],fsize[1],supersample=3,opacity=False)[0]           # ImagingCore object
	return im
#	return Image.Image()._makeself(im)

def SaveSession(trigger,x,file):
	""" This is used to save parameters to a file. This should happen without intervention of any other
	EMANimator modules"""
	global models

	### this dumps memories
	file.write("import Animator,Animator.Memory\nAnimator.Memory.gui()\nimport SimpleSession\nimport chimera\nfrom chimera import selection\n")
	file.write("import Animator.ModelParms_chimera\nModelParms=Animator.ModelParms_chimera\nfrom Animator.ModelParms_chimera import AnimMatrix\n")
	try:
		file.write("Animator.Memory.dialog.nmem=%d\n"%int(len(models["CAM"].memories)))
	except:
		return
	file.write("def AMRCB(arg):\n ModelParms.updateModList()\n")
	for key in models.keys():
		mod=models[key]
		if (not hasattr(mod,"memories")) : continue

		if (key=="CAM") : file.write(" ModelParms.models['CAM'].memories=%s\n"%str(mod.memories))
		else :
			file.write(" nid=SimpleSession.modelMap[(%s,0)][0].id\n"%key)
			file.write(" ModelParms.models[nid].memories=%s\n"%str(mod.memories))

	file.write("import SimpleSession\nSimpleSession.registerAfterModelsCB(AMRCB, 0)\n")

	### This is for dumping animations

	global modules
	file.write("import Animator,Animator.Animator\n")
	file.write("def localmap(t):\n try: ret=(SimpleSession.modelMap[(t[0],0)][0].id,t[1])\n except: ret=t\n return ret\n")
	file.write("def AMRCBanim(n):\n")
	file.write(" ModelParms.modules=[]\n")
	for i in modules:
		ip={}
		for p in i.parms.keys():
			ip[p]=i.parms[p][:4]		# this strips off the widget reference if present
		file.write(" ModelParms.modules.append(%s())\n ModelParms.modules[-1].parms=%s\n"%(str(i.__class__),str(ip)))
		file.write(" ModelParms.modules[-1].actors=map(lambda x:localmap(x),%s)\n"%str(i.actors))
	file.write(" Animator.Animator.gui()\n")
	file.write("SimpleSession.registerAfterModelsCB(AMRCBanim, 0)\n")

# session saving support
chimera.triggers.addHandler(SimpleSession.SAVE_SESSION, SaveSession, None)

def maybeRefresh(self, *triggerArgs, **kw):
	if ('model list change' in triggerArgs[-1].reasons) : updateModList()

triggerOpenModels = chimera.triggers.addHandler('OpenModels', maybeRefresh, None)



############################

class AnimMatrix:
	"""This is a slow but effective representation of a 4x4 transformation matrix
	it can be initialized using a variety of optional parameters. Note that chimera
	matrices are only 4x3 so pretranslations are absorbed into the post-translation
	it is NOT fast. It is designed for infrequent operations."""
	def __init__(self,list=None,chimera=None):
		if (list!=None and len(list)==16) : self.mx=map(lambda x:float(x),list)
		elif (chimera!=None) : self.mx=map(lambda x:float(x),str(chimera).split())+[0.0,0.0,0.,1.0]
		else : self.mx=[1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]

	def __repr__(self):
		return "AnimMatrix([%1.5f, %1.5f, %1.5f, %1.5f,\n           %1.5f, %1.5f, %1.5f, %1.5f,\n           %1.5f, %1.5f, %1.5f, %1.5f,\n           %1.5f, %1.5f, %1.5f,%1.5f])\n"%(
			self.mx[0],self.mx[1],self.mx[2],self.mx[3],self.mx[4],self.mx[5],self.mx[6],self.mx[7],
			self.mx[8],self.mx[9],self.mx[10],self.mx[11],self.mx[12],self.mx[13],self.mx[14],self.mx[15])
#		return "AnimMatrix(list=%s)"%str(self.mx)

	def getChimera(self):
                #LAVU chimera.Xform_xform() --> chimera.Xform.xform()
                #ret=chimera.Xform_xform(self.mx[0],self.mx[1],self.mx[2],self.mx[3],self.mx[4],self.mx[5],
                #        self.mx[6],self.mx[7],self.mx[8],self.mx[9],self.mx[10],self.mx[11],1)
                try:
                    ret=chimera.Xform_xform(self.mx[0],self.mx[1],self.mx[2],self.mx[3],self.mx[4],self.mx[5],
                            self.mx[6],self.mx[7],self.mx[8],self.mx[9],self.mx[10],self.mx[11],1)
                except:
                    ret=chimera.Xform.xform(self.mx[0],self.mx[1],self.mx[2],self.mx[3],self.mx[4],self.mx[5],
                            self.mx[6],self.mx[7],self.mx[8],self.mx[9],self.mx[10],self.mx[11],1)
		ret.translate(self.mx[12],self.mx[13],self.mx[14])
		return ret

	def getMatrix(self):
		return self.mx

	def applyRotVec(self,v):
		"This will apply the rotation portion of the matrix to a vector"
		return (v[0]*self.mx[0]+v[1]*self.mx[1]+v[2]*self.mx[2],
				v[0]*self.mx[4]+v[1]*self.mx[5]+v[2]*self.mx[6],
				v[0]*self.mx[8]+v[1]*self.mx[9]+v[2]*self.mx[10])

	def mult(self,b):
		a=self.mx
		b=b.mx
		c=AnimMatrix()
		c.mx[0]=a[0]*b[0]+a[1]*b[4]+a[2]*b[8]
		c.mx[1]=a[0]*b[1]+a[1]*b[5]+a[2]*b[9]
		c.mx[2]=a[0]*b[2]+a[1]*b[6]+a[2]*b[10]
		c.mx[3]=a[3]

		c.mx[4]=a[4]*b[0]+a[5]*b[4]+a[6]*b[8]
		c.mx[5]=a[4]*b[1]+a[5]*b[5]+a[6]*b[9]
		c.mx[6]=a[4]*b[2]+a[5]*b[6]+a[6]*b[10]
		c.mx[7]=a[7]

		c.mx[8]=a[8]*b[0]+a[9]*b[4]+a[10]*b[8]
		c.mx[9]=a[8]*b[1]+a[9]*b[5]+a[10]*b[9]
		c.mx[10]=a[8]*b[2]+a[9]*b[6]+a[10]*b[10]
		c.mx[11]=a[11]

		c.mx[12:16]=a[12:16]
		return c

	def rotate(self,ang,v):
		x,y,z=v
		n=sqrt(x**2+y**2+z**2)
		if (n==0) :
			n=1
			z=1
		x/=n
		y/=n
		z/=n

		r=AnimMatrix()
		r.setQuat((cos(ang/2.0),x*sin(ang/2.0),y*sin(ang/2.0),z*sin(ang/2.0)))
		return self.mult(r)

	# this method was adapted from the Python computer graphics kit
	# http://cgkit.sourceforge.net/
	def getQuat(self):
		"""return a quaternion representation of a matrix"""
		d1,d2,d3 = self.mx[0],self.mx[5],self.mx[10]
		t = d1+d2+d3+1.0
		if t>0.0:
			s = 0.5/sqrt(t)
			return (0.25/s,(self.mx[9]-self.mx[6])*s,(self.mx[2]-self.mx[8])*s,(self.mx[4]-self.mx[1])*s)
		else:
			ad1 = abs(d1)
			ad2 = abs(d2)
			ad3 = abs(d3)
			if ad1>=ad2 and ad1>=ad3:
				s = sqrt(1.0+d1-d2-d3)*2.0
				return ((self.mx[6]+self.mx[9])/s,0.5/s,(self.mx[1]+self.mx[4])/s,(self.mx[2]+self.mx[8])/s)
			elif ad2>=ad1 and ad2>=ad3:
				s = sqrt(1.0+d2-d1-d3)*2.0
				return ((self.mx[2]+self.mx[8])/s,(self.mx[1]+self.mx[4])/s,0.5/s,(self.mx[6]+self.mx[9])/s)
			else:
				s = sqrt(1.0+d3-d1-d2)*2.0
				return ((self.mx[1]+self.mx[4])/s,(self.mx[2]+self.mx[8])/s,(self.mx[6]+self.mx[9])/s,0.5/s)

	def setQuat(self,q):
		"""set matrix from quaternion q=(w,x,y,z)"""
		s=sqrt(q[0]**2+q[1]**2+q[2]**2+q[3]**2)
		q=(q[0]/s,q[1]/s,q[2]/s,q[3]/s)
		self.mx[0]=1.0-2.0*(q[2]*q[2]+q[3]*q[3])
		self.mx[1]=2.0*(q[1]*q[2]-q[0]*q[3])
		self.mx[2]=2.0*(q[3]*q[1]+q[0]*q[2])
		self.mx[4]=2.0*(q[1]*q[2]+q[0]*q[3])
		self.mx[5]=1.0-2.0*(q[1]*q[1]+q[3]*q[3])
		self.mx[6]=2.0*(q[2]*q[3]-q[0]*q[1])
		self.mx[8]=2.0*(q[3]*q[1]-q[0]*q[2])
		self.mx[9]=2.0*(q[2]*q[3]+q[0]*q[1])
		self.mx[10]=1.0-2.0*(q[1]*q[1]+q[2]*q[2])

	def getAllPretran(self):
		"""This will convert any posttranslation into pretranslation and
		return the aggregate pretranslation"""
		return (self.mx[12]+self.mx[0]*self.mx[3]+self.mx[4]*self.mx[7]+self.mx[8]*self.mx[11],
		         self.mx[13]+self.mx[1]*self.mx[3]+self.mx[5]*self.mx[7]+self.mx[9]*self.mx[11],
				 self.mx[14]+self.mx[2]*self.mx[3]+self.mx[6]*self.mx[7]+self.mx[10]*self.mx[11])

	def getAllPosttran(self):
		"""This will convert any posttranslation into pretranslation and
		return the aggregate pretranslation"""
		return (self.mx[3]+ self.mx[0]*self.mx[12]+self.mx[1]*self.mx[13]+self.mx[2]*self.mx[14],
		         self.mx[7]+ self.mx[4]*self.mx[12]+self.mx[5]*self.mx[13]+self.mx[6]*self.mx[14],
				 self.mx[11]+self.mx[8]*self.mx[12]+self.mx[9]*self.mx[13]+self.mx[10]*self.mx[14])

	def getPretran(self):
		"pull out the pretranslation component of the current matrix"
		return self.mx[12:15]

	def setPretran(self,dxdydz):
		"setPretran(tuple) - set the pretranslation component directly"
		self.mx[12:15]=list(dxdydz)

	def getPosttran(self):
		return (self.mx[3],self.mx[7],self.mx[11])

	def setPosttran(self,dxdydz):
		self.mx[3]=dxdydz[0]
		self.mx[7]=dxdydz[1]
		self.mx[11]=dxdydz[2]

############################

class ModelParms:
	"""This class ecapsulates various parameters of visualization objects, making all
	useful properties appear to be a single dictionary. This layer isolates the
	underlying visualization back-end from the animation module itself. The member
	variables are not usually accessed directly. pkeys is a list of available
	keys, values are not archived internally, but are stored in their real locations.
	target is a reference to the actual visualization object.

	valid value types:
	color: (r,g,b,a) tuple
	vector: (x,y,z) tuple
	matrix: AnimMatrix object (4x4 matrix as a 16 element list starting at the upper left)
	float
	string
	int
	choice: string from a ':' delimited list"""

	def __init__(self,target=None):
		self.pkeys={}
		self.target=None
		if (target!=None) : self.setTarget(target)

	def setTarget(self,target):
		"""This will determine the class of the target, and setup the list of available
		keys appropriately. The keys list is [type,label,active flag]"""
		t = target
		self.target=t
		if isinstance(t, Molecule):
			self.pkeys={"xform":["matrix","Orientation",1],"color":["color","Model Color",1],"display":["int","Display",1]}
		elif isinstance(t, Volume_Model):
			self.pkeys={"xform":["matrix","Orientation",1],"display":["int","Display",1],"clip":["int","Use Clip",1]}
		elif isinstance(t,VRMLModel):
			self.pkeys={"xform":["matrix","Orientation",1],"display":["int","Display",1]}
		elif isinstance(t,Surface_Model) and t.name.endswith(' surfaces'):
			# Multiscale model.
			self.pkeys={"xform":["matrix","Orientation",1],"display":["int","Display",1]}
		elif isinstance(t,Volume):
			self.pkeys={"xform":["matrix","Orientation",1],"color":["color","Model Color",1],"display":["int","Display",1],"isothr":["float","Isosurf Thr.",1],
				"clip":["int","Use Clip",1],"clipnorm":["vector","Clip Dir.",1],"cliploc":["vector","Clip Loc.",1]}
			for r in VolumeViewer.volume_list():
				if target in r.models() : self.region=r
		elif isinstance(t, LensViewer):
			self.pkeys={"zoom":["float","Zoom",1]}
			target.name="Camera"
		else : print "Unknown model type ", str(t.__class__)

	def keys(self,activeonly=0):
		"""returns a list of target keys"""
		if activeonly:
			return filter(lambda x:self.pkeys[x][2],self.pkeys.keys())
		return self.pkeys.keys()

	def __len__(self):
		return len(self.pkeys)

	def keylabel(self,key):
		"""returns the label corresponding to a key"""
		return self.pkeys[key][1]

	def keytype(self,key):
		"""Returns the parameter type corresponding to a key,
		ie - 'float', 'color', etc."""
		return self.pkeys[key][0]

	def name(self):
		"""This returns the name of the target"""
		if self.target==None: return "Undefined"
		try:
			return "%s (%s)"%(self.target.name,self.target.id())
		except:
			return "%s"%(self.target.name)

	def modelid(self):
		"""This will return a unique (for this session) identifier for a model"""
		try:
			return self.target.id()
		except:
			return None

	def __getitem__(self,index):
		"""This object acts much like a dictionary externally. Internally it must know how to
		talk to each model class."""
		t = self.target
		tn = str(t.__class__)
		if isinstance(t, Molecule):
			if (index=="xform") : return AnimMatrix(chimera=t.openState.xform)
			elif (index=="color") : return t.color.ambientDiffuse+(t.color.opacity,)
			elif (index=="display") : return t.display
			else :
				print("Unknown property ",tn,index)
				return None
		elif isinstance(t, Volume_Model):
			if (index=="xform") : return AnimMatrix(chimera=t.openState.xform)
			elif (index=="display") : return t.display
			elif (index=="clip") : return t.useClipPlane
			else :
				print("Unknown property ",tn,index)
				return None
		elif isinstance(t, VRMLModel):
			if (index=="xform") : return AnimMatrix(chimera=t.openState.xform)
			elif (index=="display") : return t.display
			else :
				print("Unknown property ",tn,index)
				return None

		elif isinstance(t, Surface_Model) and t.name.endswith(' surfaces'):
			if (index=="xform") : return AnimMatrix(chimera=t.openState.xform)
			elif (index=="display") : return t.display
			else :
				print("Unknown property ",tn,index)
				return None
		elif isinstance(t,Volume):
			try:
				if (index=="xform") : return AnimMatrix(chimera=t.openState.xform)
	#AnimMatrix(chimera=self.region.orientation)
				elif (index=="color") : return self.region.surface_colors[0]
	#return t.oslChildren()[0].color()
				elif (index=="display") : return t.display
				elif (index=="clip") : return t.useClipPlane
				elif (index=="isothr") : return self.region.surface_levels[0]
				elif (index=="clipnorm") : return (t.clipPlane.normal.x,t.clipPlane.normal.y,t.clipPlane.normal.z)
				elif (index=="cliploc") : return (t.clipPlane.origin.x,t.clipPlane.origin.y,t.clipPlane.origin.z)
				else :
					print("Unknown property ",tn,index)
					return None
			except: return None
		elif isinstance(t,LensViewer):
			if (index=="zoom") : return t.scaleFactor
			else :
				print("Unknown property ",tn,index)
				return None

	def __setitem__(self,index,value):
		"""This object acts much like a dictionary"""
		t = self.target
		tn = str(t.__class__)
		if isinstance(t, Molecule):
			if (index=="xform") : t.openState.xform=value.getChimera()
			elif (index=="color") :
				t.color.ambientDiffuse=(value[0],value[1],value[2])
				t.color.opacity=value[3]
			elif (index=="display") : t.display=value
			else :
				print("Unknown property ",tn,index)
				return None

		elif isinstance(t, Volume_Model):
			if (index=="xform") :
#				print value.getQuat()
				t.openState.xform=value.getChimera()
				t.orientation=value.getChimera()
#				self.region.update_surface(0,self.region.rendering_options)
			elif (index=="display") : t.display=value
			elif (index=="clip") : t.useClipPlane=value
			else :
				print("Unknown property ",tn,index)
				return None

		elif isinstance(t, VRMLModel):
			if (index=="xform") : t.openState.xform=value.getChimera()
			elif (index=="display") : t.display=value
			else :
				print("Unknown property ",tn,index)
				return None

		elif isinstance(t, Surface_Model) and t.name.endswith(' surfaces'):
			if (index=="xform") : t.openState.xform=value.getChimera()
			elif (index=="display") : t.display=value
			else :
				print("Unknown property ",tn,index)
				return None
		elif isinstance(t, Volume):
			if (index=="xform") :
#				print value.getQuat()
				t.openState.xform=value.getChimera()
				self.region.orientation=value.getChimera()
#				self.region.update_surface(0,self.region.rendering_options)
			elif (index=="color") :
				self.region.surface_colors[0]=value
				self.region.update_surface(0,self.region.rendering_options)
			elif (index=="display") : t.display=value
			elif (index=="clip") : t.useClipPlane=value
			elif (index=="isothr") :
				if (fabs(self.region.surface_levels[0]/value-1.0)>.0001) :
					self.region.surface_levels[0]=value
					self.region.update_surface(0,self.region.rendering_options)
			elif (index=="cliploc") :
				t.clipPlane=chimera.Plane(chimera.Point(value[0],value[1],value[2]),t.clipPlane.normal)
			elif (index=="clipnorm") :
				if tuple(value)==(0,0,0): value=(1.0,0,0)
				t.clipPlane=chimera.Plane(t.clipPlane.origin,chimera.Vector(value[0],value[1],value[2]))
			else :
				print("Unknown property ",tn,index)
				return None
		elif isinstance(t, LensViewer):
			if (index=="zoom") : t.scaleFactor=float(value)
			else :
				print("Unknown property ",tn,index)
				return None

	def __contains__(self,value):
		if value in self.pkeys: return true
		return false

