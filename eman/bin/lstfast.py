#!/usr/bin/env python
# 05/06/05  lstfast.py  Steven Ludtke
# This program will produce an optimized LST file (LSX file)
# This will be MUCH faster when files are >~10,000 particles

import os
import sys
import string
import time 

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



def main():

	if len(sys.argv)<2 :
		print "Usage lstfast.py <lst file> ..."
		sys.exit(1)
		
	LOGbegin(sys.argv)
	
	for f in sys.argv[1:]:
		try: fin=open(f,"r")
		except:
			print "Could not open '%s'. Skipping"%f
			continue
		
		
		maxlen=0
		while (1):
			try: l=fin.readline()
			except: break
			l=l.strip()
			if len(l)==0 : break
			if l[0]=="#" : continue
			if len(l)>maxlen: maxlen=len(l) + 1
		maxlen += 1	# include line end \n
			
		out=file("lstfast.tmp","w")
		out.write("#LSX\n#If you edit this file, you MUST rerun lstfast.py on it before using it!\n# %d\n"%maxlen)
		fin.seek(0)
		
		while (1):
			try: l=fin.readline()
			except: break
			l=l.strip()
			if len(l)==0 : break
			if l[0]=="#" : continue
			out.write(l+' '*(maxlen-len(l)-1)+"\n")
		
		fin.close()
		out.close()
		os.unlink(f)
		os.rename("lstfast.tmp",f)

	LOGend()
	
main()
