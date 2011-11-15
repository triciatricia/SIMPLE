# -----------------------------------------------------------------------------
#
import chimera
from chimera import selection

# -----------------------------------------------------------------------------
# Set of Markers and Links between them.
#
class Marker_Set:

  def __init__(self, name):

    self.name = name
    self.marker_molecule = None         # Molecule model used for markers
    self.marker_residue = None
    self.curve_model = None             # VRML smooth interpolated curve
    self.next_marker_id = 1
    self.atom_to_marker = {}
    self.bond_to_link = {}
    self.file_path = None

  # ---------------------------------------------------------------------------
  #
  def marker_molecule_and_residue(self):

    if self.marker_molecule == None:
      m = chimera.Molecule()
      m.name = self.name
      chimera.openModels.add([m])
      self.marker_molecule = m
      add_model_closed_callback(m, self.model_closed_cb)
      #
      # Need to create a residue because atom without residue causes
      # unknown C++ exceptions.
      #
      rid = chimera.MolResId(1, ' ')
      self.marker_residue = m.newResidue('markers', rid)

    return self.marker_molecule, self.marker_residue

  # ---------------------------------------------------------------------------
  #
  def transform(self):

    molecule, residue = self.marker_molecule_and_residue()
    return molecule.openState.xform
  
  # ---------------------------------------------------------------------------
  #
  def place_marker(self, xyz, rgba, radius, id = None):

    if id == None:
      id = self.next_marker_id
      self.next_marker_id = self.next_marker_id + 1
    else:
      self.next_marker_id = max(self.next_marker_id, id + 1)
      
    m = Marker(self, id, xyz, rgba, radius)

    return m

  # ---------------------------------------------------------------------------
  #
  def markers(self):

    return self.atom_to_marker.values()

  # ---------------------------------------------------------------------------
  #
  def show_markers(self, show):

    if self.marker_molecule:
      for a in self.marker_molecule.atoms:
        a.display = show
  
  # ---------------------------------------------------------------------------
  #
  def show_links(self, show):

    if self.marker_molecule == None:
      return

    if show:
      mode = chimera.Bond.Always
    else:
      mode = chimera.Bond.Never
    for b in self.marker_molecule.bonds:
      b.display = mode

  # ---------------------------------------------------------------------------
  #
  def selected_markers(self):

    atoms = selection.currentAtoms()
    markers = []
    for a in atoms:
      if self.atom_to_marker.has_key(a):
        markers.append(self.atom_to_marker[a])
    return markers

  # ---------------------------------------------------------------------------
  #
  def selected_links(self):

    links = []
    bonds = selection.currentBonds()
    for b in bonds:
      if self.bond_to_link.has_key(b):
        links.append(self.bond_to_link[b])
    return links

  # ---------------------------------------------------------------------------
  #
  def show_curve(self, radius, band_length, subdivisions):

    if self.marker_molecule == None:
      return

    chains = atom_chains(self.marker_molecule)
    
    import vrml_curve
    vrml = vrml_curve.vrml_header()

    for atoms, bonds in chains:
      xyz_path = map(atom_position, atoms)
      point_colors = map(lambda a: a.color.rgba()[:3], atoms)
      segment_colors = map(lambda b: b.color.rgba()[:3], bonds)
      vrml = vrml + vrml_curve.vrml_banded_tube(xyz_path, point_colors,
                                                segment_colors, radius,
                                                subdivisions, band_length)

    m = chimera.openModels.open(vrml, 'VRML', sameAs = self.marker_molecule)[0]
    m.name = 'path tracer curve'
    self.curve_parameters = (radius, band_length, subdivisions)
    self.curve_model = m
    add_model_closed_callback(m, self.curve_model_closed_cb)

  # ---------------------------------------------------------------------------
  #
  def unshow_curve(self):

    if self.curve_model:
      chimera.openModels.close([self.curve_model])
      self.curve_model = None
  
  # ---------------------------------------------------------------------------
  #
  def save_as_xml(self, out):

    ea = getattr(self, 'extra_attributes', {})
    out.write('<marker_set name="%s"%s>\n' %
	      (self.name, attribute_strings(ea)))

    markers = self.atom_to_marker.values()
    markers.sort(lambda m1, m2: cmp(m1.id, m2.id))
    for m in markers:
      id_text = 'id="%d"' % m.id
      xyz_text = 'x="%.5g" y="%.5g" z="%.5g"' % m.xyz()

      rgb = tuple(m.rgba()[:3])
      if rgb == (1,1,1):
        rgb_text = ''
      else:
        rgb_text = 'r="%.5g" g="%.5g" b="%.5g"' % rgb

      radius_text = 'radius="%.5g"' % m.radius()

      if m.note():
        note_text = ' note="%s"' % xml_escape(m.note())
        note_rgb = tuple(m.note_rgba()[:3])
        if note_rgb == (1,1,1):
          note_rgb_text = ''
        else:
          note_rgb_text = ' nr="%.5g" ng="%.5g" nb="%.5g"' % note_rgb
      else:
        note_text = ''
        note_rgb_text = ''
      
      ea = getattr(m, 'extra_attributes', {})

      out.write('<marker %s %s %s %s%s%s%s/>\n' %
                (id_text, xyz_text, rgb_text, radius_text,
                 note_text, note_rgb_text, attribute_strings(ea)))

    links = self.bond_to_link.values()
    for e in links:
      id_text = 'id1="%d" id2="%d"' % (e.marker1.id, e.marker2.id)
      rgb_text = 'r="%.5g" g="%.5g" b="%.5g"' % e.rgba()[:3]
      radius_text = 'radius="%.5g"' % e.radius()
      ea = getattr(e, 'extra_attributes', {})
      out.write('<link %s %s %s%s/>\n' % (id_text, rgb_text, radius_text,
					  attribute_strings(ea)))
      
    out.write('</marker_set>\n')
      
  # ---------------------------------------------------------------------------
  #
  def model_closed_cb(self, model):

    self.marker_molecule = None
    self.marker_residue = None
    self.next_marker_id = 1
      
    self.atom_to_marker = {}
    self.bond_to_link = {}
      
  # ---------------------------------------------------------------------------
  #
  def curve_model_closed_cb(self, model):

    self.curve_model = None
    
  # ---------------------------------------------------------------------------
  #
  def close(self):

    if self.marker_molecule:
      chimera.openModels.close([self.marker_molecule])
      
    if self.curve_model:
      chimera.openModels.close([self.curve_model])
      self.curve_model = None

