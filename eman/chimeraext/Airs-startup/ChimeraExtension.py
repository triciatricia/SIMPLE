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

class AIRSDialogEMO(chimera.extension.EMO):
    """AIRS Dialog
    """
    
    def name(self):
        return 'AIRS Dialog'
    def description(self):
        return 'AIRS dialog'
    def categories(self):
        return ['AIRS']
#    def icon(self):
#        return self.path('segmentmask.gif')
    def activate(self):
        self.module().show_airs_dialog()
        return None

# -------------------------------------------------------------------------

chimera.extension.manager.registerExtension(AIRSDialogEMO(__file__))

# -------------------------------------------------------------------------
