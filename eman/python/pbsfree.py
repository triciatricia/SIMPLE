#!/usr/bin/env python

# by Wen Jiang <wjiang@gmail.com> 2005-11-24

# $Id: pbsfree.py,v 1.3 2005/11/25 01:15:21 wjiang Exp $

import os

class Node:
	def __init__(self):
		self.name = ""
		self.status = "" # free, used, down
		self.ncpu = 0
		self.ncpu_used = 0
		self.ncpu_free = 0
	def __str__(self):
		s  = "Node     name: %s\n" % (self.name)
		s += "       status: %s\n" % (self.status)
		s += "  # all  cpus: %d\n" % (self.ncpu)
		s += "  # used cpus: %d\n" % (self.ncpu_used)
		s += "  # free cpus: %d\n" % (self.ncpu_free)
		return s

lines = os.popen("pbsnodes -a","r").readlines()

seplines = []
for i in range(len(lines)):
	line = lines[i]
	if not line[0].isspace(): seplines.append(i)
seplines.append(len(lines))
	
nodes = []
for i in range(len(seplines)-1):
	i0 = seplines[i]
	i1  = seplines[i+1]
	
	node = Node()
	node.name = lines[i0].strip()
	for j in range(i0+1,i1):
		try:
			#print j, lines[j]
			key, val = lines[j].split("=")
			key = key.strip()
			val = val.strip()
			
			if key == "state":
				if val == "free": node.status = "free"
				elif val in ["job-busy","job-exclusive"]: node.status = "used"
				else: node.status = "down"
			elif key in ["np", "pcpus"]: node.ncpu = int(val)
			elif key in ["resources_available.ncpus"]: node.ncpu_free = int(val)
			elif key in ["resources_assigned.ncpus"]: node.ncpu_used = int(val)
		except:
			pass

	if node.ncpu < node.ncpu_free + node.ncpu_used:
		print "WARNING: node %s: total %d CPUS < %d used + %d free" % \
			(node.name, node.ncpu, node.ncpu_used, node.ncpu_free)
		node.ncpu_free = node.ncpu - node.ncpu_used
	if node.ncpu_free ==0 and node.ncpu_used ==0:
		if node.status == "free": node.ncpu_free = node.ncpu
		elif node.status == "used": node.ncpu_used = node.ncpu
	nodes.append(node)

nfreenodes = 0
nfreecpus = 0
ntotalnodes = 0
ntotalcpus = 0
nusednodes = 0
nusedcpus = 0
ndownnodes = 0
ndowncpus = 0

for node in nodes:
	ntotalnodes += 1
	ntotalcpus += node.ncpu
	if node.status == "free": 
		nfreenodes += 1
		nfreecpus += node.ncpu_free
		nusedcpus += node.ncpu_used
	elif node.status == "used":
		nusednodes += 1
		nfreecpus += node.ncpu_free
		nusedcpus += node.ncpu_used
	else:
		ndownnodes += 1
		ndowncpus += node.ncpu
		
print "Number of  all nodes: %3d\tcpu: %3d" % (ntotalnodes, ntotalcpus)
print "-----------------------------------------"
print "Number of used nodes: %3d\tcpu: %3d" % (nusednodes, nusedcpus)
print "Number of down nodes: %3d\tcpu: %3d" % (ndownnodes, ndowncpus)
print "Number of free nodes: %3d\tcpu: %3d" % (nfreenodes, nfreecpus)

