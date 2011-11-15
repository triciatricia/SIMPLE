# -------------------------------------------------------------------------
# VolumeMorph/morphsimple.py
#
# Airs-Segment package - Volume Morph module
# 
# Author:
#       Lavu Sridhar, Baylor College of Medicine (BCM)
#
# Revisions:
#       2006.06.21: Lavu Sridhar, BCM
#
# To Do:
#       See comments marked with # @
# 
# Key:
#       VU: Version Upgrade
#
"""Morphing of volume density maps.

Performs volume morphing using linear deformation.
"""
# -------------------------------------------------------------------------

# general modules
import os
import math

# chimera related modules
import chimera

# -------------------------------------------------------------------------
# simple morph 
# -------------------------------------------------------------------------

def simple_morph(data, morph0, morph1, outMapName, frac, thr, filt):
    """simple_morph(data, morph0, morph1, outMapName, frac, thr, filt)

    Input:
        data        input VolumeData data object (grid data object)
        morph0      initial morph model (from PDB)
        morph1      final   morph model (from PDB)
        outMapName  output volume density map file name (MRC)
        frac        apply deformation to fraction=frac
        thr         threshold the input volume density map
        filt        apply low pass filter to morphed density

    Output:


    Applies simple morphing using linear deformation between
    the atom positions in the initial morph model (PDB) and 
    the atom positions in the final   morph model (PDB).

    The morphed density can be filtered using a low pass filter
    applied via the EMAN proc3d command.
    """

    use_filt = 1
    use_thr  = 1
    
    if filt == None: use_filt = 0
    if thr  == None: use_thr  = 0
    if ((frac < 0.1) or (frac > 1.0)): frac = 1.0

    ijk_origin = (0,0,0)
    ijk_size = data.size
    xyz_origin = data.origin
    xyz_step = data.step

    xS,yS,zS = ijk_size

    # volume original map values
    vomv = data.submatrix(ijk_origin,ijk_size)

    m0a = morph0.atoms
    m1a = morph1.atoms

    mLa = m0a.__len__()
    if m1a.__len__() > mLa:
        print '\tsecond morph model has more atoms than first!\n'

    import Numeric

    # volume displacement vectors and weights
    vdv = Numeric.zeros((zS,yS,xS,3),Numeric.Float32)
    vdw = Numeric.zeros((zS,yS,xS), Numeric.Float32)

    # volume morph map values
    vmmv = Numeric.zeros((zS,yS,xS),  Numeric.Float32)

    # morph model atom coordinates
    m0c =  Numeric.zeros((mLa,3),Numeric.Float32) # ijk coord
    m1c =  Numeric.zeros((mLa,3),Numeric.Float32) # ijk coord

    # morph model displacements
    m10 =  Numeric.zeros((mLa,3),Numeric.Float32) # ijk coord

    # compute the displacement (Ang) due to atoms in morph models
    for ia in range(mLa):
        a0c = data.xyz_to_ijk(m0a[ia].coord())
        a1c = data.xyz_to_ijk(m1a[ia].coord())
        a10 = map(lambda x,y,z=frac: (x-y)*z, a1c,a0c)
        for ic in range(3):
            m0c[ia][ic] = a0c[ic]
            m1c[ia][ic] = a1c[ic]
            m10[ia][ic] = a10[ic]

    print '\tcomputing deformation...'
    for ia in range(mLa):

        if math.fmod(ia,mLa/4) == 0.0:
            print '\t\t%0.0f percent complete ' % ((ia*100.0)/mLa)

        a0c = m0c[ia]
        sf = 10. # sphere of influence

        # range of voxels to consider
        ixyz0 = map(lambda x,y=sf: int(x-y), a0c)
        ixyz1 = map(lambda x,y=sf: int(x+y), a0c)
        ixyz0 = map(lambda x,y : (x > y)*x, ixyz0,ijk_origin)
        ixyz0 = map(lambda x,y : (x < y)*x, ixyz0,ijk_size)
        ixyz1 = map(lambda x,y : (x > y)*x, ixyz1,ijk_origin)
        ixyz1 = map(lambda x,y : (x < y)*x, ixyz1,ijk_size)
        ix0, iy0, iz0 = ixyz0
        ix1, iy1, iz1 = ixyz1
        
        for iz in range(iz0, iz1):
            for iy in range(iy0, iy1):
                for ix in range(ix0, ix1):

                    # ad and ad2 are distances between voxel and atom
                    ad2 = sum(map(lambda x,y: (x-y)*(x-y), [ix,iy,iz],a0c))
                    ad = math.sqrt(ad2)
                    
                    if ad < 2.0*sf:

                        # compute displacement
                        a10 = m10[ia]
                        disp = map(lambda x: x, a10)
                        # if outside sphere of radius sf, apply a decay
                        if ad > sf/1.0:
                            disp = map(lambda x,y=math.exp(-ad/1.): x*y,disp)

                        # update weight and displacement
                        w1 = vdw[iz][iy][ix] # old weight
                        w2 = 1/ad            # current weight
                        w0 = w1+w2           # new weight
                        for ic in range(3):
                            vdv[iz][iy][ix][ic] = \
                                (w1*vdv[iz][iy][ix][ic] + w2*disp[ic])/w0
                        vdw[iz][iy][ix] = w0

    print '\tapplying deformation...'
    for iz in range(zS):
        if math.fmod(iz,zS/4) == 0.0:
            print '\t\t%0.0f percent complete ' % ((iz*100.0)/zS)
        for iy in range(yS):
            for ix in range(xS):

                # get and threshold current voxel value
                v0 = vomv[iz][iy][ix]
                if (use_thr and v0 < thr): v0 = 0.0 ## THRESH

                # get new location for voxel
                dv0 = vdv[iz][iy][ix]
                ix1 = int(math.floor(ix + dv0[0]))
                iy1 = int(math.floor(iy + dv0[1]))
                iz1 = int(math.floor(iz + dv0[2]))

                # update density if new voxel location is valid
                if ((iz1 > -1) and (iz1 < zS) and (iy1 > -1) and (iy1 < yS)
                    and (ix1 > -1) and (ix1 < xS)):
                    vmmv[iz1][iy1][ix1] = vmmv[iz1][iy1][ix1] + v0

    from VolumeData import arraygrid
    outmap = arraygrid.Array_Grid_Data(vmmv, xyz_origin, xyz_step)

    if use_filt: outfile = 'morphTemp.mrc'
    else: outfile = outMapName
        
    import SegmentWrite
    from SegmentWrite import mrc_write
    SegmentWrite.mrc_write.save_mrc(outmap,path=outfile)

    if use_filt:

        print '\tapplying filter using EMAN proc3d command...'
        import os

        outfile_dir = os.getcwd()
        outfile_name = os.path.basename(outfile)
        outfile_path = os.path.join(outfile_dir, outfile_name)

        cmd0 = 'proc3d'
        cmd0 = cmd0 + ' %s' % outfile_path
        cmd0 = cmd0 + ' %s' % outMapName
        cmd0 = cmd0 + ' lp=%d' % (int(filt/xyz_step[0]))

        print cmd0
        os.system(cmd0)

    return

    
