#!/usr/bin/env python
#
# Segment Volume package - Segment Simple module
# 
# Author:
#       Lavu Sridhar, Baylor College of Medicine (BCM)
#
# Revisions:
#       2005.01.15: Lavu Sridhar, BCM
#       2005.02.15: Lavu Sridhar, BCM
#       2006.05.24: Lavu Sridhar, BCM (VU Circle Mask)
#
# To Do:
#       See comments marked with # @
# 
"""Segments out a bunch of box regions from a density map

 1. Segment out box regions around markers (-ve radius = zero
          out box) into <num> output files.
 boxes.py <input.mrc> <output_name.mrc> boxes=<marker.temp.cmm>
          num=<single or multiple> 
  or
 2. Clip out box region (xn,yn,zn,xc,yc,zc) and pad to
         size (xp,yp,zp) and center (xpc,ypc,zpc) 
 boxes.py <input.mrc> <output.mrc> clip=<xn,yn,zn,xc,yc,zc>
          [pad=<xp,yp,zp,xpc,ypc,zpc>]
  or
 3. Clip out circular region (xn,yn,zn,xc,yc,zc) and pad to
         size (xp,yp,zp) and center (xpc,ypc,zpc) 
 boxes.py <input.mrc> <output.mrc> circle=<xn,yn,zn,xc,yc,zc>
          [pad=<xp,yp,zp,xpc,ypc,zpc>]
  or
 4. Segment out nearest neighborhood regions around markers
         into <num> output files.
 boxes.py <input.mrc> <output_name.mrc> near=<markers.temp.cmm>
          num=<single or multiple> near

 This script file is called by Segment Simple and Segment Marker
 sub-modules of the Segment Simple module in the Segment Volume
 package.

 Note that markers.cmm are not the same as the Chimera marker files.
"""

# -------------------------------------------------------------------------

import os
import sys

from sys import argv

# ensure EMAN is included in PYTHONPATH

import EMAN

# -------------------------------------------------------------------------
# EMAN based local functions
# -------------------------------------------------------------------------

def readMarkerFile(fileName):
    """readMarkerFile(filename) - read marker file.

    Input:
        fileName    marker file name

    Output:
        boxes       a list, each entry - integers of box
                    center and box radius

    Read box info from marker file (for marker mode).
    Returns boxes which has the box center (x,y,z) and
    box radius, all integers.
    """
    
    markerFile = open(markerFileName,'r')
    markerLines = markerFile.readlines()
    markerFile.close()
    
    boxes = []
    for line in markerLines:
        # check if box
        isbox = str(line[1:7].strip())
        if isbox == "BOX":
            boxCenterX, boxCenterY, boxCenterZ, boxRadius = \
                        line[9:50].split(' ')
            boxCenterX = int(boxCenterX)
            boxCenterY = int(boxCenterY)
            boxCenterZ = int(boxCenterZ)
            boxRadius = int(boxRadius)
            boxes.append([boxCenterX,boxCenterY,boxCenterZ,boxRadius])

    return boxes

def chopBlock(bigmap, xStart,yStart,zStart, xSize,ySize,zSize):
    """chopBlock(bigmap, xStart, yStart, zStart,
                 xSize, ySize, zSizez) - chop out box using EMAN

    Input:
        bigmap      input map
        xStart      starting coordinates of block in bigmap
        yStart
        zStart
        xSize       block size
        ySize
        zSize

    Output:
        chunk       output map of size (xSize, ySize, zSize)

    Chops out a box region starting at (xStart,yStart,zStart)
    with box dimensions (xSize,ySize,zSize), from bigmap.
    
    Uses EMAN's clip function, which pad's output if required.
    """

    chunk = bigmap.copy()
    chunk = chunk.clip(xStart,yStart,zStart,xSize,ySize,zSize)
    chunk.update()

    return chunk

