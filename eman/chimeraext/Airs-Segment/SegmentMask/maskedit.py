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
"""Creates mask for volume data.

"""

# -------------------------------------------------------------------------

import os
import sys

from sys import argv

# ensure EMAN is included in PYTHONPATH

import EMAN

mask_type_choices = {0: 'Cuboid      ',
                     1: 'Ellipsoid   ',
                     2: 'Cylindrical ',
                     3: 'Pyramid     ',
                     4: 'Cone        '}

# -------------------------------------------------------------------------
# Create mask functions
# -------------------------------------------------------------------------

def create_mask(mask_shape,p0,p1,p2,mask_path,mask_origin,
                mask_size,mask_step,talign,ralign,radial=0):

    ijk_size = mask_size
    xyz_step = mask_step
    xyz_origin = mask_origin

    #@ Right now, we do not have an EMData.setXYZOrigin
    #  function. Therefore, we offset the origin first
    #  using talign, then later shift origin by talign
    xyz_origin = map(lambda a,b,c:a+b*c, xyz_origin, talign,xyz_step)

    if   mask_shape == mask_type_choices[0]:
        arr = create_cuboid_arr(p0,p1,p2,ijk_size,radial)
    elif mask_shape == mask_type_choices[1]:
        arr = create_ellipsoid_arr(p0,p1,p2,ijk_size,radial)
    elif mask_shape == mask_type_choices[2]:
        arr = create_cylinder_arr(p0,p1,ijk_size,radial)
    elif mask_shape == mask_type_choices[3]:
        if   p2 == 3:
            arr = create_pyramid3_arr(p0,p1,ijk_size,radial)
        elif p2 == 4:
            arr = create_pyramid4_arr(p0,p1,ijk_size,radial)
        else:
            msg = 'failed - pyramid allows 3 or 4 sides only'
            return msg
    elif mask_shape == mask_type_choices[4]:
        arr = create_cone_arr(p0,p1,ijk_size,radial)
    else:
        msg = 'failed - uknown shape'
        return msg

    if arr == None:
        return 'failed'
    
    from VolumeData import arraygrid
    data_map = arraygrid.Array_Grid_Data(arr, xyz_origin, xyz_step)

    import SegmentWrite
    from SegmentWrite import mrc_write
    if not mrc_write.save_mrc(data_map, path='temp_mask.mrc'):
        return "failed"

    import EMAN
    data_eman = EMAN.EMData()
    data_eman.readImage('temp_mask.mrc')

    data_eman.setTAlign(talign[0],talign[1],talign[2])
    data_eman.setRAlign(ralign[1],ralign[0],ralign[2])
    data_eman.rotateAndTranslate()
    # data_eman.setXYZOrigin(xyz_origin)
    data_eman.update()

    if ralign[0] == 0.0 and ralign[1] == 0.0 and ralign[2] == 0.0:
        data_update = 0
    else:
        data_update = 1

    if data_update == 1:
        dat = data_eman.getData()
        for ix in range(data_eman.xSize()):
            for iy in range(data_eman.ySize()):
                for iz in range(data_eman.zSize()):
                    if dat[ix][iy][iz] >= 0.1:
                        dat[ix][iy][iz] = 1.0
                    else:
                        dat[ix][iy][iz] = 0.0
        data_eman.setData(dat)
        data_eman.update()
    
    data_eman.writeImage(mask_path,-1)

    mask_file = os.path.basename(mask_path)
    msg = 'written %s' % mask_file

    return msg

# -------------------------------------------------------------------------
# Cuboid mask functions
# -------------------------------------------------------------------------

