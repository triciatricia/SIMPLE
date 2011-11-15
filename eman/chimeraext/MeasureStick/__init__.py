# -----------------------------------------------------------------------------
# Calculate where the mouse position lies on the near and far clip planes.
# Make a mouse mode where a button click causes a VRML line to be drawn
# under the mouse from near to far clip planes.
#
# This calculation is intended to be used to extract a 1 dimensional
# z slice of a volume under the mouse, display it in a separate window,
# and drop a marker on top of the first peak above a threshold.  The
# depth position of the marker can be moved in the 1D slice window
# with the mouse.  The marker will be an atom in a molecule.
#
import math
import os
import sys
import shutil
import Pmw
import Tkinter
from Tkinter import *
import tkMessageBox


import chimera
from chimera.baseDialog import ModelessDialog

# -----------------------------------------------------------------------------
#
class Volume_Path_Dialog(ModelessDialog):

  title = 'Measuring Stick'
  name = 'volume path'
  buttons = ('Import XML...', 'Close')
  help = 'ContributedSoftware/volumepathtracer/framevolpath.html'

  # ---------------------------------------------------------------------------
  #
  def fillInUI(self, parent):

    self.marker_sets = []
    self.links_list = []
    self.active_marker_set = None
    self.slice_line_model = None        # VRML model showing slice position
    self.shown_slice = None             # For interactive marker z movement
    self.max_line_id = None             # Canvas id for slice graph depth line
    self.form_link_trigger = None
    self.last_selected_marker = None    # For linking consecutively selected
                                        #   markers.
    self.bound_button = None          # Mouse button bound for Marker placement
    self.show_note_trigger = None
    self.grabbed_marker = None

    self.open_dialog = None
    
    parent.columnconfigure(0, weight = 1)
    row = 0

    import Tkinter
    from CGLtk import Hybrid

    pb = Hybrid.Checkbutton_Row(parent, 'Panels ',
                                ('Markers', 'Curve', 'Mouse', 'Sets', 'Slice'))
    pb.frame.grid(row = row, column = 0, sticky = 'nw')
    row = row + 1
    (self.markers_panel_button,
     self.curve_panel_button,
     self.mouse_panel_button,
     self.sets_panel_button,
     self.slice_panel_button) = pb.checkbuttons

    self.toplevel_widget = parent.winfo_toplevel()
    self.toplevel_widget.withdraw()

    for b in pb.checkbuttons:
      b.callback(self.allow_toplevel_resize_cb)

    msm = Hybrid.Option_Menu(parent, 'Marker set ')
    msm.frame.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    msm.add_callback(self.marker_set_menu_cb)
    self.marker_set_menu = msm

    msp = Tkinter.Frame(parent)
    self.sets_panel_button.popup_frame(msp, row = row, column = 0,
                                       sticky = 'news')
    parent.rowconfigure(row, weight = 1)
    row = row + 1
    self.make_marker_sets_panel(msp)

    ap = Tkinter.Frame(parent)
    self.markers_panel_button.popup_frame(ap, row = row, column = 0,
                                          sticky = 'nw')
    row = row + 1
    self.make_markers_panel(ap)

    cp = Tkinter.Frame(parent)
    self.curve_panel_button.popup_frame(cp, row = row, column = 0,
                                        sticky = 'nw')
    row = row + 1
    self.make_curve_panel(cp)

    mmp = Tkinter.Frame(parent)
    self.mouse_panel_button.popup_frame(mmp, row = row, column = 0,
                                        sticky = 'nw')
    row = row + 1
    self.make_mouse_mode_panel(mmp)
    self.mouse_panel_button.variable.set(1)

    sp = Tkinter.Frame(parent)
    self.slice_panel_button.popup_frame(sp, row = row, column = 0,
                                        sticky = 'news')
    row = row + 1
    self.make_slice_panel(sp)
    
    msg = Tkinter.Label(parent, width = 40, anchor = 'w', justify = 'left')
    msg.grid(row = row, column = 0, sticky = 'ew')
    row = row + 1
    self.message_label = msg

    self.new_marker_set('marker set 1')
    
    callbacks = (self.mouse_down_cb, self.mouse_drag_cb, self.mouse_up_cb)
    from chimera import mousemodes
    mousemodes.addFunction('mark volume', callbacks, self.mouse_mode_icon())

    import SimpleSession
    chimera.triggers.addHandler(SimpleSession.SAVE_SESSION,
				self.save_session_cb, None)
    chimera.triggers.addHandler(chimera.CLOSE_SESSION,
				self.close_session_cb, None)

  # ---------------------------------------------------------------------------
  #
  def make_markers_panel(self, frame):

    import Tkinter
    from CGLtk import Hybrid

    row = 0
    
    smf = Tkinter.Frame(frame)
    smf.grid(row = row, column = 0, sticky = 'w')
    row = row + 1

    sm = Hybrid.Button_Row(smf, 'Markers: ',
                           (('Show', lambda s=self: s.show_markers(1)),
                            ('Hide', lambda s=self: s.show_markers(0)),
                            ('Delete', self.delete_markers_cb)))
    sm.frame.grid(row = 0, column = 0, sticky = 'w')
    
    from CGLtk.color import ColorWell
    mc = ColorWell.ColorWell(smf, callback = self.marker_color_cb)
    self.marker_color = mc
    mc.showColor((1,1,1), doCallback = 0)
    mc.grid(row = 0, column = 1, sticky = 'w')

    mr = Hybrid.Entry(smf, ' Radius', 5)
    mr.frame.grid(row = 0, column = 2, sticky = 'w')
    mr.entry.bind('<KeyPress-Return>', self.marker_radius_cb)
    self.marker_radius_entry = mr.variable

    mnf = Tkinter.Frame(frame)
    mnf.grid(row = row, column = 0, sticky = 'ew')
    row = row + 1
    mnf.columnconfigure(0, weight = 1)
    
    mn = Hybrid.Entry(mnf, 'Marker note: ', 10)
    mn.frame.grid(row = 0, column = 0, sticky = 'ew')
    mn.entry.bind('<KeyPress-Return>', self.marker_note_cb)
    self.marker_note = mn.variable

    msh = Hybrid.Button_Row(mnf, '',
                            (('Show', lambda s=self: s.show_marker_notes(1)),
                             ('Hide', lambda s=self: s.show_marker_notes(0)),
                             ('Delete', self.delete_marker_notes_cb)))
    msh.frame.grid(row = 0, column = 1, sticky = 'w')

    nc = ColorWell.ColorWell(mnf, callback = self.note_color_cb)
    self.note_color = nc
    nc.showColor((1,1,1), doCallback = 0)
    nc.grid(row = 0, column = 2, sticky = 'w')

    sno = Hybrid.Checkbutton(frame,
                             'Show/hide/color notes for selected markers only',
                             0)
    sno.button.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    self.selected_notes_only = sno.variable
    
    lf = Tkinter.Frame(frame)
    lf.grid(row = row, column = 0, sticky = 'w')
    row = row + 1

    sl = Hybrid.Button_Row(lf, 'Links: ',
                           (('Show', lambda s=self: s.show_links(1)),
                            ('Hide', lambda s=self: s.show_links(0)),
                            ('Delete', self.delete_links_cb)))
    sl.frame.grid(row = 0, column = 0, sticky = 'w')

    lc = ColorWell.ColorWell(lf, callback = self.link_color_cb)
    self.link_color = lc
    lc.showColor((1,1,1), doCallback = 0)
    lc.grid(row = 0, column = 1, sticky = 'w')

    lr = Hybrid.Entry(lf, ' Radius', 5)
    lr.frame.grid(row = 0, column = 2, sticky = 'w')
    lr.entry.bind('<KeyPress-Return>', self.link_radius_cb)
    self.link_radius_entry = lr.variable
    
    tf = Tkinter.Frame(frame)
    tf.grid(row = row, column = 0, sticky = 'w')
    row = row + 1

    tb = Tkinter.Button(tf, text = 'Transfer',
                        command = self.transfer_markers_cb)
    tb.grid(row = 0, column = 0, sticky = 'w')

    tl = Tkinter.Label(tf, text = ' selected markers to current set')
    tl.grid(row = 0, column = 1, sticky = 'w')
    
  # ---------------------------------------------------------------------------
  #
  def make_curve_panel(self, frame):

    import Tkinter
    from CGLtk import Hybrid

    row = 0

    br = Hybrid.Button_Row(frame, 'Curve: ',
                           (('Show', self.show_curve_cb),
                            ('Unshow', self.unshow_curve_cb)))
    br.frame.grid(row = row, column = 0, sticky = 'w')
    row = row + 1

    cr = Hybrid.Entry(frame, 'Curve radius: ', 5, '0')
    cr.frame.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    self.curve_radius = cr.variable

    bl = Hybrid.Entry(frame, 'Band length: ', 5, '0')
    bl.frame.grid(row = row, column = 0, sticky = 'w')
    row = row + 1    
    self.curve_band_length = bl.variable

    sd = Hybrid.Entry(frame, 'Segment subdivisions: ', 5, '10')
    sd.frame.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    self.curve_segment_subdivisions = sd.variable

  # ---------------------------------------------------------------------------
  #
  def make_mouse_mode_panel(self, frame):

    import Tkinter
    from CGLtk import Hybrid

    row = 0
    frame.columnconfigure(0, weight = 1)
    
    pmf = Tkinter.Frame(frame)
    pmf.grid(row = row, column = 0, sticky = 'w')
    row = row + 1

    mb = Hybrid.Option_Menu(pmf, 'Use ', 'button 1', 'button 2', 'button 3',
                            'ctrl button 1', 'ctrl button 2', 'ctrl button 3')
    mb.variable.set('ctrl button 3')
    mb.frame.grid(row = 0, column = 0, sticky = 'w')
    mb.add_callback(self.bind_placement_button_cb)
    self.placement_button = mb

    mbl = Tkinter.Label(pmf, text = ' to place/move markers')
    mbl.grid(row = 0, column = 1, sticky = 'w')

    row = row+1
    distance_label = Tkinter.Label(pmf, text = ' distance' )
    distance_label.grid(row=row, column = 0, sticky = 'w')
    self.distance_string=StringVar()
    distance_entry = Tkinter.Entry(pmf, width=4, textvariable=self.distance_string, state='readonly')
    self.distance_string.set("0.00")
    distance_entry.grid(row=row, column = 1, sticky = 'w')

    pm = Hybrid.Checkbutton(frame, 'Place markers on spots with mouse', 1)
    pm.button.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    self.place_markers_on_data = pm.variable
    pm.callback(self.bind_placement_button_cb)

    dm = Hybrid.Checkbutton(frame, 'Drop markers on empty space with mouse', 0)
    dm.button.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    self.place_markers_on_space = dm.variable
    dm.callback(self.bind_placement_button_cb)

    mm = Hybrid.Checkbutton(frame, 'Move markers with mouse', 0)
    mm.button.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    self.move_markers = mm.variable
    mm.callback(self.bind_placement_button_cb)

    self.bind_placement_button_cb()
    
    mc = Hybrid.Checkbutton(frame, 'Marker color matches volume color', 0)
    mc.button.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    self.marker_matches_volume_color = mc.variable
    
    lm = Hybrid.Checkbutton(frame, 'Link new marker to selected marker', 1)
    lm.button.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    self.link_to_selected = lm.variable

    lc = Hybrid.Checkbutton(frame, 'Link consecutively selected markers', 0)
    lc.callback(self.consecutive_selection_cb)
    lc.button.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    self.link_consecutive = lc.variable

  # ---------------------------------------------------------------------------
  #
  def make_marker_sets_panel(self, frame):

    import Tkinter
    from CGLtk import Hybrid

    row = 0
    frame.columnconfigure(0, weight = 1)
    
    msl = Hybrid.Scrollable_List(frame, 'Marker Sets', 2,
                                 self.marker_set_selection_cb)
    self.marker_set_listbox = msl.listbox
    msl.frame.grid(row = row, column = 0, sticky = 'news')
    frame.rowconfigure(row, weight = 1)
    row = row + 1

    rms = Hybrid.Entry(frame, 'Rename marker set ', 25)
    rms.frame.grid(row = row, column = 0, sticky = 'ew')
    row = row + 1
    self.marker_set_rename = rms.variable
    rms.entry.bind('<KeyPress-Return>', self.rename_marker_set_cb)

    bf = Tkinter.Frame(frame)
    bf.grid(row = row, column = 0, sticky = 'w')
    row = row + 1

    save_menu_entries = (
      ('save current marker set', self.save_marker_set_cb),
      ('save current marker set as...', self.save_marker_set_as_cb),
      ('save all marker sets as...', self.save_all_marker_sets_cb),
      ('save selected marker sets as...', self.save_selected_marker_sets_cb)
      )

    sm = Hybrid.Menu(bf, 'Export XML', save_menu_entries)
    sm.button.configure(borderwidth = 2, relief = 'raised')
    sm.button.grid(row = 0, column = 0, sticky = 'w')
    
    mbr = Hybrid.Button_Row(bf, '',
                            (('New', self.new_marker_set_cb),
                             ('Remove', self.close_marker_set_cb)))
    mbr.frame.grid(row = 0, column = 1, sticky = 'w')
    
  # ---------------------------------------------------------------------------
  #
  def make_slice_panel(self, frame):

    import Tkinter
    from CGLtk import Hybrid

    row = 0
    
    frame.columnconfigure(0, weight = 1)
    
    c = Tkinter.Canvas(frame, height = 100)
    frame.rowconfigure(row, weight = 1)
    c.grid(row = row, column = 0, sticky = 'news')
    row = row + 1
    self.canvas = c

    sc = Hybrid.Checkbutton(frame, 'Slice graph color matches volume color', 0)
    sc.button.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    self.use_volume_colors = sc.variable

    trf = Tkinter.Frame(frame)
    trf.grid(row = row, column = 0, sticky = 'nw')
    row = row + 1
    
    trb = Tkinter.Button(trf, text = 'Reset',
			 command = self.reset_thresholds_cb)
    trb.grid(row = 0, column = 0, sticky = 'w')

    trl = Tkinter.Label(trf, text = ' thresholds to displayed levels')
    trl.grid(row = 0, column = 1, sticky = 'w')

    slf = Tkinter.Frame(frame)
    slf.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    
    ss = Hybrid.Checkbutton(slf, 'Show slice line using color ', 0)
    ss.button.grid(row = 0, column = 0, sticky = 'w')
    ss.callback(self.show_slice_line_cb)
    self.show_slice_line = ss.variable

    from CGLtk.color import ColorWell
    sc = ColorWell.ColorWell(slf)
    self.slice_color = sc
    sc.showColor((1,1,1))
    sc.grid(row = 0, column = 1, sticky = 'w')

  # ---------------------------------------------------------------------------
  # After user resizes dialog by hand it will not resize automatically when
  # panels are added or deleted.  This allows the automatic resize to happen.
  #
  def allow_toplevel_resize_cb(self):

    self.toplevel_widget.geometry('')

  # ---------------------------------------------------------------------------
  #
  def mouse_mode_icon(self):

    import os.path
    icon_path = os.path.join(os.path.dirname(__file__), 'marker.gif')
    from PIL import Image
    image = Image.open(icon_path)
    from chimera import chimage
    from chimera import tkgui
    icon = chimage.get(image, tkgui.app)
    return icon
      
  # ---------------------------------------------------------------------------
  #
  def map(self, event):

    if self.show_note_trigger == None:
      ct = chimera.triggers
      self.show_note_trigger = \
        ct.addHandler('selection changed', self.show_note_cb, None)

  # ---------------------------------------------------------------------------
  #
  def unmap(self, event):

    if self.show_note_trigger:
      ct = chimera.triggers
      ct.deleteHandler('selection changed', self.show_note_trigger)
      self.show_note_trigger = None
    
  # ---------------------------------------------------------------------------
  #
  def save_session_cb(self, trigger, x, file):

    import session
    session.save_path_tracer_state(self, file)
    
  # ---------------------------------------------------------------------------
  #
  def close_session_cb(self, trigger, a1, a2):

    self.remove_marker_sets(self.marker_sets)

  # ---------------------------------------------------------------------------
  #
  def ImportXML(self):

    self.open_marker_set_cb()
    
  # ---------------------------------------------------------------------------
  #
  def open_marker_set_cb(self):

    if self.open_dialog == None:
      import OpenSave
      d = OpenSave.OpenModeless(title = 'Open Marker Set',
                                filters = [('Chimera Markers', '*.cmm')],
                                defaultFilter = 0,
                                command = self.open_file_dialog_cb)
      self.open_dialog = d
    else:
      self.open_dialog.enter()

  # ---------------------------------------------------------------------------
  #
  def open_file_dialog_cb(self, apply, dialog):

    if not apply:
      return            # User pressed Cancel

    for path in dialog.getPaths():
      self.open_marker_set(path)

  # ---------------------------------------------------------------------------
  #
  def open_marker_set(self, path):
    
    file = open(path, 'r')
    import markerset
    marker_sets = markerset.load_marker_set_xml(file)
    file.close()
    
    if len(marker_sets) == 1:
      marker_sets[0].file_path = path

    for ms in marker_sets:
      self.add_marker_set(ms)

    if len(chimera.openModels.list()) == len(marker_sets):
      chimera.viewer.viewAll()    # Make camera show all models
    
  # ---------------------------------------------------------------------------
  #
  def save_marker_set_cb(self):

    if self.active_marker_set:
      self.save_marker_sets([self.active_marker_set], ask_path = 0)
      
  # ---------------------------------------------------------------------------
  #
  def save_marker_set_as_cb(self):

    if self.active_marker_set:
      self.save_marker_sets([self.active_marker_set], ask_path = 1)
    
  # ---------------------------------------------------------------------------
  #
  def save_all_marker_sets_cb(self):

    self.save_marker_sets(self.marker_sets, ask_path = 1)
    
  # ---------------------------------------------------------------------------
  #
  def save_selected_marker_sets_cb(self):

    mslist = self.selected_marker_sets()
    self.save_marker_sets(mslist, ask_path = 1)

  # ---------------------------------------------------------------------------
  # Save marker sets in one file.
  #
  def save_marker_sets(self, mslist, ask_path):

    if len(mslist) == 0:
      self.message('No marker sets saved')
      return

    path = self.get_file_path(mslist, ask_path)

    if not path:
      return

    out = open(path, 'w')
    import markerset
    markerset.save_marker_sets(mslist, out)
    out.close()

    for ms in mslist:
      ms.file_path = path

  # ---------------------------------------------------------------------------
  #
  def get_file_path(self, mslist, ask_path):

    paths = {}
    for ms in mslist:
      paths[ms.file_path] = 1

    if len(paths) == 1:
      common_path = paths.keys()[0]
    else:
      common_path = None
      
    if not ask_path and common_path:
      return common_path
    
    path_list = filter(lambda p: p, paths.keys())
    if path_list:
      default_path = path_list[0]
    else:
      default_path = None

    if len(mslist) == 1:
      title = 'Save Marker Set %s' % ms.name
    else:
      title = 'Save %d Marker Sets' % len(mslist)
      
    path = self.ask_for_save_path(title, default_path)

    return path

  # ---------------------------------------------------------------------------
  #
  def ask_for_save_path(self, title, default_path):

    if default_path:
      import os.path
      initialdir, initialfile = os.path.split(default_path)
    else:
      initialdir, initialfile = None, None

    import OpenSave
    d = OpenSave.SaveModal(title = title,
                           initialdir = initialdir,
                           initialfile = initialfile,
                           filters = [('Chimera Markers', '*.cmm', '')])
    paths_and_types = d.run(self.toplevel_widget)
    if paths_and_types and len(paths_and_types) == 1:
      path = paths_and_types[0][0]
    else:
      path = None

    return path

  # ---------------------------------------------------------------------------
  #
  def close_marker_set_cb(self):

    self.remove_marker_sets(self.selected_marker_sets())

  # ---------------------------------------------------------------------------
  #
  def remove_marker_sets(self, marker_sets):
    
    mstable = {}
    for ms in marker_sets:
      mstable[ms] = 1

    open = []
    for ms in self.marker_sets:
      if mstable.has_key(ms):
        ms.close()
      else:
        open.append(ms)
    self.marker_sets = open

    if self.active_marker_set and mstable.has_key(self.active_marker_set):
      if len(self.marker_sets) >= 1:
        ams = self.marker_sets[0]
      else:
        ams = None
      self.set_active_marker_set(ams)

    self.update_marker_set_listbox()

  # ---------------------------------------------------------------------------
  #
  def set_active_marker_set(self, marker_set):

    self.active_marker_set = marker_set
    if marker_set:
      name = marker_set.name
    else:
      name = ''
    self.marker_set_rename.set(name)
    self.marker_set_menu.variable.set(name, invoke_callbacks = 0)
          
  # ---------------------------------------------------------------------------
  #
  def rename_marker_set_cb(self, event):

    ams = self.active_marker_set
    if ams == None:
      return
    
    ams.name = self.marker_set_rename.get()
    i = self.marker_sets.index(ams)

    listbox = self.marker_set_listbox
    listbox.delete(i)
    listbox.insert(i, ams.name)

    menu = self.marker_set_menu
    menu.remove_entry(i)
    menu.insert_entry(i, ams.name)
    menu.variable.set(ams.name, invoke_callbacks = 0)
    
  # ---------------------------------------------------------------------------
  #
  def update_marker_set_listbox(self):

    listbox = self.marker_set_listbox
    listbox.delete(0, 'end')
    for ms in self.marker_sets:
      listbox.insert('end', ms.name)

    menu = self.marker_set_menu
    menu.remove_all_entries()
    for ms in self.marker_sets:
      menu.add_entry(ms.name)

    ams = self.active_marker_set
    if ams:
      menu.variable.set(ams.name, invoke_callbacks = 0)

  # ---------------------------------------------------------------------------
  #
  def marker_set_selection_cb(self, event):

    mslist = self.selected_marker_sets()
    if len(mslist) == 1:
      self.set_active_marker_set(mslist[0])

  # ---------------------------------------------------------------------------
  # If no list box line is selected, include the active marker set.
  #
  def selected_marker_sets(self):

    indices = map(int, self.marker_set_listbox.curselection())
    marker_sets = map(lambda i, msl=self.marker_sets: msl[i], indices)

    if len(marker_sets) == 0 and self.active_marker_set:
      marker_sets = [self.active_marker_set]
      
    return marker_sets

  # ---------------------------------------------------------------------------
  #
  def new_marker_set_cb(self):

    name = 'marker set %d' % (len(self.marker_sets) + 1)
    return self.new_marker_set(name)

  # ---------------------------------------------------------------------------
  #
  def new_marker_set(self, name):

    import markerset
    ms = markerset.Marker_Set(name)
    self.add_marker_set(ms)
    return ms
    
  # ---------------------------------------------------------------------------
  #
  def add_marker_set(self, marker_set):
    
    self.marker_sets.append(marker_set)
    self.marker_set_listbox.insert('end', marker_set.name)
    self.marker_set_menu.add_entry(marker_set.name)
    self.set_active_marker_set(marker_set)

  # ---------------------------------------------------------------------------
  #
  def marker_set_menu_cb(self):

    name = self.marker_set_menu.variable.get()
    ms = self.find_marker_set_by_name(name)
    self.set_active_marker_set(ms)

  # ---------------------------------------------------------------------------
  #
  def find_marker_set_by_name(self, name):
    
    for ms in self.marker_sets:
      if ms.name == name:
        return ms

    return None
    
  # ---------------------------------------------------------------------------
  #
  def bind_placement_button_cb(self):

    bind = (self.place_markers_on_data.get() or
            self.place_markers_on_space.get() or
            self.move_markers.get())
    self.bind_placement_button(bind)
    
  # ---------------------------------------------------------------------------
  #
  def bind_placement_button(self, bind):

    if bind:
      button, modifiers = self.placement_button_spec()
      if self.bound_button != (button, modifiers):
        self.bind_placement_button(0)
        from chimera import mousemodes
        mousemodes.setButtonFunction(button, modifiers, 'mark volume')
        self.bound_button = (button, modifiers)
    elif self.bound_button:
      button, modifiers = self.bound_button
      from chimera import mousemodes
      def_mode = mousemodes.getDefault(button, modifiers)
      if def_mode:
        mousemodes.setButtonFunction(button, modifiers, def_mode)
      self.bound_button = None

  # ---------------------------------------------------------------------------
  #
  def placement_button_spec(self):

    name = self.placement_button.variable.get()
    name_to_bspec = {'button 1':('1', []), 'ctrl button 1':('1', ['Ctrl']),
                     'button 2':('2', []), 'ctrl button 2':('2', ['Ctrl']),
                     'button 3':('3', []), 'ctrl button 3':('3', ['Ctrl'])}
    bspec = name_to_bspec[name]
    return bspec
    
  # ---------------------------------------------------------------------------
  #
  def grab_marker(self, pointer_x, pointer_y):

    import markerset
    marker = markerset.pick_marker(pointer_x, pointer_y, self.marker_sets)
    if marker:
      self.message('Grabbed marker')
      self.last_pointer_xy = (pointer_x, pointer_y)
    self.grabbed_marker = marker

    return marker
    
  # ---------------------------------------------------------------------------
  #
  def add_marker(self, pointer_x, pointer_y,
		 place_markers_on_data, place_markers_on_space):

    slice, no_slice_warning = self.data_slice(pointer_x, pointer_y)

    self.erase_slice_line()
        
    if slice:
      self.display_slice_line(slice)
      self.update_slice_graphs(slice)

    marker_set = self.active_marker_set
    if marker_set == None:
      marker_set = self.new_marker_set_cb()

    if (slice and place_markers_on_data and
        self.mark_first_maximum(slice, marker_set)):
      return

    if place_markers_on_space:
      if slice:
	self.mark_slice_midpoint(slice, marker_set)
      else:
	self.mark_clip_planes_midpoint(pointer_x, pointer_y, marker_set)
      return

    if place_markers_on_data and slice == None:
      self.message(no_slice_warning)
      return

    self.message('')
    
  # ---------------------------------------------------------------------------
  # Used with 3D input devices.
  #
  # The user interface option to turn on and off marker placement and motion
  # apply are intended only to restrict mouse input.  So they are not checked
  # here.
  #
  def add_marker_3d(self, xyz):

    marker_set = self.active_marker_set
    if marker_set == None:
      marker_set = self.new_marker_set_cb()

    if not self.mark_data(xyz, marker_set):
      self.mark_point(xyz, marker_set)
    
  # ---------------------------------------------------------------------------
  #
  def grab_marker_3d(self, xyz):

    import markerset
    marker = markerset.pick_marker_3d(xyz, self.marker_sets)
    if marker:
      self.message('Grabbed marker')
    self.grabbed_marker = marker
    return marker
    
  # ---------------------------------------------------------------------------
  #
  def select_marker_3d(self, xyz):

    import markerset
    marker = markerset.pick_marker_3d(xyz, self.marker_sets)
    if marker:
      self.select_marker(marker)
    return marker

  # ---------------------------------------------------------------------------
  #
  def data_slice(self, pointer_x, pointer_y):
    
    r = self.data_region()
    if r == None:
      return None, 'No volume region'

    xyz_in, xyz_out, model = self.volume_segment(r, pointer_x, pointer_y)

    if model == None:
      return None, 'Volume not shown'

    if xyz_in == None or xyz_out == None:
      return None, 'No intersection with volume'

    slice = Slice(r, xyz_in, xyz_out)

    return slice, ''

  # ---------------------------------------------------------------------------
  #
  def volume_segment(self, data_region, pointer_x, pointer_y):
    
    mlist = data_region.models()
    if len(mlist) == 0:
      return None, None, None
    
    from VolumeViewer import slice
    m = mlist[0]
    xyz_in, xyz_out = slice.box_intercepts(pointer_x, pointer_y,
                                           m.openState.xform,
                                           data_region.xyz_region())

    return xyz_in, xyz_out, m

  # ---------------------------------------------------------------------------
  #
  def reset_thresholds_cb(self):

    if self.shown_slice:
      self.shown_slice.reset_thresholds()

  # ---------------------------------------------------------------------------
  #
  def update_slice_graphs(self, slice):
    
    c = self.canvas
    c.delete('all')
    slice.show_slice_graphs(c, self.use_volume_colors.get())
    self.shown_slice = slice
    
  # ---------------------------------------------------------------------------
  #
  def mark_first_maximum(self, slice, marker_set):

    t_max, v_max, trace = slice.first_maximum_above_threshold()
    if t_max == None:
      return 0

    self.show_slice_maximum(t_max)

    dr_xyz = linear_combination(1-t_max, slice.xyz_in, t_max, slice.xyz_out)
    ms_xyz = transform_coordinates(dr_xyz, slice.data_region.transform(),
				   marker_set.transform())
    if self.marker_matches_volume_color.get():
      rgba = trace.visible_data.volume_rgba(v_max)
    else:
      rgba = self.marker_color.rgba
    marker_radius, link_radius = self.marker_and_link_radius(marker_set,
							     slice.data_region)
    marker = self.drop_and_link_marker(ms_xyz, rgba,
				       marker_radius, link_radius,
                                       marker_set)
    self.message('Dropped marker on data')
    slice.marker = marker
    
    return 1
    
  # ---------------------------------------------------------------------------
  # Place marker if data value is above detection threshold.
  #
  # Xyz position must be in Chimera world coordinates.
  #
  def mark_data(self, xyz, marker_set):

    dr = self.data_region()
    if dr == None:
      return 0

    from VolumeViewer import slice
    dr_xyz = slice.eye_to_object_coordinates(xyz, dr.transform())
    ms_xyz = slice.eye_to_object_coordinates(xyz, marker_set.transform())

    visible_data = self.visible_data_above_threshold(dr, dr_xyz)
    if visible_data == None:
      return 0

    if self.marker_matches_volume_color.get():
      data_value = visible_data.interpolated_value(dr_xyz)
      rgba = visible_data.volume_rgba(data_value)
    else:
      rgba = self.marker_color.rgba
    marker_radius, link_radius = self.marker_and_link_radius(marker_set)
    marker = self.drop_and_link_marker(ms_xyz, rgba,
				       marker_radius, link_radius,
                                       marker_set)
    self.message('Dropped marker on data')
    return 1

  # ---------------------------------------------------------------------------
  #
  def visible_data_above_threshold(self, data_region, xyz):

    vdlist = visible_data(data_region)
    for visdata in vdlist:
      if visdata.interpolated_value(xyz) > visdata.threshold():
	return visdata
    return None

  # ---------------------------------------------------------------------------
  #
  def mark_slice_midpoint(self, slice, marker_set):

    dr_xyz = linear_combination(.5, slice.xyz_in, .5, slice.xyz_out)
    ms_xyz = transform_coordinates(dr_xyz, slice.data_region.transform(),
				   marker_set.transform())
    rgba = self.marker_color.rgba
    marker_radius, link_radius = self.marker_and_link_radius(marker_set,
							     slice.data_region)
    self.drop_and_link_marker(ms_xyz, rgba, marker_radius, link_radius,
                              marker_set)
    self.message('Dropped marker on empty space')
    
  # ---------------------------------------------------------------------------
  #
  def mark_clip_planes_midpoint(self, pointer_x, pointer_y, marker_set):

    from VolumeViewer import slice
    xyz_in, xyz_out = slice.clip_plane_points(pointer_x, pointer_y)
    xyz = linear_combination(.5, xyz_in, .5, xyz_out)
    self.mark_point(xyz, marker_set)
    
  # ---------------------------------------------------------------------------
  # Xyz position must be in Chimera world coordinates.
  #
  def mark_point(self, xyz, marker_set):

    from VolumeViewer import slice
    ms_xyz = slice.eye_to_object_coordinates(xyz, marker_set.transform())
    rgba = self.marker_color.rgba
    marker_radius, link_radius = self.marker_and_link_radius(marker_set)
    self.drop_and_link_marker(ms_xyz, rgba, marker_radius, link_radius,
                              marker_set)
    self.message('Dropped marker on empty space')

  # ---------------------------------------------------------------------------
  # Xyz position must be in marker set coordinates.
  #
  def drop_and_link_marker(self, xyz, rgba, marker_radius, link_radius,
                           marker_set):

    marker = marker_set.place_marker(xyz, rgba, marker_radius)
    if self.link_to_selected.get():
      markers = self.selected_markers()
      if len(markers) == 1:
        self.create_link(marker, markers[0], self.link_color.rgba, link_radius)
    self.select_marker(marker)
    return marker

  # ---------------------------------------------------------------------------
  # Put vertical line on graph to indicate first maximum.
  #
  def show_slice_maximum(self, t_max):
          
    c = self.canvas
    w = c.winfo_width()
    x = int(t_max*w)
    h = c.winfo_height()
    self.max_line_id = c.create_line(x, 0, x, h)
    c.tag_bind(self.max_line_id, "<Button1-Motion>", self.move_marker_cb,
               add = 1)

  # ---------------------------------------------------------------------------
  #
  def create_link(self, m1, m2, rgba, radius):

    if m1.marker_set != m2.marker_set or m1 == m2 or m1.linked_to(m2):
      return

    import markerset
    e = markerset.Link(m1, m2, rgba, radius)

    map(lambda e: e.deselect(), self.selected_links())
    e.select()
    self.links_list.append(e)
    
  # ---------------------------------------------------------------------------
  #
  def move_marker(self, pointer_x, pointer_y, shift):

    m = self.grabbed_marker
    if m == None:
      return

    xyz = m.xyz()
    xform = m.marker_set.transform()
    last_x, last_y = self.last_pointer_xy
    dx = pointer_x - last_x
    dy = -(pointer_y - last_y)
    if shift:
      if abs(dx) > abs(dy):   dz = -dx
      else:                   dz = -dy
      dx = dy = 0
    else:
      dz = 0

    vx, vy, vz = screen_axes(xyz, xform)
    delta_xyz = linear_combination_3(dx, vx, dy, vy, dz, vz)
    new_xyz = map(lambda a,b: a+b, xyz, delta_xyz)
    m.set_xyz(new_xyz)

    self.last_pointer_xy = (pointer_x, pointer_y)
    if len(self.links_list) > 0:
    	for next_link in self.links_list:
		if next_link.marker1==self.grabbed_marker or next_link.marker2==self.grabbed_marker:
    			next_link.print_link_distance(self.distance_string)
    
  # ---------------------------------------------------------------------------
  # Used with 3D input devices.
  #
  def move_marker_3d(self, xyz):

    m = self.grabbed_marker
    if m == None:
      return

    from VolumeViewer import slice
    ms_xyz = slice.eye_to_object_coordinates(xyz, m.marker_set.transform())

    m.set_xyz(ms_xyz)
  
  # ---------------------------------------------------------------------------
  #
  def ungrab_marker(self):

    self.grabbed_marker = None
    self.message('')
  
  # ---------------------------------------------------------------------------
  #
  def selected_markers(self):

    mlist = []
    for ms in self.marker_sets:
      mlist = mlist + ms.selected_markers()
    return mlist
    
  # ---------------------------------------------------------------------------
  # Select new marker and deselect other markers.
  #
  def select_marker(self, marker):

    marker.select()
    for m in self.selected_markers():
      if m != marker:
	m.deselect()
    
  # ---------------------------------------------------------------------------
  #
  def unselect_all_markers(self):

    for m in self.selected_markers():
      m.deselect()
  
  # ---------------------------------------------------------------------------
  #
  def selected_links(self):

    llist = []
    for ms in self.marker_sets:
      llist = llist + ms.selected_links()
    return llist
  
  # ---------------------------------------------------------------------------
  #
  def show_markers(self, show):

    marker_set = self.active_marker_set
    if marker_set:
      marker_set.show_markers(show)

  # ---------------------------------------------------------------------------
  #
  def marker_note_cb(self, event):

    note_text = self.marker_note.get()
    for m in self.selected_markers():
      m.set_note(note_text)
      m.show_note(1)
          
  # ---------------------------------------------------------------------------
  #
  def note_color_cb(self, rgba):

    for m in self.chosen_note_markers():
      m.set_note_rgba(self.note_color.rgba)
    
  # ---------------------------------------------------------------------------
  #
  def show_marker_notes(self, show):

    markers = self.chosen_note_markers()
    for m in markers:
      m.show_note(show)
    
  # ---------------------------------------------------------------------------
  #
  def delete_marker_notes_cb(self):

    for m in self.selected_markers():
      m.set_note('')
          
  # -------------------------------------------------------------------------
  # Update marker note entry field when marker is selected.
  #
  def show_note_cb(self, trigger, user_data, selection):

    markers = self.selected_markers()
    if len(markers) == 1:
      m = markers[0]
      note = m.note()
      note_rgba = m.note_rgba()
    else:
      note = ''
      note_rgba = (1,1,1,1)
    self.marker_note.set(note)
    self.note_color.showColor(note_rgba, doCallback = 0)
    
  # ---------------------------------------------------------------------------
  #
  def chosen_note_markers(self):
    
    if self.selected_notes_only.get():
      markers = self.selected_markers()
    else:
      markers = self.all_current_markers()

    return markers
    
  # ---------------------------------------------------------------------------
  #
  def all_current_markers(self):
      
    marker_set = self.active_marker_set
    if marker_set == None:
      markers = []
    else:
      markers = marker_set.markers()

    return markers
  
  # ---------------------------------------------------------------------------
  #
  def show_links(self, show):

    ams = self.active_marker_set
    if ams:
      ams.show_links(show)
  
  # ---------------------------------------------------------------------------
  #
  def show_slice_line_cb(self):

    if not self.show_slice_line.get():
      self.erase_slice_line()
  
  # ---------------------------------------------------------------------------
  # Make a VRML line containing a single line connecting 2 points.
  #
  def display_slice_line(self, slice):

    if self.show_slice_line.get():
      mlist = slice.data_region.models()
      if len(mlist) == 0:
        return
      model = mlist[0]
      vrml = line_vrml(slice.xyz_in, slice.xyz_out, self.slice_color.rgba)
      lm = chimera.openModels.open(vrml, 'VRML', sameAs = model)[0]
      self.slice_line_model = lm
  
  # ---------------------------------------------------------------------------
  #
  def erase_slice_line(self):

    if self.slice_line_model:
      close_model(self.slice_line_model)
      self.slice_line_model = None
    
  # ---------------------------------------------------------------------------
  #
  def move_marker_cb(self, event):

    x = event.x
    c = self.canvas

    h = c.winfo_height()
    c.coords(self.max_line_id, x, 0, x, h)

    if self.shown_slice:
      slice = self.shown_slice
      if hasattr(slice, 'marker'):
        t = float(x) / slice.graph_width
        xyz = linear_combination(1-t, slice.xyz_in, t, slice.xyz_out)
        slice.marker.set_xyz(xyz)
      
  # ---------------------------------------------------------------------------
  #
  def marker_and_link_radius(self, marker_set, data_region = None):

    if data_region:
      marker_radius = self.marker_radius(data_region)
      link_radius = self.link_radius(data_region)
    else:
      marker_radius = self.marker_radius(marker_set = marker_set)
      link_radius = self.link_radius()
      if link_radius == None:
        link_radius = .5 * marker_radius

    return marker_radius, link_radius
  
  # ---------------------------------------------------------------------------
  #
  def marker_radius_cb(self, event):

    radius = self.marker_radius()
    if radius == None:
      return
    
    for m in self.selected_markers():
      m.set_radius(radius)
      
  # ---------------------------------------------------------------------------
  #
  def marker_radius(self, data_region = None, marker_set = None):
    
    rstring = self.marker_radius_entry.get()
    try:
      radius = float(rstring)
      if radius <= 0:
        radius = None
    except ValueError:
      radius = None

    if radius == None and data_region:
      radius = data_plane_spacing(data_region)

    if radius == None and marker_set:
      mlist = marker_set.markers()
      if len(mlist) > 0:
	radius = mlist[0].radius()
      else:
	radius = .01 * clip_plane_spacing()

    return radius
  
  # ---------------------------------------------------------------------------
  #
  def link_radius_cb(self, event):

    radius = self.link_radius()
    if radius == None:
      return
    
    for e in self.selected_links():
      e.set_radius(radius)
      
  # ---------------------------------------------------------------------------
  #
  def link_radius(self, data_region = None):
    
    rstring = self.link_radius_entry.get()
    try:
      radius = float(rstring)
      if radius < 0:
        radius = None
    except ValueError:
      radius = None

    if radius == None and data_region:
      radius = .5 * data_plane_spacing(data_region)

    return radius
          
  # ---------------------------------------------------------------------------
  #
  def link_color_cb(self, rgba):

    for e in self.selected_links():
      e.set_rgba(self.link_color.rgba)
          
  # ---------------------------------------------------------------------------
  #
  def marker_color_cb(self, rgba):

    for m in self.selected_markers():
      m.set_rgba(self.marker_color.rgba)
    
  # ---------------------------------------------------------------------------
  #
  def data_region(self):

    from VolumeViewer import active_volume
    return active_volume()
  
  # ---------------------------------------------------------------------------
  # This code relies on markers being implemented as atoms.
  #
  def consecutive_selection_cb(self):

    from chimera import triggers
    if self.link_consecutive.get():
      if self.form_link_trigger == None:
        self.form_link_trigger = \
          triggers.addHandler('selection changed', self.form_link_cb, None)
        markers = self.selected_markers()
        if len(markers) == 1:
          self.last_selected_marker = markers[0]
    elif self.form_link_trigger:
      triggers.deleteHandler('selection changed', self.form_link_trigger)
      self.form_link_trigger = None
  
  # ---------------------------------------------------------------------------
  # Link consecutively selected_markers.
  #
  def form_link_cb(self, trigger, user_data, selection):

    markers = self.selected_markers()
    if len(markers) == 0:
      self.last_selected_marker = None
    if len(markers) == 1:
      marker = markers[0]
      if self.last_selected_marker:
        link_radius = self.link_radius()
        if link_radius == None:
          link_radius = .5 * marker.radius()
        self.create_link(marker, self.last_selected_marker,
                         self.link_color.rgba, link_radius)
      self.last_selected_marker = marker
    
  # ---------------------------------------------------------------------------
  #
  def delete_markers_cb(self):

    selected = self.selected_markers()
    if (self.shown_slice and
        hasattr(self.shown_slice, 'marker') and
        self.shown_slice.marker in selected):
      delattr(self.shown_slice, 'marker')
    if self.last_selected_marker in selected:
      self.last_selected_marker = None
    if self.grabbed_marker in selected:
      self.grabbed_marker = None
    for m in selected:
      m.delete()

  # ---------------------------------------------------------------------------
  #
  def delete_links_cb(self):

    links = self.selected_links()
    map(lambda e: e.delete(), links)

  # ---------------------------------------------------------------------------
  # Transfer selected markers to current marker set.
  #
  def transfer_markers_cb(self):

    ams = self.active_marker_set
    if ams == None:
      return

    mlist = self.selected_markers()

    import markerset
    count =  markerset.transfer_markers(mlist, ams)
    if count == None:
      self.message('Markers not transfered.  Markers in one set\n'
                   'cannot link to markers in a different set')
    else:
      self.message('Transfered %d markers.' % count)
    
  # ---------------------------------------------------------------------------
  #
  def show_curve_cb(self):

    ams = self.active_marker_set
    if ams == None:
      return

    self.unshow_curve_cb()

    radius = float_variable_value(self.curve_radius, 0)
    band_length = float_variable_value(self.curve_band_length, 0)
    subdivisions = integer_variable_value(self.curve_segment_subdivisions, 0)

    ams.show_curve(radius, band_length, subdivisions)

  # ---------------------------------------------------------------------------
  #
  def unshow_curve_cb(self):

    ams = self.active_marker_set
    if ams:
      ams.unshow_curve()
    
  # ---------------------------------------------------------------------------
  #
  def message(self, string):

    self.message_label['text'] = (string)
    self.message_label.update()

  # ---------------------------------------------------------------------------
  #
  def mouse_down_cb(self, viewer, event):

    grabbed = (self.move_markers.get() and self.grab_marker(event.x, event.y))
    if not grabbed:
      self.add_marker(event.x, event.y,
		      self.place_markers_on_data.get(),
		      self.place_markers_on_space.get())
    
  # ---------------------------------------------------------------------------
  #
  def mouse_drag_cb(self, viewer, event):

    if not self.move_markers.get():
      return

    shift_mask = 1
    shift = (event.state & shift_mask)
    self.move_marker(event.x, event.y, shift)
  
  # ---------------------------------------------------------------------------
  #
  def mouse_up_cb(self, viewer, event):

    self.ungrab_marker()
  
  # ---------------------------------------------------------------------------
  #
  def Close(self):

    self.erase_slice_line()
    self.link_consecutive.set(0)
    ModelessDialog.Close(self)

