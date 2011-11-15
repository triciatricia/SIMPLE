"""For help on EMAN, look up libpyEM instead of EMAN"""
from libpyEM import *
#from libpyCylinder import *
import sys, os, os.path
import tempfile
import math
import time
import string

EMANVERSION="EMAN v1.8x"

EMData.MRC = Image.mrc
EMData.SPIDER = Image.spider
EMData.IMAGIC = Image.img
EMData.PGM = Image.pgm
EMData.LST = Image.lst
EMData.PIF = Image.pif
EMData.PNG = Image.png
EMData.HDF = Image.hdf5
EMData.DM3 = Image.dm3
EMData.TIF = Image.tif
EMData.VTK = Image.vtk
EMData.SAL = Image.sal
EMData.ICOS = Image.map
EMData.IMAGIC3D = Image.img3d
EMData.EMIM = Image.emim
EMData.SINGLE_SPIDER = Image.single_spider
EMData.GATAN = Image.dm2
EMData.AMIRA = Image.amira
EMData.XPLOR = Image.xplor
EMData.ANY = Image.any

Euler.EMAN = EulerType.eman
Euler.IMAGIC = EulerType.imagic
Euler.SPIN = EulerType.spin
Euler.QUAT = EulerType.quat
Euler.MATRIX = EulerType.matrix
Euler.SGIROT = EulerType.sgirot
Euler.SPIDER = EulerType.spider
Euler.MRC = EulerType.mrc

try:
	a=enumerate([1,2])
except:
	def enumerate(x): return zip(range(len(x)),x)

def writelist(fsp,lst,x0=0,dx=1.0):
	out=file(fsp,"w")
	for i,j in enumerate(lst):
		out.write("%1.3g\t%1.3g\n"%(i*dx+x0,j))
	out.close()

def displayphase(img):
	"""This will display complex phases of a single image with the phase-origin in the middle"""
	fsp=os.path.basename(tempfile.mktemp())+".mrc"
	if (img.isComplex()) : f=img
	else: f=img.doFFT()
	f.toCorner()
	f.ri2ap()
	for i in range(0,f.xSize()*f.ySize(),2):
		f.setValueAt(i,0,0,f.valueAt(i+1,0,0))
		f.setValueAt(i+1,0,0,0)
	f.ap2ri()

	f.writeImage(fsp)
	os.system("v2 "+fsp)
	os.unlink(fsp)
EMData.displayphase=displayphase

def pseudocomplex(img):
	"""This will create a volume data set from a complex volume where the left half of the image
	represents the phases and the right half represents amplitudes. Note that it is rescaled to
	be cubic in a lossy way."""
	if (type(img)==type("a")) :
		fsp=img
		img=EMData()
		img.readImage(fsp)
		img=img.doFFT()
		img.toCorner()
	if (not img.isComplex()) : return None
	img.ap2ri()
	sig=img.Sigma()
	img.ri2ap()
	ret=EMData()
	ret.setSize(img.xSize()-2,img.ySize(),img.zSize())
	for z in range(ret.zSize()):
		for y in range(ret.ySize()):
			for x in range(ret.xSize()/2):
				ret.setValueAt(ret.xSize()/2-x-1,y,z,img.valueAt(x*2+1,y,z)+math.pi)
				ret.setValueAt(x+ret.xSize()/2,y,z,img.valueAt(x*2,y,z)*math.pi/sig)
	ret.update()
	return ret