# -----------------------------------------------------------------------------
# Marker is implemented as a Chimera Atom.
#
class Marker:

  def __init__(self, marker_set, id, xyz, rgba, radius):

    self.marker_set = marker_set
    self.id = id
    self.note_text = ''
    self.note_color = (1,1,1,1)
        
    molecule, residue = marker_set.marker_molecule_and_residue()
    name = 'm%d' % id
    a = molecule.newAtom(name, chimera.elements.H)
    residue.addAtom(a)
    c = chimera.Coord()
    c.x, c.y, c.z = xyz
    a.setCoord(c)                               # a.coord = c does not work
    a.radius = radius
    a.drawMode = chimera.Atom.Sphere
    a.color = chimera_color(rgba)

    self.atom = a

    marker_set.atom_to_marker[a] = self
  
  # ---------------------------------------------------------------------------
  #
  def xyz(self):

    c = self.atom.coord()
    return (c.x, c.y, c.z)
  
  # ---------------------------------------------------------------------------
  #
  def set_xyz(self, xyz):

    c = chimera.Coord()
    c.x, c.y, c.z = xyz
    self.atom.setCoord(c)
  
  # ---------------------------------------------------------------------------
  #
  def rgba(self):

    return self.atom.color.rgba()
  
  # ---------------------------------------------------------------------------
  #
  def set_rgba(self, rgba):

    self.atom.color = chimera_color(rgba)

  # ---------------------------------------------------------------------------
  #
  def radius(self):

    return self.atom.radius
  
  # ---------------------------------------------------------------------------
  #
  def set_radius(self, radius):

    self.atom.radius = radius

  # ---------------------------------------------------------------------------
  #
  def note(self):

    return self.note_text
  
  # ---------------------------------------------------------------------------
  #
  def set_note(self, note):

    self.note_text = note
    if self.note_shown():
      self.show_note(1)

  # ---------------------------------------------------------------------------
  #
  def note_rgba(self):

    return self.note_color
  
  # ---------------------------------------------------------------------------
  #
  def set_note_rgba(self, rgba):

    self.note_color = rgba
    if self.note_shown():
      self.show_note(1)
  
  # ---------------------------------------------------------------------------
  #
  def show_note(self, show):

    if show and self.note_text:
        self.atom.label = self.note_text
        self.atom.labelColor = chimera_color(self.note_color)
    else:
      self.atom.label = ''
  
  # ---------------------------------------------------------------------------
  #
  def note_shown(self):

    if self.atom.label:
      return 1
    return 0

  # ---------------------------------------------------------------------------
  #
  def select(self):

    selection.addCurrent(self.atom)

  # ---------------------------------------------------------------------------
  #
  def deselect(self):

    selection.removeCurrent(self.atom)

  # ---------------------------------------------------------------------------
  #
  def links(self):

    bonds = self.atom.bonds.values()
    llist = map(lambda b, b2m = self.marker_set.bond_to_link: b2m[b], bonds)
    return llist
    
  # ---------------------------------------------------------------------------
  #
  def linked_markers(self):

    atoms = self.atom.bonds.keys()
    mlist = map(lambda a, a2m = self.marker_set.atom_to_marker: a2m[a], atoms)
    return mlist
  
  # ---------------------------------------------------------------------------
  #
  def linked_to(self, marker):

    b = self.atom.findBond(marker.atom)
    if b:
      return self.marker_set.bond_to_link[b]
    return None
    
  # ---------------------------------------------------------------------------
  #
  def delete(self):

    a = self.atom

    ms = self.marker_set
    for b in a.bonds.values():
      ms.bond_to_link[b].delete()

    a.molecule.deleteAtom(a)
    self.atom = None
    del ms.atom_to_marker[a]
  
