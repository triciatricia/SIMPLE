# -------------------------------------------------------------------------
# VolumeMorph/ChimeraExtension.py
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
"""Morphing of volume density maps.

Chimera Extension manager registering modules:
(1) 'Volume Morph'
"""
# -------------------------------------------------------------------------

import chimera.extension

# -------------------------------------------------------------------------

class VolumeMorphEMO(chimera.extension.EMO):
    """Volume Morph
    """

    def name(self):
        return 'Volume Morph'
    def description(self):
        return 'Morph volume density map'
    def categories(self):
        return ['AIRS']
    def icon(self):
        return self.path('volmorph.gif')
    def activate(self):
        self.module('volmorph').show_vol_morph_dialog()
        return None

# -------------------------------------------------------------------------

chimera.extension.manager.registerExtension(VolumeMorphEMO(__file__))

# -------------------------------------------------------------------------