def ampcomplex(img):
	"""This will create a volume data set from a complex volume where both halves of the image
	represents amplitudes. Note that it is rescaled to
	be cubic in a lossy way."""
	if (type(img)==type("a")) :
		fsp=img
		img=EMData()
		img.readImage(fsp)
		img=img.doFFT()
		img.toCorner()
	if (not img.isComplex()) : return None
	img.ap2ri()
	sig=img.Sigma()
	img.ri2ap()
	ret=EMData()
	ret.setSize(img.xSize()-2,img.ySize(),img.zSize())
	for z in range(ret.zSize()):
		for y in range(ret.ySize()):
			for x in range(ret.xSize()/2):
				ret.setValueAt(ret.xSize()/2-x-1,y,z,img.valueAt(x*2,y,z))
				ret.setValueAt(x+ret.xSize()/2  ,ret.ySize()-y,z,img.valueAt(x*2,y,z))
	ret.update()
	return ret

def display(lst) :
	"""This is used to display a list of EMData objects"""
	fspbase = os.path.basename(tempfile.mktemp())
	fspimg = fspbase + ".img"
	fsphed = fspbase + ".hed"
	
	for i in lst:
		i.writeImage(fspimg, -1, Image.img)

	os.system("v2 " + fspimg)
	os.unlink(fspimg)
	os.unlink(fsphed)

def triplot(tuplelist):
	"""this will display a list of 2- or 3-tuples in a 'triview'"""
	out=os.popen("triplot -&","w")
	for i in tuplelist:
		if (len(i)==2) : out.write("%f\t%f\n"%(float(i[0]),float(i[1])))
		elif (len(i)>2) : out.write("%f\t%f\t%f\n"%(float(i[0]),float(i[1]),float(i[2])))
	out.close()

def image2list(filename):
	ptcls = []
	d = EMData()
	imgnum, imgtype = fileCount(filename)
	if imgtype == "lst":
		fp = open(filename,'r')
		lines = fp.readlines()
		if lines[0].startswith("#LST"): line0 = 1
		elif lines[0].startswith("#LSX"): line0 = 3
		for l in lines[line0:]:
			tkns = l.split()
			if len(tkns)==7 and l.find("euler")==-1:
				index, img, alt, az, phi, x, y = tkns
				ptcls.append((img, int(index), float(alt) * math.pi/180., float(az) * math.pi/180., float(phi) * math.pi/180., float(x), float(y)))
			elif len(tkns) >=4 and l.find("euler")!=-1:
				img = tkns[1]
				index = int(tkns[0])
				for t in tkns[2:]:
					if t.startswith("euler="):
						angs = t[6:].split(',')
						if len(angs)!=3: 
							raise ValueError("Wrong format for \"%s\"" % (t))
						else:
							alt = float(angs[0])
							az  = float(angs[1])
							phi = float(angs[2])
					elif t.startswith("center="):
						centers = t[7:].split(',')
						if len(centers)!=2: 
							raise ValueError("Wrong format for \"%s\"" % (t))
						else:
							x = float(centers[0])
							y = float(centers[1])
				ptcls.append((img, int(index), float(alt) * math.pi/180., float(az) * math.pi/180., float(phi) * math.pi/180., float(x), float(y)))
			else:
				index = tkns[0]
				img = tkns[1]
				ptcls.append((img, int(index), 0, 0, 0, 0, 0))
	else:
		for i in range(imgnum):
			d.readImage(filename,i,1)
			ptcls.append((filename, i, d.alt(), d.az(), d.phi(), d.get_center_x(), d.get_center_y()))
	return ptcls

def imagelist2lstfile(imagelist, filename, use_abspath = 0):
	all_lines = []
	for img in imagelist:
		imgname = img[1]
		if use_abspath: imgname = os.path.abspath(img[1])
		
		line="%d\t%s\t%g\t%g\t%g\t%g\t%g\n" % (imgname, img[0], img[2]*180./math.pi,   img[3]*180./math.pi, img[4]*180./math.pi, img[5], img[6])
		all_lines.append(line)
	
	maxlen = 0;
	for l in all_lines:
		if len(l)>maxlen: maxlen = len(l)
	
	lstfp = open(filename,"w")
	lstfp.write("#LSX\n#If you edit this file, you MUST rerun lstfast.py on it before using it!\n# %d\n"% (maxlen))
	for l in all_lines: 
		l=l.strip()
		lstfp.write(l+' '*(maxlen-len(l)-1)+"\n")
	lstfp.close()

