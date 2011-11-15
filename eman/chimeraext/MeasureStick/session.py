# -----------------------------------------------------------------------------
# Save and restore volume path tracer state.
#
  
# -----------------------------------------------------------------------------
#
def save_path_tracer_state(path_tracer_dialog, file):

  s = Path_Tracer_Dialog_State()
  s.state_from_dialog(path_tracer_dialog)
  
  from SessionUtil import objecttree
  t = objecttree.instance_tree_to_basic_tree(s)

  file.write('\n')
  file.write('def restore_volume_path_tracer():\n')
  file.write(' path_tracer_state = \\\n')
  objecttree.write_basic_tree(t, file, indent = '  ')
  file.write('\n')
  file.write(' import VolumePath.session\n')
  file.write(' VolumePath.session.restore_path_tracer_state(path_tracer_state)\n')
  file.write('\n')
  file.write('try:\n')
  file.write('  restore_volume_path_tracer()\n')
  file.write('except:\n')
  file.write("  reportRestoreError('Error restoring volume path tracer')\n")
  file.write('\n')
  
# -----------------------------------------------------------------------------
#
def restore_path_tracer_state(path_tracer_dialog_basic_state):

  from SessionUtil.stateclasses import Model_State, Xform_State

  classes = (
    Path_Tracer_Dialog_State,
    Marker_Set_State,
    Marker_State,
    Link_State,
    Model_State,
    Xform_State,
    )
  name_to_class = {}
  for c in classes:
    name_to_class[c.__name__] = c

  from SessionUtil import objecttree
  s = objecttree.basic_tree_to_instance_tree(path_tracer_dialog_basic_state,
                                             name_to_class)

  import VolumePath
  d = VolumePath.volume_path_dialog(create = 1)

  set_dialog_state(s, d)

# -----------------------------------------------------------------------------
#
def set_dialog_state(path_tracer_dialog_state, path_tracer_dialog):

  path_tracer_dialog_state.restore_state(path_tracer_dialog)

