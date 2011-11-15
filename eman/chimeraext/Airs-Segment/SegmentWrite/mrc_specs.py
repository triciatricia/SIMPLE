# -------------------------------------------------------------------------
# SegmentWrite/mrc_specs.py
#
# Segment Volume package - Segment Write module
# 
# Author:
#       Lavu Sridhar, Baylor College of Medicine (BCM)
#
# Revisions:
#       2005.01.21: Lavu Sridhar, BCM
#       2005.02.15: Lavu Sridhar, BCM
#
# To Do:
#       See comments marked with # @
#
"""MRC data format description (*.mrc). 

 This specification is derived from EMAN's mrc.h header file.
 It includes minor notational modifications, with comments
 indicating correspondence with Chimera's VolumeData data
 object (grid data object) specs and Chimera's mrc format
 specs (see mrc_format.py in mrc module of VolumeData module
 in Chimera).
"""
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
# Credits from original mrc.h not included.
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
# Returns the MRC specs and with comments indicating correspondence
# with Chimera's VolumeData data object (grid data object) specs
# and Chimera's mrc format specs (see mrc_format.py in mrc module
# of VolumeData module in Chimera).
# -------------------------------------------------------------------------

def mrc_specs():
    """mrc 2000 Data Format Decscription (.mrc)
----------------------------------------
 
  Header parameters
  -----------------
  
  MRC_LABEL_SIZE      80   
  MRC_USER            25
  MRC_NUM_LABELS      10
 
  Dimensions - Map and Coord
  --------------------------
  
  There are two different dimensions: map dimensions and coord
  dimensions. The first corresponds to actual map values, ie,
  the numbers in the map. These dimensions are referred to as
  columns, rows, and sections. The second corresponds to the
  actual data values, ie, the real coordinate space. In most 
  cases, columns correspond to x coordinate, rows correspond
  to y coordinate, and sections correspond to z coordinate.
 
  Header Description
  ------------------
 
  (nc, nr, ns)  - int 
        Map dimensions. nc corresponds to the fastest changing in
        map and ns corresponds to the slowest changing in map.
        Chimera: Uses to get data_size in coord dimensions.
                 Stored as mrc_data.matrix_size 
 
  mode - int 
        Indicates data value type. See above.
        Chimera: Uses to determine mrc_data.element_type
 
  (ncstart, nrstart,nsstart) - int 
        Number of first column, row, section in the map (map
        dimensions), default is 0,0,0.
        Chimera: May use for data_origin in coord dimensions
 
  (mx, my, mz) - int
        Number of intervals along the X,Y,Z coordinates (coord 
        dimensions).
        Chimera: Uses with next for data_step in X,Y,Z coordinates
 
  (xlen, ylen, zlen) - float
        Cell dimensions in Angstroms, along the X,Y,Z coordinates
        (coord dimensions)
        Chimera: Uses with prev for data_step in X,Y,Z coordinates
 
  (alpha, beta, gamma) - float
        Cell angles in Degress, along the X,Y,Z coordinates (coord
        dimensions)
        Chimera: Does not use. Can add attribute as cell_angles.
 
  (mapc, mapr, maps) - int
        Indicates correspondence between the map dimensions
        (columns, rows, sections) and coord dimensions (X,Y,Z).
        Each of mapc, mapr, maps can take values 1, 2, or 3,
        with 1 corresponding to X coord, 2  to Y coord, and
        3 to Z coord.
        Default (mapc,mapr,maps) is assumed to be (1,2,3).
        Chimera: Uses to convert map to coordinate dimensions.
                 Stored as mrc_data.xyz_matrix_axes (0,1,2)
                 
  (amin, amax, amean) - float
        Min, max, and mean density value.
        Chimera: Stores first 2 as mrc_data.min_intesity and
                 mrc_data.max_intesity
 
  ispg - int
        Space group number (0 for images).
 
  nsymbt - int
        Number of chars used for storing symmetry operators.
 
  user[MRC_USER] - int
 
  (xorigin, yorigin, zorigin) - float
        X origin, Y origin, Z origin.
        Older MRC formats have only X origin and Y origin.
        Chimera: Uses to determine data_origin when Z origin
                 present or when not (0,0,0). Stores the final
                 computed origin as mrc_data.data_origin
  map[4] - char
        Constant string "MAP "
        Chimera: Uses to check if MRC 2000 format with xyz origin.
 
  machinestamp - int
        Machine stamp in CCP4 convention:
        ieee big endian=0x11110000, ieee little endian=0x44440000
 
  rms - float
        rms deviation of map from mean density
 
  nlabl - int
        Number of labels being used. Max allowed: 10 text
        labels of 80 characters each.
 
  labels[MRC_NUM_LABELS][MRC_LABEL_SIZE] - char
 
  Data mode
  ---------
  
  The different modes supported by the MRC format:

    MODE                #  type                  Chimera's MRC type
    ------------------------------------------------------------------
    MODE_char           0  signed 8 bit          Numeric.UnsignedInt8
    MODE_short          1  16 bit                Numeric.Int16
    MODE_float          2  32 bit float          Numeric.Float32
    MODE_short_COMPLEX  3  complex 16 bit int    - NOT SUPPORTED -
    MODE_float_COMPLEX  4  complex 32 bit float  - NOT SUPPORTED -
 
  All modes before MODE_short_COMPLEX must be real, all those after
  it must be complex.
 
  Chimera supports MODE_char, MODE_short, and MODE_float.
    """
    return

# -------------------------------------------------------------------------
