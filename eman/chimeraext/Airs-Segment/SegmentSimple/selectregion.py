# -------------------------------------------------------------------------
# SegmentSimple/selectregion.py
#
# Segment Volume package - Segment Simple module
# 
# Author:
#       Lavu Sridhar, Baylor College of Medicine (BCM)
#
# Revisions:
#       2004.12.20: Lavu Sridhar, BCM
#       2005.02.15: Lavu Sridhar, BCM
#       2005.07.15: Lavu Sridhar, BCM
#       2005.09.06: Lavu Sridhar, BCM (VU 1.2129 Chimera)
#       2005.11.15: Lavu Sridhar, BCM (VU 1.2179 Chimera)
#
# To Do:
#       See comments marked with # @
# 
# Key:
#       VU: Version Upgrade
#
"""Segmentation of MRC density maps.

Adds mouse interactivity to GUI to aid segmentation using
simple regions:
(1) Cuboid regions
(2) ...
"""
# -------------------------------------------------------------------------

# general modules

# chimera related modules
import chimera

import VolumeViewer

# -------------------------------------------------------------------------
# box region selector
# -------------------------------------------------------------------------

class Select_Box:
    """Class: Select_Box(segment_dialog)

    Creates a box region selector for use in simple segmentation.
    """
    
    def __init__(self, seg_dialog):
        """__init__(seg_dialog) - initialize and add mouse callbacks.

        Creates a box region selector for use in simple segmentation.
        """

        self.box_model = Box_Model()
        self.seg_dialog = seg_dialog
        #VU 1.2179
        # self.xyz_in = None        
        # self.xyz_out = None       
        self.ijk_in = None          
        self.ijk_out = None         
        self.mode_name = 'seg box region'
        self.bound_button = None
        self.drag_button = None

        callbacks = (self.mouse_down_cb, self.mouse_drag_cb,
                     self.mouse_up_cb)

        icon_file = None

        from chimera import mousemodes
        mousemodes.addFunction(self.mode_name, callbacks, icon_file)

    def data_region(self):
        """data_region()

        Output:
            data_region
            
        Return data region in focus in the segment dialog.
        """

        # @ should this be from simple seg dialog?
        return self.seg_dialog.data_panel.focus_region

    # ---------------------------------------------------------------------
    # Mouse buttons
    # ---------------------------------------------------------------------

    def bind_mouse_button(self, button, modifiers):
        """bind_mouse_button(button, modifiers)

        """

        # first unbind and then bind
        self.unbind_mouse_button()
        
        from chimera import mousemodes
        mousemodes.setButtonFunction(button, modifiers, self.mode_name)

        self.bound_button = (button, modifiers)

    def unbind_mouse_button(self):
        """unbind_mouse_button()

        """

        if self.bound_button:
            button, modifiers = self.bound_button
            from chimera import mousemodes
            def_mode = mousemodes.getDefault(button, modifiers)
            if def_mode:
                mousemodes.setButtonFunction(button, modifiers, def_mode)
            self.bound_button = None

    def mouse_down_cb(self, viewer, event):
        """mouse_down_cb(viewer, event)

        On mouse press: Move box, or move face, or create box.
        """

        self.drag_occured = 0

        if self.box_model.box_shown():
            # box shown, so move box or move face
            bm = self.box_model
            faces = bm.pierced_faces(event.x, event.y)
            if len(faces) == 0:
                self.drag_mode = 'move box'
            else:
                self.drag_mode = 'move face'
                shift_mask = 1
                shift = (event.state & shift_mask)
                if shift and len(faces) >= 2:
                    face = faces[1]
                else:
                    face = faces[0]
                self.drag_face = face
                nx, ny, nz = apply(bm.face_normal, (face[0], 1))
                if abs(nx) > abs(ny):
                    self.face_direction = (sign(nx),0)
                else:
                    self.face_direction = (0, sign(ny))
            self.last_xy = (event.x, event.y)
        else:
            # box not shown, so delete any hidden box, create new box
            self.box_model.delete_box()
            self.drag_mode = 'create'
            #VU 1.2179
            # self.xyz_in = None   
            # self.xyz_out = None  
            self.ijk_in = None     
            self.ijk_out = None    
            self.sweep_out_box(event.x, event.y)

    def mouse_drag_cb(self, viewer, event):
        """mouse_drag_cb(viewer, event)

        On mouse drag: Move box, move face, or create box.
        """

        self.drag_occured = 1

        # move box or move face or create box
        if self.drag_mode == 'move box':
            shift_mask = 1
            shift = (event.state & shift_mask)
            self.move_box(event.x, event.y, shift)
        elif self.drag_mode == 'move face':
            self.move_face(event.x, event.y)
        elif self.drag_mode == 'create':
            self.sweep_out_box(event.x, event.y)

    def mouse_up_cb(self, viewer, event):
        """mouse_up_cb(viewer, event)

        On mouse raise: If no drag occured, and if box created
        and shown, return, and if box not created or box not
        shown, then toggle box. If drag occured, pass box
        boundary to segment dialog.
        """

        if not self.drag_occured:
            if self.drag_mode == 'create' and self.box_model.box_shown():
                return
            self.toggle_box()
          
        if self.drag_occured:
            d = self.seg_dialog
            #VU 1.2179
            ijk_in, ijk_out = self.box_model.box
            d.selection_to_parameters_cb(ijk_in, ijk_out, ijk=1)
            # xyz_in, xyz_out = self.box_model.box_bounds()
            # d.selection_to_parameters_cb(xyz_in,xyz_out)
                                                
    # ---------------------------------------------------------------------
    # Box related functions
    # ---------------------------------------------------------------------

    def toggle_box(self):
        """toggle_box()

        If box model shown, then delete it. If not shown, and if no
        focus region in segment dialog, then quit. If not shown, and
        if focus region found, then get its transform and apply to
        box after creating box.
        """

        bm = self.box_model
        if bm.box_shown():
            bm.delete_box()
        else:
            box, transform, xform = \
                 box_transform_and_xform(self.data_region())
            if box and xform:
                bm.reshape_box(box, transform, xform)
            #VU 1.2179
            # # @ which data region is this??? should we do nothing???
            # data_region = self.data_region()
            # if data_region == None:
            #    return
            # #VU 1.2129
            # # xform = data_region.transform()
            # import SegmentMenu
            # from SegmentMenu import datamenuseg
            # xform = datamenuseg.get_data_region_xform(data_region)
            # if xform == None:
            #    return
            # #VU 1.2129
            # # box = data_region.xyz_region()
            # import SegmentMenu
            # from SegmentMenu import datamenuseg
            # box = datamenuseg.get_data_region_bounds(data_region)
            # bm.reshape_box(box, xform)

    def sweep_out_box(self, pointer_x, pointer_y):
        """sweep_out_box(pointer_x, pointer_y)

        Create box if data region found and it has been transformed.
        """

        box, tf, xform = box_transform_and_xform(self.data_region())
        if box == None:
            return

        transform = box_to_eye_transform(tf, xform)

        from VolumeViewer import slice
        ijk_in, ijk_out = slice.box_intercepts(pointer_x, pointer_y,
                                               transform, box)
        if ijk_in == None or ijk_out == None:
          return
        
        if self.ijk_in == None:
            self.ijk_in = ijk_in
        if self.ijk_out == None:
            self.ijk_out = ijk_out
          
        drag_box = bounding_box((ijk_in, ijk_out,
                                 self.ijk_in, self.ijk_out))
        self.box_model.reshape_box(drag_box, tf, xform)

        #VU 1.2179
        # data_region = self.data_region()
        # if data_region == None:
        #    return
        # 
        # #VU 1.2129
        # # xform = data_region.transform()
        # import SegmentMenu
        # from SegmentMenu import datamenuseg
        # xform = datamenuseg.get_data_region_xform(data_region)
        # if xform == None:
        #    return
        #
        # #VU 1.2129
        # # bounds = data_region.xyz_region()
        # import SegmentMenu
        # from SegmentMenu import datamenuseg
        # bounds = datamenuseg.get_data_region_bounds(data_region)
        # 
        # from VolumeViewer import slice
        # xyz_in, xyz_out = slice.box_intercepts(pointer_x, pointer_y,
        #                                       xform, bounds)
        #
        # if xyz_in == None or xyz_out == None:
        #     return
        # 
        # if self.xyz_in == None:
        #    self.xyz_in = xyz_in
        # if self.xyz_out == None:
        #    self.xyz_out = xyz_out
        # 
        # box = bounding_box((xyz_in, xyz_out, self.xyz_in, self.xyz_out))
        # self.box_model.reshape_box(box, xform)

    def move_box(self, pointer_x, pointer_y, shift):
        """move_box(pointer_x, pointer_y, shift)

        Move box by pointer_x, pointer_y. If shift = 1, move in z
        direction (view direction).
        """

        last_x, last_y = self.last_xy
        dx = pointer_x - last_x
        dy = pointer_y - last_y
        self.last_xy = (pointer_x, pointer_y)

        bm = self.box_model
        d = bm.view_distance()
        psize = pixel_size(d)
    
        if shift:
            if abs(dx) > abs(dy):     dz = dx
            else:                     dz = dy
            delta_xyz = (0, 0, dz * psize)
        else:
            delta_xyz = (dx * psize, -dy * psize, 0)
    
        bm.move_box(delta_xyz)

    def move_face(self, pointer_x, pointer_y):
        """move_face(pointer_x, pointer_y)

        Move face by pointer_x, pointer_y, from last_xy
        """

        last_x, last_y = self.last_xy
        dx = pointer_x - last_x
        dy = pointer_y - last_y
        self.last_xy = (pointer_x, pointer_y)

        bm = self.box_model
        d = bm.view_distance()
        psize = pixel_size(d)
        fd = self.face_direction
        dist = (dx * fd[0] + -dy * fd[1]) * psize

        axis, side = self.drag_face
        bm.move_face(axis, side, dist)

