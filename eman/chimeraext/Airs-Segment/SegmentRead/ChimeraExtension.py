# -------------------------------------------------------------------------
# SegmentRead/ChimeraExtension.py
#
# Segment Volume package - Segment Read module
# 
# Author:
#       Lavu Sridhar, Baylor College of Medicine (BCM)
#
# Revisions:
#       2005.02.12: Lavu Sridhar, BCM
#       2005.02.15: Lavu Sridhar, BCM
#
# To Do:
#       See comments marker with # @
# 
"""Read additional volume data formats used in Segment Volume package.

Chimera Extension manager registering modules:
(1) 'Segment Read'
"""
# -------------------------------------------------------------------------

import chimera.extension

# -------------------------------------------------------------------------

class SegmentReadEMO(chimera.extension.EMO):
    """Read Volume data
    """
    
    def name(self):
        return 'Segment Read'
    def description(self):
        return 'Read volume data in additional formats'
    def categories(self):
        return ['AIRS']
    def icon(self):
        return self.path('segmentread.gif')
    def activate(self):
        self.module('').show_seg_read_dialog()
        return None

# -------------------------------------------------------------------------

chimera.extension.manager.registerExtension(SegmentReadEMO(__file__))

# -------------------------------------------------------------------------