# -----------------------------------------------------------------------------
# Graph the data values along a line passing through a volume on a Tkinter
# canvas.  The volume data is graphed using a Trace object.
#
class Slice:

  def __init__(self, data_region, xyz_in, xyz_out):

    self.data_region = data_region
    self.xyz_in = xyz_in
    self.xyz_out = xyz_out

    self.canvas = None
    self.graph_width = None
    self.traces = []

  # ---------------------------------------------------------------------------
  #
  def show_slice_graphs(self, canvas, use_volume_colors):

    c = canvas
    self.canvas = c
    self.graph_width = c.winfo_width()

    vdlist = visible_data(self.data_region)

    n = len(vdlist)
    h = c.winfo_height()
    ystep = h / n
    if n > 1:
      ypad = ystep / 4
    else:
      ypad = 3                                                     # pixels
    ymin = ypad
    ymax = max(ypad, ystep - ypad)

    traces = []
    for visdata in vdlist:
      t = Trace(visdata, self.xyz_in, self.xyz_out, c, ymin, ymax,
		use_volume_colors)
      traces.append(t)
      ymin = ymin + ystep
      ymax = ymax + ystep
    self.traces = traces

  # ---------------------------------------------------------------------------
  #
  def reset_thresholds(self):

    dr = self.data_region
    if hasattr(dr, 'volume_path_threshold'):
      delattr(dr, 'volume_path_threshold')
    self.redraw_threshold_lines()

  # ---------------------------------------------------------------------------
  #
  def redraw_threshold_lines(self):

    for t in self.traces:
      t.redraw_threshold_line()

  # ---------------------------------------------------------------------------
  #
  def first_maximum_above_threshold(self):

    t_max = None
    v_max = None
    trace_max = None
    for trace in self.traces:
      t, v = trace.first_maximum_above_threshold()
      if t != None and (t_max == None or t < t_max):
        t_max = t
	v_max = v
        trace_max = trace
    return t_max, v_max, trace_max

