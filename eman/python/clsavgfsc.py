#!/usr/bin/env python
import EMAN
import sys

APIX=1.06          # Angstroms/pixel

img1=EMAN.EMData()      # create a new image object
img2=EMAN.EMData()

file=sys.argv[1]
n=int(sys.argv[2])

img1.readImage(file,n*2)    # read image 5 from the image file
img2.readImage(file,n*2+1)

fsc=img1.fsc(img2)

n=0.0
for f in fsc:
        print n/(APIX*img1.xSize()),f
        n+=1.0