def create_cuboid_arr(p0,p1,p2,ijk_size,radial):
    
    ijk_center = map(lambda a: a/2, ijk_size)
    ix0 = ijk_center[0] - p0/2
    ix1 = ijk_center[0] + p0/2
    iy0 = ijk_center[1] - p1/2
    iy1 = ijk_center[1] + p1/2
    iz0 = ijk_center[2] - p2/2
    iz1 = ijk_center[2] + p2/2

    import Numeric
    etype = Numeric.Float32
    arr = Numeric.zeros((ijk_size[2],ijk_size[1],ijk_size[0]),etype)

    import math
    d_max = math.sqrt( math.pow(p0/2.,2) +
                       math.pow(p1/2.,2) +
                       math.pow(p2/2.,2))
    for ix in range(ix0,ix1):
        for iy in range(iy0,iy1):
            for iz in range(iz0,iz1):
                if (ix >= 0 and ix < ijk_size[0] and
                    iy >= 0 and iy < ijk_size[1] and
                    iz >= 0 and iz < ijk_size[2]):
                    if radial == 0:
                        arr[iz][iy][ix] = 1.0
                    else:
                        d = math.sqrt( math.pow(ix - ijk_center[0],2.) +
                                       math.pow(iy - ijk_center[1],2.) +
                                       math.pow(iz - ijk_center[2],2.) )
                        arr[iz][iy][ix] = d/d_max

    return arr

# -------------------------------------------------------------------------
# Ellipsoid mask functions
# -------------------------------------------------------------------------

def create_ellipsoid_arr(p0,p1,p2,ijk_size,radial):

    ijk_center = map(lambda a: a/2, ijk_size)
    
    ix0 = ijk_center[0] - p0/2
    ix1 = ijk_center[0] + p0/2
    iy0 = ijk_center[1] - p1/2
    iy1 = ijk_center[1] + p1/2
    iz0 = ijk_center[2] - p2/2
    iz1 = ijk_center[2] + p2/2

    import Numeric
    etype = Numeric.Float32
    arr = Numeric.zeros((ijk_size[2],ijk_size[1],ijk_size[0]),etype)

    import math
    rad_max = [p0/2., p1/2., p2/2.]
    for ix in range(ix0,ix1):
        for iy in range(iy0,iy1):
            for iz in range(iz0,iz1):
                if (ix >= 0 and ix < ijk_size[0] and
                    iy >= 0 and iy < ijk_size[1] and
                    iz >= 0 and iz < ijk_size[2]):
                    rad = math.sqrt(
                        math.pow( (ix - ijk_center[0])/rad_max[0],2) +
                        math.pow( (iy - ijk_center[1])/rad_max[1],2) +
                        math.pow( (iz - ijk_center[2])/rad_max[2],2))
                    if rad <= 1.0:
                        if radial == 0:
                            arr[iz][iy][ix] = 1.0
                        else:   
                            arr[iz][iy][ix] = rad

    return arr

# -------------------------------------------------------------------------
# Cylindrical mask functions
# -------------------------------------------------------------------------

def create_cylinder_arr(p0,p1,ijk_size,radial):

    ijk_center = map(lambda a: a/2, ijk_size)
    
    ix0 = ijk_center[0] - p0/2
    ix1 = ijk_center[0] + p0/2
    iy0 = ijk_center[1] - p0/2
    iy1 = ijk_center[1] + p0/2
    iz0 = ijk_center[2] - p1/2
    iz1 = ijk_center[2] + p1/2

    import Numeric
    etype = Numeric.Float32
    arr = Numeric.zeros((ijk_size[2],ijk_size[1],ijk_size[0]),etype)

    import math
    rad_max = p0/2.
    for ix in range(ix0,ix1):
        for iy in range(iy0,iy1):
            for iz in range(iz0,iz1):
                if (ix >= 0 and ix < ijk_size[0] and
                    iy >= 0 and iy < ijk_size[1] and
                    iz >= 0 and iz < ijk_size[2]):
                    rad = math.sqrt( math.pow(ix - ijk_center[0],2) +
                                     math.pow(iy - ijk_center[1],2) )
                    if rad < rad_max:
                        if radial == 0:
                            arr[iz][iy][ix] = 1.0
                        else:   
                            arr[iz][iy][ix] = rad/rad_max
    return arr

# -------------------------------------------------------------------------
# Pyramid mask functions
# -------------------------------------------------------------------------