# -----------------------------------------------------------------------------
#
class Visible_Data:

  def __init__(self, data_region):

    self.data_region = data_region

  # ---------------------------------------------------------------------------
  #
  def interpolated_value(self, xyz):

    matrix = self.data_region.matrix(read_matrix = 0)
    if type(matrix) == type(None):
      return 0

    ijk = xyz_to_ijk(self.data_region, xyz)
    v = interpolated_value(ijk, matrix)
    return v

  # ---------------------------------------------------------------------------
  #
  def threshold(self):

    dr = self.data_region
    if hasattr(dr, 'volume_path_threshold'):
      return dr.volume_path_threshold

    if dr.surface and dr.surface_levels:
      threshold = min(dr.surface_levels)
    elif dr.solid and dr.solid_levels:
      threshold = min(dr.solid_levels)[0]
    else:
      threshold = None

    return threshold

  # ---------------------------------------------------------------------------
  #
  def set_threshold(self, threshold):

    self.data_region.volume_path_threshold = threshold

  # ---------------------------------------------------------------------------
  #
  def using_displayed_threshold(self):

    return not hasattr(self.data_region, 'volume_path_threshold')

  # ---------------------------------------------------------------------------
  # Find the closest displayed data color for the given data value.
  # If no data value is given, use the color for the lowest threshold.
  # Otherwise use the color of the first surface level below the data value
  # if surfaces are shown.  If not level is below the data level use the
  # color of the lowest surface.  For the interpolated solid use the
  # interpolated color for the data, or if the data value
  # is outside the threshold range, use the closest endpoint color.
  #
  def volume_rgba(self, data_value = None):

    data_region = self.data_region

    if data_region.surface and data_region.surface_levels:
      tclist = map(lambda t,c: (t,c),
		   data_region.surface_levels, data_region.surface_colors)
      tclist.sort()
      if data_value != None:
	tclower = filter(lambda tc, v=data_value: tc[0] <= v , tclist)
	if tclower:
	  rgba = tclower[-1][1]
	else:
	  rgba = tclist[-1][1]
      else:
	rgba = tclist[0][1]
    elif data_region.solid and data_region.solid_levels:
      tclist = map(lambda tf,c: (tf[0],c),
		   data_region.solid_levels, data_region.solid_colors)
      tclist.sort()
      if data_value != None:
	if data_value <= tclist[0][0]:
	  rgba = tclist[0][1]
	elif data_value >= tclist[-1][0]:
	  rgba = tclist[-1][1]
	else:
	  k = 1
	  while tclist[k][0] <= data_value: 
	    k = k + 1
	  d0, rgba0 = tclist[k-1]
	  d1, rgba1 = tclist[k]
	  f = (data_value - d0) / (d1 - d0)
	  rgba = map(lambda c0, c1, f=f: (1-f)*c0 + f*c1, rgba0, rgba1)
      else:
	rgba = tclist[-1][1]
    else:
      rgba = (0,0,0,0)

    return rgba

