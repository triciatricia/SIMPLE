# -------------------------------------------------------------------------
# SegmentTrack/ChimeraExtension.py
#
# Segment Volume package - Segment Track module
# 
# Author:
#       Lavu Sridhar, Baylor College of Medicine (BCM)
#
# Revisions:
#       2005.01.17: Lavu Sridhar, BCM
#       2005.02.15: Lavu Sridhar, BCM
#
"""Tracking Model Transforms in Chimera coordinate space.

Chimera Extension manager registering modules:
(1) 'Track Transform'
"""

# -------------------------------------------------------------------------

import chimera.extension

# -------------------------------------------------------------------------
 
class TrackXformEMO(chimera.extension.EMO):
    """Track Chimera transformations.
    """

    def name(self):
        return 'Track Transform'
    def description(self):
        return 'Track model transformation in camera coordinates'
    def categories(self):
        return ['AIRS']
    def icon(self):
        return self.path('trackxform.gif')
    def activate(self):
        self.module('trackxform').show_track_xform_dialog()
        return None

# -------------------------------------------------------------------------

chimera.extension.manager.registerExtension(TrackXformEMO(__file__))

# -------------------------------------------------------------------------

