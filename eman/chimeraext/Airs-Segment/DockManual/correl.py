# -------------------------------------------------------------------------
# DockManual/correl.py
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
# To Do:
#       See comments marked with # @
#
"""Computes correlation between a PDB strucutres
and density maps, using EMAN programs.
"""

# -------------------------------------------------------------------------

def read_pdb_lines(file_PDB_name):
    """read_pdb_lines(file_PDB_name)

    Input:
        file_PDB_name   PDB file name
        
    Output:
        linesPDB        lines from PDB file
    
    Reads lines from PDB file - file_PDB_name.
    """

    filePDB = open(file_PDB_name,'r')
    linesPDB = filePDB.readlines()
    filePDB.close()

    return linesPDB

def check_ijk_good(ijk, data_size):
    """check_ijk_good(ijk, data_size)

    Input:
        ijk         ijk coordinates
        data_size   size of data

    Output:
        1/0         1 if ijk is within data size, else 0

    Checks if voxel specified by ijk is within data matrix
    size specified as data_size.
    """
        
    if (ijk[0] >= 0 and ijk[0] < data_size[0] and
        ijk[1] >= 0 and ijk[1] < data_size[1] and
        ijk[2] >= 0 and ijk[2] < data_size[1]):
        return 1
    else:
        return 0

def get_volume_data_value(data, xyz, mrc_matrix):
    """get_volume_data_value(data, xyz, mrc_matrix)

    Input:
        data            Chimera's VolumeData grid object
        xyz             xyz coordinates (float)
        mrc_matrix      MRC matrix

    Output:
        tri_lin_interp  tri-linear interpolated value
                            at xyz point

    Get volume data value at xyz from mrc matrix using
    trilinear interpolation between the voxels surrounding
    the point xyz.
    """

    ijk_orig = data.xyz_to_ijk(xyz)

    import math
    ijk_floor = map(lambda x: int(math.floor(x)), ijk_orig)
    
    ijk_000 = ijk_floor
    ijk_100 = [ijk_floor[0]+1, ijk_floor[1],   ijk_floor[2]  ]
    ijk_010 = [ijk_floor[0],   ijk_floor[1]+1, ijk_floor[2]  ]
    ijk_001 = [ijk_floor[0],   ijk_floor[1],   ijk_floor[2]+1]

    ijk_110 = [ijk_floor[0]+1, ijk_floor[1]+1, ijk_floor[2]  ]
    ijk_011 = [ijk_floor[0]  , ijk_floor[1]+1, ijk_floor[2]+1]
    ijk_101 = [ijk_floor[0]+1, ijk_floor[1],   ijk_floor[2]+1]

    ijk_111 = [ijk_floor[0]+1, ijk_floor[1]+1, ijk_floor[2]+1]
    
    tuv_0 = map(lambda x,y: x-y, ijk_orig, ijk_floor)
    tuv_1 = map(lambda x  : 1.0-x, tuv_0)

    data_size = data.size
    mrc_zero = 0.

    ijk_now = ijk_000
    if check_ijk_good(ijk_now, data_size):
        mrc_000 = mrc_matrix[ijk_now[0]][ijk_now[1]][ijk_now[2]]
    else: mrc_000 = mrc_zero

    ijk_now = ijk_100
    if check_ijk_good(ijk_now, data_size):
        mrc_100 = mrc_matrix[ijk_now[0]][ijk_now[1]][ijk_now[2]]
    else: mrc_100 = mrc_zero
    ijk_now = ijk_010
    if check_ijk_good(ijk_now, data_size):
        mrc_010 = mrc_matrix[ijk_now[0]][ijk_now[1]][ijk_now[2]]
    else: mrc_010 = mrc_zero
    ijk_now = ijk_001
    if check_ijk_good(ijk_now, data_size):
        mrc_001 = mrc_matrix[ijk_now[0]][ijk_now[1]][ijk_now[2]]
    else: mrc_001 = mrc_zero

    ijk_now = ijk_110
    if check_ijk_good(ijk_now, data_size):
        mrc_110 = mrc_matrix[ijk_now[0]][ijk_now[1]][ijk_now[2]]
    else: mrc_110 = mrc_zero
    ijk_now = ijk_011
    if check_ijk_good(ijk_now, data_size):
        mrc_011 = mrc_matrix[ijk_now[0]][ijk_now[1]][ijk_now[2]]
    else: mrc_011 = mrc_zero
    ijk_now = ijk_101
    if check_ijk_good(ijk_now, data_size):
        mrc_101 = mrc_matrix[ijk_now[0]][ijk_now[1]][ijk_now[2]]
    else: mrc_101 = mrc_zero

    ijk_now = ijk_111
    if check_ijk_good(ijk_now, data_size):
        mrc_111 = mrc_matrix[ijk_now[0]][ijk_now[1]][ijk_now[2]]
    else: mrc_111 = mrc_zero

    mrc = []
    mrc.append(tuv_1[0]*tuv_1[1]*tuv_1[2]*mrc_000)

    mrc.append(tuv_0[0]*tuv_1[1]*tuv_1[2]*mrc_100)
    mrc.append(tuv_1[0]*tuv_0[1]*tuv_1[2]*mrc_010)
    mrc.append(tuv_1[0]*tuv_1[1]*tuv_0[2]*mrc_001)

    mrc.append(tuv_0[0]*tuv_0[1]*tuv_1[2]*mrc_110)
    mrc.append(tuv_1[0]*tuv_0[1]*tuv_0[2]*mrc_011)
    mrc.append(tuv_0[0]*tuv_1[1]*tuv_0[2]*mrc_101)

    mrc.append(tuv_0[0]*tuv_0[1]*tuv_0[2]*mrc_111)

    tri_lin_interp = sum(mrc)

    return tri_lin_interp

