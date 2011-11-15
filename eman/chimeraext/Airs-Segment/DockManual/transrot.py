# -------------------------------------------------------------------------
# DockManual/transrot.py
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
"""Handles rotation conventions and conversions. Also contains
notes on the various EMAN and Chimera angle conventions.
"""

# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
# Rotation and its conversions in different conventions
# -------------------------------------------------------------------------

class cRotation:
    """Class: cRotation

    Rotation class. Allows to convert from different angle
    conventions using the rotaiton matrix as the base
    representation. Supports:

    0. Rotation matrix
    1. Quaternions (qx,qy,qz,qw)
    2. Chimera Spin axis convention in radians.
    3. EMAN Euler convention (az, alt, phi) in radians.

    Rotation matrix is actually represented as a linear vector
    m[0] m[3] m[6]
    m[1] m[4] m[7]
    m[2] m[5] m]8]
    """

    def __init__(self, rot_mat=[1.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,1.0],
                 quat=[0.0,0.0,0.0,1.0], euler_val=[0.0,0.0,0.0],
                 axis_val=[0.0,0.0,1.0],ang_val=0.0, rot_type=0):

        if   rot_type == 0:   # rotation matrix
            pass
        elif rot_type == 1: # quaternion
            rot_mat = self.get_matrix_from_quaternion(quat)
        elif rot_type == 2: # chimera spin axis
            rot_mat = self.get_matrix_from_axis_angle(axis_val, ang_val)
        elif rot_type == 3: # EMAN Euler
            rot_mat = self.get_matrix_from_euler(euler_val)
        else:
            # flag unknown
            pass
 
        self.rot_mat = rot_mat

        self.quat = self.get_quaternion_from_matrix()
        self.axis_val, self.ang_val = \
                       self.get_axis_angle_from_matrix()
        self.euler_val = self.get_euler_from_matrix()

    # -----------------------------------------------------------------
    # Basics
    # -----------------------------------------------------------------

    def matrix_identity(self):
        """matrix_identity() - returns identity matrix
        """

        rot_mat = [1.0,0.0,0.0, 0.0,1.0,0.0, 0.0,0.0,1.0]

        return rot_mat

    def get_quaternion(self):

        return self.quat
    
    def get_axis_angle(self):

        return self.axis_val, self.ang_val

    def get_euler_val(self):

        return self.euler_val

    def get_rotation_matrix(self):

        return self.rot_mat
        
    # -----------------------------------------------------------------
    # Rotation Matrix <---> Quaternion
    # -----------------------------------------------------------------

    def get_matrix_from_quaternion(self, quat):
        """get_matrix_from_quaternion(quat)

        Convert Quaternion to rotation matrix
        
        Input:
            quat        Quaternion (qx,qy,qz,qw)
        
        Output:
            rot_mat     rotation matrix
        """

        quat = quaternion_rectify(quat)

        qx,qy,qz,qw = quat

        rot_mat = self.matrix_identity()

        rot_mat[0] = 1 - 2*qy*qy - 2*qz*qz
        rot_mat[1] = 2*qx*qy + 2*qw*qz
        rot_mat[2] = 2*qx*qz - 2*qw*qy
        rot_mat[3] = 2*qx*qy - 2*qw*qz
        rot_mat[4] = 1 - 2*qx*qx - 2*qz*qz
        rot_mat[5] = 2*qy*qz + 2*qw*qx
        rot_mat[6] = 2*qx*qz + 2*qw*qy
        rot_mat[7] = 2*qy*qz - 2*qw*qx
        rot_mat[8] = 1 - 2*qx*qx - 2*qy*qy

        return rot_mat

    def get_quaternion_from_matrix(self, rot_mat=None):
        """get_quaternion_from_matrix(rot_mat=None)
        
        Convert rotation matrix to Quaternion.
        
        Input:
            rot_mat=None    rotation matrix
        
        Output:
            quat            Quaternion (qx,qy,qz,qw)

        If rot_mat=None, then self.rot_mat is used.
        """

        if rot_mat == None:
            rot_mat = self.rot_mat
        
        import math

        n  = 1.0 + rot_mat[0] + rot_mat[4] + rot_mat[8]
        n1 = 1.0 + rot_mat[0] - rot_mat[4] - rot_mat[8]
        n2 = 1.0 - rot_mat[0] + rot_mat[4] - rot_mat[8]
        n3 = 1.0 - rot_mat[0] - rot_mat[4] + rot_mat[8]

        if n > 1e-6:
            qw = (math.sqrt(n))/2.
            qx = (rot_mat[5] - rot_mat[7])/(4.0*qw)
            qy = (rot_mat[6] - rot_mat[2])/(4.0*qw)
            qz = (rot_mat[1] - rot_mat[3])/(4.0*qw)
        elif (rot_mat[0] > rot_mat[4]) and (rot_mat[0] > rot_mat[8]):
            qx = (math.sqrt(n1))/2.
            qy = (rot_mat[3] + rot_mat[1])/(4.0*qx)
            qz = (rot_mat[6] + rot_mat[2])/(4.0*qx)
            qw = (rot_mat[7] - rot_mat[5])/(4.0*qx)
        elif rot_mat[4] > rot_mat[8]:
            qy = (math.sqrt(n2))/2.
            qx = (rot_mat[3] + rot_mat[1])/(4.0*qy)
            qz = (rot_mat[7] + rot_mat[5])/(4.0*qy)
            qw = (rot_mat[6] - rot_mat[2])/(4.0*qy)
        else:
            qz = (math.sqrt(n3))/2.
            qx = (rot_mat[6] + rot_mat[2])/(4.0*qz)
            qy = (rot_mat[7] + rot_mat[5])/(4.0*qz)
            qw = (rot_mat[3] - rot_mat[1])/(4.0*qz)
 
        quat = [qx,qy,qz,qw]

        quat = quaternion_rectify(quat)
        
        return quat

    # ---------------------------------------------------------------------
    # Rotation Matrix <----> Chimera Spin Axis
    # ---------------------------------------------------------------------

    def get_matrix_from_axis_angle(self, axis_val, ang_val):
        """get_matrix_from_axis_angle(axis_val, ang_val)
        
        Convert axis angle to rotation matrix.

        Input:
            axis_val    spin axis x,y,z
            ang_val     spin angle (radians)

        Output:
            rot_mat     rotation matrix
        """

        rot_mat = self.matrix_identity()

        axis_val, ang_val = axis_angle_rectify(axis_val, ang_val)

        x,y,z = axis_val
        
        import math
        c = math.cos(ang_val)
        s = math.sin(ang_val)
        t = 1-c
        
        rot_mat[0] = t*x*x + c
        rot_mat[1] = t*x*y + z*s
        rot_mat[2] = t*x*z - y*s
        rot_mat[3] = t*x*y - z*s
        rot_mat[4] = t*y*y + c
        rot_mat[5] = t*y*z + x*s
        rot_mat[6] = t*x*z + y*s
        rot_mat[7] = t*y*z - x*s
        rot_mat[8] = t*z*z + c
        
        return rot_mat

    def get_axis_angle_from_matrix(self, rot_mat=None):
        """get_axis_angle_from_matrix(rot_mat=None)

        Convert rotation matrix to axis angle.

        Input:
            rot_mat=None     rotation matrix

        Output:
            axis_val        spin axis x,y,z
            ang_val         spin angle (radians)

        If rot_mat=None, then self.rot_mat is used.
        """

        if rot_mat == None:
            rot_mat = self.rot_mat

        rot_mat = rotation_matrix_rectify(rot_mat)
        
        import math

        n = (rot_mat[0] + rot_mat[4] + rot_mat[8] - 1.0)/2.0
        
        ang_val = math.acos(n)

        s = math.sin(ang_val)
        c = math.cos(ang_val)
        
        if (s < 1e-6) and (1-c > 1e-6):   
            x = math.sqrt((rot_mat[0]+1.)/2.)
            y = math.sqrt((rot_mat[4]+1.)/2.)
            z = math.sqrt((rot_mat[8]+1.)/2.)
        else:
            x = rot_mat[5] - rot_mat[7]
            y = rot_mat[6] - rot_mat[2]
            z = rot_mat[1] - rot_mat[3]

        axis_val = [x,y,z]

        axis_val, ang_val = axis_angle_rectify(axis_val, ang_val)
        
        return axis_val, ang_val
    
    # ---------------------------------------------------------------------
    # Rotation Matrix <----> EMAN Euler
    # ---------------------------------------------------------------------

    def get_matrix_from_euler(self, euler_val):
        """get_matrix_from_euler(euler_val)

        Convert EMAN Euler angles to rotation matrix.

        Input:
            euler_val   EMAN euler angles (az, alt, phi) - (radians)

        Output:
            rot_mat     rotation matrix
        """

        a0, a1, a2 = euler_val

        import math

        rot_mat = self.matrix_identity()

        rot_mat[0] =   math.cos(a2)*math.cos(a0) \
                     - math.sin(a2)*math.sin(a0)*math.cos(a1)
        rot_mat[1] =   math.cos(a2)*math.sin(a0) \
                     + math.sin(a2)*math.cos(a0)*math.cos(a1)
        rot_mat[2] =   math.sin(a2)*math.sin(a1)
        rot_mat[3] = - math.sin(a2)*math.cos(a0) \
                     - math.cos(a2)*math.sin(a0)*math.cos(a1)
        rot_mat[4] = - math.sin(a2)*math.sin(a0) \
                     + math.cos(a2)*math.cos(a0)*math.cos(a1)
        rot_mat[5] =   math.cos(a2)*math.sin(a1)
        rot_mat[6] =   math.sin(a1)*math.sin(a0)
        rot_mat[7] = - math.sin(a1)*math.cos(a0)
        rot_mat[8] =   math.cos(a1)

        return rot_mat

    def get_euler_from_matrix(self, rot_mat=None):
        """get_euler_from_matrix(rot_mat=None)

        Convert rotation matrix to EMAN Euler angles.

        Input:
            rot_mat=None    rotation matrix

        Output:
            euler_val   EMAN euler angles (az, alt, phi) - (radians)

        If rot_mat=None, then self.rot_mat is used.
        """

        if rot_mat == None:
            rot_mat = self.rot_mat

        import math

        a0 = math.atan2(rot_mat[6], -rot_mat[7])
        a1 = math.acos(rot_mat[8])
        a2 = math.atan2(rot_mat[2],  rot_mat[5])
        if rot_mat[8] > 0.999999:
            a0 = math.atan2(rot_mat[1],  rot_mat[4])
            a1 = 0.0
            a2 = 0.0
        if rot_mat[8] < -0.999999:
            a0 = math.atan2(rot_mat[1], -rot_mat[4])
            a1 = math.pi
            a2 = 0.0

        euler_val = [a0, a1, a2]
        
        euler_val = euler_rectify(euler_val)
        
        return euler_val

    # ---------------------------------------------------------------------
    # Intermediate conversions through rotation matrix
    # ---------------------------------------------------------------------

    # ---------------------------------------------------------------------
    # EMAN Euler  <-----> Quaternion
    # ---------------------------------------------------------------------

    def get_euler_from_quaternion(self, quat):
        """get_euler_from_quaternion(quat)

        Convert Quaternion to EMAN Euler angles.
        
        Input:
            quat        Quaternion (qx,qy,qz,qw)

        Output:
            euler_val   EMAN Euler angles (az, alt, phi) - (radians)
        """

        rot_mat = self.get_matrix_from_quaternion(quat)
        euler_val = self.get_euler_from_matrix(rot_mat)
        
        return euler_val

    def get_quaternion_from_euler(self, euler_val):
        """get_quaternion_from_euler(euler_val)

        Convert EMAN Euler angles to Quaternion.

        Input:
            euler_val   EMAN Euler angles (az, alt, phi) - (radians)

        Output:
            quat        Quaternion (qx,qy,qz,qw)
        """

        a0, a1, a2 = euler_val

        rot_mat = self.get_matrix_from_euler(euler_val)
        quat = self.get_quaternion_from_matrix(rot_mat)

        return quat

    # ---------------------------------------------------------------------
    # EMAN Euler  <-----> Axis Angle
    # ---------------------------------------------------------------------

    def get_euler_from_axis_angle(self, axis_val, ang_val):
        """get_euler_from_axis_angle(axis_val, ang_val)

        Convert Axis Angle to EMAN Euler angles.
        
        Input:
            axis_val    spin axis x,y,z
            ang_val     spin angle (radians)

        Output:
            euler_val   EMAN Euler angles (az, alt, phi) - (radians)
        """

        rot_mat = self.get_matrix_from_axis_angle(axis_val, ang_val)
        euler_val = self.get_euler_from_matrix(rot_mat)

        return euler_val

    def get_axis_angle_from_euler(self, euler_val):
        """get_axis_angle_from_euler(euler_val)

        Convert EMAN Euler angles to Axis Angle.
        
        Input:
            euler_val   EMAN Euler angles (az, alt, phi) - (radians)

        Output:
            axis_val    spin axis x,y,z
            ang_val     spin angle (radians)
        """

        rot_mat = self.get_matrix_from_euler(euler_val)
        axis_val, ang_val = self.get_axis_angle_from_matrix(rot_mat)

        return axis_val, ang_val

    # ---------------------------------------------------------------------
    # Axis Angle  <-----> Quaternion
    # ---------------------------------------------------------------------

    def get_axis_angle_from_quaternion(self, quat):
        """get_axis_angle_from_quaternion(quat)

        Convert Quaternion to axis angle.
        
        Input:
            axis_val    spin axis x,y,z
            ang_val     spin angle (radians)

        Output:
            quat        quaternion normalized (qx,qy,qz,qw)
        """

        rot_mat = self.get_matrix_from_quaternion(quat)
        axis_val, ang_val = self.get_axis_angle_from_matrix(rot_mat)

        return axis_val, ang_val
    
    def get_quaternion_from_axis_angle(axis_val, ang_val):
        """get_quaternion_from_axis_angle(axis_val, ang_val)

        Convert axis angle to Quaternion
        
        Input:
            axis_val    spin axis x,y,z
            ang_val     spin angle (radians)

        Output:
            quat        quaternion normalized (qx,qy,qz,qw)
        """

        rot_mat =  self.get_matrix_from_axis_angle(axis_val, ang_val)
        quat = self.get_quaternion_from_matrix(rot_mat)

        return quat

