#!/usr/bin/env python
import EMAN 
try:
	from optparse import OptionParser
except:
	from optik import OptionParser
import math
import os
import sys

def main():
	options, args = parseOptions()
	boxsize = options.boxsize
	gnx = options.ncol
	gny = options.nrow
	
	m = EMAN.EMData()
	m.readImage(args[0])
	nx = m.xSize()
	ny = m.ySize()

	if options.boxfile:
		boxes = EMAN.readEMANBoxfile(options.boxfile)
	else:
		boxes = genGridBoxes(nx, ny, boxsize, gap_ratio = .5)
	grids = groupBoxes(boxes, nx, ny, gnx, gny)
	
	for j in range(gny):
		for i in range(gnx):
			fftavg = genAveragePowerSpectrum(m, grids[j][i])
			tnffile = "%s-%d-%d.tnf" % (os.path.splitext(args[0])[0], i, j)
			fftavg.writeImage(tnffile)
	fftavg = genAveragePowerSpectrum(m, boxes)
	tnffile = "%s.tnf" % (os.path.splitext(args[0])[0])
	fftavg.writeImage(tnffile)
			
def genAveragePowerSpectrum(image, boxes):
	boxsize = boxes[0][3]
	fftavg = EMAN.EMData()
	fftavg.setSize(boxsize+2,boxsize)
	fftavg.setComplex(1)
	fftavg.zero()
	
	for b in boxes:
		bimg = image.clip(b[0]-b[2]/2, b[1]-b[3]/2, boxsize, boxsize)
		bimg.applyMask(-1,6)
		bimg.normalize()
		fft = bimg.doFFT()
		fft.multConst(fft.ySize())
		fftavg.addIncoherent(fft)
	fftavg.multConst(1./math.sqrt(len(boxes)))
	return fftavg

def groupBoxes(boxes, nx, ny, gnx, gny):
	grids = [0] * gny
	for j in range(gny): grids[j] = [[]] * gnx
	
	for b in boxes:
		i = (b[0] - b[2]/2) * gnx / nx
		j = (b[1] - b[3]/2) * gny / ny
		grids[j][i].append(b)
	
	return grids

def genGridBoxes(nx, ny, boxsize, gap_ratio = 0):
	boxes = []
	nxboxes = int((nx-boxsize*gap_ratio)/(boxsize*(1+gap_ratio)))
	nyboxes = int((ny-boxsize*gap_ratio)/(boxsize*(1+gap_ratio)))
	
	for j in range(nyboxes):
		for i in range(nxboxes):
			xc = int(boxsize*gap_ratio + i*boxsize*(1+gap_ratio) + boxsize/2)
			yc = int(boxsize*gap_ratio + j*boxsize*(1+gap_ratio) + boxsize/2)
			boxes.append((xc, yc, boxsize, boxsize))
	return boxes

def parseOptions():
	parser = OptionParser(usage = "%s [options] <images>" % (sys.argv[0]))

	parser.add_option("--boxfile",dest="boxfile",type="string", help="box file", default="")
	parser.add_option("--boxsize",dest="boxsize",type="int", help="individual box size", default=256)
	parser.add_option("--nrow",dest="nrow",type="int", help="number of rows to divide the whole image", default=4)
	parser.add_option("--ncol",dest="ncol",type="int", help="number of columns to divide the whole image", default=3)
	
	(options, args) = parser.parse_args()
	if len(args)!=1 : 
		parser.print_help()
		sys.exit(1)
	return (options, args)

if __name__ == "__main__":
    main()
