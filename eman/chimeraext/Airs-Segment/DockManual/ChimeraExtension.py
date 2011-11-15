# -------------------------------------------------------------------------
# DockManual/ChimeraExtension.py
#
# Segment Volume package - Dock Manual module
# 
# Author:
#       Lavu Sridhar, Baylor College of Medicine (BCM)
#
# Revisions:
#       2005.04.15: Lavu Sridhar, BCM
#       2005.04.25: Lavu Sridhar, BCM
#
"""Docking PDB structures into MRC density manually.

Chimera Extension manager registering modules:
(1) 'Dock Manual'
"""

# -------------------------------------------------------------------------

import chimera.extension

# -------------------------------------------------------------------------

class DockManualEMO(chimera.extension.EMO):
    """Dock manually using mouse.
    """

    def name(self):
        return 'Dock Manually'
    def description(self):
        return 'Dock a PDB structure into an MRC density map' + \
               ' manually'
    def categories(self):
        return ['AIRS']
    def icon(self):
        return self.path('dockmanual.gif')
    def activate(self):
        self.module('dockmanual').show_dock_manual_dialog()
        return None

# -------------------------------------------------------------------------

chimera.extension.manager.registerExtension(DockManualEMO(__file__))

# -------------------------------------------------------------------------

