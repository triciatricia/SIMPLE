import os
import sys

try:
	import chimera
	from chimera.baseDialog import ModelessDialog
	import VolumeViewer
except:
	print "Chimera not found"
	ModelessDialog=Tkinter.Window

def getVolumeNames():
	from VolumeViewer import Volume
	names = [m.name for m in chimera.openModels.list()
		 if isinstance(m,Volume)]
	return names

def getPDBNames():
	from chimera import Molecule
	names = [m.name for m in chimera.openModels.list()
		 if isinstance(m,Molecule)]
	return names
	
def getAllNames():
	files=[]
	files=map(lambda x:x.name,chimera.openModels.list())
	return files


def volume_data_set(model):
	from VolumeViewer import volume_list
	for v in volume_list():
		if model in v.models():
			return v
	return None

def getPath(filename):
	openfiles=chimera.openModels.list()
	for model in openfiles:
		filecheck=str(model.name)
		if  filecheck==str(filename):
			from VolumeViewer import Volume
			from chimera import Molecule
			if isinstance(model, Volume):
				path=str(volume_data_set(model).data.path)
			elif isinstance(model, Molecule):
				modelfile=model.openedAs
				path=str(modelfile[0])
			else:
				path=""
			if filecheck==path:
				path=os.path.abspath(model.name)

	return path
	
def getMapInfo(model):
	from VolumeViewer import volume_list
	for v in volume_list():
		if v.data.name == volume_name.strip():
			return (v.data.size, v.data.origin)
	return (None, None)
		
def cleanFileName(model):
	name=model.split("<")[0]
	name.strip()
	return name


def cleanTempFiles(filelist):
	for tempfile in filelist:
		cmd0="rm -f %s"%(str(tempfile))
		os.system(cmd0)
	return
