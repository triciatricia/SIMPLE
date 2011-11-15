# -----------------------------------------------------------------------------
# Create constant intensity surface or mesh model from 3D data in a
# Numeric Python array.
#
import chimera

# -----------------------------------------------------------------------------
# Create and display isosurfaces and meshes for multi-component volume data.
#
# Argument align can be a model to align with or a transform matrix.
#
class Multi_Surface:

  def __init__(self, name, align = None, message_cb = None):

    self.name = name
    self.align = align
    if isinstance(self.align, chimera.Model):
      add_model_closed_callback(self.align, self.attached_model_closed_cb)

    self.message_cb = message_cb

    self.outline_box = None
    self.surfaces = []
    self.smodel = None
    
  # ---------------------------------------------------------------------------
  # Replaces existing surfaces.
  #
  def show_surfaces(self, surfaces, outline_box_rgb):
 
    if self.model() == None:
      self.create_model()

    m = self.model()
    m.display = 1

    xyz_region = self.bounding_box(surfaces)
    show_outline_box = (outline_box_rgb and xyz_region)
    if self.outline_box == None:
      self.outline_box = Outline_Box(m)
    self.outline_box.show(show_outline_box, xyz_region, outline_box_rgb)

    slist = []
    for s in surfaces:
      ms = self.matching_surface(s)
      if ms:
        ms.set_color(s.rgba)
        ms.set_display_style(s.show_mesh, s.mesh_lighting,
                             s.two_sided_lighting, s.flip_normals,
                             s.line_thickness, s.smooth_lines,
                             s.dim_transparency)
        slist.append(ms)
        self.surfaces.remove(ms)
      else:
        s.show(m, self.message_cb)
        slist.append(s)

    for s in self.surfaces:
      s.erase_surface()

    self.surfaces = slist
    
  # ---------------------------------------------------------------------------
  # Find a surface matching except for color.
  #
  def matching_surface(self, s):

    for ms in self.surfaces:
      if (ms.level == s.level and
          id(ms.matrix) == id(s.matrix) and
          ms.name == s.name and
          ms.xyz_origin == s.xyz_origin and
          ms.xyz_step == s.xyz_step and
          ms.same_smoothing(s) and
          ms.same_subdivision(s)):
        return ms

    return None
  
  # ---------------------------------------------------------------------------
  #
  def create_model(self):

    import _surface
    m = _surface.Surface_Model()
    m.name = self.name
    self.smodel = m

    attached_model = None
    if isinstance(self.align, chimera.Model):
      attached_model = self.align

    chimera.openModels.add([m], sameAs = attached_model, skipViewAll = 1)
    add_model_closed_callback(m, self.model_closed_cb)

    if isinstance(self.align, chimera.Xform):
      m.openState.xform = self.align
  
  # ---------------------------------------------------------------------------
  #
  def bounding_box(self, components):

    xyz_region = None
    for c in components:
      c_region = c.bounding_box()
      if xyz_region == None:
        xyz_region = c_region
      else:
        xyz_region = (map(lambda a,b: min(a,b), xyz_region[0], c_region[0]),
                      map(lambda a,b: max(a,b), xyz_region[1], c_region[1]))
    return xyz_region
  
  # ---------------------------------------------------------------------------
  #
  def model(self):

    return self.smodel
      
  # ---------------------------------------------------------------------------
  #
  def close_model(self):

    m = self.model()
    if m:
      chimera.openModels.close([m])
      
  # ---------------------------------------------------------------------------
  #
  def model_closed_cb(self, model):

    self.smodel = None
    self.surfaces = []
    self.outline_box = None
      
  # ---------------------------------------------------------------------------
  #
  def attached_model_closed_cb(self, model):

    self.align = None
  