# -----------------------------------------------------------------------------
# Graph the data values along a line passing through a volume.
#
class Trace:

  def __init__(self, visible_data, xyz_in, xyz_out,
               canvas, ymin, ymax, use_volume_color):

    self.visible_data = visible_data

    self.canvas = canvas
    self.canvas_y_range = (ymin, ymax)
    
    dr = visible_data.data_region
    self.trace = slice_data_values(dr, xyz_in, xyz_out)

    threshold = visible_data.threshold()

    self.value_range = self.calculate_value_range(threshold)
    self.plot_scale = self.calculate_plot_scale()

    self.use_volume_color = use_volume_color

    color = self.volume_color()
    xy_values = self.trace_values_to_canvas_xy(self.trace)
    canvas.create_line(xy_values, fill = color)

    if threshold != None:
      self.threshold_line_id = self.plot_threshold_line(threshold, color)
    else:
      self.threshold_line_id = None

  # ---------------------------------------------------------------------------
  #
  def calculate_value_range(self, threshold):
    
    values = map(lambda tv: tv[1], self.trace)
    min_value = min(values)
    max_value = max(values)

    if threshold != None:
      min_value = min(min_value, threshold)
      max_value = max(max_value, threshold)
    value_range = max_value - min_value

    return (min_value, max_value)

  # ---------------------------------------------------------------------------
  #
  def calculate_plot_scale(self):

    w = self.canvas.winfo_width()
    x_scale = w
    vrange = self.value_range[1] - self.value_range[0]
    if vrange == 0:
      y_scale = 1
    else:
      ymin, ymax = self.canvas_y_range
      y_scale = max(1, ymax - ymin) / float(vrange)

    return (x_scale, y_scale)

  # ---------------------------------------------------------------------------
  #
  def trace_values_to_canvas_xy(self, tvlist):

    x_scale, y_scale = self.plot_scale
    y0 = self.canvas_y_range[1]
    v0 = self.value_range[0]
    return map(lambda tv, xs=x_scale, y0=y0, ys=y_scale, v0=v0:
               (xs * tv[0], y0 - ys * (tv[1] - v0)),
               tvlist)

  # ---------------------------------------------------------------------------
  #
  def volume_color(self):

    if not self.use_volume_color:
      return 'black'
    
    color_256 = lambda c: min(255, max(0, int(256*c)))
    rgb_256 = map(color_256, self.visible_data.volume_rgba()[:3])
    color = '#%02x%02x%02x' % tuple(rgb_256)
    return color

  # ---------------------------------------------------------------------------
  #
  def plot_threshold_line(self, threshold, color):

    thresh_xy = self.trace_values_to_canvas_xy(((0,threshold),(1,threshold)))
    if self.visible_data.using_displayed_threshold():
      dash_pattern = '.'
    else:
      dash_pattern = '-'
    c = self.canvas
    id = c.create_line(thresh_xy, fill = color, dash = dash_pattern)
    c.tag_bind(id, "<Button1-Motion>", self.move_line_cb, add = 1)
    return id

  # ---------------------------------------------------------------------------
  #
  def redraw_threshold_line(self):

    color = self.volume_color()
    threshold = self.visible_data.threshold()
    if threshold != None:
      if self.threshold_line_id != None:
        self.canvas.delete(self.threshold_line_id)
      self.threshold_line_id = self.plot_threshold_line(threshold, color)

  # ---------------------------------------------------------------------------
  #
  def move_line_cb(self, event):

    line_id = self.threshold_line_id
    ymin, ymax = self.canvas_y_range
    min_value, max_value = self.value_range
    
    y = event.y
    c = self.canvas
    w = c.winfo_width()
    c.coords(line_id, 0, y, w, y)
    
    if ymax > ymin:
      f = float(y - ymin) / (ymax - ymin)
      threshold = (1-f) * max_value + f * min_value
      self.visible_data.set_threshold(threshold)
      c.itemconfigure(line_id, dash = '-')

  # ---------------------------------------------------------------------------
  #
  def first_maximum_above_threshold(self):

    thresh = self.visible_data.threshold()
    trace = self.trace
    n = len(trace)
    for k in range(n):
      t, v = trace[k]
      if v >= thresh:
        if ((k-1 < 0 or trace[k-1][1] < v) and
            (k+1 >= n or trace[k+1][1] <= v)):
          return t, v
    return None, None
