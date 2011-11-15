import os
import time
import Animator
import Memory
from math import sqrt,pi,floor,ceil
from pprint import pprint
try:
	import ModelParms_chimera
	ModelParms=ModelParms_chimera
except:
	print "Chimera Not found"

# Note, if you add a module here, you need to add it to modlist in Animator.py

# base class for animation modules
class AniModule:
	"""The 'parms' dictionary contains all parameters for this animation module
		along with information necessary to let the user modify these values. The
		dictionary key is the name of the parameter. Each value is a 4-list containing
		the actual value, the type, a description for editing purposes, and the (x,y) location in the UI. 'start' and
		'duration' must always be included. If you wish
		the user to be able to edit the value graphically, use one of the following types:
		int, float, vector, string, time, memory, choice:c1:c2:c3:etc"""

	name="Base Animation Class"
	color="black"

	def __init__(self,start=0.0,duration=1.0):
		self.parms={"start":[start,"time","Start Time",(0,0)],"duration":[duration,"time","Duration",(1,0)]}

	def doit(self,objects,curtime,firstlast):
		"""Implement this method in subclasses to provide the actual functionality
		objects is a list of (obj id,parm id) tuples from ModelParms.models
		curtime is the time for the current frame
		firstlast is -1 on the first invocation, 0 in the middle and 1 for the final invocation
			this handles potential problems with the first or last frame in the sequence
			never being generated due to the specific timestep"""
		pass

	def active(self,curtime):
		"""generally won't need to be reimplemented"""
		if (curtime>self.parms["start"][0] and curtime<self.parms["start"][0]+self.parms["duration"][0]) : return 1
		return 0

	def types(self):
		"""returns a list of variable types this module can modify"""
		return []

	def fractime(self,curtime):
		"This determines the current time as a fraction from 0 to 1, including acceleration options"
		start=float(self.parms["start"][0])
		dur=float(self.parms["duration"][0])

		try: ain=(float(self.parms["accelin"][0]))/dur
		except : ain=0
		try: aout=(float(self.parms["accelout"][0]))/dur
		except : aout=0

		if (ain>dur/2.0) : ain=0.5
		if (aout>dur/2.0) : aout=0.5

		if (ain==0 and aout==0) :
			return (curtime-start)/dur

		curtime=(curtime-start)/dur
		a=2.0*aout/(ain*(ain**2+2.0*aout-ain*aout-2*aout**2))
		if (curtime<ain) : ret=0.5*a*curtime**2
		elif (curtime<=1.0-aout) : ret=0.5*a*ain**2+(curtime-ain)*a*ain
		else : ret=0.5*a*ain**2+(1.0-ain-aout)*a*ain+0.5*a*ain/aout*(ain**2-(curtime-1)**2)
		return ret
# Simple position A -> position B transformation
# no method selection yet
class AniMotion(AniModule):
	name="Mem A->B"
	color="#9090f0"

	def __init__(self,start=0.0,duration=1.0):
		self.parms={"start":[start,"time","Start Time",(0,0)],"duration":[duration,"time","Duration",(1,0)],
			"locA":[1,"memory","Start Memory",(0,1)],
			"locB":[2,"memory","End Memory",(1,1)],"accelin":[0,"time","Accel Start:",(0,2)]
			,"accelout":[0,"time","Decel Stop:",(1,2)],"offset":[(0,0,0),"vector","Offset (rotation)",(0,3)]}

	def types(self):
		"""returns a list of variable types this module can modify"""
		return ["color","vector","matrix","float","string","int","choice"]

	def doit(self,objects,curtime,firstlast):
		frac=self.fractime(curtime)
		if (firstlast==1) : frac=1.0
		if (firstlast==-1) : frac=0.0
		frac1=(1.0-frac)

		for obj in objects:
			try:
				mdl=ModelParms.models[obj[0]]
				parm=obj[1]
				ptype=mdl.aniparms.keytype(parm)
				mem1=self.parms["locA"][0]
				mem2=self.parms["locB"][0]
				off=self.parms["offset"][0]

				if (ptype=="matrix") :
					q1=mdl.memories[mem1][parm].getQuat()		# get original orientation as quaternion
					q2=mdl.memories[mem2][parm].getQuat()		# get final "
					t1=mdl.memories[mem1][parm].getAllPretran()	# converts posttranslation to pretranslation
					t2=mdl.memories[mem2][parm].getAllPretran()

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

					t=(frac1*t1[0]+frac*t2[0]+off[0],		# with a linear shift of the rotation center
					frac1*t1[1]+frac*t2[1]+off[1],
					frac1*t1[2]+frac*t2[2]+off[2])

					mx=ModelParms.AnimMatrix()
					mx.setQuat(q)
					mx.setPretran(t)
					mdl.aniparms[parm]=mx

				elif (ptype=="float") :
					mdl.aniparms[parm]=mdl.memories[mem1][parm]*frac1 + mdl.memories[mem2][parm]*frac

				elif (ptype=="int") :
					v1=int(mdl.memories[mem1][parm])
					v2=int(mdl.memories[mem2][parm])
					if (v1>v2) :
						mdl.aniparms[parm]=int(ceil(v1*frac1 + v2*frac))
					else :
						mdl.aniparms[parm]=int(floor(v1*frac1 + v2*frac))

				elif (ptype=="color"):
					c1=mdl.memories[mem1][parm]
					c2=mdl.memories[mem2][parm]
					mdl.aniparms[parm]=(c1[0]*frac1+c2[0]*frac,c1[1]*frac1+c2[1]*frac,c1[2]*frac1+c2[2]*frac,c1[3]*frac1+c2[3]*frac)

				elif (ptype=="vector"):
					c1=mdl.memories[mem1][parm]
					c2=mdl.memories[mem2][parm]
					mdl.aniparms[parm]=(c1[0]*frac1+c2[0]*frac,c1[1]*frac1+c2[1]*frac,c1[2]*frac1+c2[2]*frac)

				elif (ptype=="string" or ptype[:6]=="choice"):
					if (frac>0): mdl.aniparms[parm]=mdl.memories[mem2][parm]
					mdl.aniparms[parm]=mdl.memories[mem1][parm]

			except:
				print "AniMotion failed"

