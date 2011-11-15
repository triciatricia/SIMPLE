#!/usr/bin/env python
###	extractmonomers.py	Steven Ludtke	05/22/2007
### This program will extract monomers from individual particles
###

#N extractmonomers.py
#F This program will extract individual monomers from individual symmetric particles using masks after normal refinement
#T X
#1
#P <cls file>	Path to a .cls file to extract particles from
#U extractmonomers.py <cls file> <3d model> <monomer mask> <particle-monomer mask> <symmetry> <sf file> [dump] [mask]
#D After running a normal refinement with symmetry imposed, it may be interesting to investigate
#E dynamics of individual monomers. This program will take a refined .cls file and extract
#E all of the monomers from each particle by subtracting away the unwanted density (with
#E CTF taken into account).  The result will be a stack of monomer images which can be used for
#E further processing.
#D This program is HIGHLY EXPERIMENTAL !  Contact Steve Ludtke before using.


from EMAN import *
from sys import argv
from math import *
from sys import exit
from EMAN import *
try:
	from optparse import OptionParser
except:
	from optik import OptionParser

def LOGbegin(ARGV):
        out=open(".emanlog","a")
        b=string.split(ARGV[0],'/')
        ARGV[0]=b[len(b)-1]
        out.write("%d\t%d\t1\t%d\t%s\n"%(os.getpid(),time.time(),os.getppid(),string.join(ARGV," ")))
        out.close()

def LOGend():
        out=open(".emanlog","a")
        out.write("%d\t%d\t2\t-\t\n"%(os.getpid(),time.time()))
        out.close()


progname = os.path.basename(sys.argv[0])
usage = """Usage: %prog <cls file> <3d model> <monomer mask> <particle-monomer mask> <symmetry> <sf file> [--newbox=<newbox>] [--dump] [--mask] [--ac=<amp cont 0-1>] [--bfactor=<bfactor>]

"""

parser = OptionParser(usage=usage,version=EMANVERSION)

parser.add_option("--newbox", type="int",help="Size to clip final monomers to",default=None)
parser.add_option("--dump", action="store_true", default=False, help="Dump a lot of debugging images to dump.hed")
parser.add_option("--mask", action="store_true", default=False, help="Apply 2D masks to monomers after subtraction")
parser.add_option("--ac", type="float",help="Replace the amplitude contrast with a fixed value, range 0-1",default=None)
parser.add_option("--bfactor", type="float",help="Replace the B-factor with a fixed value",default=None)

(options, args) = parser.parse_args()
if len(args)<6 : parser.error("Missing arguments")

appinit(argv)
LOGbegin(argv)

clspath=args[0]
nimg=fileCount(clspath)[0]-1

model=EMData()
model.readImage(args[1],-1)

# mask for a monomer
maskmono=EMData()
maskmono.readImage(args[2],-1)

# mask for the whole structure
maskrest=EMData()
maskrest.readImage(args[3],-1)

#print model.zSize(),maskrest.zSize()
modelrest=model.copy(0)
modelrest.mult(maskrest)
modelrest.writeImage("modelrest.mrc")

modelmono=model.copy(0)
modelmono.mult(maskmono)
modelmono.cmCenter()
center=(modelmono.Dx(),modelmono.Dy(),modelmono.Dz())

sym=args[4]

sffile=args[5]
sf=XYData()
sf.readFile(sffile)
sf.logy()

oldbox=model.xSize()
if options.newbox : newbox=options.newbox
else: newbox=oldbox

# dumps a lot of intermediate images to 'dump.img'
if options.dump : dodump=1
else : dodump=0

# applies a per-monomer mask to extracted monomers
if options.mask : domask=1
else : domask=0

oproj=EMData()
oproj.readImage(clspath,0)
euler=oproj.getEuler()

euler.setSym(sym)
for imn in range(1,nimg+1):
	print "\r%d    "%imn
	# read the particle and preprocess
	ptcl=EMData()
	ptcl.readImage(clspath,imn)
	ptcl.edgeNormalize()
	
	# transform into 'projection' orientation
	ptcl.rotateAndTranslate()
	if ptcl.isFlipped() : ptcl.hFlip()

	# Modify CTF if necessary
	ctf=ptcl.getCTF()
	if options.ac : ctf[3]=options.ac
	if options.bfactor : ctf[1]=options.bfactor
	
	# power spectrum of particle
	ptclf=ptcl.doFFT()
	ptclpow=[]
	ptclf.calcRadDist(ptcl.xSize()/2,0,1.,ptclpow)
	
	# projection of the unmasked model
	proj=model.project3d(euler.alt(),euler.az(),euler.phi(),-6)
	projf=proj.doFFT()
	projpow=[]
	projf.calcRadDist(ptcl.xSize()/2,0,1.,projpow)
	
	# CTF curve (4 is absolute SNR,5 is Wiener filter)
	ctf=ptcl.ctfCurve(5,sf)
	
	# Now compute a filter to best match the projection to the particle
	filt=[]
	for i in range(len(ptclpow)): 
		filt.append(sqrt(ctf[i*5]*ptclpow[i]/projpow[i]))	# the *5 is from the CTFOS #define
	
	projf.applyRadFn(len(filt),0,1.0,filt)
	projfilt=projf.doIFT()
	norm=projfilt.normalizeTo(ptcl)

	e1=euler.FirstSym()
	if imn==1: 
		avgs=[[]]		 # we are going to build a list of averages for each orientation while we're at it
		avgs2=[[]]
	symn=0
	while (e1.valid()):
		if (dodump and symn==0) :
			ptcl.writeImage("dump.hed",-1)
			proj.writeImage("dump.hed",-1)
		projrest=modelrest.project3d(e1.alt(),e1.az(),e1.phi(),-6)
		projmask=maskmono.project3d(e1.alt(),e1.az(),e1.phi(),-6)
		projmask.realFilter(2,.01)
		
		# Find center of masked particle
		eul=Euler(e1.alt(),e1.az(),e1.phi())
		mx=eul.getByType(eul.MATRIX)
		cx=(center[0]*mx[0]+center[1]*mx[1]+center[2]*mx[2])
		cy=(center[0]*mx[3]+center[1]*mx[4]+center[2]*mx[5])
