#!/usr/bin/env python
import os

for i in range(1,40):
	os.system("rm -f cls*lst")
	try:
		r=os.system("tar xf cls.%d.tar 2>/dev/null"%i)
	except:
		continue
	if r : continue
	l=[]
	for j in range(9999):
		try: fin=open("cls%04d.lst"%j,"r")
		except : break
		l2=fin.readlines()
		fin.close()
		l2=[int(x.split()[0]) for x in l2[2:]]
		l+=l2
	l.sort()
	l.reverse()

	print "Iteration ",i
	print "%d ptcl"%len(l)
	for j in range(1,len(l)):
		if l[j]-l[j-1]>1 : print range(l[j-1]+1,l[j])