# -------------------------------------------------------------------------
# Correction factors
# -------------------------------------------------------------------------

def quaternion_rectify(quat):
    """quaternion_rectify(quat)

    Returns rectified quaternion with norm 1.

    Input:
        quat     quaternion (qx,qy,qz,qw)

    Output:
        quat     quaternion normalized (qx,qy,qz,qw)
    """

    qx,qy,qz,qw = quat
    
    import math
    qs = math.sqrt(qx*qx + qy*qy + qz*qz + qw*qw)

    qx = qx/qs
    qy = qy/qs
    qz = qz/qs
    qw = qw/qs

    quat = [qx,qy,qz,qw]
    
    return quat

def euler_rectify(euler_val):
    """euler_rectify(euler_val)

    Rectify EMAN Euler angles.

    Input:
        euler_val       EMAN Euler angles (az, alt, phi) - (radians)

    Output:
        euler_val       EMAN Euler angles (az, alt, phi) - (radians)
    """

    import math
    
    for a in range(3):
        try:
            float(euler_val[a])
        except:
            euler_val[a] = 0.0

    a0, a1, a2 = euler_val

    if math.sqrt(a1*a1) <= 0.0001:
        a0 = a0 + a2
        a2 = 0.0

    a1 = math.fmod(a1, float(2.0*math.pi))

    a2 = math.fmod(a2, float(2.0*math.pi))
    if a2 < 0.0:
        a2 = a2 + 2*math.pi
    a0 = math.fmod(a0, float(2.0*math.pi))
    if a0 < 0.0:
        a0 = a0 + 2*math.pi
        
    euler_val = [a0, a1, a2]
    
    return euler_val