def get_CA_xyz_from_lines(linesPDB):
    """get_CA_xyz_from_lines(linesPDB)

    Input:
        linesPDB    lines from a PDB file

    Output:
        xyz_CA      list of xyz positions of C-alpha atoms
        
    Get C-alpha positions from the lines obtained from PDB file.
    """

    xyz_CA = []
    for linePDB in linesPDB:
        isatom = str(linePDB[0:6].strip())
        if (isatom == 'ATOM'):
            atomelem = linePDB[13:15]
            if atomelem == 'CA':
                xyz_atom = [linePDB[30:38], linePDB[38:46], linePDB[46:54]]
                xyz_atom = map(lambda x: float(x), xyz_atom)
                xyz_CA.append(xyz_atom)
            
    return xyz_CA

def get_CA_xyz_from_atoms(atomsPDB):
    """get_CA_xyz_from_atoms(atomsPDB)

    Input:
        atomsPDB    list of atoms from PDB strucutre

    Output:
        xyz_CA      list of xyz positions of C-alpha atoms
    
    Get C-alpha positions from atoms obtained from PDB structure.
    """

    xyz_CA = []    
    for atom in atomsPDB:
        if atom.name == 'CA':
            xyz_vec = atom.xformCoord()
            xyz_CA.append([xyz_vec.x, xyz_vec.y, xyz_vec.z])

    return xyz_CA

def get_mrc_values_at_xyz(xyz_values, data):
    """get_mrc_values_at_xyz(xyz_values, data)

    Input:
        xyz_values      list of xyz positions
        data            Chimera's VolumeData grid object

    Output:
        mrc_xyz_values  density values at xyz_values

    Get MRC density values at locations in xyz_values for
    data specified by Chimera VolumeData grid object data.
    """

    mrc_matrix = data.submatrix([0,0,0],data.size)
    
    mrc_xyz_values = []
    for xyz in xyz_values:
        mrc_xyz = get_volume_data_value(data,xyz, mrc_matrix)
        mrc_xyz_values.append(mrc_xyz)
        
    return mrc_xyz_values

def get_mean(list_values):
    """get_mean(list_values)

    Input:
        list_values      list of values

    Output:
        list_mean        mean value of input list of values
        
    Compute the mean of the list of values in list_values.
    Returns 0.0 if input list is empty.
    """

    list_mean = 0.
    
    list_values_len = len(list_values)
    if list_values_len == 0:
        return list_mean
    
    list_mean = sum(list_values)
    list_mean = list_mean/float(list_values_len)

    return list_mean

def get_pdb_file_mean(file_PDB_name, data):
    """get_pdb_file_mean(file_PDB_name, data)

    Input:
        file_PDB_name   PDB file containing C-alpha atoms
        data            Chimera grid data object used to
                            compute the mean density

    Output:
        mrc_xyz_CA_mean mean density value of data computed
                            at all C-alpha atoms in PDB file
        
    Get the mean of the density values in data, at locations
    of C-alpha atoms in PDB structure in file_PDB_name.
    """

    linesPDB = read_pdb_lines(file_PDB_name)
    
    xyz_CA = get_CA_xyz_from_lines(linesPDB)

    mrc_xyz_CA = get_mrc_values_at_xyz(xyz_CA, data)

    mrc_xyz_CA_mean = get_mean(mrc_xyz_CA)

    return mrc_xyz_CA_mean

def get_pdb_xform_mean(model, data):
    """get_pdb_xform_mean(model, data)

    Input:
        model           Chimera model containing the
                            C-alpha atoms
        data            Chimera grid data object used to
                            compute the mean density

    Output:
        mrc_xyz_CA_mean     mean density value of data
                                computed at all C-alpha
                                atoms in model
        
    Get the mean of the density values in data, at locations
    of C-alpha atoms in Chimera model in model.

    Note that the model could have undergone rigid body
    transformations. The program computes densities at
    transformed coordinates of the C-alpha atoms.
    """

    atomsPDB = model.atoms

    xyz_CA = get_CA_xyz_from_atoms(atomsPDB)

    mrc_xyz_CA = get_mrc_values_at_xyz(xyz_CA, data)

    mrc_xyz_CA_mean = get_mean(mrc_xyz_CA)

    return mrc_xyz_CA_mean

def get_mean_density(model, data):
    """get_mean_density(model, data)

    Input:
        model       Chimera model containing the
                        C-alpha atoms
        data        Chimera grid data object used to
                        compute the mean density

    Output:
        mean1       mean density value of data computed
                        at locations in model
        
    Get the mean of the density values in data, at locations
    of C-alpha atoms in Chimera model in model.

    Note that the model could have undergone rigid body
    transformations. The program computes densities at
    transformed coordinates of the C-alpha atoms.
    """

    mean1 = get_pdb_xform_mean(model,data)

    return mean1

# -------------------------------------------------------------------------