# -----------------------------------------------------------------------------
#
def visible_data(data_region):

  if data_region.shown():
    return [Visible_Data(data_region)]
  return []

# -----------------------------------------------------------------------------
#
def slice_data_values(data_region, xyz_in, xyz_out):

  matrix = data_region.matrix(read_matrix = 0)
  if type(matrix) == type(None):
    return []

  d = distance(xyz_in, xyz_out)
  #
  # Sample step of 1/2 voxel size can easily miss single bright voxels.
  # A possible fix is to compute the extrema in each voxel the slice line
  # passes through.  Use these points instead of a uniform spaced sampling.
  #
  sample_step = .5 * data_plane_spacing(data_region)
  t_step = sample_step / d
  steps = 1 + max(1, int(1.0/t_step))

  ijk_in = xyz_to_ijk(data_region, xyz_in)
  ijk_out = xyz_to_ijk(data_region, xyz_out)

  trace = []
  for k in range(steps):
    t = min(1.0, k * t_step)
    ijk = linear_combination(1-t, ijk_in, t, ijk_out)
    v = interpolated_value(ijk, matrix)
    trace.append((t,v))

  return trace

# -----------------------------------------------------------------------------
#
def xyz_to_ijk(data_region, xyz):

  xyz_origin, xyz_step = data_region.xyz_origin_and_step()
  ijk = map(lambda a,b,c: float(a-b)/c, xyz, xyz_origin, xyz_step)
  return ijk