# -------------------------------------------------------------------------
# General functions VU 1.2179
# -------------------------------------------------------------------------

def box_transform_and_xform(data_region):
    """box_transform_and_xform(data_region):

    """

    if data_region == None:
        return None, None, None

    xform = data_region.model_transform()
    if xform == None:
        return None, None, None

    tf = data_region.data.ijk_to_xyz_transform
    box = data_region.ijk_bounds()

    return box, tf, xform

def box_to_eye_transform(box_transform, xform):
    """box_to_eye_transform(box_transform, xform):
    
    Combine transform of ijk_box to object coordinates
    and model xform mapping object coordinates to eye
    coordinates.
    """

    from PDBmatrices import matrices
    model_transform = matrices.xform_matrix(xform)
    # chimera.Xform -> 3x4 matrix
    transform = matrices.multiply_matrices(model_transform,
                                           box_transform)
    return transform

def eye_to_box_transform(box_transform, xform):
    """eye_to_box_transform(box_transform, xform):
    
    Eye to box coordinate transform.
    """

    tf = box_to_eye_transform(box_transform, xform)
    from PDBmatrices import matrices
    inv_tf = matrices.invert_matrix(tf)
    return inv_tf

# -------------------------------------------------------------------------

class Box_Model:
    """Class: Box_Model()

    Creates a molecule with 8 corner atoms and bonds between them
    to define a cuboid box model for use in box region selector,
    given by Class: Select_Box.
    """

    def __init__(self):
        """__init__() - create a box model using 8 corner atoms.
        """

        self.corner_atoms = None
        #VU 1.2179
        self.box = None
        self.box_transform = None

    def box_bounds(self):
        """box_bounds()

        Output:
            xyz_min
            xyz_max
            
        Return bounding box of molecule - corner atoms 0 and 7.
        """

        return self.box

        #VU 1.2179
        # m = self.model()
        # if m == None or not m.display:
        #    return None, None
        # 
        # c_min = self.corner_atoms[0].coord()
        # xyz_min = c_min.x, c_min.y, c_min.z
        # 
        # c_max = self.corner_atoms[7].coord()
        # xyz_max = c_max.x, c_max.y, c_max.z
        # 
        # return xyz_min, xyz_max

    # ---------------------------------------------------------------------
    # Create/destroy/display box functions    
    # ---------------------------------------------------------------------

    def create_box(self):
        """create_box()

        Output:
            corners      8 corner atoms
            
        Create a molecule with 8 corner atoms to represent a box model.
        """

        m = chimera.Molecule()
        m.name = 'Subregion Box'
        chimera.openModels.add([m])
        add_model_closed_callback(m, self.model_closed_cb)

        rid = chimera.MolResId(1)
        r = m.newResidue('markers', rid)

        corners = []
        for name in ('a000', 'a001', 'a010', 'a011',
                     'a100', 'a101', 'a110', 'a111'):
            a = m.newAtom(name, chimera.elements.H)
            r.addAtom(a)
            corners.append(a)

        red = chimera.MaterialColor(1,0,0,1)
        for a1, a2 in ((0,1), (2,3), (4,5), (6,7),
                       (0,2), (1,3), (4,6), (5,7),
                       (0,4), (1,5), (2,6), (3,7)):
            b = m.newBond(corners[a1], corners[a2])
            b.halfbond = 0
            b.drawMode = chimera.Bond.Wire
            b.color = red

        return corners

    def model(self):
        """model()

        Output:
            molecule/None

        Returnn molecule if it exists. Return None otherwise.
        """
    
        if self.corner_atoms:
            return self.corner_atoms[0].molecule
        return None

    def xform(self):
        """xform()

        Output:
            xform/None

        Return the transform of molecule model if it exists.
        Return None otherwise.
        """
        
        m = self.model()
        if m == None:
            return None

        xf = m.openState.xform
        return xf

    def display_box(self, show):
        """display_box(show)

        Display box if show = 1.
        """

        m = self.model()
        if m:
            m.display = show

    def box_shown(self):
        """box_shown()

        Output:
            True/False
            
        Return True if molecule model exists and is displayed.
        """

        m = self.model()
        return m != None and m.display

    def delete_box(self):
        """delete_box()

        Delete box by closing molecule model.
        """

        if self.corner_atoms:
            m = self.model()
            chimera.openModels.close([m])
            self.corner_atoms = None

    # ---------------------------------------------------------------------
    # Modify box functions    
    # ---------------------------------------------------------------------

    #VU 1.2179
    # def reshape_box(self, box, xform):
    #     """reshape_box(box, xform)
    def reshape_box(self, box, box_transform, xform = None):
        """reshape_box(box, box_transform, xform=None)

        Reshape the box. If the molecule does not exist, create it.
        Apply input transform to molecule. Get current coordinates
        from input box, and apply them to the atoms of the molecule.
        """

        if self.corner_atoms == None:
            self.corner_atoms = self.create_box()

        # Make sure box transform is same as volume model
        # VU 1.2179
        if xform:
            m = self.model()
            m.openState.xform = xform
        # m = self.model()
        # m.openState.xform = xform

        corners = transform_box_corners(box, box_transform)
        #VU 1.2179
        # corner_xyz = []
        # for i0,i1,i2 in ((0,0,0), (0,0,1), (0,1,0), (0,1,1),
        #                  (1,0,0), (1,0,1), (1,1,0), (1,1,1)):
        #     xyz = (box[i0][0], box[i1][1], box[i2][2])
        #     corner_xyz.append(xyz)

        c = chimera.Coord()
        for k in range(8):
            #VU 1.2179
            c.x, c.y, c.z = corners[k]
            # c.x, c.y, c.z = corner_xyz[k]
            self.corner_atoms[k].setCoord(c)

        self.display_box(1)

        #VU 1.2179
        self.box = box
        self.box_transform = box_transform

    def move_box(self, delta_xyz):
        """move_box(delta_xyz)

        Move box by transformed displacement of delta_xyz.
        """

        xf = self.xform()
        #VU 1.2179
        # if xf == None:
        if xf == None or self.box == None:
            return

        tf = eye_to_box_transform(self.box_transform, xf)
        from PDBmatrices.matrices import apply_matrix_without_translation
        shift = apply_matrix_without_translation(tf, delta_xyz)
        box = translate_box(self.box, shift)
        self.reshape_box(box, self.box_transform)

        #VU 1.2179
        # # Applying xform to Vector not available from Python.
        #
        # # So set xform translation to zero and apply the delta_xyz 
        # # displacement to Point, and get transformed displacement.
        # axis, angle = xf.getRotation()
        # rot = chimera.Xform_rotation(axis, -angle)
        # dp = apply(chimera.Point, delta_xyz)
        # delta_model = rot.apply(dp)
        # 
        # # dx, dy, dz = delta_xyz
        # for a in self.corner_atoms:
        #     c = a.coord()
        #     (c.x, c.y, c.z) = (c.x + delta_model.x,
        #                        c.y + delta_model.y,
        #                        c.z + delta_model.z)
        #     a.setCoord(c)

    #VU 1.2179
    # def move_face(self, axis, side, delta):
    #     """move_face(axis, side, delta)
    #     Move face atoms of face (axis, side) by delta amount.
    #     """
    def move_face(self, axis, side, delta_eye):
        """move_face(axis, side, delta_eye)

        Move face atoms of face (axis, side) by delta_eye amount.
        delta_eye is in eye distance units.
        """

        # figure out delta in box coordinates
        axis_vector = [0,0,0]
        axis_vector[axis] = 1
        from PDBmatrices.matrices import apply_matrix_without_translation
        scale = length(apply_matrix_without_translation(self.box_transform,
                                                        axis_vector))
        delta_box = delta_eye / scale

        box = map(list, self.box)
        box[side][axis] += delta_box
        self.reshape_box(box, self.box_transform)
        
        #VU 1.2179
        # atoms = self.face_atoms(axis, side)
        # for a in atoms:
        #     c = a.coord()
        #     xyz = [c.x, c.y, c.z]
        #     xyz[axis] += delta
        #     c.x, c.y, c.z = xyz
        #     a.setCoord(c)
          
    # ---------------------------------------------------------------------
    # Box properties functions    
    # ---------------------------------------------------------------------

    #VU 1.2179 (not used)
    # def face_atoms(self, axis, side):
    #     """face_atoms(axis, side)
    #
    #    Input:
    #        axis    0 or 1 or 2 (x or y or z)
    #        side    0 or 1 (-ve or +ve)
    #        
    #    Output:
    #        atoms/None
    #        
    #    Return corner atoms describing the face (axis, side).
    #    Return None if no corner atoms.
    #    """
    #
    #    if self.corner_atoms == None:
    #        return None
    # 
    #    corner_indices = ((0,0,0), (0,0,1), (0,1,0), (0,1,1),
    #                      (1,0,0), (1,0,1), (1,1,0), (1,1,1))
    #    atoms = []
    #    for k in range(8):
    #        if corner_indices[k][axis] == side:
    #            atoms.append(self.corner_atoms[k])
    #
    #    return atoms

    def view_distance(self):
        """view_distances() - return view distance

        Output
            d       view distance
        """

        xf = self.xform()
        if xf == None or self.box == None:
            d = near_clip_plane_distance()
        else:
            tf = box_to_eye_transform(self.box_transform, xf)
            from PDBmatrices import matrices
            center = matrices.apply_matrix(tf, box_center(self.box))
            z_box = center[2]
            eye_number = 0
            z_eye = chimera.viewer.camera.eyePos(eye_number)[2]
            z_range = z_eye - z_box
            d = max(z_range, near_clip_plane_distance())
        
        #VU 1.2179
        # xyz_min, xyz_max = self.box_bounds()
        # if xyz_min == None or xyz_max == None:
        #     d = near_clip_plane_distance()
        # else:
        #     cx, cy, cz = map(lambda a, b: .5*(a + b), xyz_min, xyz_max)
        #     c = chimera.Point(cx, cy, cz)
        #     center = self.xform().apply(c)
        #     
        #     z_box = center.z
        #     eye_number = 0
        #     z_eye = chimera.viewer.camera.eyePos(eye_number)[2]
        #     z_range = z_eye - z_box
        #     d = max(z_range, near_clip_plane_distance())
            
        return d

    def face_normal(self, axis, side):
        """face_normal(axis, side)

        Input:
            axis    0 or 1 or 2 (x or y or z)
            side    0 or 1 (-ve or +ve)
            
        Output:
            normal  tuple
            
        Return face normal of face (axis, side) in Chimera coordinates.
        Normal is specified as a tuple (x,y,z).
        """

        xf = self.xform()
        if xf == None:
            return None

        #VU 1.2179
        xform = xf
        
        from PDBmatrices import matrices
        inv_s = matrices.invert_matrix(self.box_transform)
        n = inv_s[axis,:3]
        if side == 0:
            n = -n
        model_transform = matrices.xform_matrix(xform)
        ne = matrices.apply_matrix_without_translation(model_transform, n)
        ne = normalize_vector(ne)

        return ne
        
        #VU 1.2179
        # n = [0,0,0]
        # if side:
        #     n[axis] = 1
        # else:
        #     n[axis] = -1
        # np = apply(chimera.Point, n)
        # 
        # axis, angle = xf.getRotation()
        # rot = chimera.Xform_rotation(axis, angle)
        # normal = rot.apply(np)
        # 
        # return (normal.x, normal.y, normal.z)

    def pierced_faces(self, screen_x, screen_y):
        """pierced_faces(screen_x, screen_y)

        Output:
            faces       list of faces with each face having
                        axis (0 or 1 or 2 for x or y or z)
                        and side (0 or 1 for -ve or +ve)

        Return faces pierced. Empty list if none.
        """

        xf = self.xform()
        if xf == None or self.box == None:
            return []

        transform = box_to_eye_transform(self.box_transform, xf)

        from VolumeViewer import slice
        ijk_in, ijk_out = slice.box_intercepts(screen_x, screen_y,
                                               transform, self.box)

        faces = []

        if ijk_in:
            faces.append(self.closest_face(ijk_in,  self.box))
        if ijk_out:
            faces.append(self.closest_face(ijk_out, self.box))

        #VU 1.2179            
        # faces = []
        # 
        # xf = self.xform()
        # if xf == None:
        #    return faces
        #
        # xyz_region = self.box_bounds()
        # from VolumeViewer import slice
        # xyz_in, xyz_out = slice.box_intercepts(screen_x, screen_y,
        #                                        xf, xyz_region)
        # 
        # if xyz_in:
        #     faces.append(self.closest_face(xyz_in, xyz_region))
        # if xyz_out:
        #     faces.append(self.closest_face(xyz_out, xyz_region))

        return faces

    # ---------------------------------------------------------------------
    # Get face of box that is closest to ijk
    #
    #VU 1.2179
    #
    # def closest_face(self, xyz, xyz_region):
    #     """closest_face(xyz, xyz_region)
    #
    #    Input:
    #         xyz         location
    #        xyz_region  box
    #        
    #    Output:
    #        face        closest face having
    #                    axis (0 or 1 or 2 for x or y or z)
    #                    and side (0 or 1 for -ve or +ve)
    #
    #    Return closest face of xyz_region that is closest to xyz.
    #    Closest face is specified as a tuple (axis, side).
    #    """
    def closest_face(self, ijk, box):
        """closest_face(ijk, box)

        Input:
            ijk         location
            box         box
            
        Output:
            face        closest face having
                        axis (0 or 1 or 2 for x or y or z)
                        and side (0 or 1 for -ve or +ve)

        Return closest face of box that is closest to ijk.
        Closest face is specified as a tuple (axis, side).
        """

        closest_dist = None
        for axis in range(3):
            for side in range(2):
                #VU 1.2179
                # d = abs(xyz[axis] - xyz_region[side][axis])
                d = abs(ijk[axis] - box[side][axis])
                if closest_dist == None or d < closest_dist:
                    closest_dist = d
                    closest = (axis, side)
        return closest

    def model_closed_cb(self, model):
        """model_closed_cb(model) - callback for model close
        
        When molecule is closed, remove cuboid region and atoms.
        """

        self.corner_atoms = None
        #VU 1.2179
        self.box = None
        self.box_transform = None