def merge_lstfiles(lstfiles, finallstfile, delete_lstfiles = 0):
	all_lines = []
	for f in lstfiles: 
		if os.path.exists(f):
			fp = open(f,'r')
			lines = fp.readlines()
			fp.close()
			if lines[0].startswith("#LST"): line0 = 1
			elif lines[0].startswith("#LSX"): line0 = 3
			if len(lines)>line0: all_lines += lines[line0:]
		else:
			print "WARNING: cannot find list file \"%s\"" % ( f )
	if len(all_lines):
		print "%d images saved to %s" % ( len(all_lines), finallstfile )
		fp = open(finallstfile, 'w')
		fp.write("#LST\n")
		for l in all_lines: fp.write(l)
		fp.close()
		cmd = "images2lst.py %s %s" % (finallstfile, finallstfile)
		print cmd
		os.system(cmd)
	if delete_lstfiles:
		for f in lstfiles: os.remove(f)

def readCTFParm(filename = "ctfparm.txt", return_type="list"):
	"""read in the CTF parameters and return in either a dictionary or a list"""
	ctfparm_dict = { }
	ctfparm_list = [ ]
	for l in open(filename):
		mid, ctfparm = l.strip().split();
		df, b, amp, ac, n1, n2, n3, n4, V, Cs, apix, sffile = ctfparm.split(",")
		ctfparm_dict[mid] = {"defocus":float(df), "B":float(b), "amplitude":amp,  "ac":ac, 
							"n1":float(n1), "n2":float(n2), "n3":float(n3), "n4":float(n4), 
							"V":float(V), "Cs":float(Cs), "apix":float(apix),  "sffile":sffile }
		ctfparm_list.append((mid, float(df), float(b), float(amp), float(ac), float(n1), float(n2), 
							float(n3), float(n4), float(V), float(Cs), float(apix), sffile))
		
	if return_type == "dict": return ctfparm_dict
	else: return ctfparm_list

def writeCTFParm(filename,ctflist):
	"""Writes a 'ctfparm.txt' style file using the list format 
	projvided by readCTFParm() above. Erases existing file."""
	out=file(filename,"w")
	for i in ctflist:
		if len(i) != 13 :
			print "List element does not contain 13 elements"
			break
		out.write("%s\t%s\n"%(i[0],','.join([str(j) for j in i[1:]])))
	out.close()

def readEMANBoxfile(file):	# read one box file in EMAN boxer format
	boxes=[] 
	for l in open(file):
		tokens = l.split()
		nx = int(tokens[2])
		ny = int(tokens[3])
		xc = int(tokens[0])+nx/2
		yc = int(tokens[1])+ny/2
		boxes.append((xc, yc, nx, ny))
	return boxes

def resizeBoxes(new_nx, new_ny):
	boxes = []
	for b in boxes: boxes.append((b[0], b[1], new_nx, new_ny))
	return boxes
	
def scaleBoxes(boxes, scale):
	boxes2 = []
	for b in boxes: boxes2.append((int(b[0]*scale), int(b[1]*scale), int(b[2]*scale), int(b[3]*scale)))
	return boxes2
	
def writeEMANBoxfile(file, boxes):
	fp = open(file,'w')
	for b in boxes: fp.write("%d\t%d\t%d\t%d\t-3\n" % (b[0]-b[2]/2, b[1]-b[3]/2, b[2], b[3]))
	fp.close()

