#!/bin/env python
import os

d=os.listdir(".")
a=set([i[:-4] for i in d if i[-4:]==".mrc"])
b=set([i[:-4] for i in d if i[-4:]==".box"])
a=a-b

for i in a: 
	os.system("boxer %s scale=.25 contrast=.5"%i)
