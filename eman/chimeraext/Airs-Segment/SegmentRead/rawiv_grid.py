# -------------------------------------------------------------------------
# SegmentRead/rawiv_grid.py
#
# Segment Volume package - Segment Read module
# 
# Author:
#       Lavu Sridhar, Baylor College of Medicine (BCM)
#
# Revisions:
#       2005.01.20: Lavu Sridhar, BCM
#       2005.02.15: Lavu Sridhar, BCM
#       2005.09.06: Lavu Sridhar, BCM (VU 1.2129 Chimera)
#
# To Do:
#       See comments marked with # @
#
# Key:
#       VU: Version Upgrade
#
"""Wraps RawIV format data as grid data for displaying surface,
meshes, and volumes. The data file read operations are handled
by the module rawiv_format.

File format specs are in the file (rawiv_specs.py)
"""

# -------------------------------------------------------------------------

import rawiv_format

from VolumeData import Grid_Data, Grid_Component

# -------------------------------------------------------------------------

class RawIV_Grid(Grid_Data):
    """Class: RawIV_Grid(path) - wraps RawIV data as grid data

    Reads RawIV format data from file specified by path and wraps the
    data as grid data for displaying surface, meshes, and volumes.
    """

    def __init__(self, path):
        """__init__(path) - wraps RawIV data as grid data.
        """

        rawiv_data = rawiv_format.RawIV_Data(path)
        self.rawiv_data = rawiv_data

        size = rawiv_data.data_size
        xyz_step = rawiv_data.data_step
        xyz_origin = rawiv_data.data_origin
        Grid_Data.__init__(self, size, rawiv_data.element_type,
                           xyz_origin, xyz_step,
                           path = path, file_type = 'rawiv')

    def submatrix(self, ijk_origin, ijk_size):
        """submatrix(ijk_origin, ijk_size) - numeric submatrix.

        Input:
            ijk_origin      submatrix origin
            ijk_size        submatrix size

        Output:
            matrix          submatrix

        Returns the 3D submatrix of size ijk_size and origin
        ijk_orign from the data component.
        """

        return self.rawiv_data.submatrix(ijk_origin, ijk_size)

# -------------------------------------------------------------------------
