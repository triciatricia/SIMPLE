# -------------------------------------------------------------------------
# SegmentSimple/ChimeraExtension.py
#
# Segment Volume package - Segment Simple module
# 
# Author:
#       Lavu Sridhar, Baylor College of Medicine (BCM)
#
# Revisions:
#       2005.01.17: Lavu Sridhar, BCM
#       2005.02.15: Lavu Sridhar, BCM
#
# To Do:
#       See comments marked with # @
# 
"""Segmentation of MRC density maps.

Chimera Extension manager registering modules:
(1) 'Segment Simple'
(2) 'Segment Markers'
"""
# -------------------------------------------------------------------------

import chimera.extension

# -------------------------------------------------------------------------

class SegmentSimpleEMO(chimera.extension.EMO):
    """Segment using simple regions
    """

    def name(self):
        return 'Segment Simple'
    def description(self):
        return 'Segment a simple region out of a volume density map'
    def categories(self):
        return ['AIRS']
    def icon(self):
        return self.path('segmentsimple.gif')
    def activate(self):
        self.module('simple').show_seg_simple_dialog()
        return None

# -------------------------------------------------------------------------

class SegmentMarkerEMO(chimera.extension.EMO):
    """Segment using regions at markers
    """

    def name(self):
        return 'Segment Markers'
    def description(self):
        return 'Segment regions of an MRC density map using markers'
    def categories(self):
        return ['AIRS']
    def icon(self):
        return self.path('segmentmarker.gif')
    def activate(self):
        self.module('marker').show_seg_marker_dialog()
        return None

# -------------------------------------------------------------------------

chimera.extension.manager.registerExtension(SegmentSimpleEMO(__file__))
chimera.extension.manager.registerExtension(SegmentMarkerEMO(__file__))

# -------------------------------------------------------------------------