def zeroBlock(bigmap, xStart,yStart,zStart, xSize,ySize,zSize):
    """zeroBlock(bigmap, xStart, yStart, zStart,
                 xSize, ySize, zSize) - chop out box using EMAN

    Input:
        bigmap      input map
        xStart      starting coordinates of block in bigmap
        yStart
        zStart
        xSize       block size
        ySize
        zSize

    Output:
        chunk       output map set to zero and of size
                    (xSize, ySize, zSize)

    Chops out a box region starting at (xStart,yStart,zStart)
    with box dimensions (xSize,ySize,zSize), from bigmap and
    sets all values to 0.
    
    Uses EMAN's clip function, which pads output if required.
    """    
    
    chunk = bigmap.copy()
    chunk = chunk.clip(xStart,yStart,zStart,xSize,ySize,zSize)
    chunk.zero()
    
    return chunk

# -------------------------------------------------------------------------
# Local functions
# -------------------------------------------------------------------------

def copyBlock(outmap, chunk, xStart,yStart,zStart):
    """copyBlock(outmap, chunk, xStart, yStart, zStart) 

    Input:
        outmap      output map
        chunk       input map to be copied
        xStart      starting location in outmap
        yStart          
        zStart

    Output:
        outmap      map after copying chunk

    Copies block of data in chunk to outmap at starting point
    given by (xStart,yStart,zStart), without shrinking or
    padding outmap.
    """
    

    # check boundary conditions
    chunk_xSize = chunk.xSize()
    if xStart < 0: x1 = 0
    else: x1 = xStart
    if xStart+chunk_xSize > outmap.xSize(): x2 = outmap.xSize()
    else: x2 = xStart+chunk_xSize

    chunk_ySize = chunk.ySize()
    if yStart < 0: y1 = 0
    else: y1 = yStart
    if yStart+chunk_ySize > outmap.ySize(): y2 = outmap.ySize()
    else: y2 = yStart+chunk_ySize

    chunk_zSize = chunk.zSize()
    if zStart < 0: z1 = 0
    else: z1 = zStart
    if zStart+chunk_zSize > outmap.zSize(): z2 = outmap.zSize()
    else: z2 = zStart+chunk_zSize

    # copy the part of chunk that is within outmap boundary
    for x in range(x1,x2):
        for y in range(y1,y2):
            for z in range(z1,z2):
                val = chunk.valueAt(x-xStart,y-yStart,z-zStart)
                outmap.setValueAt(x,y,z,val)

    outmap.update()
    
    return outmap

def findNearMaps(inpMap, xCenters, yCenters, zCenters):
    """findNearMaps(inpMap, xCenters, yCenters, zCenters)

    Input:
        inpMap          input map
        xCenters        neighborhood centers
        yCenters
        zCenters

    Output:
        outMaps         list of output map, with one map
                        for each neighborhood center

    Find and return nearest neighborhood maps around centers
    given by (xCenters,yCenter,zCenters). Used in near mode.

    Use a threshold to speed up things.
    """
    
    # @ Use a threshold to speed up things.

    thr = 0
    
    outMaps = []
    numMaps = len(xCenters)
    
    for i in range(numMaps):
        outMap = inpMap.copy()
        outMap.zero()
        outMaps.append(outMap)

    xStart = 0
    yStart = 0
    zStart = 0
    xEnd = inpMap.xSize()
    yEnd = inpMap.ySize()
    zEnd = inpMap.zSize()

    for x in range(xStart,xEnd):
        for y in range(yStart,yEnd):
            for z in range(zStart,zEnd):
                val = inpMap.valueAt(x,y,z)
                if val > thr:
                    i = findNearPoint(x,y,z, xCenters,yCenters,zCenters)
                    outMaps[i].setValueAt(x,y,z,val)

    return outMaps

def findNearPoint(x,y,z, xCenters,yCenters,zCenters):
    """findNearPoint(x,y,z, xCenters,yCenters,zCenters)

    Find nearest point to (x,y,z) from all the points in
    (xCenters, yCenters, zCenters). Used in near mode.
    """

    numPoints = len(xCenters)

    d1 = None
    p1 = 0
    for p in range(numPoints):
        d = (x-xCenters[p])**2 + (y-yCenters[p])**2 + (z-zCenters[p])**2
        if d == 0:
            return p
        if d1 == None:
            d1 = d
            p1 = p
        if d < d1:
            d1 = d
            p1 = p

    return p1


