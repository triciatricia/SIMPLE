# -------------------------------------------------------------------------
# SegmentMask/ChimeraExtension.py
#
# Segment Volume package - Segment Mask module
# 
# Author:
#       Lavu Sridhar, Baylor College of Medicine (BCM)
#
# Revisions:
#       2005.04.15: Lavu Sridhar, BCM
#
# To Do:
#       See comments marker with # @
# 
"""Mask volume data used in Segment Volume package.

Chimera Extension manager registering modules:
(1) 'Segment Mask'
"""
# -------------------------------------------------------------------------

import chimera.extension

# -------------------------------------------------------------------------

class SegmentMaskEMO(chimera.extension.EMO):
    """Mask Volume data
    """
    
    def name(self):
        return 'Segment Mask'
    def description(self):
        return 'Mask volume data'
    def categories(self):
        return ['AIRS']
    def icon(self):
        return self.path('segmentmask.gif')
    def activate(self):
        self.module('maskmain').show_seg_mask_dialog()
        return None

# -------------------------------------------------------------------------

chimera.extension.manager.registerExtension(SegmentMaskEMO(__file__))

# -------------------------------------------------------------------------
