# -------------------------------------------------------------------------
# SegmentWrite/ChimeraExtension.py
#
# Segment Volume package - Segment Write module
# 
# Author:
#       Lavu Sridhar, Baylor College of Medicine (BCM)
#
# Revisions:
#       2005.01.22: Lavu Sridhar, BCM
#       2005.02.15: Lavu Sridhar, BCM
#
# To Do:
#       See comments marker with # @
# 
"""Save Chimera grid data objects in volume data formats.

Chimera Extension manager registering modules:
(1) 'Segment Write'
"""
# -------------------------------------------------------------------------

import chimera.extension

# -------------------------------------------------------------------------

class SegmentWriteEMO(chimera.extension.EMO):
    """Save volume data
    """
    
    def name(self):
        return 'Segment Write'
    def description(self):
        return 'Save volume data'
    def categories(self):
        return ['AIRS']
    def icon(self):
        return self.path('segmentwrite.gif')
    def activate(self):
        self.module('').show_seg_write_dialog()
        return None

# -------------------------------------------------------------------------

chimera.extension.manager.registerExtension(SegmentWriteEMO(__file__))

# -------------------------------------------------------------------------