def axis_angle_rectify(axis_val, ang_val):
    """axis_angle_rectify(axis_val, ang_val)

    Rectify Axis Angle values.

    Input:
        axis_val    rotation axis
        ang_val     angle of rotation about rotation axis (radians)

    Output:
        axis_val    rotation axis
        ang_val     angle of rotation about rotation axis (radians)
    """

    import math

    # normalize
    x,y,z = axis_val
    axis_norm = math.sqrt(x*x + y*y + z*z)
    if axis_norm < 1e-6:
        ang_val = 0.0
        axis_val = [0.0,0.0,1.0]
    else:
        axis_val = map(lambda u,v=axis_norm: u/v,  axis_val)

    # check if need to switch direction of axis vector        
    ang_val = math.fmod(ang_val, float(2.0*math.pi))
    if ang_val > math.pi:
        axis_val = map(lambda x: -x, axis_val)
        ang_val = 2*math.pi - ang_val

    return axis_val, ang_val

def rotation_matrix_rectify(rot_mat):
    """rotation_matrix_rectify(rot_mat)

    Rectifies rotation matrix, by rounding off any elements
    smaller than 1e-6.
    
    Input:
        rot_mat     rotation matrix

    Output:
        rot_mat     rotation matrix
    """

    v_small = 1e-6
    
    for a in range(9):
        if rot_mat[a] < v_small and rot_mat[a] > -v_small:
            rot_mat[a] = 0.0
        if rot_mat[a] + 1 < v_small and rot_mat[a] + 1 > -v_small:
            rot_mat[a] = -1.0
        if rot_mat[a] - 1 < v_small and rot_mat[a] - 1 > -v_small:
            rot_mat[a] = 1.0

    return rot_mat
        
