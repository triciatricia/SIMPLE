# -------------------------------------------------------------------------
# SegmentWrite/mrc_write.py
#
# Segment Volume package - Segment Write module
#
# Author:
#       Lavu Sridhar,  Baylor College of Medicine (BCM)
#
# Revisions:
#       2005.01.22: Lavu Sridhar, BCM
#       2005.02.15: Lavu Sridhar, BCM
#
# To Do:
#       See comments marked with # @
#
"""Writes MRC format data from Chimera's VolumeData data
object (grid data object).

 Chimera can only read MRC files which it stores in grid data objects.
 Tihs modules takes a grid data object (see VolumeData in Chimera),
 and saves the grid data in MRC format using the values in matrix.
 
 A matrix with modified values correspdonding to grid data object
 rather than the original matrix/data values, can be saved along
 with the updated orignal header.

 Note that the matrix values should be in zyx order.

The MRC data format specs are in the file (mrc_specs.py).
"""

# -------------------------------------------------------------------------

import Numeric

from mrc_header import MRC_Data_Header

# -------------------------------------------------------------------------

MODE_char           = 0
MODE_short          = 1
MODE_float          = 2
MODE_short_COMPLEX  = 3
MODE_float_COMPLEX  = 4

# -------------------------------------------------------------------------

class MRC_Grid_Write:
    """Class MRC_Grid_Write(grid_object, path, matrix_values=None)
    - writes grid data in MRC file format.

    Input:
        grid_object         VolumeData grid data object
        path                Output MRC file path
        matrix_values       data pixel values in zyx order
   
    Writes grid data in grid_object in the MRC file specified by
    path. If the matrix values are not given, then the values
    are obtained from the grid_object file. The matrix values
    are specified in zyx order.
    """
    
    def __init__(self, grid_object, path, matrix_values=None):

        self.data = grid_object
        self.path = path
            
        self.mrc_data_header =  \
                        MRC_Data_Header(grid_object, matrix_values)

        self.map_matrix_axes = self.mrc_data_header.map_matrix_axes
        self.element_type = self.mrc_data_header.element_type
        self.matrix = self.mrc_data_header.matrix # Numeric array

        v = self.mrc_data_header.header

        file_write = open(self.path,'wb')
        self.write_mrc_header(file_write, v)
        self.data_offset = file_write.tell()
        file_write.close()
        
        self.write_mrc_matrix()

    # ---------------------------------------------------------------------
    # MRC header.
    # ---------------------------------------------------------------------

    def write_mrc_header(self, file_write, v):
        """write_mrc_header(file_write,v) - write MRC header

        Input:
            file_write  Output file
            v           MRC header (dictionary)

        Write MRC header in v to file_write.
        """

        i32 = Numeric.Int32
        f32 = Numeric.Float32

        nc_nr_ns = v['nc'], v['nr'], v['ns']
        self._write_values(file_write, nc_nr_ns, i32)

        self._write_values(file_write, (v['mode'],), i32)

        nc_nr_ns_start = v['ncstart'], v['nrstart'], v['nsstart']
        self._write_values(file_write, nc_nr_ns_start, i32)

        mx_my_mz = v['mx'], v['my'], v['mz']
        self._write_values(file_write, mx_my_mz, i32)

        xyz_len = v['xlen'], v['ylen'], v['zlen']
        self._write_values(file_write, xyz_len, f32)

        cell_angles = v['alpha'], v['beta'], v['gamma']
        self._write_values(file_write, cell_angles, f32)

        map_axes = v['mapc'], v['mapr'], v['maps']
        self._write_values(file_write, map_axes, i32)

        min_max_mean = v['amin'], v['amax'], v['amean']
        self._write_values(file_write, min_max_mean, f32)

        self._write_values(file_write, (v['ispg'],), i32)
        self._write_values(file_write, (v['nsymbt'],), i32)
        self._write_values(file_write, (v['user'],), i32)

        xyz_origin = v['xorigin'], v['yorigin'], v['zorigin']
        self._write_values(file_write, xyz_origin, f32)

        file_write.write(v['map'])

        self._write_values(file_write, (v['machst'],), i32)
        self._write_values(file_write, (v['rms'],), f32)
        self._write_values(file_write, (v['nlabl'],), i32)
        for i in range(len(v['labels'])):
            file_write.write(v['labels'][i])

    # ---------------------------------------------------------------------
    # Write header to file
    # ---------------------------------------------------------------------

    def _write_values(self, file_write, values, etype):
        """_write_values(file_write,values,etype) - write values.

        Input:
            file_write  Output file
            values      Output values
            etype       Output value type
            
        Convert values to type etype and then write to file.
        """

        if len(values) == 1:
            values_array = Numeric.array((values,),etype)
        else:
            values_array = Numeric.array(values, etype)
        string = self._write_values_to_string(values_array, etype)
        file_write.write(string)

    def _write_values_to_string(self, values, etype):
        """write_values_to_string(values,etype) - convert to string.

        Input:
            values      Output values
            etype       Output value type
            
        Output:
            string_out  Output string
            
        Convert each value to type etype and return all as a string.
        """

        values = values.astype(etype)
        string_out = values.tostring()
        return string_out

    # ---------------------------------------------------------------------
    # Write matrix data to file
    # ---------------------------------------------------------------------

    def write_mrc_matrix(self):
        """write_mrc_matrix() - write matrix data to file.

        Write data values to file, after the header.
        """

        matrix = self.matrix
        
        matrix = self.permute_matrix_to_map_axis_order(matrix)
        a = Numeric.ravel(matrix)
        
        data = a.tostring()

        file_write = open(self.path,'ab')
        file_write.write(data)
        file_write.close()
        
    def permute_matrix_to_map_axis_order(self, matrix):
        """permute_matrix_to_map_axis_order(matrix)

        Input:
            matrix      data pixel values in zyx order

        Output:
            map_matrix  data pixel values in map order
            
        Converts matrix to map order and returns the matrix.
        Map order corresponds to (rows, columns, sections),
        whereas input matrix order correspodns to (z,y,x).
        """

        if self.map_matrix_axes == (0,1,2):
            return matrix

        # @ ensure that this is correct
        axis_order = map(lambda a: 2-a, self.map_matrix_axes)
        axis_order.reverse()
        map_matrix = Numeric.transpose(matrix, axis_order)

        return map_matrix
    
# -------------------------------------------------------------------------
# MRC Command-line functions
# -------------------------------------------------------------------------

def save_mrc(grid_object, path):
    """save_mrc(grid_oject, path) - save as mrc file in path.

    Input:
        grid_object     VolumeData grid data object
        path            output MRC file path

    Output:
        grid_object     VolumeData grid data object
        
    Save the data in grid_object (see Volume Data module in
    Chimera) in MRC file format in file specified by path.
    """

    return MRC_Grid_Write(grid_object, path)

def save_mrc_matrix(grid_object, path, matrix):
    """save_mrc_matrix(grid_oject, path, matrix) - save matrix
    and grid object as mrc file in path.

    Input:
        grid_object     VolumeData grid data object
        path            output MRC file path
        matrix          data pixel values in zyx matrix order

    Output:
        grid_object     VolumeData grid data object
        
    Save the data in grid_object (see Volume Data module in
    Chimera) in MRC file format in file specified by path.

    This function uses the values in the matrix rather than the
    values from the original data file. The matrix is specified
    in zyx order.
    """

    return MRC_Grid_Write(grid_object, path, matrix)

# -------------------------------------------------------------------------
