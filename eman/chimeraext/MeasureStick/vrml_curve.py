# -----------------------------------------------------------------------------
# Make a vrml model containing smooth curves through specified points.
#
import math

from CGLutil import vrml

# -----------------------------------------------------------------------------
#
def vrml_header():

  return '#VRML V2.0 utf8\n\n'

# -----------------------------------------------------------------------------
#
def vrml_banded_tube(points, point_colors, segment_colors,
                     radius, segment_subdivisions, band_length):

  import spline
  plist = spline.overhauser_spline_points(points, segment_subdivisions)
  if len(plist) <= 1:
    return ''

  pcolors, scolors = band_colors(plist, point_colors, segment_colors,
                                 segment_subdivisions, band_length)

  
  if radius == 0:
    return vrml_lines(plist, pcolors)

  return vrml_tube(plist, pcolors, scolors, radius)
  
# -----------------------------------------------------------------------------
# Calculate point and segment colors for an interpolated set of points.
# Point colors are extended to interpolated points and segments within
# band_length/2 arc distance.
#
def band_colors(plist, point_colors, segment_colors,
                segment_subdivisions, band_length):
                
  n = len(point_colors)
  pcolors = []
  scolors = []
  for k in range(n-1):
    j = k * (segment_subdivisions + 1)
    import spline
    arcs = spline.arc_lengths(plist[j:j+segment_subdivisions+2])
    bp0, mp, bp1 = band_points(arcs, band_length)
    for p in range(bp0):
      pcolors.append(point_colors[k])
    for p in range(mp):
      pcolors.append(segment_colors[k])
    for p in range(bp1-1):
      pcolors.append(point_colors[k+1])
    for s in range(bp0-1):
      scolors.append(point_colors[k])
    for s in range(mp+1):
      scolors.append(segment_colors[k])
    for s in range(bp1-1):
      scolors.append(point_colors[k+1])
  pcolors.append(point_colors[-1])
  return pcolors, scolors
  
# -----------------------------------------------------------------------------
# Count points within band_length/2 of each end of an arc.
#
def band_points(arcs, band_length):
      
  arc = arcs[-1]
  half_length = min(.5 * band_length, .5 * arc)
  bp0 = mp = bp1 = 0
  for p in range(len(arcs)):
    l0 = arcs[p]
    l1 = arc - arcs[p]
    if l0 <= half_length:
      if l1 <= half_length:
        if l0 <= l1:
          bp0 = bp0 + 1
        else:
          bp1 = bp1 + 1
      else:
        bp0 = bp0 + 1
    elif l1 <= half_length:
      bp1 = bp1 + 1
    else:
      mp = mp + 1

  return bp0, mp, bp1
  
# -----------------------------------------------------------------------------
# Return VRML string drawing a piecewise linear approximation to an
# Overhauser spline.  An Overhauser spline uses cubic segments that
# join at the given points and have continuous tangent vector.
# For the end segments I use a quadratic curve.
#
def vrml_overhauser_spline(points, rgb, radius, segment_subdivisions):

  import spline
  plist = spline.overhauser_spline_points(points, segment_subdivisions)
  if len(plist) <= 1:
    return ''
  
  colors = [rgb] * len(plist)
  
  if radius == 0:
    return vrml_lines(plist, colors)

  return vrml_tube(plist, colors, colors[:-1], radius)

# -----------------------------------------------------------------------------
# Return VRML string to draw a piecewise linear curve.
#
def vrml_lines(points, colors):

  pstring, pistring = vrml_point_indexing(points)
  cstring, cistring = vrml_color_indexing(colors)

  vrml = ('Shape {\n' +
          '\tgeometry IndexedLineSet {\n' +
          '\t\tcoord Coordinate {\n' +
          '\t\t\tpoint %s' % pstring +
          '\t\t}\n' +
          '\t\tcoordIndex %s' % pistring +
          '\t\tcolor Color {\n' +
          '\t\t\tcolor %s' % cstring +
          '\t\t}\n' +
          '\t\tcolorIndex %s' % cistring +
          '\t}\n' +
          '}\n')
  return vrml