# -------------------------------------------------------------------------
# circle region selector
# -------------------------------------------------------------------------

class Select_Circle:
    """Class: Select_Circle(segment_dialog)

    Creates a circle region selector for use in simple segmentation.
    """

    def __init__(self, seg_dialog):
        """__init__(seg_dialog) - initialize and add mouse callbacks.

        Creates a circle region selector for use in simple
        segmentation.
        """

        #VU Circle Mask
        self.circle_model = Circle_Model()
        self.seg_dialog = seg_dialog
        #VU 1.2179
        # self.xyz_in = None
        # self.xyz_out = None
        self.ijk_in = None
        self.ijk_out = None
        self.mode_name = 'seg circle region'
        self.bound_button = None
        self.drag_button = None

        callbacks = (self.mouse_down_cb, self.mouse_drag_cb,
                     self.mouse_up_cb)

        icon_file = None

        from chimera import mousemodes
        mousemodes.addFunction(self.mode_name, callbacks, icon_file)

    def data_region(self):
        """data_region()

        Output:
            data_region

        Return data region in focus in the segment dialog.
        """

        # @ should this be from simple seg dialog?
        return self.seg_dialog.data_panel.focus_region

    # ---------------------------------------------------------------------
    # Mouse buttons
    # ---------------------------------------------------------------------

    def bind_mouse_button(self, button, modifiers):
        """bind_mouse_button(button, modifiers)

        """

        # first unbind and then bind
        self.unbind_mouse_button()
        
        from chimera import mousemodes
        mousemodes.setButtonFunction(button, modifiers, self.mode_name)

        self.bound_button = (button, modifiers)

    def unbind_mouse_button(self):
        """unbind_mouse_button()

        """

        if self.bound_button:
            button, modifiers = self.bound_button
            from chimera import mousemodes
            def_mode = mousemodes.getDefault(button, modifiers)
            if def_mode:
                mousemodes.setButtonFunction(button, modifiers, def_mode)
            self.bound_button = None

    def mouse_down_cb(self, viewer, event):
        """mouse_down_cb(viewer, event)

        On mouse press: Move circle, or move face, or create circle.
        """

        self.drag_occured = 0

        if self.circle_model.circle_shown():
            # circle shown, so move circle or move face
            cm = self.circle_model
            faces = cm.pierced_faces(event.x, event.y)
            if len(faces) == 0:
                self.drag_mode = 'move circle'
            else:
                self.drag_mode = 'move face'
                shift_mask = 1
                shift = (event.state & shift_mask)
                if shift and len(faces) >= 2:
                    face = faces[1]
                else:
                    face = faces[0]
                self.drag_face = face
                nx, ny, nz = apply(cm.face_normal, (face[0], 1))
                if abs(nx) > abs(ny):
                    self.face_direction = (sign(nx),0)
                else:
                    self.face_direction = (0, sign(ny))
            self.last_xy = (event.x, event.y)
        else:
            # circle not shown, so delete any hidden circle, create new circle
            self.circle_model.delete_circle()
            self.drag_mode = 'create'
            #VU 1.2179
            # self.xyz_in = None   
            # self.xyz_out = None  
            self.ijk_in = None     
            self.ijk_out = None    
            self.sweep_out_circle(event.x, event.y)

    def mouse_drag_cb(self, viewer, event):
        """mouse_drag_cb(viewer, event)

        On mouse drag: Move circle, move face, or create circle.
        """

        self.drag_occured = 1

        # move circle or move face or create circle
        if self.drag_mode == 'move circle':
            shift_mask = 1
            shift = (event.state & shift_mask)
            self.move_circle(event.x, event.y, shift)
        elif self.drag_mode == 'move face':
            self.move_face(event.x, event.y)
        elif self.drag_mode == 'create':
            self.sweep_out_circle(event.x, event.y)

    def mouse_up_cb(self, viewer, event):
        """mouse_up_cb(viewer, event)

        On mouse raise: If no drag occured, and if circle created
        and shown, return, and if circle not created or circle not
        shown, then toggle circle. If drag occured, pass circle
        boundary to segment dialog.
        """

        if not self.drag_occured:
            if self.drag_mode == 'create' and self.circle_model.circle_shown():
                return
            self.toggle_circle()
          
        if self.drag_occured:
            d = self.seg_dialog
            #VU 1.2179
            ijk_in, ijk_out = self.circle_model.circle
            d.selection_to_parameters_cb(ijk_in, ijk_out, ijk=1)
            # xyz_in, xyz_out = self.circle_model.circle_bounds()
            # d.selection_to_parameters_cb(xyz_in,xyz_out)
                                                
    # ---------------------------------------------------------------------
    # Circle related functions VU Circle Mask
    # ---------------------------------------------------------------------

    def toggle_circle(self):
        """toggle_circle()

        If circle model shown, then delete it. If not shown, and if no
        focus region in segment dialog, then quit. If not shown, and
        if focus region found, then get its transform and apply to
        circle after creating circle.
        """

        cm = self.circle_model
        if cm.circle_shown():
            cm.delete_circle()
        else:
            box, transform, xform = \
                 box_transform_and_xform(self.data_region())
            if box and xform:
                cm.reshape_circle(box, transform, xform)
            #VU 1.2179
            # # @ which data region is this??? should we do nothing???
            # data_region = self.data_region()
            # if data_region == None:
            #    return
            # #VU 1.2129
            # # xform = data_region.transform()
            # import SegmentMenu
            # from SegmentMenu import datamenuseg
            # xform = datamenuseg.get_data_region_xform(data_region)
            # if xform == None:
            #    return
            # #VU 1.2129
            # # box = data_region.xyz_region()
            # import SegmentMenu
            # from SegmentMenu import datamenuseg
            # box = datamenuseg.get_data_region_bounds(data_region)
            # cm.reshape_circle(box, xform)

    def sweep_out_circle(self, pointer_x, pointer_y):
        """sweep_out_circle(pointer_x, pointer_y)

        Create circle if data region found and it has been transformed.
        """

        box, tf, xform = box_transform_and_xform(self.data_region())
        if box == None:
            return

        transform = box_to_eye_transform(tf, xform)

        from VolumeViewer import slice
        ijk_in, ijk_out = slice.box_intercepts(pointer_x, pointer_y,
                                               transform, box)
        if ijk_in == None or ijk_out == None:
          return
        
        if self.ijk_in == None:
            self.ijk_in = ijk_in
        if self.ijk_out == None:
            self.ijk_out = ijk_out
          
        drag_circle = bounding_box((ijk_in, ijk_out,
                                    self.ijk_in, self.ijk_out))
        self.circle_model.reshape_circle(drag_circle, tf, xform)

        #VU 1.2179
        # data_region = self.data_region()
        # if data_region == None:
        #    return
        # 
        # #VU 1.2129
        # # xform = data_region.transform()
        # import SegmentMenu
        # from SegmentMenu import datamenuseg
        # xform = datamenuseg.get_data_region_xform(data_region)
        # if xform == None:
        #    return
        #
        # #VU 1.2129
        # # bounds = data_region.xyz_region()
        # import SegmentMenu
        # from SegmentMenu import datamenuseg
        # bounds = datamenuseg.get_data_region_bounds(data_region)
        # 
        # from VolumeViewer import slice
        # xyz_in, xyz_out = slice.box_intercepts(pointer_x, pointer_y,
        #                                       xform, bounds)
        #
        # if xyz_in == None or xyz_out == None:
        #     return
        # 
        # if self.xyz_in == None:
        #    self.xyz_in = xyz_in
        # if self.xyz_out == None:
        #    self.xyz_out = xyz_out
        # 
        # box = bounding_box((xyz_in, xyz_out, self.xyz_in, self.xyz_out))
        # self.circle_model.reshape_circle(box, xform)

    def move_circle(self, pointer_x, pointer_y, shift):
        """move_circle(pointer_x, pointer_y, shift)

        Move circle by pointer_x, pointer_y. If shift = 1, move in z
        direction (view direction).
        """

        last_x, last_y = self.last_xy
        dx = pointer_x - last_x
        dy = pointer_y - last_y
        self.last_xy = (pointer_x, pointer_y)

        cm = self.circle_model
        d = cm.view_distance()
        psize = pixel_size(d)
    
        if shift:
            if abs(dx) > abs(dy):     dz = dx
            else:                     dz = dy
            delta_xyz = (0, 0, dz * psize)
        else:
            delta_xyz = (dx * psize, -dy * psize, 0)
    
        cm.move_circle(delta_xyz)

    def move_face(self, pointer_x, pointer_y):
        """move_face(pointer_x, pointer_y)

        Move face by pointer_x, pointer_y, from last_xy
        """

        last_x, last_y = self.last_xy
        dx = pointer_x - last_x
        dy = pointer_y - last_y
        self.last_xy = (pointer_x, pointer_y)

        cm = self.circle_model
        d = cm.view_distance()
        psize = pixel_size(d)
        fd = self.face_direction
        dist = (dx * fd[0] + -dy * fd[1]) * psize

        axis, side = self.drag_face
        cm.move_face(axis, side, dist)

