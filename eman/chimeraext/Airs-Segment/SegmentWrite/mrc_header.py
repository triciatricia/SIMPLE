# -------------------------------------------------------------------------
# SegmentWrite/mrc_header.py
# 
# Segment Volume package - Segment Write module
#
# Author:
#       Lavu Sridhar, Baylor College of Medicine (BCM)
#
# Revisions:
#       2005.01.22: Lavu Sridhar, BCM
#       2005.02.15: Lavu Sridhar, BCM
#       2005.09.06: Lavu Sridhar, BCM (VU 1.2129 Chimera)
#
# Key:
#       VU: Version Upgrade
#
"""Computes MRC format data header from Chimera's
VolumeData data object (grid data object).

The MRC data format specs are in the file (mrc_specs.py).
"""
# -------------------------------------------------------------------------

import os

import Numeric

# -------------------------------------------------------------------------

MODE_char           = 0
MODE_short          = 1
MODE_float          = 2
MODE_short_COMPLEX  = 3
MODE_float_COMPLEX  = 4

MRC_USER_2000  = 25
MRC_NUM_LABELS = 10
MRC_LABEL_SIZE = 80

# -------------------------------------------------------------------------

class MRC_Data_Header:
    """Class: MRC_Data_Header(grid_object, matrix_values=None) -
    compute header for MRC file format

    Input:
        grid_object         VolumeData grid data object
        matrix_values       data pixel values in zyx matrix order
        
    Computers header for MRC file format from grid_data (see
    VolumeData module in Chimera) and matrix values. If no
    matrix values are given, then it reads the values from
    the grid data and stores them as 3D Numeric
    array. The matrix values are in zyx order.

    Returns the header values as follows (all 32 bit fields)

        Fields: Keys
        ------  ----
        00-02 : nc, nr, ns 
        03    : mode 
        04-06 : ncstart, nrstart, nsstart
        07-09 : mx, my, mz  
        10-12 : xlen, ylen, zlen 
        13-15 : alpha, beta, gamma 
        16-18 : mapc, mapr, maps 
        19-21 : amin, amax, amean 
        22-23 : ispg, nsymbt 
        24-48 : user
        49    : map
        50-52 : xorigin, yorigin, zorigin
        53    : machst
        54    : rms
        55    : nlabl
        56-255: labels (10 80 character text labels)
     
    """

    def __init__(self, grid_object, matrix_values=None):
        """__init__(grid_object, matrix_values=None) - header
        for MRC file format.
        """

        self.data = grid_object

        # Ensure matrix is a Numeric.array() and in zyx order
        if matrix_values is None:
            self.matrix =  self.mrc_matrix_values()
        else:
            self.matrix = self.check_matrix_values(matrix_values)

        mrc_header = self.mrc_header_values()
        self.header = mrc_header

    # ---------------------------------------------------------------------
    # Matrix values
    # ---------------------------------------------------------------------

    def check_matrix_values(self, matrix_values):
        """check_matrix_values(matrix_values) - check if matrix valid.

        Input:
            matrix_values       3D Numeric array

        Output:
            matrix              A valid 3D Numeric array
            
        Esnure matrix is a Numeric array and of size corresponding to
        data. The matrix needs to be in zyx order. Returns matrix.
        """

        data_size = list(self.data.size)
        data_size.reverse()

        try:
            matrix_size = matrix_values.shape
            matrix_size = list(matrix_size)
        except AttributeError:
            raise AttributeError, ('Input a 3D Numeric array matrix ' +
                                   '(in zyx order)!')

        # compare matrix size and data size 
        if matrix_size != data_size:
            raise ValueError, ('Input a 3D Numeric array in zyx order ' +
                               'of size (%d,%d,%d)' % tuple(matrix_size))

        matrix = matrix_values
        
        return matrix
    
    def mrc_matrix_values(self):
        """mrc_matrix_values() - read matrix values from file.

        Output:
            matrix      3D Numeric array matrix in zyx order
            
        Reads the data from the original file and returns the data
        as a matrix. This is used if no input matrix values are given.
        """

        ijk_origin = (0,0,0)
        ijk_size = self.data.size
        
        matrix = self.data.submatrix(ijk_origin, ijk_size)
        return matrix

    # ---------------------------------------------------------------------
    # Header values
    # ---------------------------------------------------------------------

    def mrc_header_values(self):
        """mrc_header_values()

        Output:
            v           MRC header
            
        Compute and determine the MRC header values and return them.
        """
        
        v = {}

        # Use size of matrix to determine data size, as matrix
        # may have been modified from original data matrix.
        # data_size = self.data.size
        data_size = list(self.matrix.shape)
        data_size.reverse()

        # If data originally came from MRC file, then get the
        # map axes and original element type, to determine mode
        mrc_data = self._original_mrc_data()
        if mrc_data:
            map_matrix_axes = map(lambda a:a+1, mrc_data.xyz_matrix_axes)
            element_type = mrc_data.element_type
        else:
            map_matrix_axes = (1,2,3)
            element_type = Numeric.Float32
        self.map_matrix_axes = map(lambda a: a-1, map_matrix_axes)
        
        # map_matrix_axes and data_size are used to get the number
        # of columns, rows, and sections for the MRC map dimensions.
        map_matrix_size = (data_size[map_matrix_axes[0]-1],
                           data_size[map_matrix_axes[1]-1],
                           data_size[map_matrix_axes[2]-1])
        v['nc'], v['nr'], v['ns'] = map_matrix_size

        if element_type == Numeric.Float32: map_mode = MODE_float
        elif element_type == Numeric.Int16: map_mode = MODE_short
        elif element_type == Numeric.Int8:  map_mode = MODE_char
        else:
            raise SyntaxError, ('Data type (%s) ' % element_type +
                                'is not 16 bit int or 8 bit int ' + 
                                'or 32 bit float')
        v['mode'] = map_mode
        self.element_type = element_type

        # @ Default values should be zero according to specs
        #   map_matrix_start = map(lambda a: -a/2, map_matrix_size)
        map_matrix_start = (0,0,0)
        v['ncstart'], v['nrstart'], v['nsstart'] = map_matrix_start

        xyz_intervals = map(lambda a: a-1, data_size)
        v['mx'], v['my'], v['mz'] = xyz_intervals

        #VU 1.2129
        # Grid_Data's xyz_step changed to step
        try:
            # newer versions
            data_step = self.data.step
        except:
            # older versions
            data_step = self.data.xyz_step
        xyz_length = map(lambda a,b: a*b, data_step, xyz_intervals)
        v['xlen'], v['ylen'], v['zlen'] = xyz_length

        if hasattr(self.data, 'cell_angles'):
            cell_angles = self.data.cell_angles
        else: cell_angles = (90.0,90.0,90.0)
        v['alpha'], v['beta'], v['gamma'] = cell_angles

        v['mapc'], v['mapr'], v['maps'] = map_matrix_axes 

        min_intesity, max_intesity, mean_intesity, rms_intensity = \
                      self._min_max_mean_rms_intensity()
        v['amin'] = min_intesity
        v['amax'] = max_intesity
        v['amean'] = mean_intesity
        
        v['ispg'] = 0
        v['nsymbt'] = 0

        mrc_user = []
        for i  in range(MRC_USER_2000):
            mrc_user.append(0)
        v['user'] = mrc_user

        #VU 1.2129
        # Grid_Data's xyz_origin changed to origin
        try:
            # newer versions
            data_origin = self.data.origin
        except:
            # older versions
            data_origin = self.data.xyz_origin
        v['xorigin'], v['yorigin'], v['zorigin'] = data_origin

        v['map'] = 'MAP '

        # Machine stamp - part of the CCP4 format.
        import sys
        if sys.byteorder == 'little': machine_stamp = 0x44440000
        elif sys.byteorder == 'big':  machine_stamp = 0x11110000
        else:
            raise SyntaxError, ('Sytem byte order appears to be ' +
                                'neither little-endian nor big-endian')
        v['machst'] = machine_stamp

        # @ Check if correct interpretation
        v['rms'] = rms_intensity

        v['nlabl'] = 1

        # @ How to retain any labels from original MRC data?
        #   For now, just include a label stating that file was
        #   'Last modified by Chimera'
        labels = []
        for i in range(MRC_NUM_LABELS):
            labels.append(' '*MRC_LABEL_SIZE)
        import time
        time_stamp = time.strftime('%Y %b %d')
        label_Chimera = 'Last modified on %s by Chimera' % time_stamp
        labels[0] = label_Chimera + labels[0][len(label_Chimera):] 
        v['labels'] = labels

        return v
    
    def _original_mrc_data(self):
        """_original_mrc_data() - return mrc_data if original is MRC.

        Output:
            mrc_data        VolumeData grid data object of MRC type
                            or None
                            
        If data originally came from MRC file, return mrc_data.
        mrc_data will be used to compute map matrix axes and the
        original map mode.
        """
        
        file_type = self.data.file_type

        if file_type == 'mrc' and hasattr(self.data, 'mrc_data'):
            return self.data.mrc_data
        
        return None
    
    def _min_max_mean_rms_intensity(self):
        """_min_max_mean_rms_intesity() - return intensity parmaeters.

        Output:
            min         min intensity of matrix
            max         max intensity of matrix
            mean        mean intensity of matrix
            rms         RMS intensity of matrix
            
        Compute min, max, mean, rms intensity values of matrix.
        """

        # @ Slowest part of the WriteMRC module.
        
        matrix = self.matrix
        
        matrix_size = matrix.shape
        size = Numeric.multiply.reduce(matrix_size)
        a = Numeric.ravel(matrix)

        min_intensity = min(a)
        max_intensity = max(a)
        mean_intensity = sum(a)/float(size)

        ms_intensity = sum(pow(a,2))/float(size)
        ms_intensity = ms_intensity - pow(mean_intensity,2)
        rms_intensity = pow(ms_intensity,0.5)

        return min_intensity, max_intensity, mean_intensity, rms_intensity

# -------------------------------------------------------------------------