# -----------------------------------------------------------------------------
#
def clip_plane_spacing():

  c = chimera.viewer.camera
  view = 0
  left, right, bottom, top, znear, zfar, f = c.window(view)
  return zfar - znear

# -----------------------------------------------------------------------------
#
def data_plane_spacing(data_region):

  ijk_min, ijk_max, ijk_step = data_region.region
  data = data_region.data_set.data
  xyz_step = map(lambda a, b: a * b, data.xyz_step, ijk_step)
  spacing = min(xyz_step)
  return spacing

# -----------------------------------------------------------------------------
# Check if model already deleted before trying to close.
#
def close_model(m):

  model_deleted = 0
  try:
    m.display
  except RuntimeError:
    model_deleted = 1
    
  if not model_deleted:
    chimera.openModels.close([m])

# -----------------------------------------------------------------------------
# Return VRML for a line connecting two points.
#
def line_vrml(xyz_1, xyz_2, rgba):

  vrml_template = (
'''#VRML V2.0 utf8

Transform {
  children Shape {
    appearance Appearance {
      material Material {
        emissiveColor %s
        transparency %s
      }
    }
    geometry IndexedLineSet {
      coord Coordinate {
	point [ %s ]
      }
      coordIndex [ 0 1 ]
    }
  }
}
'''
  )

  rgb = '%.3g %.3g %.3g' % rgba[:3]
  transparency = '%.3g' % (1-rgba[3])
  pformat = '%.5g %.5g %.5g'
  p1 = pformat % xyz_1
  p2 = pformat % xyz_2
  points = '%s, %s' % (p1, p2)
  vrml = vrml_template % (rgb, transparency, points)

  return vrml

