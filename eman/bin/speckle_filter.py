#!/usr/bin/env python

import EMAN
import math
import sys

def changeValue(data,x,y,z, window_size=2):
	neighbors = []
	nx = data.xSize()
	ny = data.ySize()
	nz = data.zSize()
	
	for neighbor_z in range(z-window_size,z+window_size+1):
		for neighbor_y in range(y-window_size,y+window_size+1):
			for neighbor_x in range(x-window_size,x+window_size+1):
				if (neighbor_z>=0) and (neighbor_z<nz) and (neighbor_y>=0) and (neighbor_y<ny) and (neighbor_x>=0) and (neighbor_x < nx):
					neighbors.append(data.valueAt(neighbor_x,neighbor_y,neighbor_z))
 	neighbors.sort()
	median = neighbors[int(math.floor(len(neighbors)/2))]
	data.setValueAt(x,y,z,median)


def speckle_filter(data, sigma=5):
	mean = data.Mean()
	stdev = data.Sigma()
	
	x,y,z = data.MinLoc()
	value  = data.valueAt(x,y,z)
	#print mean
	#print value
	#print stdev
	print "\tRemoving + speckls"
	while ((abs(value - mean)/stdev) > sigma):
		changeValue(data,x,y,z)
		x,y,z = data.MinLoc()
		value2  = data.valueAt(x,y,z)
		if value2 == value: break
		else: value = value2
	
	
	x,y,z = data.MaxLoc()
	value  = data.valueAt(x,y,z)
	#print mean
	#print value
	#print stdev
	print "\tRemoving - speckls"
	while ((abs(value - mean)/stdev) > sigma):
		changeValue(data,x,y,z)
		x,y,z = data.MaxLoc()
		value2  = data.valueAt(x,y,z)
		if value2 == value: break
		else: value = value2

	return data	
	



def main():
	if len(sys.argv) != 3:
		print "Usage::  %s <input particles file name> <output particles file name>"%(sys.argv[0])
		sys.exit(-1)
	input = sys.argv[1]
	output = sys.argv[2]
	
	stack=EMAN.readImages(input,-1,-1)
	i = 0
	for image in stack:
		print "Working on image %s"%(i)
		new_image = speckle_filter(image)
		new_image.writeImage(output,i)
		i=i+1

if __name__ == '__main__':
	main()
