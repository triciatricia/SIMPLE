# -----------------------------------------------------------------------------
# Cubic spline through points in 3D.
#
import math

# -----------------------------------------------------------------------------
# Return cubically interpolated point list.  An Overhauser spline
# (aka Catmul-Rom spline) uses cubic segments that join at the given points
# and have continuous tangent vector.  The tangent vector at point i equals
# the difference vector between points i+1 and i-1.
# For the end segments I use a quadratic curve.
#
# It is assumed that the points are objects with operators +, -,
# and * (by float) defined.  For example, Numeric Python arrays work.
# But points that are lists or tuples will not work.
#
def overhauser_spline_points(points, segment_subdivisions):

  if len(points) <= 1:
    plist = []
  elif len(points) == 2:
    plist = linear_segment_points(points[0], points[1], segment_subdivisions)
  else:
    p0 = points[2]
    p1 = points[1]
    p2 = points[0]
    t1 = p2 - p0
    plist = quadratic_segment_points(p1, t1, p2, segment_subdivisions)[1:]
    plist.reverse()

    for k in range(1, len(points)-2):
      p0 = points[k-1]
      p1 = points[k]
      p2 = points[k+1]
      p3 = points[k+2]
      t1 = p2 - p0
      t2 = p3 - p1
      plist = plist + cubic_segment_points(p1, t1, p2, t2,
                                           segment_subdivisions)[:-1]

    p0 = points[-3]
    p1 = points[-2]
    p2 = points[-1]
    t1 = p2 - p0
    plist = plist + quadratic_segment_points(p1, t1, p2, segment_subdivisions)

  return plist

# -----------------------------------------------------------------------------
# Return a sequence of points along a cubic starting at p1 with tangent t1
# and ending at p2 with tangent t2.
#
def cubic_segment_points(p1, t1, p2, t2, subdivisions):

  s = p2 - p1
  a = t2 + t1 - s * 2
  b = s * 3 - t2 - t1 * 2
  c = t1
  d = p1
  points = []
  for k in range(subdivisions + 2):
    t = float(k) / (subdivisions + 1)
    p = d + (c + (b + a * t) * t) * t
    points.append(p)
  return points

# -----------------------------------------------------------------------------
# Return a sequence of points along a quadratic starting at p1 with tangent t1
# and ending at p2.
#
def quadratic_segment_points(p1, t1, p2, subdivisions):

  a = p2 - p1 - t1
  b = t1
  c = p1
  points = []
  for k in range(subdivisions + 2):
    t = float(k) / (subdivisions + 1)
    p = c + (b + a * t) * t
    points.append(p)
  return points

# -----------------------------------------------------------------------------
# Return a sequence of points along a linear segment starting at p1 and ending
# at p2.
#
def linear_segment_points(p1, p2, subdivisions):

  a = p2 - p1
  b = p1
  points = []
  for k in range(subdivisions + 2):
    t = float(k) / (subdivisions + 1)
    p = b + a * t
    points.append(p)
  return points
  
# -----------------------------------------------------------------------------
# Return a list of arc lengths for a piecewise linear curve specified by
# points.  The points should be objects with operator - defined such as
# Numeric Python arrays.  There number of arc lengths returned equals the
# number of points, the first arc length being 0.
#
def arc_lengths(points):

  arcs = [0]
  for s in range(len(points)-1):
    d = points[s+1] - points[s]
    length = math.sqrt(d[0]*d[0] + d[1]*d[1] + d[2]*d[2])
    arcs.append(arcs[s] + length)
  return arcs