def parseFocalPairInfo(filename, tolower=0):
	r"""
	the file is a text file with 3 column format: <microscopy date yyyy/mm/dd> <the micrograph/CCD image id> <exposure number>
	most of the time, the file is generated by pydb.py
	"""
	import datetime, re
	
	info={}
	all = []
	for l in open(filename):
		l2 = l.strip()
		if l2[0] == "#": continue
		try:
			day, image, exposure = l2.split()
		except:
			print "file %s is in wrong format" % (filename)
			break
		
		try:
			y, m, d = day.split("/")
		except:
			print "line \"%s\" does not have correct date" % (l2, day)
			break
		
		date = datetime.date(int(y),int(m),int(d))
		if not info.has_key(date): info[date] = {"pairs":{}, "singles_first":[], "singles_other":[]}
		
		if image.startswith("ccd_"): image=image[4:]
		if tolower: image = image.lower()
		
		all.append((date, image, int(exposure)))
		#print all[-1]
	
	re_pattern =  re.compile(r"^(?P<imgid>\d+)(?P<prefix>.*)$")
	def cmp_all(a, b):
		if a[0] != b[0]: 	# first sort according to date
			return cmp(a[0], b[0])
		else:
			try:
				sa = re_pattern.search(a[1][::-1])
				sb = re_pattern.search(b[1][::-1])
				ida = int(sa.group("imgid")[::-1])
				prefixa = sa.group("prefix")[::-1]
				idb = int(sb.group("imgid")[::-1])
				prefixb = sb.group("prefix")[::-1]
				
				if prefixa != prefixb: return cmp(prefixa, prefixb)
				else: return cmp(ida, idb)
			except:
				if a[1] != b[1]: return cmp(a[1], b[1])
				else: return cmp(a[2], b[2])
	
	all.sort(cmp_all)
			
	imgnum = len(all)
	done = [0] * imgnum

	for i in range(imgnum):
		i2 = i+1
		if all[i][2]==1:
			if i2<imgnum and all[i2][2]==2:
				id1 = 0; id2 = 0
				try:
					id1 = int(re_pattern.search(all[i][1][::-1]).group("imgid")[::-1])
					id2 = int(re_pattern.search(all[i2][1][::-1]).group("imgid")[::-1])
				except:
					pass
				if all[i][0] == all[i2][0] and id2==id1+1:
					info[all[i][0]]["pairs"][all[i][1]] = (all[i][1], all[i2][1])
					info[all[i][0]]["pairs"][all[i2][1]] = (all[i][1], all[i2][1])
					done[i] = 1
					done[i2]= 1
					#print "pairs: %s\t%s" % (all[i], all[i2])
		
	for i in range(imgnum):
		if done[i] == 0:
			if all[i][2] == 1: info[all[i][0]]["singles_first"].append(all[i][1])
			else: info[all[i][0]]["singles_other"].append(all[i][1])
			#print "single: %s" % ( str(all[i]) )
			
	return info

