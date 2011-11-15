# -------------------------------------------------------------------------
# SegmentRead/rawiv_read.py
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
#       See comments marked with # @
#
"""Read and display RawIV data.

 Reads and wraps the RawIV data in the file specified by path
 and returns a Chimera grid data object (see the Volume Data
  module in Chimera).
"""

# -------------------------------------------------------------------------

from rawiv_grid import RawIV_Grid

# -------------------------------------------------------------------------
# RawIV read functions
# -------------------------------------------------------------------------

def open_rawiv(path):
    """open_rawiv(path) - open a RawIV file specifed by path

    Input:
        path            input file
        
    Output:
        grid_object     VolumeData grid data object
        
    Reads and wraps the RawIV data in the file specified by path
    and returns a Chimera grid data object (see the Volume Data
    module in Chimera).
    """
    
    return RawIV_Grid(path)

def display_rawiv(path):
    """display_rawiv(path) - open and display a RawIV file.

    Input:
        path            input file

    Output:
        grid_object     VolumeData grid data object
        data_region     VolumeViewer data region
    
    Reads and displays the RawIV data in the file specified by path
    and returns a Chimera grid data object and a data region (see
    the Volume Data and Volume Viewer modules in Chimera).
    """

    grid_object = open(path)
    from VolumeViewer import volume_from_grid_data
    data_region = volume_from_grid_data(grid_object)

    return grid_object, data_region

# -------------------------------------------------------------------------