# -----------------------------------------------------------------------------
#
def interpolated_value(ijk, matrix):

  ib, jb, kb = map(lambda x, f=math.floor: int(f(x)), ijk)
  Ib, Jb, Kb = ib+1, jb+1, kb+1
  sk, sj, si = matrix.shape
  if ib >= 0 and Ib < si and jb >= 0 and Jb < sj and kb >= 0 and Kb < sk:
    io, jo, ko = ijk[0] - ib, ijk[1] - jb, ijk[2] - kb
    Io, Jo, Ko = 1-io, 1-jo, 1-ko
    v = (Io*(Jo*(Ko*matrix[kb,jb,ib] + ko*matrix[Kb,jb,ib]) +
             jo*(Ko*matrix[kb,Jb,ib] + ko*matrix[Kb,Jb,ib])) +
         io*(Jo*(Ko*matrix[kb,jb,Ib] + ko*matrix[Kb,jb,Ib]) +
             jo*(Ko*matrix[kb,Jb,Ib] + ko*matrix[Kb,Jb,Ib])))
  else:
    v = 0
  return v

# -----------------------------------------------------------------------------
# Return vx, vy, and vz screen vectors in object coordinates.
# The vx vector is scaled so that one screen pixel displacement in x is
# equivalent to an object coordinate displacement vx at the given xyz
# position.  The vy vector is scaled likewise.  The vz vector length
# is set to equal the vy vector length.
#
def screen_axes(xyz, object_xform):

  c = chimera.viewer.camera
  view = 0
  llx, lly, width, height = c.viewport(view)
  left, right, bottom, top, znear, zfar, f = c.window(view)

  if c.ortho:
    zratio = 1
  else:
    xyz_eye = object_to_eye_coordinates(xyz, object_xform)
    zeye = xyz_eye[2]
    eye_z = c.eyePos(view)[2]
    zratio = (eye_z - zeye) / znear
  
  xs = zratio * float(right - left) / width
  ys = zratio * float(top - bottom) / height
  zs = ys
  
  from VolumeViewer import slice
  ex, ey, ez = (xs,0,0), (0,ys,0), (0,0,zs)
  v0 = slice.eye_to_object_coordinates((0,0,0), object_xform)
  vx = slice.eye_to_object_coordinates(ex, object_xform)
  vx = map(lambda a,b: a-b, vx, v0)
  vy = slice.eye_to_object_coordinates(ey, object_xform)
  vy = map(lambda a,b: a-b, vy, v0)
  vz = slice.eye_to_object_coordinates(ez, object_xform)
  vz = map(lambda a,b: a-b, vz, v0)
  
  return vx, vy, vz