# -----------------------------------------------------------------------------
# Link is implemented as a Chimera Bond.
#
class Link:

  def __init__(self, marker1, marker2, rgba, radius):

    self.marker1 = marker1
    self.marker2 = marker2

    ms = marker1.marker_set
    molecule, residue = ms.marker_molecule_and_residue()
    b = molecule.newBond(marker1.atom, marker2.atom)
    self.bond = b
    ms.bond_to_link[b] = self

    self.set_rgba(rgba)
    self.set_radius(radius)

  
  # ---------------------------------------------------------------------------
  #
  def rgba(self):

    return self.bond.color.rgba()
    
  # ---------------------------------------------------------------------------
  #
  def set_rgba(self, rgba):

    color = chimera_color(rgba)
    self.bond.color = color
    self.bond.halfbond = 0
  # ---------------------------------------------------------------------------
  #
  def print_link_distance(self, distance_string):
    distance= chimera.Coord.dist(self.marker1.atom.coord(), self.marker2.atom.coord())
    print distance
    distance_string.set(str(distance))
    
  # ---------------------------------------------------------------------------
  #
  def radius(self):

    b = self.bond
    if b.drawMode == chimera.Bond.Wire:
      radius = 0.0
    else:
      radius = b.order * self.molecule().stickSize
    return radius
      
  # ---------------------------------------------------------------------------
  # In stick representation, bond radius is shown as bond order times the
  # molecule stick size.  Use the bond order to control radius.
  #
  def set_radius(self, radius):

    b = self.bond
    m = self.molecule()
    if radius == 0 or m.stickSize == 0:
      b.drawMode = chimera.Bond.Wire
      b.order = 1
    else:
      b.drawMode = chimera.Bond.Stick
      b.order = radius / m.stickSize

  # ---------------------------------------------------------------------------
  #
  def molecule(self):

    ms = self.marker1.marker_set
    molecule, residue = ms.marker_molecule_and_residue()
    return molecule

  # ---------------------------------------------------------------------------
  #
  def select(self):
        
    selection.addCurrent(self.bond)
    
  # ---------------------------------------------------------------------------
  #
  def deselect(self):

    selection.removeCurrent(self.bond)
    
  # ---------------------------------------------------------------------------
  #
  def delete(self):

    b = self.bond
    b.molecule.deleteBond(b)
    self.bond = None
    ms = self.marker1.marker_set
    del ms.bond_to_link[b]
    
# -----------------------------------------------------------------------------
# Return a list of atom chains for a molecule.  An atom chain is a sequence
# of atoms connected by bonds where all non-end-point atoms have exactly 2
# bonds.  A chain is represented by a 2-tuple, the first element being the
# ordered list of atoms, and the second being the ordered list of bonds.
# In a chain which is a cycle all atoms have 2 bonds and the first and
# last atom in the chain are the same.  Non-cycles have end point atoms
# with more or less than 2 bonds.
#
def atom_chains(molecule):

  used_bonds = {}
  chains = []
  for a in molecule.atoms:
    if len(a.bonds) != 2:
      for b in a.bonds.values():
        if not used_bonds.has_key(b):
          used_bonds[b] = 1
          c = trace_chain(a, b)
          chains.append(c)
          end_bond = c[1][-1]
          used_bonds[end_bond] = 1

  #
  # Pick up cycles
  #
  reached_atoms = {}
  for atoms, bonds in chains:
    for a in atoms:
      reached_atoms[a] = 1

  for a in molecule.atoms:
    if not reached_atoms.has_key(a):
      bonds = a.bonds.values()
      if len(bonds) == 2:
        b = bonds[0]
        c = trace_chain(a, b)
        chains.append(c)
        for a in c[0]:
          reached_atoms[a] = 1
      
  return chains
          