# -----------------------------------------------------------------------------
#
class Surface:

  def __init__(self, name, matrix, xyz_origin, xyz_step,
               level, rgba, show_mesh, mesh_lighting,
               two_sided_lighting, flip_normals,
               line_thickness, smooth_lines, dim_transparency,
               subdivide_surface, subdivision_levels,
               surface_smoothing, smoothing_factor, smoothing_iterations):

    self.name = name
    self.matrix = matrix
    self.xyz_origin = xyz_origin
    self.xyz_step = xyz_step
    self.level = level
    self.rgba = rgba
    self.show_mesh = show_mesh
    self.mesh_lighting = mesh_lighting
    self.two_sided_lighting = two_sided_lighting
    self.flip_normals = flip_normals
    self.line_thickness = line_thickness
    self.smooth_lines = smooth_lines
    self.dim_transparency = dim_transparency
    self.subdivide_surface = subdivide_surface
    self.subdivision_levels = subdivision_levels
    self.surface_smoothing = surface_smoothing
    self.smoothing_factor = smoothing_factor
    self.smoothing_iterations = smoothing_iterations

    self.model = None
    self.group = None
      
  # ---------------------------------------------------------------------------
  #
  def show(self, model, message_cb):

    self.erase_surface()

    if self.rgba == None:
      return

    import _contour
    c = _contour.Contour(self.matrix)

    if message_cb:
      message = message_cb
    else:
      message = lambda msg: 0

    message('Computing %s surface' % self.name)
    varray, tarray = c.surface(self.level)
    if self.subdivide_surface:
      import _surface
      for level in range(self.subdivision_levels):
        varray, tarray = _surface.subdivide_triangles(varray, tarray)
    if self.surface_smoothing:
      import _surface
      _surface.smooth_vertex_positions(varray, tarray,
                                       self.smoothing_factor,
                                       self.smoothing_iterations)
    _contour.shift_and_scale_vertices(varray, self.xyz_origin, self.xyz_step)
    message('Making %s surface with %d triangles' %
	    (self.name, len(tarray)))
    group = model.add_group(varray, tarray, self.rgba)
    self.group = group
    self.model = model
    self.set_display_style(self.show_mesh, self.mesh_lighting,
                           self.two_sided_lighting, self.flip_normals,
                           self.line_thickness, self.smooth_lines,
                           self.dim_transparency, only_if_changed = 0)
    if (hasattr(model,"colorizer")) : model.colorizer(self,varray,tarray,self.rgba)
    message('')

  # ---------------------------------------------------------------------------
  #
  def set_color(self, rgba):

    rgba_changed = (rgba != self.rgba)
    if rgba_changed:
      if self.group:
        self.group.set_color(rgba[0], rgba[1], rgba[2], rgba[3])
      self.rgba = rgba
      
  # ---------------------------------------------------------------------------
  #
  def set_display_style(self, show_mesh, mesh_lighting, two_sided_lighting,
                        flip_normals, line_thickness, smooth_lines,
                        dim_transparency, only_if_changed = 1):

    if (only_if_changed and
	show_mesh == self.show_mesh and
	mesh_lighting == self.mesh_lighting and
        two_sided_lighting == self.two_sided_lighting and
        flip_normals == self.flip_normals and
        line_thickness == self.line_thickness and
        smooth_lines == self.smooth_lines and
        dim_transparency == self.dim_transparency):
      return

    if self.model:
      g = self.group
      if show_mesh:
	style = g.Mesh
      else:
	style = g.Solid
      g.set_display_style(style)
      lit = not show_mesh or mesh_lighting
      g.set_use_lighting(lit)
      if flip_normals and self.level < 0:
        g.set_normal_orientation(g.Righthanded)
      else:
        g.set_normal_orientation(g.Lefthanded)
      g.set_two_sided_lighting(two_sided_lighting)
      g.line_thickness = line_thickness
      g.smooth_lines = smooth_lines
      if dim_transparency:
        bmode = g.SRC_ALPHA_DST_1_MINUS_ALPHA
      else:
        bmode = g.SRC_1_DST_1_MINUS_ALPHA
      g.transparency_blend_mode = bmode

    self.show_mesh = show_mesh
    self.mesh_lighting = mesh_lighting
    self.two_sided_lighting = two_sided_lighting
    self.flip_normals = flip_normals
    self.line_thickness = line_thickness
    self.smooth_lines = smooth_lines
    self.dim_transparency = dim_transparency
      
  # ---------------------------------------------------------------------------
  #
  def bounding_box(self):

    xyz_min = map(lambda orig, step: orig - .5*step,
                  self.xyz_origin, self.xyz_step)
    import Numeric
    zsize, ysize, xsize = Numeric.shape(self.matrix)
    grid_size = (xsize, ysize, zsize)
    xyz_max = map(lambda orig, size, step: orig + (size-.5)*step,
                  self.xyz_origin, grid_size, self.xyz_step)
    return (xyz_min, xyz_max)
      
  # ---------------------------------------------------------------------------
  #
  def erase_surface(self):

    if self.model:
      self.model.remove_group(self.group)
      self.model = None
      self.group = None
    
  # ---------------------------------------------------------------------------
  # Check if surface s has same smoothing as this one.
  #
  def same_smoothing(self, s):

    return ((not self.surface_smoothing and not s.surface_smoothing) or
            (self.surface_smoothing and s.surface_smoothing and
             self.smoothing_factor == s.smoothing_factor and
             self.smoothing_iterations == s.smoothing_iterations))
    
  # ---------------------------------------------------------------------------
  # Check if surface s has same smoothing as this one.
  #
  def same_subdivision(self, s):

    return ((not self.subdivide_surface and not s.subdivide_surface) or
            (self.subdivide_surface and s.subdivide_surface and
             self.subdivision_levels == s.subdivision_levels))

