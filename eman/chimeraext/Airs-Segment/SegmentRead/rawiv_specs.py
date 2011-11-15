# -------------------------------------------------------------------------
# SegmentRead/rawiv_specs.py
#
# Segment Volume package - Segment Read module
# 
# Author:
#       Lavu Sridhar, Baylor College of Medicine (BCM)
#
# Revisions:
#       2005.01.20: Lavu Sridhar, BCM
#       2005.02.15: Lavu Sridhar, BCM
#
# To Do:
#       See comments marked with # @
#
"""RawIV data format description (*.rawiv). 

 This specification is derived from the following website:
 http://ccvweb.csres.utexas.edu/docs/data-formats/rawiv.html
 Comments regarding the interpretation of the specs are
 included in various parts of the file (rawiv_format.py).
"""

# -------------------------------------------------------------------------

def rawiv_specs():
    """rawiv Data Format Description (.rawiv)
--------------------------------------
 
  The rawiv data format is used to represent 3D volumetric data of
  scalar fields defined on a regular grid. A rawiv file is created by
  adding the header (described below) to the raw format.
  
  Everything is in big-endian. Big endian is the byte order on Sun,
  SGI, IBM architectures. Intel's byte order is little endian. 
  
  Header Description
  ------------------
  
  Order of information is as below, concatenated contiguously.
  
  (minX) (minY) (minZ) (maxX) (maxY) (maxZ) (numVerts) (numCells)
  (dimX) (dimY) (dimZ) (originX) (originY) (originZ) (spanX) (spanY)
  (spanZ)
 
  where:
 
  (minX, minY, minZ) are the co-ordinates of the 1st voxel.
  (maxX, maxY, maxZ) are the co-ordinates of the last voxel.
  The mins, and maxs are floats.
  
  These define the bounding box of the data in co-ordinate space.
  
  numVerts is the number of vertices in the grid.
  numVerts = dimX * dimY * dimZ
  numVerts is an unsigned int.
  
  numCells is the number of cells in the grid.
  numCells = (dimX - 1) * (dimY - 1) * (dimZ - 1)
  numCells is an unsigned int.
  
  dimX = number of vertices in x direction
  dimY = number of vertices in y direction
  dimZ = number of vertices in z direction
  The dims are unsigned ints.
  
  originX
  originY
  originZ
  The origins are floats.
 
  The existance of the origin co-ordinates is somewhat of a
  mystery. Some developers claim the origin co-ordinates are exactly 
  the same as the co-ordinates of the first voxel.
  
  The spans are the spacing between one vertex and the next along the
  given description.
  
  spanX = (maxX - minX)/(dimX - 1)
  spanY = (maxY - minY)/(dimY - 1)
  spanZ = (maxZ - minY)/(dimZ - 1)
  The spans are all floats.
  
  The size of a rawiv header is 68 bytes.
 
  Conflict Resolution
  --------------------
 
  There are a number of fields in the header that are redundant. For
  example, numVerts = dimX * dimY * dimZ. If while reading the rawiv
  format, you find that numVerts != dimX * dimY * dimZ , then the
  appropriate action is to determine that the rawiv file is corrupted.
 
  Data Portion
  ------------
 
  Next follows the actual data in the raw format.
 
  A rawiv file is created by concatenating a raw file to a file
  containing the rawiv header.
 
  The suffix on the name of a rawiv file .rawiv
 
  The raw portion of the rawiv file is in binary big-Endian format used
  to represent 3D volumetric data of scalar fields defined on a regular
  grid. It is simply a sequence of values. These values can be floats,
  unsigned shorts, or unsigned chars.
 
  The data is listed with the x co-ordinate varying fastest, and z
  varying slowest.
 
  So, in C++ syntax a reader would contain the following code snippet:
 
 	for (int z=0; z < dimZ; z++)
 		for (int y=0; y < dimY; y++)
 			for (int x=0; x < dimX; x++)
 			{
 				//read data here
 			}
 
  Size specification
  ------------------
   
  1 byte           = 8 bits. 
  1 float          = 4 bytes.
  1 unsigned int   = 4 bytes. 
  1 unsigned short = 2 bytes. 
  1 character is   = 1 byte.

  Data mode
  ---------

   MODE         #  type             Chimera's RawIV type
   -------------------------------------------------------------------
   MODE_uchar   0  unsigned char    Numeric.UnsignedInt8
   MODE_ushort  1  unsigned short   Numeric.UnsignedInt16
   MODE_float   2  float            Numeric.Float32
    """
    return

# -------------------------------------------------------------------------