# -----------------------------------------------------------------------------
#
def transform_coordinates(from_xyz, from_transform, to_transform):

  xyz = object_to_eye_coordinates(from_xyz, from_transform)
  from VolumeViewer import slice
  to_xyz = slice.eye_to_object_coordinates(xyz, to_transform)
  return to_xyz

# -----------------------------------------------------------------------------
# Transform from object to eye coordinates
#
def object_to_eye_coordinates(xyz_object, object_xform):

  c_xyz_object = apply(chimera.Point, xyz_object)
  c_xyz_eye = object_xform.apply(c_xyz_object)
  xyz_eye = (c_xyz_eye.x, c_xyz_eye.y, c_xyz_eye.z)
  return xyz_eye

# -----------------------------------------------------------------------------
# Return vector a*u + b*v where a, b are scalars.
#
def linear_combination(a, u, b, v):

  return tuple(map(lambda uc, vc, a=a, b=b: a*uc + b*vc, u, v))
  
# -----------------------------------------------------------------------------
# Return vector a*u + b*v + c*w where a, b, c are scalars.
#
def linear_combination_3(a, u, b, v, c, w):

  return tuple(map(lambda uk, vk, wk, a=a, b=b, c=c: a*uk + b*vk + c*wk,
                   u, v, w))

# -----------------------------------------------------------------------------
#
def distance(u, v):

  sum2 = 0
  for a in range(len(u)):
    d = u[a] - v[a]
    sum2 = sum2 + d * d

  return math.sqrt(sum2)
  
# -----------------------------------------------------------------------------
#
def integer_variable_value(v, default = None):
  try:
    return int(v.get())
  except:
    return default
    
# -----------------------------------------------------------------------------
#
def float_variable_value(v, default = None):
  try:
    return float(v.get())
  except:
    return default
  
# -----------------------------------------------------------------------------
#
def volume_path_dialog(create = 0):

  from chimera import dialogs
  return dialogs.find(Volume_Path_Dialog.name, create=create)
  
# -----------------------------------------------------------------------------
#
def show_volume_path_dialog():

  from chimera import dialogs
  return dialogs.display(Volume_Path_Dialog.name)
    
# -----------------------------------------------------------------------------
#
from chimera import dialogs
dialogs.register(Volume_Path_Dialog.name, Volume_Path_Dialog, replace = 1)