# -----------------------------------------------------------------------------
#
class Outline_Box:

  def __init__(self, model):

    self.model = model
    self.group = None
    self.xyz_region = None
    self.rgb = None
    
  # ---------------------------------------------------------------------------
  #
  def show(self, show, xyz_region, rgb):

    if show and xyz_region and rgb:
      changed = (xyz_region != self.xyz_region or rgb != self.rgb)
      if changed:
        self.erase_box()
        self.make_box(xyz_region, rgb)
    else:
      self.erase_box()
      
  # ---------------------------------------------------------------------------
  #
  def make_box(self, xyz_region, rgb):

    (x0, y0, z0), (x1, y1, z1) = xyz_region
    vlist = ((x0,y0,z0), (x0,y0,z1), (x0,y1,z0), (x0,y1,z1),
	     (x1,y0,z0), (x1,y0,z1), (x1,y1,z0), (x1,y1,z1))
    import Numeric
    vlist_f32 = Numeric.array(vlist, Numeric.Float32)
    qlist = ((0,4,5,1), (0,2,6,4), (0,1,3,2), (7,3,1,5), (7,6,2,3), (7,5,4,6))

    rgba = tuple(rgb) + (1,)
    group = self.model.add_group(vlist_f32, qlist, rgba)
    group.set_display_style(group.Mesh)
    group.set_use_lighting(0)

    self.group = group
    self.xyz_region = xyz_region
    self.rgb = rgb

  # ---------------------------------------------------------------------------
  #
  def erase_box(self):

    if self.group != None:
      self.model.remove_group(self.group)
      self.group = None
      self.xyz_region = None
      self.rgb = None
      
# -----------------------------------------------------------------------------
# Invoke a callback when a specified model is closed.
#
def add_model_closed_callback(model, callback):

  def cb(trigger_name, args, closed_models):
    model, callback, trigger = args
    if model in closed_models:
      callback(model)
      chimera.openModels.deleteRemoveHandler(trigger)
      args[2] = None    # Break circular link to trigger

  args = [model, callback, None]
  trigger = chimera.openModels.addRemoveHandler(cb, args)
  args[2] = trigger