def pre_mpirun(mpilib = "mpich2", mpi_nodefile = "", single_job_per_node = 1, cpus = 0):
	def nodes(filename):
		nodes = []
		for l in open(filename):
			if l[0]=='#': continue
			node = l.strip()
			nodes.append(node)
		return nodes
	
	def number_of_nodes(filename):
		return len(nodes(filename))
		
	def unique_nodes(filename):
		nodes = []
		for l in open(filename):
			if l[0]=='#': continue
			node = l.strip()
			if node in nodes: pass
			else: nodes.append(node)
		return nodes
		
	def number_of_unique_nodes(filename):
		return len(unique_nodes(filename))

	def create_mpi_local_nodefile(filename = "mpi_nodefile", node_list=[]):
		print "Creating local mpi nodefile: %s" % (os.path.abspath(filename))
		fp = open(filename,"w")
		if node_list:
			for node in node_list:
				fp.write("%s\n" % (node))
		else:
			fp.write("localhost\n")
		fp.close()

	if single_job_per_node:
		get_nodes = unique_nodes
		get_nodes_num = number_of_unique_nodes
	else:
		get_nodes = nodes
		get_nodes_num = number_of_nodes

	if mpi_nodefile:
		mpi_nodefile_src = mpi_nodefile
	elif os.environ.has_key("PBS_NODEFILE"): 
		mpi_nodefile_src = os.environ["PBS_NODEFILE"]
	else:
		mpi_nodefile_src = ""
		
	if (mpi_nodefile_src and mpi_nodefile_src != "$PBS_NODEFILE") and \
		(not mpi_nodefile_src or not os.path.exists(mpi_nodefile_src) or \
		(single_job_per_node and (number_of_nodes(mpi_nodefile_src) != number_of_unique_nodes(mpi_nodefile_src)))):
		mpi_nodefile_work = "mpi_nodefile"
		if mpi_nodefile_src and os.path.exists(mpi_nodefile_src):
			node_list = get_nodes(mpi_nodefile_src)
			create_mpi_local_nodefile(filename = mpi_nodefile_work, node_list=node_list)
			print "using %s created from %s for mpi tasks" % (mpi_nodefile_work, mpi_nodefile_src)
		else:
			create_mpi_local_nodefile(filename = mpi_nodefile_work)
			print "WARNING: no mpi nodefile is given, only single node is used!"
	else:
		mpi_nodefile_work = mpi_nodefile_src

	node_num = cpus
	if not node_num: node_num = get_nodes_num(mpi_nodefile_work)
	
	if mpilib == "mpich2": # ["none","mpich1","mpich2","lam"]
		cmd = "mpdboot --file=%s -n %d;" % (mpi_nodefile_work, node_num)
	elif mpilib in ["mpich1","lam"]:
		cmd = ""
	
	if mpilib == "mpich2": # mpich2
		cmd_prefix = cmd+"mpiexec -machinefile %s -n %d" % (mpi_nodefile_work, node_num)
	elif mpilib in ["mpich1","lam"]: # mpich1
		cmd_prefix = cmd+"mpirun -machinefile %s -np %d" % (mpi_nodefile_work, node_num)
	else:
		cmd_prefix = cmd + ""
	
	return 	cmd_prefix

def post_mpirun(mpilib):
	if mpilib == "mpich2": # mpich2
		cmd = "mpdallexit"
		#print cmd
		#os.system(cmd)
	else:
		cmd = ""
	return cmd

def LOGbegin(ARGV):
	if sys.platform == "win32": os.getppid = os.getpid
	out=open(".emanlog","a")
	b=string.split(ARGV[0],'/')
	ARGV[0]=b[len(b)-1]
	out.write("%d\t%d\t1\t%d\t%s\n" % (os.getpid(),time.time(),os.getppid(),string.join(ARGV," ")))
	out.close()
	return os.getpid()

def LOGInfile(pid,file):
	out=open(".emanlog","a")
	out.write("%d\t%d\t%d\t%s\t\n" % (pid,time.time(),10,file))
	out.close()

def LOGReffile(pid,file):
	out=open(".emanlog","a")
	out.write("%d\t%d\t%d\t%s\t\n" % (pid,time.time(),12,file))
	out.close()

def LOGOutfile(pid,file):
	out=open(".emanlog","a")
	out.write("%d\t%d\t%d\t%s\t\n" % (pid,time.time(),11,file))
	out.close()
	
def LOGend():
	out=open(".emanlog","a")
	out.write("%d\t%d\t2\t-\t\n" % (os.getpid(),time.time()))
	out.close()

def which(program, useCurrentDir=0):
	"""unix which command equivalent"""
	location = None
	if program.find(os.sep)!=-1: 
		file = os.path.abspath(program)
		if os.path.exists(file) and os.access(file, os.X_OK):
			location = os.path.abspath(file)
	else:
		path=os.environ["PATH"]
		if useCurrentDir: path=".:%s" % (path)
		dirs = path.split(":")
		for d in dirs:
			file = os.path.join(d,program)
			if os.path.exists(file) and os.access(file, os.X_OK): 
				location = os.path.abspath(file)
				break
	return location
		