# -------------------------------------------------------------------------

class Circle_Model:
    """Class: Circle_Model()

    Creates a molecule with 8 corner atoms and bonds between them
    to define a cuboid box model for use in circle region selector,
    given by Class: Select_Circle.
    """

    def __init__(self):
        """__init__() - create a circle model using 8 corner atoms.
        """

        self.corner_atoms = None
        #VU 1.2179
        self.circle = None
        self.circle_transform = None

    def circle_bounds(self):
        """circle_bounds()

        Output:
            xyz_min
            xyz_max
            
        Return bounding box of molecule - corner atoms 0 and 7.
        """

        return self.circle

        #VU 1.2179
        # m = self.model()
        # if m == None or not m.display:
        #    return None, None
        # 
        # c_min = self.corner_atoms[0].coord()
        # xyz_min = c_min.x, c_min.y, c_min.z
        # 
        # c_max = self.corner_atoms[7].coord()
        # xyz_max = c_max.x, c_max.y, c_max.z
        # 
        # return xyz_min, xyz_max

    # ---------------------------------------------------------------------
    # Create/destroy/display circle functions    
    # ---------------------------------------------------------------------

    def create_circle(self):
        """create_circle()

        Output:
            corners      8 corner atoms
            
        Create a molecule with 8 corner atoms to represent a circle model.
        """

        m = chimera.Molecule()
        m.name = 'Subregion Circle'
        chimera.openModels.add([m])
        add_model_closed_callback(m, self.model_closed_cb)

        rid = chimera.MolResId(1)
        r = m.newResidue('markers', rid)

        corners = []
        for name in ('a000', 'a001', 'a010', 'a011',
                     'a100', 'a101', 'a110', 'a111'):
            a = m.newAtom(name, chimera.elements.H)
            r.addAtom(a)
            corners.append(a)

        red = chimera.MaterialColor(1,0,0,1)
        for a1, a2 in ((0,1), (2,3), (4,5), (6,7),
                       (0,2), (1,3), (4,6), (5,7),
                       (0,4), (1,5), (2,6), (3,7)):
            b = m.newBond(corners[a1], corners[a2])
            b.halfbond = 0
            b.drawMode = chimera.Bond.Wire
            b.color = red

        return corners

    def model(self):
        """model()

        Output:
            molecule/None

        Returnn molecule if it exists. Return None otherwise.
        """
    
        if self.corner_atoms:
            return self.corner_atoms[0].molecule
        return None

    def xform(self):
        """xform()

        Output:
            xform/None

        Return the transform of molecule model if it exists.
        Return None otherwise.
        """
        
        m = self.model()
        if m == None:
            return None

        xf = m.openState.xform
        return xf

    def display_circle(self, show):
        """display_circle(show)

        Display circle if show = 1.
        """

        m = self.model()
        if m:
            m.display = show

    def circle_shown(self):
        """circle_shown()

        Output:
            True/False
            
        Return True if molecule model exists and is displayed.
        """

        m = self.model()
        return m != None and m.display

    def delete_circle(self):
        """delete_circle()

        Delete circle by closing molecule model.
        """

        if self.corner_atoms:
            m = self.model()
            chimera.openModels.close([m])
            self.corner_atoms = None

    # ---------------------------------------------------------------------
    # Modify circle functions    
    # ---------------------------------------------------------------------

    #VU 1.2179
    # def reshape_circle(self, box, xform):
    #     """reshape_circle(box, xform)
    def reshape_circle(self, box, box_transform, xform = None):
        """reshape_circle(box, box_transform, xform=None)

        Reshape the circle. If the molecule does not exist, create it.
        Apply input transform to molecule. Get current coordinates
        from input box, and apply them to the atoms of the molecule.
        """

        if self.corner_atoms == None:
            self.corner_atoms = self.create_circle()

        # Make sure circle transform is same as volume model
        # VU 1.2179
        if xform:
            m = self.model()
            m.openState.xform = xform
        # m = self.model()
        # m.openState.xform = xform

        corners = transform_box_corners(box, box_transform)
        #VU 1.2179
        # corner_xyz = []
        # for i0,i1,i2 in ((0,0,0), (0,0,1), (0,1,0), (0,1,1),
        #                  (1,0,0), (1,0,1), (1,1,0), (1,1,1)):
        #     xyz = (box[i0][0], box[i1][1], box[i2][2])
        #     corner_xyz.append(xyz)

        c = chimera.Coord()
        for k in range(8):
            #VU 1.2179
            c.x, c.y, c.z = corners[k]
            # c.x, c.y, c.z = corner_xyz[k]
            self.corner_atoms[k].setCoord(c)

        self.display_circle(1)

        #VU 1.2179
        self.circle = box
        self.circle_transform = box_transform

    def move_circle(self, delta_xyz):
        """move_circle(delta_xyz)

        Move circle by transformed displacement of delta_xyz.
        """

        xf = self.xform()
        #VU 1.2179
        # if xf == None:
        if xf == None or self.circle == None:
            return

        tf = eye_to_box_transform(self.circle_transform, xf)
        from PDBmatrices.matrices import apply_matrix_without_translation
        shift = apply_matrix_without_translation(tf, delta_xyz)
        box = translate_box(self.circle, shift)
        self.reshape_circle(box, self.circle_transform)

        #VU 1.2179
        # # Applying xform to Vector not available from Python.
        #
        # # So set xform translation to zero and apply the delta_xyz 
        # # displacement to Point, and get transformed displacement.
        # axis, angle = xf.getRotation()
        # rot = chimera.Xform_rotation(axis, -angle)
        # dp = apply(chimera.Point, delta_xyz)
        # delta_model = rot.apply(dp)
        # 
        # # dx, dy, dz = delta_xyz
        # for a in self.corner_atoms:
        #     c = a.coord()
        #     (c.x, c.y, c.z) = (c.x + delta_model.x,
        #                        c.y + delta_model.y,
        #                        c.z + delta_model.z)
        #     a.setCoord(c)

    #VU 1.2179
    # def move_face(self, axis, side, delta):
    #     """move_face(axis, side, delta)
    #     Move face atoms of face (axis, side) by delta amount.
    #     """
    def move_face(self, axis, side, delta_eye):
        """move_face(axis, side, delta_eye)

        Move face atoms of face (axis, side) by delta_eye amount.
        delta_eye is in eye distance units.
        """

        # figure out delta in box coordinates
        axis_vector = [0,0,0]
        axis_vector[axis] = 1
        from PDBmatrices.matrices import apply_matrix_without_translation
        scale = length(apply_matrix_without_translation(self.circle_transform,
                                                        axis_vector))
        delta_box = delta_eye / scale

        box = map(list, self.circle)
        box[side][axis] += delta_box
        self.reshape_circle(box, self.circle_transform)
        
        #VU 1.2179
        # atoms = self.face_atoms(axis, side)
        # for a in atoms:
        #     c = a.coord()
        #     xyz = [c.x, c.y, c.z]
        #     xyz[axis] += delta
        #     c.x, c.y, c.z = xyz
        #     a.setCoord(c)

    # ---------------------------------------------------------------------
    # Circle properties functions    
    # ---------------------------------------------------------------------

    #VU 1.2179 (not used)
    # def face_atoms(self, axis, side):
    #     """face_atoms(axis, side)
    #
    #    Input:
    #        axis    0 or 1 or 2 (x or y or z)
    #        side    0 or 1 (-ve or +ve)
    #        
    #    Output:
    #        atoms/None
    #        
    #    Return corner atoms describing the face (axis, side).
    #    Return None if no corner atoms.
    #    """
    #
    #    if self.corner_atoms == None:
    #        return None
    # 
    #    corner_indices = ((0,0,0), (0,0,1), (0,1,0), (0,1,1),
    #                      (1,0,0), (1,0,1), (1,1,0), (1,1,1))
    #    atoms = []
    #    for k in range(8):
    #        if corner_indices[k][axis] == side:
    #            atoms.append(self.corner_atoms[k])
    #
    #    return atoms

    def view_distance(self):
        """view_distances() - return view distance

        Output
            d       view distance
        """

        xf = self.xform()
        if xf == None or self.circle == None:
            d = near_clip_plane_distance()
        else:
            tf = box_to_eye_transform(self.circle_transform, xf)
            from PDBmatrices import matrices
            center = matrices.apply_matrix(tf, box_center(self.circle))
            z_box = center[2]
            eye_number = 0
            z_eye = chimera.viewer.camera.eyePos(eye_number)[2]
            z_range = z_eye - z_box
            d = max(z_range, near_clip_plane_distance())
        
        #VU 1.2179
        # xyz_min, xyz_max = self.box_bounds()
        # if xyz_min == None or xyz_max == None:
        #     d = near_clip_plane_distance()
        # else:
        #     cx, cy, cz = map(lambda a, b: .5*(a + b), xyz_min, xyz_max)
        #     c = chimera.Point(cx, cy, cz)
        #     center = self.xform().apply(c)
        #     
        #     z_box = center.z
        #     eye_number = 0
        #     z_eye = chimera.viewer.camera.eyePos(eye_number)[2]
        #     z_range = z_eye - z_box
        #     d = max(z_range, near_clip_plane_distance())
            
        return d

    def face_normal(self, axis, side):
        """face_normal(axis, side)

        Input:
            axis    0 or 1 or 2 (x or y or z)
            side    0 or 1 (-ve or +ve)
            
        Output:
            normal  tuple
            
        Return face normal of face (axis, side) in Chimera coordinates.
        Normal is specified as a tuple (x,y,z).
        """

        xf = self.xform()
        if xf == None:
            return None

        #VU 1.2179
        xform = xf
        
        from PDBmatrices import matrices
        inv_s = matrices.invert_matrix(self.circle_transform)
        n = inv_s[axis,:3]
        if side == 0:
            n = -n
        model_transform = matrices.xform_matrix(xform)
        ne = matrices.apply_matrix_without_translation(model_transform, n)
        ne = normalize_vector(ne)

        return ne
        
        #VU 1.2179
        # n = [0,0,0]
        # if side:
        #     n[axis] = 1
        # else:
        #     n[axis] = -1
        # np = apply(chimera.Point, n)
        # 
        # axis, angle = xf.getRotation()
        # rot = chimera.Xform_rotation(axis, angle)
        # normal = rot.apply(np)
        # 
        # return (normal.x, normal.y, normal.z)

    def pierced_faces(self, screen_x, screen_y):
        """pierced_faces(screen_x, screen_y)

        Output:
            faces       list of faces with each face having
                        axis (0 or 1 or 2 for x or y or z)
                        and side (0 or 1 for -ve or +ve)

        Return faces pierced. Empty list if none.
        """

        xf = self.xform()
        if xf == None or self.circle == None:
            return []

        transform = box_to_eye_transform(self.circle_transform, xf)

        from VolumeViewer import slice
        ijk_in, ijk_out = slice.box_intercepts(screen_x, screen_y,
                                               transform, self.circle)

        faces = []

        if ijk_in:
            faces.append(self.closest_face(ijk_in,  self.circle))
        if ijk_out:
            faces.append(self.closest_face(ijk_out, self.circle))

        #VU 1.2179            
        # faces = []
        # 
        # xf = self.xform()
        # if xf == None:
        #    return faces
        #
        # xyz_region = self.box_bounds()
        # from VolumeViewer import slice
        # xyz_in, xyz_out = slice.box_intercepts(screen_x, screen_y,
        #                                        xf, xyz_region)
        # 
        # if xyz_in:
        #     faces.append(self.closest_face(xyz_in, xyz_region))
        # if xyz_out:
        #     faces.append(self.closest_face(xyz_out, xyz_region))

        return faces

    # ---------------------------------------------------------------------
    # Get face of box that is closest to ijk
    #
    #VU 1.2179
    #
    # def closest_face(self, xyz, xyz_region):
    #     """closest_face(xyz, xyz_region)
    #
    #    Input:
    #         xyz         location
    #        xyz_region  box
    #        
    #    Output:
    #        face        closest face having
    #                    axis (0 or 1 or 2 for x or y or z)
    #                    and side (0 or 1 for -ve or +ve)
    #
    #    Return closest face of xyz_region that is closest to xyz.
    #    Closest face is specified as a tuple (axis, side).
    #    """
    def closest_face(self, ijk, box):
        """closest_face(ijk, box)

        Input:
            ijk         location
            box         box
            
        Output:
            face        closest face having
                        axis (0 or 1 or 2 for x or y or z)
                        and side (0 or 1 for -ve or +ve)

        Return closest face of box that is closest to ijk.
        Closest face is specified as a tuple (axis, side).
        """

        closest_dist = None
        for axis in range(3):
            for side in range(2):
                #VU 1.2179
                # d = abs(xyz[axis] - xyz_region[side][axis])
                d = abs(ijk[axis] - box[side][axis])
                if closest_dist == None or d < closest_dist:
                    closest_dist = d
                    closest = (axis, side)
        return closest

    def model_closed_cb(self, model):
        """model_closed_cb(model) - callback for model close
        
        When molecule is closed, remove cuboid region and atoms.
        """

        self.corner_atoms = None
        #VU 1.2179
        self.circle = None
        self.circle_transform = None