# -----------------------------------------------------------------------------
# Return VRML strings for xyz coordinate table and point index list.
#
def vrml_point_indexing(points):

  pstring = '[\n'
  for p in points:
    pstring = pstring + '\t\t\t\t%g %g %g,\n' % tuple(p)
  pstring = pstring + '\t\t\t]\n'

  n = len(points)
  pistring = '[\n'
  for i in range(n):
    pistring = pistring + '\t\t\t%d,\n' % i
  pistring = pistring + '\t\t]\n'

  return pstring, pistring

# -----------------------------------------------------------------------------
# Return VRML strings for color table and color index list.
#
def vrml_color_indexing(colors):

  ctable = {}
  for c in colors:
    ctable[c] = 1

  cstring = '[\n'
  cindex = 0
  for c in ctable.keys():
    cstring = cstring + '\t\t\t\t%g %g %g,\n' % c
    ctable[c] = cindex
    cindex = cindex + 1
  cstring = cstring + '\t\t\t]\n'

  cistring = '[\n'
  for c in colors:
    cistring = cistring + '\t\t\t%d,\n' % ctable[c]
  cistring = cistring + '\t\t]\n'

  return cstring, cistring

# -----------------------------------------------------------------------------
# Return VRML string to that draws a tube.
# Cylinders are drawn between consecutive points with spheres at each point
# to join cylinders at a bend and to cap the ends.
#
def vrml_tube(points, point_colors, segment_colors, radius):

  wrl = vrml.Transform()
  for k in range(len(points)):
    p = points[k]
    translate = vrml.Transform(translation=tuple(p))
    s = vrml.Sphere(radius = radius, color = point_colors[k])
    translate.addChild(s)
    wrl.addChild(translate)
  for k in range(len(points) - 1):
    c = cylinder_node(points[k], points[k+1], radius, segment_colors[k])
    wrl.addChild(c)
  return vrml.vrml(wrl)

# -----------------------------------------------------------------------------
# Return VRML node for a cylinder with axis specified by end points.
#
def cylinder_node(p1, p2, radius, rgb):

  transform = vrml.Transform()
  axis = p2 - p1
  length = math.sqrt(axis[0]*axis[0] + axis[1]*axis[1] + axis[2]*axis[2])
  if length > 0:
    center = .5 * (p1 + p2)
    translate = vrml.Transform(translation=tuple(center))
    transform.addChild(translate)
    rot_axis = (axis[2], 0, -axis[0])
    rot_angle = math.atan2(math.sqrt(axis[0]*axis[0] + axis[2]*axis[2]), axis[1])
    rotate = vrml.Transform(rotation=rot_axis + (rot_angle,))
    translate.addChild(rotate)
    cylinder = vrml.Cylinder(radius=radius, height=length, color=rgb,
			     top = 0, bottom = 0)
    rotate.addChild(cylinder)
  return transform
  
# -----------------------------------------------------------------------------
# Use VRML NurbsCurve extension to create spline.  Curve will not pass through
# points and will not extend to the end points.  This is taken from the
# Chimera Ribbon extension.
#
def vrml_nurbs_spline(points, rgb):

  pstring = '[\n'
  for p in points:
    pstring = pstring + '\t\t\t\t%g %g %g,\n' % tuple(p)
  pstring = pstring + '\t\t\t]\n'

  n = len(points)
  knots = '[\n'
  knots = knots + '\t\t\t0, 0,\n'
  for i in range(n):
    knots = knots + '\t\t\t%d,\n' % i
  knots = knots + '\t\t\t%d, %d\n' % (n-1, n-1)
  knots = knots + '\t\t]\n'

  vrml = ('Shape {\n' +
          '\tappearance Appearance {\n' +
          '\t\tmaterial Material {\n' +
          '\t\t\temissiveColor %.2f %.2f %.2f\n' % rgb +
          '\t\t}\n' +
          '\t}\n' +
          '\tgeometry NurbsCurve {\n' +
          '\t\tcoord Coordinate {\n' +
          '\t\t\tpoint %s' % pstring +
          '\t\t}\n' +
          '\t\tnumControlPoints %d\n' % n +
          '\t\tknotVector %s' % knots +
          '\t}\n' +
          '}\n')
  return vrml
