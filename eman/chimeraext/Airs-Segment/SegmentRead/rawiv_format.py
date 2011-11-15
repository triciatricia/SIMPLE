# -------------------------------------------------------------------------
# SegmentRead/rawiv_format.py
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
"""Reads RawIV format data. Assumes input file is encoded in
big-endian (which is a requirement for RawIV format).

File format specs are in the file (rawiv_specs.py)
"""

# -------------------------------------------------------------------------

import os
import struct

import Numeric

# -------------------------------------------------------------------------

MODE_uchar   = 0 # unsigned char
MODE_ushort  = 1 # unsigned short
MODE_float   = 2 # float

RAWIV_HEADER = 68 # size of RawIV header in bytes

# -------------------------------------------------------------------------

class RawIV_Data:
    """Class: RawIV_Data(path) - read data from file.
    
    Reads the RawIV data from file specified by path.
    """
    
    def __init__(self, path):
        """__init__(path) - read RawIV data from file.
        """

        self.path = path
        self.name = os.path.basename(path)

        file_read = open(path,'rb')

        file_read.seek(0,2)          # go to the end of file
        file_size = file_read.tell() # get the file size
        file_read.seek(0,0)          # go to the beginning of file

        # Input is big-endian. Swap bytes if system is little-endian.
        import sys
        if sys.byteorder == 'little': self.swap_bytes = 1
        else: self.swap_bytes = 0

        v = self.read_header_values(file_read, file_size)
        self.check_header_values(v, file_size)

        self.data_offset = file_read.tell()

        # @ how to determine from data?
        #   It appears that (x,y,z) are chosen based with x being
        #   the fastest changing and z being the slowest changing  
        self.xyz_matrix_axes = (0,1,2)

        dX_dY_dZ = v['dimX'], v['dimY'], v['dimZ']
        self.matrix_size = dX_dY_dZ
        
        xa, ya, za = self.xyz_matrix_axes
        nx, ny, nz = dX_dY_dZ[xa], dX_dY_dZ[ya], dX_dY_dZ[za],
        self.data_size = (nx,ny,nz)

        step_xyz = v['spanX'], v['spanY'], v['spanZ']
        self.data_step = step_xyz

        # @ which one?
        #   There're 2 choices for origin:(v['minX'],v['minY'],v['minZ'])
        #   or (v['originX'],v['originY'],v['originZ']). It appears that
        #   the latter one is supposed to be redundant. Using first one.
        #   origin_xyz = v['originX'], v['originY'], v['originZ']
        origin_xyz = v['minX'], v['minY'], v['minZ']
        self.data_origin = origin_xyz

        # @ Clarification of specs?
        #   The specs indicate that possible data types are 32 bit
        #   float or 16 bit unsigned int or 8 bit unsigned char. Here,
        #   8 bitunsigned char is represented as Numeric.UnsignedInt8
        if   v['mode'] == MODE_float:
            self.element_type = Numeric.Float32
        elif v['mode'] == MODE_ushort:
            self.element_type = Numeric.UnsignedInt16
        elif v['mode'] == MODE_uchar:
            self.element_type = Numeric.UnsignedInt8

        # @ how to determine these values?
        # @ are they used?
        self.min_intensity = 0
        self.max_intensity = 1

        file_read.close()
        
    # ---------------------------------------------------------------------
    # RawIV header
    # ---------------------------------------------------------------------
 
    def read_header_values(self, file_read, file_size):
        """read_header_values(file_read, file_size) - read header

        Input:
            file_read       input file
            file_size       input file size

        Output:
            v               header (a dictionary)

        See rawiv_specs.py for RawIV format specifications.
        """
        
        ui32 = Numeric.UnsignedInt32
        f32 = Numeric.Float32

        v = {}
        v['minX'], v['minY'], v['minZ'] = \
                                 self._read_values(file_read, f32, 3)
        v['maxX'], v['maxY'], v['maxZ'] = \
                                 self._read_values(file_read, f32, 3)
        v['numVerts'], v['numCells'] = \
                                 self._read_values(file_read, ui32, 2)
        v['dimX'], v['dimY'], v['dimZ'] = \
                                 self._read_values(file_read, ui32, 3)
        v['originX'], v['originY'], v['originZ'] = \
                                 self._read_values(file_read, f32, 3)
        v['spanX'], v['spanY'], v['spanZ'] = \
                                 self._read_values(file_read, f32, 3)

        # To determine the mode, ie, the data type of data values,
        # check the file size minus the header size, against the
        # number of vertices. Possible choices include 4 byte floats,
        # 2 byte unsigned short, and 1 byte unsigned char type data.
        num_verts = v['numVerts']
        num_bytes = file_size - RAWIV_HEADER
        num_bytes_per_vertex = int(round(float(num_bytes)/num_verts))
        if num_bytes_per_vertex == 1:
            v['mode'] = MODE_uchar
        elif num_bytes_per_vertex == 2:
            v['mode'] = MODE_ushort
        elif num_bytes_per_vertex == 4:
            v['mode'] = MODE_float
        else:
            v['mode'] = None
        
        return v

    def check_header_values(self, v, file_size):
        """check_header_values(v, file_size) - check header

        Input:
            v           header (a dictionary)
            file_size   input file size
            
        Check if header values are consistent.
        """

        if v['minX'] >= v['maxX'] or v['minY'] >= v['maxY'] \
           or v['minZ'] >= v['maxZ']:
            raise SyntaxError, ('Bad RawIV bounding box '+
                                '(%f,%f,%f)-(%f,%f,%f) ' % \
                                (v['minX'],v['minY'],v['minZ'],
                                 v['maxX'],v['maxY'],v['maxZ']))

        if v['dimX'] * v['dimY'] * v['dimZ'] != v['numVerts']:
            raise SyntaxError, ('RawIV data dimensions mismatch ' +
                                '(%d,%d,%d) while %d num vertices '
                                % (v['dimX'],v['dimY'],v['dimZ'],
                                   v['numVerts']))

        if (v['dimX']-1)*(v['dimY']-1)*(v['dimZ']-1) != v['numCells']:
            raise SyntaxError, ('RawIV data dimensions mismatch ' +
                                ' (%d,%d,%d) while %d grid cells '
                                % (v['dimX'],v['dimY'],v['dimZ'],
                                   v['numCells']))

        if float(v['dimX'])*float(v['dimY'])*float(v['dimZ']) > file_size:
            raise SyntaxError, ('File size %d too small for grid size '
                                % (file_size) + '(%d,%d,%d) '
                                % (v['dimX'],v['dimY'],v['dimZ']))

        #@ Not checking span values consistency

        if   v['mode'] == MODE_float:
            self.element_type = Numeric.Float32
        elif v['mode'] == MODE_ushort:
            self.element_type = Numeric.UnsignedInt16
        elif v['mode'] == MODE_uchar:
            self.element_type = Numeric.UnsignedInt8
        else:
            raise SyntaxError, ('RawIV data type (%d) ' % v['mode'] +
                                'is not unsigned 16 bit int or ' +
                                'unsigned 8 bit char or 32 bit float')
            
    def _read_values(self, file_read, etype, count):
        """_read_values(file_read, etype, count) - read values

        Input:
            file_read       input file
            etype           value data type
            count           number of values to read from file

        Output:
            values          values read from file
            
        Read values of type etype and of number count from file_read.
        """

        esize = Numeric.array((), etype).itemsize()
        string_read = file_read.read(esize * count)
        values = self._read_values_from_string(string_read,
                                               etype, count)
        return values

    def _read_values_from_string(self, string_read, etype, count):
        """_read_values_from_string(sting_read, etype, count)

        Input:
            string_read     string read from file
            etype           values data type
            count           number of values to read from string

        Read count number of values of type etype from from string.
        """

        values = Numeric.fromstring(string_read, etype)
        if self.swap_bytes:
            values = values.byteswapped()
        if count == 1:
            return values[0]
        return values

    # ---------------------------------------------------------------------
    # RawIV matrix
    # ---------------------------------------------------------------------

    def submatrix(self, ijk_origin, ijk_size):
        """submatrix(ijk_origin, ijk_size)

        Input:
            ijk_origin      submatrix origin
            ijk_size        submatrix size

        Output:
            submatrix       3D Numeric array in zyx order

        Reads the submatrix of size ijk_size and origin
        ijk_orign from the data file and returns the matrix.
        Useful when reading a potentially very large file.
        """

        xsize, ysize, zsize = self.data_size
        if (ijk_origin[0] == 0 and
            ijk_origin[1] == 0 and
            ijk_origin[2] == 0 and
            ijk_size[0] == xsize and
            ijk_size[1] == ysize and
            ijk_size[2] == zsize):
            return self.matrix()

        # ijk corresponds to xyz. Need matrix column, row, section axes.
        axes = self.xyz_matrix_axes
        crs_origin = [0,0,0]
        crs_size = [1,1,1]
        for a in range(3):
            crs_origin[axes[a]] = ijk_origin[a]
            crs_size[axes[a]]   = ijk_size[a]

        element_size = Numeric.array((), self.element_type).itemsize()
        base = self.data_offset

        file_read = open(self.path, 'rb')

        #
        # Do random access seeking in file to read needed x slices
        #
        csize, rsize, ssize = self.matrix_size
        slices = []
        sstep = rsize * csize * element_size
        rstep = csize * element_size
        cbytes = crs_size[0] * element_size
        coffset = crs_origin[0] * element_size
        for s in range(crs_origin[2], crs_origin[2]+crs_size[2]):
            sbase = base + s * sstep
            for r in range(crs_origin[1], crs_origin[1]+crs_size[1]):
                offset = sbase + r * rstep * coffset
                file_read.seek(offset)
                data = file_read.read(cbytes)
                slice = Numeric.fromstring(data, self.element_type)
                slices.append(slice)

        file_read.close()

        a = Numeric.concatenate(slices)
        if self.swap_bytes:
            a = a.byteswapped()

        size = (ijk_size[2], ijk_size[1], ijk_size[0])
        matrix = Numeric.reshape(a, size)
        matrix = self.permute_matrix_to_xyz_axis_order(matrix)

        return matrix

    def matrix(self):
        """matrix()

        Output:
            matrix       entire 3D Numeric array in zyx order

        Reads the entire matrix from the data file and returns
        the matrix. Used by submatrix when reading entire matrix.
        """

        xsize, ysize, zsize = self.data_size
        element_size = Numeric.array((), self.element_type).itemsize()
        bytes = xsize * ysize * zsize * element_size

        base = self.data_offset

        file_read = open(self.path, 'rb')
        file_read.seek(base)
        data = file_read.read(bytes)
        file_read.close()

        a = Numeric.fromstring(data, self.element_type)
        if self.swap_bytes:
            a = a.byteswapped()
        
        sizes = list(self.matrix_size)
        sizes.reverse()
        matrix = Numeric.reshape(a, sizes)
        matrix = self.permute_matrix_to_xyz_axis_order(matrix)

        return matrix

    def permute_matrix_to_xyz_axis_order(self, matrix):
        """permute_matrix_to_xyz_axis order(matrix)

        Input:
            matrix      matrix in map order

        Output:
            matrix      matrix in zyx order
            
        Convert matrix from map order to zyx order.
        """

        if self.xyz_matrix_axes == (0,1,2):
            return matrix

        axis_order = map(lambda a: 2-a, self.xyz_matrix_axes)
        axis_order.reverse()
        m = Numeric.transpose(matrix, axis_order)

        return m
                         
# -------------------------------------------------------------------------