# Simple in-place rotation
class AniSpin(AniModule):
	name="Spin"
	color="#90f090"

	def __init__(self,start=0.0,duration=1.0):
		self.parms={"start":[start,"time","Start Time",(0,0)],"duration":[duration,"time","Duration",(1,0)],
			"axis":[(0.0,1.0,0.0),"vector","Rotation Axis",(0,1)],"rotations":[1.0,"float","# Rotations",(0,2)],
			"locA":[1,"memory","Start Memory",(0,3)],
			"origin":["global","choice:global:local","Space",(0,4)],"offset":[(0,0,0),"vector","Offset",(1,4)]}

	def types(self):
		"""returns a list of variable types this module can modify"""
		return ["matrix"]

	def doit(self,objects,curtime,firstlast):
		frac=self.fractime(curtime)
		if (firstlast==1) : frac=1.0
		if (firstlast==-1) : frac=0.0
		frac1=(1.0-frac)

#		try:
		if 1:
			for obj in objects:
				mdl=ModelParms.models[obj[0]]
				parm=obj[1]
				mem1=self.parms["locA"][0]
				off=self.parms["offset"][0]
				axis=self.parms["axis"][0]

				m1=mdl.memories[mem1][parm]
				offt=m1.applyRotVec(off)
				ang=self.parms["rotations"][0]*pi*2.0*frac
				n=m1.rotate(ang,axis)
				if (self.parms["origin"][0]=="local") :
					t1=mdl.memories[mem1][parm].getAllPosttran()	# converts posttranslation to pretranslation
					n.setPosttran((t1[0]-offt[0],t1[1]-offt[1],t1[2]-offt[2]))
					n.setPretran(off)
					mdl.aniparms[parm]=n
				else:
					t1=mdl.memories[mem1][parm].getAllPretran()	# converts posttranslation to pretranslation
					n.setPretran((t1[0]+off[0],t1[1]+off[1],t1[2]+off[2]))
					n.setPosttran((-offt[0],-offt[1],-offt[2]))
					mdl.aniparms[parm]=n
#		except:
#			print "AniSpin failed"