# -------------------------------------------------------------------------
# -------------------------------- MAIN -----------------------------------
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
# Usage (3 options: marker mode, clip mode, near mode)
# -------------------------------------------------------------------------

usage = 'Usage:\t boxes.py\n\n'
usage = usage + '1. Segment out' + \
        ' box regions around markers (-ve radius = zero \n' + \
        '            out box) into <num> output files.\n'
usage = usage + '   boxes.py ' + \
        '<input.mrc> <output_name.mrc> boxes=<marker.temp.cmm> \n' + \
        '     num=<single or multiple>\n'
usage = usage + '\tor\n2. Segment out' + \
        ' box region (xn,yn,zn,xc,yc,zc) and pad to \n' + \
        '            size (xp,yp,zp) and center (xpc,ypc,zpc)\n'
usage = usage + '   boxes.py ' + \
        '<input.mrc> <output.mrc> clip=<nx,ny,nz,cx,cy,cz> \n' + \
        '     [pad=<xp,yp,zp,xpc,ypc,zpc>]\n'
usage = usage + '\tor\n3. Segment out' + \
        ' circular region (xn,yn,zn,xc,yc,zc) and pad to \n' + \
        '            size (xp,yp,zp) and center (xpc,ypc,zpc)\n'
usage = usage + '   boxes.py ' + \
        '<input.mrc> <output.mrc> circle=<nx,ny,nz,cx,cy,cz> \n' + \
        '     [pad=<xp,yp,zp,xpc,ypc,zpc>]\n'
usage = usage + '\tor\n4. Segment out' + \
        ' nearest neighborhood regions around markers\n'+ \
        '            into <num> output files.\n' 
usage = usage + '   boxes.py ' + \
        '<input.mrc> <output_name.mrc> near=<marker.temp.cmm> \n' + \
        '     num=<single or multiple>\n'

# -------------------------------------------------------------------------
# Check input arguments
# -------------------------------------------------------------------------

if len(argv) < 4:
    print 'Insufficient arguements!\n'
    print usage
    sys.exit(1)

inpMapName = argv[1]
outMapName = argv[2]

# -------------------------------------------------------------------------
# Check for mode and relevant arguments
# -------------------------------------------------------------------------

# @ do better
 
boxesMode = 0 # multiple boxes
clipMode  = 0 # clip arguments
nearMode  = 0 # nearest neighborhood
outMode   = 0 # single output file (used in near and boxes modes)
padInput  = 0 # used in clip mode
circMode  = 0 # used for circular mask
 
arg3 = argv[3]
arg3s = arg3.split('=')
if arg3s[0] == 'boxes':
    boxesMode = 1
    markerFileName = arg3s[1]
elif arg3s[0] =='near':
    nearMode = 1
    markerFileName = arg3s[1]
elif arg3s[0] == 'clip':            
    clipMode = 1                    # clip mode
    clipArg = arg3s[1].split(',')
    if len(clipArg) != 6:
        print 'Incrorrect clip parameters!\n'
        print usage
        sys.exit(1)
elif arg3s[0] == 'circle':
    clipMode = 1
    circMode = 1
    clipArg = arg3s[1].split(',')
    if len(clipArg) != 6:
        print 'Incorrect circular mask parameters!\n'
        print usage
        sys.exit(1)

if nearMode or boxesMode:
    if len(argv) == 5:
        arg4 = argv[4]
        arg4s = arg4.split('=')
        if arg4s[0] == 'num':
            if arg4s[1] == 'multiple':
                outMode = 1
            elif arg4s[1] == 'single':
                pass
            else:
                print 'Incorrect <num> parameters!\n'
                print usage
        else:
            print 'Incorrect parameters!\n'
            print usage
    else:
        print 'Insufficient parameters!\n'
        print usage

