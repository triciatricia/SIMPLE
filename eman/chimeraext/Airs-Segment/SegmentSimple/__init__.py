# -------------------------------------------------------------------------
# SegmentSimple/__init__.py
#
# Segment Volume package - Segment Simple module
# 
# Author:
#       Lavu Sridhar, Baylor College of Medicine (BCM)
#
# Files in module:
#       __init__.py
#       ChimeraExtension.py
#       simple.py           simple region based segmentation
#       marker.py           marker based segmentation
#       boxes.py            script file with EMAN interface
#       selectregion.py     select a (box) region using mouse
#       selectregionOLD.py  For Chimera versions before 1.2179
#
# Help files:
#       simple.html
#       marker.html
#
# Revisions:
#       2004.12.15: Lavu Sridhar, BCM
#       2005.02.15: Lavu Sridhar, BCM
#       2005.09.06: Lavu Sridhar, BCM (VU 1.2129 Chimera)
#       2005.10.10: Lavu Sridhar, BCM (VU 1.2176 Chimera)
#       2005.11.15: Lavu Sridhar, BCM (VU 1.2179 Chimera)
#       2006.03.06: Lavu Sridhar, BCM (VU 1.2179 Chimera) Part2
#       2006.05.24: Lavu Sridhar, BCM (VU Circle Mask)
#
# To Do:
#       See comments marked with # @
#
"""Segmentation of MRC density maps.

Package to perform segmentation of MRC density maps, using:
(1) Simple: Cuboid, spherical, or cylindrical segmentation regions.
(2) ...
"""

# -------------------------------------------------------------------------


# -------------------------------------------------------------------------
# This package relies on EMAN software. Since, Chimera unsets
# the PYTHONPATH os variable, EMAN python libraries are not
# found by Chimera!
# -------------------------------------------------------------------------

# Below is a hack that sets PYTHONPATH to include the EMAN
# library path, if an EMANDIR OS variable exists. 
#
# The assumption here is that EMAN library path is the
# directory 'lib' one level above EMANDIR.

import os
import sys

if os.environ.has_key('EMANDIR'):
    emandir = os.environ['EMANDIR']
    emanpy = os.path.join(emandir, 'lib')
    if sys.platform == 'win32':
        sep = ';' # Windows separator
    else:
        sep = ':' # Unix separator
    if (os.environ.has_key('PYTHONPATH') and
        os.environ['PYTHONPATH'] != ''):
        pypath = os.environ['PYTHONPATH'] + sep + emanpy
    else:
        pypath = emanpy
    os.environ['PYTHONPATH'] = pypath
    sys.path.append(emanpy)
else:
    msg = 'Add EMAN directory to your system path!\n'
    from chimera import replyobj
    replyobj.error(msg)

# If the above does not work, and you know the EMAN library path,
# then set it as shown below.
#
# os.environ['PYTHONPATH'] = <eman lib directory>
# Eg: os.environ['PYTHONPATH'] = '/home/lavu/EMAN/lib'
#     os.environ['PYTHONPATH'] = 'C:\\Software\\EMAN\\lib'

# -------------------------------------------------------------------------