# -----------------------------------------------------------------------------
#
def trace_chain(atom, bond):

  atoms = [atom]
  bonds = [bond]

  a = atom
  b = bond
  while 1:
    a = b.otherAtom(a)
    atoms.append(a)
    if a == atom:
      break                     # loop
    blist = a.bonds.values()
    blist.remove(b)
    if len(blist) != 1:
      break
    b = blist[0]
    bonds.append(b)
    
  return (atoms, bonds)
          
# -----------------------------------------------------------------------------
#
def chimera_color(rgba):

  c = apply(chimera.MaterialColor, list(rgba) + [None])
  return c
          
# -----------------------------------------------------------------------------
#
def atom_position(atom):

  import Numeric
  c = atom.coord()
  xyz = Numeric.array((c.x, c.y, c.z))
  return xyz
  
# -----------------------------------------------------------------------------
# Make string name1="value1" name2="value2" ... string for XML output.
#
def attribute_strings(dict):

  s = ''
  for name, value in dict.items():
    s = s + (' %s="%s"' % (name, xml_escape(value)))
  return s
  
# -----------------------------------------------------------------------------
# Replace & by &amp; " by &quot; and < by &lt; and > by &gt; in a string.
#
def xml_escape(s):

  import string
  s1 = string.replace(s, '&', '&amp;')
  s2 = string.replace(s1, '"', '&quot;')
  s3 = string.replace(s2, '<', '&lt;')
  s4 = string.replace(s3, '>', '&gt;')
  s5 = string.replace(s4, "'", '&apos;')
  return s5

# -----------------------------------------------------------------------------
#
def save_marker_sets(mslist, out):

  if len(mslist) > 1:
    out.write('<marker_sets>\n')
    
  for ms in mslist:
    ms.save_as_xml(out)

  if len(mslist) > 1:
    out.write('</marker_sets>\n')
  
# -----------------------------------------------------------------------------
#
def load_marker_set_xml(input):

  # ---------------------------------------------------------------------------
  # Handler for use with Simple API for XML (SAX2).
  #
  from xml.sax import ContentHandler
  class Marker_Set_SAX_Handler(ContentHandler):

    def __init__(self):

      self.marker_set_tuples = []
      self.set_attributes = None
      self.marker_attributes = None
      self.link_attributes = None

    # -------------------------------------------------------------------------
    #
    def startElement(self, name, attrs):

      if name == 'marker_set':
        self.set_attributes = self.attribute_dictionary(attrs)
        self.marker_attributes = []
        self.link_attributes = []
      elif name == 'marker':
        self.marker_attributes.append(self.attribute_dictionary(attrs))
      elif name == 'link':
        self.link_attributes.append(self.attribute_dictionary(attrs))

    # -------------------------------------------------------------------------
    # Convert Attributes object to a dictionary.
    #
    def attribute_dictionary(self, attrs):

      d = {}
      for key, value in attrs.items():
	d[key] = value
      return d

    # -------------------------------------------------------------------------
    #
    def endElement(self, name):

      if name == 'marker_set':
        mst = (self.set_attributes,
	       self.marker_attributes,
	       self.link_attributes)
        self.marker_set_tuples.append(mst)
        self.set_attributes = None
        self.marker_attributes = None
        self.link_attributes = None


  from xml.sax import make_parser
  xml_parser = make_parser()

  from xml.sax.handler import feature_namespaces
  xml_parser.setFeature(feature_namespaces, 0)

  h = Marker_Set_SAX_Handler()
  xml_parser.setContentHandler(h)
  xml_parser.parse(input)

  return create_marker_sets(h.marker_set_tuples)