# -------------------------------------------------------------------------








# -------------------------------------------------------------------------
# Notes
# -------------------------------------------------------------------------
#
# EMAN conventions
# ----------------
#
# Check: Euler.C in libEM in EMAN (see the CVS version) 
#
#   (a0,a1,a2) = (az_,alt_,phi_)
#
#  Matrix from EMAN Euler
#    m[0] =  cos(a2)*cos(a0) - sin(a2)*sin(a0)*cos(a1)
#    m[1] =  cos(a2)*sin(a0) + sin(a2)*cos(a0)*cos(a1)
#    m[2] =  sin(a2)*sin(a1)
#    m[3] = -sin(a2)*cos(a0) - cos(a2)*sin(a0)*cos(a1)
#    m[4] = -sin(a2)*sin(a0) + cos(a2)*cos(a0)*cos(a1)
#    m[5] =  cos(a2)*sin(a1)
#    m[6] =  sin(a1)*sin(a0)
#    m[7] = -sin(a1)*cos(a0)
#    m[8] =  cos(a1)
#
#  EMAN Euler from Matrix
#    a0 = atan2(m[6],-m[7])
#    a1 = acos(m[8])
#    a2 = atan2(m[2], m[5])
#    if m[8] >  0.999999: a1 =0,  a0 = atan2(m[1], m[4]), a2 = 0
#    if m[8] < -0.999999: a1 =pi, a0 = atan2(m[1],-m[4]), a2 = 0
#    rectify()
#
# -------------------------------------------------------------------------
#
#  EMAN Euler from Quaternion
#    1. Get Matrix from Quaternion
#    2. Get EMAN Euler from Matrix
#
#  Quaternion from EMAN Euler
#    1. Get Matrix from EMAN Euler
#    2. Get Quaternion from Matrix
#
#  Quaternion from EMAN Euler (2)
#    qw =  cos((a2+a0)/2.)*cos(a1/2.)
#    qx =  cos((a2-a0)/2.)*sin(a1/2.)
#    qy = -sin((a2-a0)/2.)*sin(a1/2.)
#    qz =  sin((a2+a0)/2.)*cos(a1/2.)
#
#  EMAN Euler from Spin Axis
#    1. Get Quaternion from Spin Axis
#    2. Get EMAN Euler from Quaternion
#
#  Spin Axis from EMAN Euler
#    1. Get Quaternion from EMAN Euler
#    2. Get Spin Axis from Quaternion
#
#  Spin Axis from EMAN Euler (2)
#    n = cos((a2+a0)/2.0)*cos(a1/2.0)
#    a = 2.0 * acos(n)
#    if (1-n*n) < 1e-6:
#      x,y,z = 0,0,1
#    else:
#      x =  cos((a2-a0)/2.)*sin(a1/2.)/sqrt(1-n*n)
#      y = -sin((a2-a0)/2.)*sin(a1/2.)/sqrt(1-n*n)
#      z =  sin((a2+a0)/2.)*cos(a1/2.)/sqrt(1-n*n)
#
# -------------------------------------------------------------------------
#
#  Matrix from Spin Axis
#    1. Get Quaternion from Spin Axis
#    2. Get matrix from Quaternion
#
#  Spin Axis from Matrix
#    ???
#
#
#  Matrix from Quaternion (quaternion normalized)
#    m[0] = 1 - 2*qy*qy - 2*qz*qz
#    m[1] = 2*qx*qy + 2*qw*qz
#    m[2] = 2*qx*qz - 2*qw*qy
#    m[3] = 2*qx*qy - 2*qw*qz
#    m[4] = 1 - 2*qx*qx - 2*qz*qz
#    m[5] = 2*qy*qz + 2*qw*qx
#    m[6] = 2*qx*qz + 2*qw*qy
#    m[7] = 2*qy*qz - 2*qw*qx
#    m[8] = 1 - 2*qx*qx - 2*qy*qy
#
#  Quaternion from Matrix
#    qw = 0.5*sqrt(   m[0] + m[4] + m[8] + 1.0)
#    qx = 0.5*sqrt(   m[0] - m[4] - m[8] + 1.0)
#    qy = 0.5*sqrt( - m[0] + m[4] - m[8] + 1.0)
#    qz = 0.5*sqrt( - m[0] - m[4] + m[8] + 1.0)
#    normalize()
#
#  Quaternion from Spin Axis
#    n = norm(x,y,z)
#    qw = cos(a/2)
#    qx = x*sin(a/2)/n
#    qy = y*sin(a/2)/n
#    qz = z*sin(a/2)/n
#
#  Spin Axis from Quaternion
#    a = 2*acos(qw)
#    n = norm(qx,qy,qz)
#    x,y,z = [qx,qy,qz]/n
#    normalize() and rectify()
#
#  Rectify Euler
#    if (!goodf(a1)), a1 = 0.0 (goodf returns 0 if infinite, NaN)
#    if (!goodf(a0)), a0 = 0.0
#    if (!goodf(a2)), a2 = 0.0
#    if sqrt(a1*a1) <= 0.0001 { a0 = a0 + a2, a2 = 0.0)
#    a2 = fmod(a2, (2.0*pi))
#    if a2 < 0, a2 = a2 + 2*pi
#    a0 = fmod(a0, (2.0*pi))
#    if a0 < 0, a0 = a0 + 2*pi
#
# Conversions
# ------------
#
# Not used here, but check...
# Check: http://www.euclideanspace.com/maths/geometry/rotations/
#
#  Axis angle to Quaternion (assumes axis normalized)
#    qx = x * s(a/2)
#    qy = y * s(a/2)
#    qz = z * s(a/2)
#    qw = c(a/2)
#
#  Quaternion to Axis angle
#    a = 2*math.acos(qw)
#    x = qx/sqrt(1-qw^2) (if sqrt(1-qw^2) < 0.001, use x,y,z = 0,0,1)
#    y = qy/sqrt(1-qw^2)
#    z = qz/sqrt(1-qw^2)
#
# -------------------------------------------------------------------------


# -------------------------------------------------------------------------
# Chimera's conventions
# -------------------------------------------------------------------------
#
#
#  Chimera's global coordinate's z axis ALWAYS points at the user.
#  Chimera's axis angle uses counter-clockwise rotation (RHS).
#
# -------------------------------------------------------------------------