if clipMode:
    if len(argv) == 4:
        padInput = 0    #  reduce box size to chunk
    else:
        arg4 = argv[4]
        arg4s = arg4.split('=')
        padInput = 1
        padArg = arg4s[1].split(',')
        if len(padArg) != 6:
            print 'Incorrect pad parameters!\n'
            print usage
            sys.exit(1)
    outMode = 0

if boxesMode:
    print ' boxes.py %s %s boxes=%s num=%s' \
          % (inpMapName, outMapName, markerFileName, arg4s[1])
elif nearMode:
    print ' boxes.py %s %s near=%s num=%s' \
          % (inpMapName, outMapName, markerFileName, arg4s[1])
elif clipMode and (not padInput) and (not circMode):
    print ' boxes.py %s %s clip=%s' \
          % (inpMapName, outMapName, arg3s[1])
elif clipMode and padInput and (not circMode):
    print ' boxes.py %s %s clip=%s pad=%s' \
          % (inpMapName, outMapName, arg3s[1], arg4s[1])
elif clipMode and (not padInput) and circMode:
    print ' boxes.py %s %s circle=%s' \
          % (inpMapName, outMapName, arg3s[1])
elif clipMode and padInput and circMode:
    print ' boxes.py %s %s circle=%s pad=%s' \
          % (inpMapName, outMapName, arg3s[1], arg4s[1])
else:
    print argv
    print usage
    sys.exit(1)
    
# -------------------------------------------------------------------------
# Read input map file
# -------------------------------------------------------------------------

inpMap = EMAN.EMData()
inpMap.readImage(inpMapName,-1)
xSize = inpMap.xSize()
ySize = inpMap.ySize()
zSize = inpMap.zSize()

# -------------------------------------------------------------------------
# Clip mode has additional inputs: 6 inputs for box size and center,
# and 3 optional inputs for output size after symmetric zero padding.
# If the 3 optional inputs are same as box size, then skip padding.
# -------------------------------------------------------------------------

if clipMode:
    
    xn = int(clipArg[0])
    yn = int(clipArg[1])
    zn = int(clipArg[2])
    xc = int(clipArg[3])
    yc = int(clipArg[4])
    zc = int(clipArg[5])

    if padInput == 1:
        xp = int(padArg[0])
        yp = int(padArg[1])
        zp = int(padArg[2])
        xpc = int(padArg[3])
        ypc = int(padArg[4])
        zpc = int(padArg[5])
        # if smaller or same as box size, then skip padding
        if (xp <= xn) and (yp <= yn) and (zp <= zn):
            padInput = 0

# -------------------------------------------------------------------------
# Check modes
# -------------------------------------------------------------------------

# For near mode, no use putting them all back together!

if nearMode:
    if outMode == 0:
        outMode = 1

# -------------------------------------------------------------------------
# Read marker file 
# -------------------------------------------------------------------------

if boxesMode or nearMode:
    boxes = readMarkerFile(markerFileName)
    
# -------------------------------------------------------------------------
# Output map file: If single output file, #?
# make a copy of the input, and initialize to 0.
# -------------------------------------------------------------------------

if outMode:
    outMaps = []
    numMaps = len(boxes)
    for i in range(numMaps):
        outMap = inpMap.copy()
        outMap.zero()
        outMaps.append(outMap)
else:
    outMap = inpMap.copy()
    outMap.zero()

# -------------------------------------------------------------------------
# If boxes mode, read mareker info and copy boxes to output map.
# -------------------------------------------------------------------------