# -------------------------------------------------------------------------
# General functions VU 1.2179
# -------------------------------------------------------------------------

def transform_box_corners(box, transform):
    """def transform_box_corners(box, transform)
    """

    corners = box_corners(box)
    from PDBmatrices.matrices import apply_matrix
    tcorners = map(lambda p: apply_matrix(transform, p), corners)
    return tcorners

def translate_box(box, offset):
    """translate_box(box, offset)
    """

    box_min, box_max = box
    shifted_box = (map(lambda a,b: a+b, box_min, offset),
                   map(lambda a,b: a+b, box_max, offset))
    return shifted_box

def box_center(box):
    """box_center(box)
    """

    ijk_min, ijk_max = box
    c = map(lambda a,b: .5*(a+b), ijk_min, ijk_max)
    return c

def box_corners(box):
    """box_corners(box)
    """
  
    corners = []
    for i0,i1,i2 in ((0,0,0), (0,0,1), (0,1,0), (0,1,1),
                     (1,0,0), (1,0,1), (1,1,0), (1,1,1)):
        c = (box[i0][0], box[i1][1], box[i2][2])
        corners.append(c)
    return corners

# -------------------------------------------------------------------------
# General functions
# -------------------------------------------------------------------------

def bounding_box(points):
    """bounding_box(points)

    Input:
        points      list of points - each a list of coordinates
        
    Output:
        xyz_min
        xyz_max
        
    Return bounding box (xyz_min, xyz_max) for a flat-faced polygon
    described by input points, with each point given by a 3 element
    list of [x,y,z] coordinates.
    """

    xyz_min = [None, None, None]
    xyz_max = [None, None, None]
    for p in points:
        for a in range(3):
            if xyz_min[a] == None or p[a] < xyz_min[a]:
                xyz_min[a] = p[a]
            if xyz_max[a] == None or p[a] > xyz_max[a]:
                xyz_max[a] = p[a]

    return xyz_min, xyz_max