# -----------------------------------------------------------------------------
#
class Path_Tracer_Dialog_State:

  version = 1
  
  state_attributes = ('is_visible',
                      'geometry',
                      'markers_panel_shown',
                      'curve_panel_shown',
                      'mouse_panel_shown',
                      'sets_panel_shown',
                      'slice_panel_shown',
                      'marker_color',
                      'marker_radius',
                      'marker_note',
                      'note_color',
                      'selected_notes_only',
                      'link_color',
                      'link_radius',
                      'curve_radius',
                      'curve_band_length',
                      'curve_segment_subdivisions',
                      'placement_button',
                      'place_markers_on_data',
                      'place_markers_on_space',
                      'move_markers',
                      'marker_matches_volume_color',
                      'link_to_selected',
                      'link_consecutive',
                      'use_volume_colors',
                      'show_slice_line',
                      'slice_color',
                      'active_marker_set_name',
                      'marker_set_states',
		      'version',
                      )
  
  # ---------------------------------------------------------------------------
  #
  def state_from_dialog(self, path_tracer_dialog):

    d = path_tracer_dialog

    self.is_visible = d.isVisible()
    self.geometry = d.toplevel_widget.wm_geometry()
    self.markers_panel_shown = d.markers_panel_button.variable.get()
    self.curve_panel_shown = d.curve_panel_button.variable.get()
    self.mouse_panel_shown = d.mouse_panel_button.variable.get()
    self.sets_panel_shown = d.sets_panel_button.variable.get()
    self.slice_panel_shown = d.slice_panel_button.variable.get()
    self.marker_color = d.marker_color.rgba
    self.marker_radius = d.marker_radius_entry.get()
    self.marker_note = d.marker_note.get()
    self.note_color = d.note_color.rgba
    self.selected_notes_only = d.selected_notes_only.get()
    self.link_color = d.link_color.rgba
    self.link_radius = d.link_radius_entry.get()
    self.curve_radius = d.curve_radius.get()
    self.curve_band_length = d.curve_band_length.get()
    self.curve_segment_subdivisions = d.curve_segment_subdivisions.get()
    self.placement_button = d.placement_button.variable.get()
    self.place_markers_on_data = d.place_markers_on_data.get()
    self.place_markers_on_space = d.place_markers_on_space.get()
    self.move_markers = d.move_markers.get()
    self.marker_matches_volume_color = d.marker_matches_volume_color.get()
    self.link_to_selected = d.link_to_selected.get()
    self.link_consecutive = d.link_consecutive.get()
    self.use_volume_colors = d.use_volume_colors.get()
    self.show_slice_line = d.show_slice_line.get()
    self.slice_color = d.slice_color.rgba

    ams = d.active_marker_set
    if ams:
      self.active_marker_set_name = ams.name
    else:
      self.active_marker_set_name = ''

    self.marker_set_states = []
    for ms in d.marker_sets:
      s = Marker_Set_State()
      s.state_from_marker_set(ms)
      self.marker_set_states.append(s)
      
    # TODO: restore vrml slice line (d.slice_line_model)

  # ---------------------------------------------------------------------------
  #
  def restore_state(self, path_tracer_dialog):

    d = path_tracer_dialog
    if self.is_visible:
      d.enter()
    d.toplevel_widget.wm_geometry(self.geometry)
    d.markers_panel_button.variable.set(self.markers_panel_shown)
    d.curve_panel_button.variable.set(self.curve_panel_shown)
    d.mouse_panel_button.variable.set(self.mouse_panel_shown)
    d.sets_panel_button.variable.set(self.sets_panel_shown)
    d.slice_panel_button.variable.set(self.slice_panel_shown)
    d.marker_color.showColor(self.marker_color, doCallback = 0)

    d.marker_radius_entry.set(self.marker_radius, invoke_callbacks = 0)
    d.marker_note.set(self.marker_note, invoke_callbacks = 0)
    d.note_color.showColor(self.note_color, doCallback = 0)
    d.selected_notes_only.set(self.selected_notes_only, invoke_callbacks = 0)
    d.link_color.showColor(self.link_color, doCallback = 0)
    d.link_radius_entry.set(self.link_radius, invoke_callbacks = 0)
    d.curve_radius.set(self.curve_radius, invoke_callbacks = 0)
    d.curve_band_length.set(self.curve_band_length, invoke_callbacks = 0)
    d.curve_segment_subdivisions.set(self.curve_segment_subdivisions,
				     invoke_callbacks = 0)
    d.placement_button.variable.set(self.placement_button,
				    invoke_callbacks = 0)
    d.place_markers_on_data.set(self.place_markers_on_data,
				invoke_callbacks = 0)
    d.place_markers_on_space.set(self.place_markers_on_space,
				 invoke_callbacks = 0)
    d.move_markers.set(self.move_markers, invoke_callbacks = 0)
    d.marker_matches_volume_color.set(self.marker_matches_volume_color,
				      invoke_callbacks = 0)
    d.link_to_selected.set(self.link_to_selected, invoke_callbacks = 0)
    d.link_consecutive.set(self.link_consecutive, invoke_callbacks = 0)
    d.use_volume_colors.set(self.use_volume_colors, invoke_callbacks = 0)
    d.show_slice_line.set(self.show_slice_line, invoke_callbacks = 0)
    d.slice_color.showColor(self.slice_color, doCallback = 0)

    for ms in self.marker_set_states:
      marker_set = ms.create_object()
      d.add_marker_set(marker_set)

    ams = d.find_marker_set_by_name(self.active_marker_set_name)
    if ams:
      d.set_active_marker_set(ams)

#
# TODO: Should I try to restore hand chosen marker thresholds for
#  volume data sets?
# data_region.components[n].volume_path_threshold
#

