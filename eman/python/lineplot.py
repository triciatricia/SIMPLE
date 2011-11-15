#!/usr/bin/env python
# This program will read a 3d volume, do a FFT, then output the intensities
# along the Z axis
# as well as an image map of the line averages of the intensities at all angles

from sys import argv
from math import pi,sin,cos
import EMAN

im1=EMAN.EMData()
im1.readImage(argv[1],-1)

out=file("plotz","w")
im2=im1.doFFT()
im2.ri2ap()
for i in range(im2.zSize()):
	out.write("%d\t%g\n"%(i-im2.zSize()/2,im2.valueAt(0,im2.ySize()/2,i)**2.0))
out.close()

out=file("ploty","w")
for i in range(im2.zSize()):
	out.write("%d\t%g\n"%(i-im2.zSize()/2,im2.valueAt(0,i,im2.ySize()/2)**2.0))
out.close()

im3=EMAN.EMData()
im3.setSize(64,64,1)

for alti in range(64):
	for azi in range(64):
		av=0
		alt=alti*pi/64.0
		az=(azi-32)*pi/64.0
		for r in range(5,im2.zSize()/2-1):
			x=2*int(r*sin(alt)*cos(az))
			y=im2.ySize()/2+int(r*sin(alt)*sin(az))
			z=im2.zSize()/2+int(r*cos(alt))
			av=av+(im2.valueAt(x,y,z))**2.0
		im3.setValueAt(azi,alti,0,av/(im2.zSize()/2.0-1.0))

im3.writeImage("imap.mrc")