class AniShowHide(AniModule):
	name="Color/Fade"
	color="#f090f0"

	def __init__(self,start=0.0,duration=1.0):
		self.parms={"start":[start,"time","Start Time",(0,0)],"duration":[duration,"time","Duration",(1,0)],
			"show":["show","choice:show:hide:fade in:fade out:change color","Mode",(0,1)],
			"typeA":["Memory","choice:Memory:Fixed","Start",(0,2)],
			"locA":[1,"memory","Memory",(1,2)],
			"startcolor":[(1.0,1.0,1.0,1.0),"color","Color",(2,2)],
			"typeB":["Memory","choice:Memory:Fixed","End",(0,3)],
			"locB":[2,"memory","Memory",(1,3)],
			"endcolor":[(1.0,1.0,1.0,1.0),"color","Color",(2,3)]}

	def types(self):
		"""returns a list of variable types this module can modify"""
		return ["color"]

	def doit(self,objects,curtime,firstlast):
		# note that if we're turning a model on that's already on, it will still go off in the first frame
		try:
			for obj in objects:
				mdl=ModelParms.models[obj[0]]
				parm=obj[1]

				print parm,self.parms["show"]

				if (self.parms["typeA"][0]=="Fixed") :		# sc is the color at time 0
					sc=self.parms["startcolor"][0]
				else :
					sc=mdl.memories[self.parms["locA"][0]][parm]

				if (self.parms["typeB"][0]=="Fixed") :		# ec is the color at time 1
					ec=self.parms["endcolor"][0]
				else :
					ec=mdl.memories[self.parms["locB"][0]][parm]

				if (self.parms["show"][0] in ["show","fade in","change color"] or (self.parms["show"][0]=="fade out" and firstlast==-1)) :
					try : mdl.aniparms["display"]=1
					except: pass
				else:
					if (self.parms["show"][0]=="hide" or firstlast==1) :
						try : mdl.aniparms["display"]=0
						except : pass

				if (self.parms["show"][0]=="show") :
					try: mdl.aniparms[parm]=sc
					except: pass

				frac=self.fractime(curtime)
				if (firstlast==-1) : frac=0
				if (firstlast==1) : frac=1.0
				if (self.parms["show"][0]=="fade in") :
					try: mdl.aniparms[parm]=(ec[0]*frac,ec[1]*frac,ec[2]*frac,ec[3]*frac)
					except: pass
				elif (self.parms["show"][0]=="fade out") :
					try: mdl.aniparms[parm]=(sc[0]*(1.0-frac),sc[1]*(1.0-frac),sc[2]*(1.0-frac),sc[3]*(1.0-frac))
					except: pass
				elif (self.parms["show"][0]=="change color") :
					mdl.aniparms[parm]=(sc[0]*(1.0-frac)+ec[0]*frac,sc[1]*(1.0-frac)+ec[1]*frac,sc[2]*(1.0-frac)+ec[2]*frac,sc[3]*(1.0-frac)+ec[3]*frac)
				elif (self.parms["show"][0]=="show") :
					mdl.aniparms[parm]=ec
		except:
			print "AniShowHide failed"

class AniSequence(AniModule):
	name="Sequence"
	color="#f0f0b0"

	def __init__(self,start=0.0,duration=1.0):
		self.parms={"start":[start,"time","Start Time",(0,0)],"duration":[duration,"time","Duration",(1,0)],
			"direction":["Forward","choice:Forward:Backward","Dir",(0,1)]
			}

	def types(self):
		"""returns a list of variable types this module can modify"""
		return ["color"]

	def doit(self,objects,curtime,firstlast):
		# note that if we're turning a model on that's already on, it will still go off in the first frame
#		try:
			frac=self.fractime(curtime)
			if (firstlast==-1) : frac=0
			if (firstlast==1) : frac=1.0
			try: 
				if self.parms["direction"][0]=="Backward" : frac=1.0-frac
			except: self.parms["direction"]=["Forward","choice:Forward:Backward","Dir",(0,1)]
			
			n=len(objects)
			objects.sort()
			for i in range(n):
				mdl=ModelParms.models[objects[i][0]]
				if (floor(frac*n*.999999)==i) : mdl.aniparms["display"]=1
				else : mdl.aniparms["display"]=0

#		except:
#			print "AniSequence failed"


"""
class AniZoom(AniModule):
	name="Zoom"
	color="#008010"
	isglobal=1

	def __init__(self,start=0.0,duration=1.0):
		self.parms={"start":[start,"time","Start Time",(0,0)],"duration":[duration,"time","Duration",(1,0)],
			"mode":["memory","choice:memory:fixed","Mode",(0,1)],"locA":[1,"memory","Start Memory",(0,2)],
			"locB":[1,"memory","End Memory",(1,2)],"fixedA":[1.0,"float","Fixed Start",(0,3)],
			"fixedB":[1.0,"float","Fixed End",(1,3)]}

	def types(self):
		"returns a list of variable types this module can modify"
		return ["color","vector","matrix","float","string","int","choice"]

	def doit(self,objects,curtime,firstlast):
#		try:
		if (self.parms["mode"][0]=="memory") :
			z0=Memory.dialog.globalz[self.parms["locA"][0]]
			z1=Memory.dialog.globalz[self.parms["locB"][0]]
		else:
			z0=float(self.parms["fixedA"][0])
			z1=float(self.parms["fixedB"][0])
#		except:
#			z0=1.0
#			z1=.0001
		frac=self.fractime(curtime)
		if (firstlast==-1) : frac=0
		if (firstlast==1) : frac=1.0
		chimera.viewer.scaleFactor=z0*(1.0-frac)+z1*frac
		print curtime,frac,z0,z1,chimera.viewer.scaleFactor
"""