#		cx=(center[0]*mx[0]+center[1]*mx[3]+center[2]*mx[6])
#		cy=(center[0]*mx[1]+center[1]*mx[4]+center[2]*mx[7])
#		cz=(center[0]*mx[2]+center[1]*mx[5]+center[2]*mx[8])
		
		# power spectrum of projection	
		projrestf=projrest.doFFT()
		
		projrestf.applyRadFn(len(filt),0,1.0,filt)
		projrestfilt=projrestf.doIFT()		# now we apply the same normalization to the masked out
		projrestfilt.multConst(norm[0])		# projection
		projrestfilt.addConst(norm[1])
		
		if (dodump and symn==0) :
			projfilt.writeImage("dump.hed",-1)
			psub=ptcl-projfilt
			psub.writeImage("dump.hed",-1)
			projrestfilt.writeImage("dump.hed",-1)
#		projfilt.writeImage("outf.hed",-1)
		
		
		psub2=ptcl-projrestfilt
		psub2.edgeNormalize()
		if (dodump and symn==0) : psub2.writeImage("dump.hed",-1)
		
		if (domask) : psub2.mult(projmask)
		projmask*=projfilt
		projmask.cmCenter()
#		print cx,cy,cz
#		print projmask.Dx(),projmask.Dy(),cx,cy
#		print projmask.Dx(),projmask.Dy()," xxx ",projrestfilt.Dx(),projrestfilt.Dy()
#		psub3=psub2.clip(int((oldbox-newbox)/2-projmask.Dx()),int((oldbox-newbox)/2-projmask.Dy()),newbox,newbox)
		psub3=psub2.clip(int((oldbox-newbox)/2-cx),int((oldbox-newbox)/2-cy),newbox,newbox)
		psub3.setRAlign(e1.alt(),e1.az(),e1.phi())
#		psub3.writeImage("monomers.hed",-1)
		psub3.writeImage(args[1].split(".")[0]+".mono.hed",-1)
		
		avgs[symn].append(psub3)

		ptcl2=ptcl.copy(0)
		if domask : ptcl2.mult(projmask)
#		ptcl2=ptcl2.clip(int((oldbox-newbox)/2-projmask.Dx()),int((oldbox-newbox)/2-projmask.Dy()),newbox,newbox)
		ptcl2=ptcl2.clip(int((oldbox-newbox)/2-cx),int((oldbox-newbox)/2-cy),newbox,newbox)
		ptcl2.setRAlign(e1.alt(),e1.az(),e1.phi())
		avgs2[symn].append(ptcl2)
		
		e1=euler.NextSym()
		symn+=1
		if imn==1: 
			avgs.append([])
			avgs2.append([])
			
	#	print psub.Sigma(),psub2.Sigma()
		
		#writelist("out.pt.txt",ptclpow,0,1.)
		#writelist("out.pr.txt",projpow,0,1.)
		#writelist("out.fl.txt",filt,0,1.)
		#writelist("out.ct.txt",ctf,0,0.2)
		#break

# Write the ctf corrected averages out for each monomer class
for imgs in avgs[:-1]:
	for i in imgs: i.setNImg(1)
	av=i.copy(0)
	av.zero()
	snr=range(av.ySize()/2*5+1)
	av.makeAverageCTFCW(imgs,sf,snr)
	av.setNImg(len(imgs))
	av.setRAlign(i.alt(),i.az(),i.phi())
	av.writeImage("classes.mono.ctfc.hed",-1)

	av.makeAverage(imgs)
	av.setRAlign(i.alt(),i.az(),i.phi())
	av.writeImage("classes.mono.hed",-1)
	
for imgs in avgs2[:-1]:
        av.makeAverageCTFCW(imgs,sf,snr)
        av.setNImg(len(imgs))
        av.setRAlign(i.alt(),i.az(),i.phi())
        av.writeImage("classes.nosub.ctfc.hed",-1)

LOGend()