# -----------------------------------------------------------------------------
#
class Marker_Set_State:
  
  version = 1

  state_attributes = ('name',
		      'marker_model',
		      'curve_model',
		      'curve_parameters',
		      'next_marker_id',
		      'file_path',
		      'markers',
		      'links',
		      'extra_attributes',
		      'version',
		      )

  # ---------------------------------------------------------------------------
  #
  def state_from_marker_set(self, marker_set):

    ms = marker_set
    self.name = ms.name

    if ms.marker_molecule:
      from SessionUtil.stateclasses import Model_State
      self.marker_model = Model_State()
      self.marker_model.state_from_model(ms.marker_molecule)
    else:
      self.marker_model = None

    if ms.curve_model:
      from SessionUtil.stateclasses import Model_State
      cm = Model_State()
      cm.state_from_model(ms.curve_model)
      self.curve_parameters = ms.curve_parameters
      self.curve_model = cm
    else:
      self.curve_model = None
      self.curve_parameters = None

    self.next_marker_id = ms.next_marker_id
    self.file_path = ms.file_path

    self.markers = []
    for m in ms.atom_to_marker.values():
      s = Marker_State()
      s.state_from_marker(m)
      self.markers.append(s)

    self.links = []
    for l in ms.bond_to_link.values():
      s = Link_State()
      s.state_from_link(l)
      self.links.append(s)

    if hasattr(ms, 'extra_attribtues'):		# from reading XML
      self.extra_attributes = ms.extra_attributes
    else:
      self.extra_attributes = None

  # ---------------------------------------------------------------------------
  #
  def create_object(self):

    import markerset
    ms = markerset.Marker_Set(self.name)

    ms.next_marker_id = self.next_marker_id
    ms.file_path = self.file_path

    id_to_marker = {}
    for m in self.markers:
      marker = m.create_object(ms)
      id_to_marker[marker.id] = marker

    for l in self.links:
      l.create_object(id_to_marker)

    if self.extra_attributes:
      ms.extra_attributes = self.extra_attributes

    if self.marker_model and ms.marker_molecule:
      self.marker_model.restore_state(ms.marker_molecule)

    cm = self.curve_model
    if cm:
      radius, band_length, subdivisions = self.curve_parameters
      ms.show_curve(radius, band_length, subdivisions)
      cm.restore_state(ms.curve_model)

    return ms

# -----------------------------------------------------------------------------
#
class Marker_State:
  
  version = 1

  state_attributes = ('id',
		      'displayed',
		      'xyz',
		      'rgba',
		      'radius',
		      'note',
		      'note_rgba',
		      'note_shown',
		      'extra_attributes',
		      'version',
		      )

  # ---------------------------------------------------------------------------
  #
  def state_from_marker(self, marker):

    m = marker
    self.id = m.id
    self.displayed = m.atom.display
    self.xyz = m.xyz()
    self.rgba = m.rgba()
    self.radius = m.radius()
    self.note = m.note()
    self.note_rgba = m.note_rgba()
    self.note_shown = m.note_shown()
    if hasattr(m, 'extra_attributes'):		# from XML file
      self.extra_attributes = m.extra_attributes
    else:
      self.extra_attributes = None

  # ---------------------------------------------------------------------------
  #
  def create_object(self, marker_set):

    import markerset
    m = markerset.Marker(marker_set, self.id, self.xyz, self.rgba, self.radius)
    m.atom.display = self.displayed
    m.set_note(self.note)
    m.set_note_rgba(self.note_rgba)
    m.show_note(self.note_shown)
    if self.extra_attributes:
      m.extra_attributes = self.extra_attributes

    # TODO: Restore selection state?

    return m

# -----------------------------------------------------------------------------
#
class Link_State:

  version = 1
  
  state_attributes = ('marker_id_1',
		      'marker_id_2',
		      'displayed',
		      'rgba',
		      'radius',
		      'extra_attributes',
		      'version',
		      )

  # ---------------------------------------------------------------------------
  #
  def state_from_link(self, link):

    l = link
    self.marker_id_1 = l.marker1.id
    self.marker_id_2 = l.marker2.id
    self.displayed = l.bond.display
    self.rgba = l.rgba()
    self.radius = l.radius()
    if hasattr(l, 'extra_attributes'):		# from XML file
      self.extra_attributes = l.extra_attributes
    else:
      self.extra_attributes = None

  # ---------------------------------------------------------------------------
  #
  def create_object(self, id_to_marker):

    m1 = id_to_marker[self.marker_id_1]
    m2 = id_to_marker[self.marker_id_2]
    import markerset
    l = markerset.Link(m1, m2, self.rgba, self.radius)
    l.bond.display = self.displayed
    if self.extra_attributes:
      m.extra_attributes = self.extra_attributes

    # TODO: Restore selection state?

    return l
