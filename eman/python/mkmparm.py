#!/usr/bin/env python
# this program creates a simple, local .mparm file with a number
# of assumptions. Please read the parallelization docs for
# EMAN before using this, assumes 2 cpus/node

import sys
import os
from sys import argv

if len(argv)==1:
	print "Please specify nodes"
	sys.exit(1)
elif len(argv)==2 :
	nodes=argv[1].split(',')
else : nodes=argv[1:]

out=open(".mparm","w")
for i in nodes:
	out.write("ssh\t2\t1\t%s\t%s\n"%(i,os.getcwd()))

out.close()
