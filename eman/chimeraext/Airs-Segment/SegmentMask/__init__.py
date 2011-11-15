# -------------------------------------------------------------------------
# SegmentMask/__init__.py
#
# Segment Volume package - Segment Mask module
# 
# Author:
#       Lavu Sridhar, Baylor College of Medicine (BCM)
#
# Files in module:
#       __init__.py         
#       maskmain.py     Main mask operations dialog
#       maskop.py       Mask operations
#       maskform.py     Create mask Dialog
#
# Help files:
#       maskmain.html, maskmain.png
#
# Revisions:
#       2005.04.15: Lavu Sridhar, BCM
#       2005.09.06: Lavu Sridhar, BCM (VU 1.2129 Chimera)
#
# To Do:
#       See comments marked with # @
#
"""GUI to create and apply a volume density mask on a
given volume density data. (see the Volume Data module
in Chimera).

Requires Segment Menu module from Segment Volume package
and EMAN.
"""

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