def create_pyramid4_arr(p0,p1,ijk_size,radial):
    
    ijk_center = map(lambda a: a/2, ijk_size)
    
    ix0 = ijk_center[0] - p0/2
    ix1 = ijk_center[0] + p0/2
    iy0 = ijk_center[1] - p0/2
    iy1 = ijk_center[1] + p0/2
    iz0 = ijk_center[2] - p1/2
    iz1 = ijk_center[2] + p1/2

    import Numeric
    etype = Numeric.Float32
    arr = Numeric.zeros((ijk_size[2],ijk_size[1],ijk_size[0]),etype)

    import math
    d_max = math.sqrt( 2* math.pow(p0/2., 2))
    for ix in range(ix0,ix1):
        for iy in range(iy0,iy1):
            d_x = math.fabs(ix - ijk_center[0])
            d_y = math.fabs(iy - ijk_center[1])
            for iz in range(iz0,iz1):
                if (ix >= 0 and ix < ijk_size[0] and
                    iy >= 0 and iy < ijk_size[1] and
                    iz >= 0 and iz < ijk_size[2]):
                    d = math.sqrt( math.pow( ix - ijk_center[0],2) +
                                   math.pow( iy - ijk_center[1],2))
                    d_end = (p0/2.)*(iz1 - iz)/(iz1 - iz0)
                    if d_x < d_end and d_y < d_end:
                        if radial == 0:
                            arr[iz][iy][ix] = 1.0
                        else:   
                            arr[iz][iy][ix] = d/d_max

    return arr

def create_pyramid3_arr(p0,p1,ijk_size,radial):

    ijk_center = map(lambda a: a/2, ijk_size)
    
    ix0 = ijk_center[0] - p0/2
    ix1 = ijk_center[0] + p0/2
    iy0 = ijk_center[1] - p0/2
    iy1 = ijk_center[1] + p0/2
    iz0 = ijk_center[2] - p1/2
    iz1 = ijk_center[2] + p1/2

    import Numeric
    etype = Numeric.Float32
    arr = Numeric.zeros((ijk_size[2],ijk_size[1],ijk_size[0]),etype)
    
    import math
    d_max = math.sqrt( 2* math.pow(p0/2., 2))
    for iz in range(iz0,iz1):
        xp = ( float(p0)/float(p1) )*(iz1 - iz)
        x2 = ijk_center[0] - xp/2.
        x3 = ijk_center[0] + xp/2.
        ix2 = int(x2)
        ix3 = int(x3)
        yp = math.sqrt(3)*xp/2.
        for ix in range(ix2,ix3):
            y2 = ijk_center[1] - (yp/3.)
            iy2 = int(y2)
            if ix < ijk_center[0]:
                y3 = math.sqrt(3)*(ix - x2) + y2
            else:
                y3 = math.sqrt(3)*(x3 - ix) + y2
            iy3 = int(y3)
            for iy in range(iy2,iy3):
                if (ix >= 0 and ix < ijk_size[0] and
                    iy >= 0 and iy < ijk_size[1] and
                    iz >= 0 and iz < ijk_size[2]):
                    if radial == 0:
                        arr[iz][iy][ix] = 1.0
                    else:
                        d = math.sqrt( math.pow( ix - ijk_center[0],2) +
                                       math.pow( iy - ijk_center[1],2))
                        arr[iz][iy][ix] = d/d_max
    
    return arr

# -------------------------------------------------------------------------
# Conic mask functions
# -------------------------------------------------------------------------

def create_cone_arr(p0,p1,ijk_size,radial):
    
    ijk_center = map(lambda a: a/2, ijk_size)
    
    ix0 = ijk_center[0] - p0/2
    ix1 = ijk_center[0] + p0/2
    iy0 = ijk_center[1] - p0/2
    iy1 = ijk_center[1] + p0/2
    iz0 = ijk_center[2] - p1/2
    iz1 = ijk_center[2] + p1/2

    import Numeric
    etype = Numeric.Float32
    arr = Numeric.zeros((ijk_size[2],ijk_size[1],ijk_size[0]),etype)

    import math
    rad_max = p0/2.
    for ix in range(ix0,ix1):
        for iy in range(iy0,iy1):
            for iz in range(iz0,iz1):
                if (ix >= 0 and ix < ijk_size[0] and
                    iy >= 0 and iy < ijk_size[1] and
                    iz >= 0 and iz < ijk_size[2]):
                    rad = math.sqrt( math.pow(ix - ijk_center[0],2) +
                                     math.pow(iy - ijk_center[1],2) )
                    d_max = rad_max*(iz1 - iz)/float(iz1-iz0)
                    if rad < d_max:
                        if radial == 0:
                            arr[iz][iy][ix] = 1.0
                        else:   
                            arr[iz][iy][ix] = rad/rad_max

    return arr

# -------------------------------------------------------------------------
