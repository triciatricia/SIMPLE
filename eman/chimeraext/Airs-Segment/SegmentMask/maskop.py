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
#
# To Do:
#       See comments marked with # @
# 
"""Applies mask to volume data.

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

def mask_check_size(data_map, mask_map):

    data_xSize = data_map.xSize()
    data_ySize = data_map.ySize()
    data_zSize = data_map.zSize()

    if (data_xSize == mask_map.xSize() and
        data_ySize == mask_map.ySize() and
        data_zSize == mask_map.zSize()):
        size_match = 1
    else:
        size_match = 0

    return size_match

def maskop_multiply(data, mask_data, out_path):

    data_map = EMAN.EMData()
    data_map.readImage(data.path)

    mask_map = EMAN.EMData()
    mask_map.readImage(mask_data.path)

    size_match = mask_check_size(data_map, mask_map)
    if size_match == 0:
        print 'Mismatch in data and mask size!\n'
        return None
        
    data_map.mult(mask_map)
    data_map.update()
    data_map.writeImage(out_path,-1)

    return 1    

def maskop_add(data, mask_data, out_path):

    data_map = EMAN.EMData()
    data_map.readImage(data.path)

    mask_map = EMAN.EMData()
    mask_map.readImage(mask_data.path)

    size_match = mask_check_size(data_map, mask_map)
    
    if size_match == 0:
        print 'Mismatch in data and mask size!\n'
        return None
        
    data_map.add(mask_map)
    data_map.update()
    data_map.writeImage(out_path,-1)

    return 1    

def maskop_add_bin(data, mask_data, out_path, sub=0):

    data_map = EMAN.EMData()
    data_map.readImage(data.path)

    mask_map = EMAN.EMData()
    mask_map.readImage(mask_data.path)

    size_match = mask_check_size(data_map, mask_map)
    
    if size_match == 0:
        print 'Mismatch in data and mask size!\n'
        return None

    # subtract mask from data
    if sub == 1: mask_map.multConst(-1.0)
        
    data_map.add(mask_map) 
    data_map.update()

    #@ Now make this binary. We could have used proc3d
    #  but that means making a system call...
    dat = data_map.getData()
    for ix in range(data_map.xSize()):
        for iy in range(data_map.ySize()):
            for iz in range(data_map.zSize()):
                if dat[ix][iy][iz] >= 0.5:
                    dat[ix][iy][iz] = 1.0
                else:
                    dat[ix][iy][iz] = 0.0
    data_map.setData(dat)
    data_map.update()
    data_map.writeImage(out_path,-1)

    return 1

# -------------------------------------------------------------------------