def near_clip_plane_distance():
    """near_clip_plane_distance()

    Output:
        znear       distance
        
    Return distance of near clip plane.
    """

    c = chimera.viewer.camera
    eye_number = 0
    left, right, bottom, top, znear, zfar, f = c.window(eye_number)
    return znear

def pixel_size(view_distance):
    """pixel_size(view_distance)

    Output
        psize       pixel size
        
    Return pixel size corresponding to view distance.
    """

    c = chimera.viewer.camera
    eye_number = 0
    llx, lly, width, height = c.viewport(eye_number)
    left, right, bottom, top, znear, zfar, f = c.window(eye_number)

    psize = float(right - left) / width
    if not c.ortho:
        zratio = view_distance / znear
        psize = psize * zratio

    return psize

def add_model_closed_callback(model, callback):
    """add_model_closed_callback(model, callback)

    """

    def cb(trigger_name, args, closed_models):
        model, callback, trigger = args
        if model in closed_models:
            callback(model)
            chimera.openModels.deleteRemoveHandler(trigger)
            args[2] = None    # Break circular link to trigger

    args = [model, callback, None]
    trigger = chimera.openModels.addRemoveHandler(cb, args)
    args[2] = trigger

def sign(x):
    """sign(x) - return 1 if non-negative, else return -1.
    """

    if x >= 0:
        return 1
    return -1

# -------------------------------------------------------------------------
# General functions VU 1.2179
# -------------------------------------------------------------------------

def normalize_vector(v):
    """normalize_vector(v)
    """

    d = length(v)
    return (v[0]/d, v[1]/d, v[2]/d)
  
def length(v):
    """length(v)
    """

    import math
    d = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    return d

# -------------------------------------------------------------------------