if boxesMode:
    
    i = 0
    for box in boxes:
        xCenter = box[0]
        yCenter = box[1]
        zCenter = box[2]
        radius = box[3]
        xStart = int(xCenter - radius)
        yStart = int(yCenter - radius)
        zStart = int(zCenter - radius)
        boxSize = int(2*radius)
        if boxSize > 0:
            print "box+    %d %d %d %d" % (xStart,yStart,zStart,boxSize)
            chunkMap = chopBlock(inpMap,xStart,yStart,zStart,
                                 boxSize,boxSize,boxSize)
            if outMode:
                outMaps[i] = copyBlock(outMaps[i],chunkMap,
                                       xStart,yStart,zStart)
                outMaps[i].update()
            else:
                outMap = copyBlock(outMap,chunkMap,xStart,yStart,zStart)
        i = i + 1
        
    i = 0        
    for box in boxes:
        xCenter = box[0]
        yCenter = box[1]
        zCenter = box[2]
        radius = box[3]
        xStart = int(xCenter + radius)
        yStart = int(yCenter + radius)
        zStart = int(zCenter + radius)
        boxSize = int(2*radius)
        if boxSize < 0:
            boxSize = abs(boxSize)
            print "box-    %d %d %d %d" % (xStart,yStart,zStart,boxSize)
            if outMode:
                chunkMap = chopBlock(inpMap,xStart,yStart,zStart,
                                     boxSize,boxSize,boxSize)
                outMaps[i] = copyBlock(outMaps[i],chunkMap,
                                       xStart,yStart,zStart)
                outMaps[i].update
            else:
                chunkMap = zeroBlock(inpMap,xStart,yStart,zStart,
                                 boxSize,boxSize,boxSize)
                outMap = copyBlock(outMap,chunkMap,xStart,yStart,zStart)
        i = i + 1

    if outMode == 0:
        outMap.update()

# -------------------------------------------------------------------------
# If clip mode, copy clip box to output map.
# -------------------------------------------------------------------------

if clipMode:
    
    # imitate proc3d stuff
    if (not (xc >= 0 and yc >= 0 and zc >= 0 and
             xc < xSize and yc < ySize and zc < zSize)):
        xc = xSize/2
        yc = ySize/2
        zc = zSize/2

    xStart = xc - xn/2
    yStart = yc - yn/2
    zStart = zc - zn/2

    chunkMap = chopBlock(inpMap,xStart,yStart,zStart,xn,yn,zn)

    if circMode:
        chunkMap.applyMask(min(xn/2,yn/2,zn/2),4,0,0,0)

    if padInput == 1:
        xpStart = xpc - xp/2
        ypStart = ypc - yp/2
        zpStart = zpc - zp/2
        # if does not include box, then skip padding
        if ((xpStart > xStart) or (xpStart + xp < xStart + xn) or
            (ypStart > yStart) or (ypStart + yp < yStart + yn) or
            (zpStart > zStart) or (zpStart + zp < zStart + zn)):
            pad_input = 0

    if   padInput == 0:
        outMap = chunkMap.copy()
        outMap.update()
    elif padInput == 1:
        # update origin to chunkMap origin from inpMap origin
        xS = xpStart - xStart
        yS = ypStart - yStart
        zS = zpStart - zStart
        outMap = chopBlock(chunkMap,xS,yS,zS,xp,yp,zp)

# -------------------------------------------------------------------------
# If near mode, then find regions nearest to markers
# -------------------------------------------------------------------------

if nearMode:

    xCenters = []
    yCenters = []
    zCenters = []
    for box in boxes:
        xCenters.append(box[0])
        yCenters.append(box[1])
        zCenters.append(box[2])

    outMaps = findNearMaps(inpMap, xCenters, yCenters, zCenters)
    
# -------------------------------------------------------------------------
# Write output map(s)
# -------------------------------------------------------------------------

if outMode:

    # remove suffix from input name
    try:
        dot_position = outMapName.rindex('.')
        first_part = outMapName[:dot_position]
        last_part = outMapName[dot_position:]
    except:
        first_part = outMapName
        last_part = ''

    for i in range(len(boxes)):
        name = first_part + '-%d' % (i)
        name = name + last_part
        outMaps[i].writeImage(name,-1)

else:
    outMap.writeImage(outMapName,-1)


# -------------------------------------------------------------------------