# -----------------------------------------------------------------------------
#
def create_marker_sets(marker_set_tuples):

  marker_sets = []
  for set_attributes, marker_attributes, link_attributes in marker_set_tuples:
    name = str(set_attributes.get('name', ''))
    ms = Marker_Set(name)
    ms.extra_attributes = leftover_keys(set_attributes, ('name',))
    id_to_marker = {}
    for mdict in marker_attributes:
      id = int(mdict.get('id', '0'))
      x = float(mdict.get('x', '0'))
      y = float(mdict.get('y', '0'))
      z = float(mdict.get('z', '0'))
      r = float(mdict.get('r', '1'))
      g = float(mdict.get('g', '1'))
      b = float(mdict.get('b', '1'))
      radius = float(mdict.get('radius', '1'))
      note = str(mdict.get('note', ''))
      nr = float(mdict.get('nr', '1'))
      ng = float(mdict.get('ng', '1'))
      nb = float(mdict.get('nb', '1'))
      m = ms.place_marker((x,y,z), (r,g,b,1), radius, id)
      m.set_note(note)
      m.set_note_rgba((nr,ng,nb,1))
      e = leftover_keys(mdict, ('id','x','y','z','r','g','b', 'radius','note',
				'nr','ng','nb'))
      m.extra_attributes = e
      id_to_marker[id] = m
    for ldict in link_attributes:
      id1 = int(ldict.get('id1', '0'))
      id2 = int(ldict.get('id2', '0'))
      r = float(ldict.get('r', '1'))
      g = float(ldict.get('g', '1'))
      b = float(ldict.get('b', '1'))
      radius = float(ldict.get('radius', '0'))
      l = Link(id_to_marker[id1], id_to_marker[id2], (r,g,b,1), radius)
      e = leftover_keys(ldict, ('id1','id2','r','g','b', 'radius'))
      l.extra_attributes = e
    marker_sets.append(ms)

  return marker_sets

# -----------------------------------------------------------------------------
#
def leftover_keys(dict, keys):

  leftover = {}
  leftover.update(dict)
  for k in keys:
    if leftover.has_key(k):
      del leftover[k]
  return leftover

# -----------------------------------------------------------------------------
#
def pick_marker(pointer_x, pointer_y, marker_sets):

  v = chimera.viewer
  time = 0
  cursor_name = ''
  v.recordPosition(time, pointer_x, pointer_y, cursor_name),
  objects = v.pick(pointer_x, pointer_y)
  atoms = filter(lambda obj: isinstance(obj, chimera.Atom), objects)
  if len(atoms) != 1:
    return None

  a = atoms[0]
  for marker_set in marker_sets:
    if marker_set.atom_to_marker.has_key(a):
      return marker_set.atom_to_marker[a]

  return None

# -----------------------------------------------------------------------------
#
def pick_marker_3d(xyz, marker_sets):

  from VolumeViewer import slice
  close = []
  for marker_set in marker_sets:
    ms_xyz = slice.eye_to_object_coordinates(xyz, marker_set.transform())
    for m in marker_set.markers():
      d = distance(m.xyz(), ms_xyz)
      if d <= m.radius():
	close.append((d,m))

  if close:
    close.sort()
    dist, closest_marker = close[0]
    return closest_marker

  return None
      
# -----------------------------------------------------------------------------
# Does not transfer markers to new marker set if different marker sets would
# be linked.  Returns None in that case.  Otherwise returns the number of
# markers transfered.
#
def transfer_markers(mlist, marker_set):

  markers = filter(lambda m, ms=marker_set: m.marker_set != ms, mlist)
  
  mtable = {}
  for m in markers:
    mtable[m] = 1

  for m in markers:
    for m2 in m.linked_markers():
      if not mtable.has_key(m2) and m2.marker_set != marker_set:
        return None        # Markers in different sets would be linked.

  # Copy markers
  mmap = {}
  xform = marker_set.transform()
  for m in markers:
    xyz = transform_coordinates(m.xyz(), m.marker_set.transform(), xform)
    mcopy = marker_set.place_marker(xyz, m.rgba(), m.radius())
    mmap[m] = mcopy

  # Copy links
  for m in markers:
    for link in m.links():
      if link.marker1 == m:
        Link(mmap[link.marker1], mmap[link.marker2],
             link.rgba(), link.radius())

  # Delete original markers and links
  for m in markers:
    m.delete()

  return len(markers)

# -----------------------------------------------------------------------------
#
def transform_coordinates(xyz, from_xform, to_xform):

  p = apply(chimera.Point, xyz)
  p1 = from_xform.apply(p)
  to_xform.invert()
  p2 = to_xform.apply(p1)
  to_xform.invert()
  return (p2.x, p2.y, p2.z)

# -----------------------------------------------------------------------------
#
def distance(xyz_1, xyz_2):

  dx = xyz_1[0] - xyz_2[0]
  dy = xyz_1[1] - xyz_2[1]
  dz = xyz_1[2] - xyz_2[2]
  d2 = dx*dx + dy*dy + dz*dz
  import math
  d = math.sqrt(d2)
  return d

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
