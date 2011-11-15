# -------------------------------------------------------------------------
# MeasureStick/__init__.py
# 
# Segment Volume package - Measure Stick module
#
# Author:
#       Lavu Sridhar, Baylor College of Medicine (BCM)
#
# Revisions:
#       2005.07.05: Lavu Sridhar, BCM
#       2005.07.15: Lavu Sridhar, BCM
#       2005.09.06: Lavu Sridhar, BCM (VU 1.2129 Chimera)
#
# To Do:
#       See comments marked with # @
#
# Key:
#       VU: Version Upgrade
#
"""Measuring stick.

GUI to measure distance between a marker set link.
"""

# -------------------------------------------------------------------------

# general modules
import os

import Tkinter

# chimera related modules

import chimera
from chimera.baseDialog import ModelessDialog
from CGLtk import Hybrid

from chimera import replyobj

# -------------------------------------------------------------------------

class Measure_Stick(ModelessDialog):
    """Class: Measure_Stick()

    The main GUI dialog for measuring stick.
    """

    title= 'Measure Stick'
    name = 'measure stick'
    buttons = ('Compute...','Close')
    help = ''

    # @ help = 'ContributedSoftware/MeasureStick/init.html'
    dir_pkg = os.path.dirname(__file__)
    help_path = os.path.join(dir_pkg, 'init.html')
    help_url = 'file://' + help_path
    help = help_url

    provideStatus = True
    statusPosition = 'above'
    statusResizing = False
    statusWidth = 40

    # ---------------------------------------------------------------------
    # Fill in UI
    # ---------------------------------------------------------------------

    def fillInUI(self, parent):
        """fillInUI(parent)
        """

        self.status('')
        
        self.volume_path_dialog = None 

        parent.columnconfigure(0, weight=1)
        self.toplevel_widget = parent.winfo_toplevel() # @ whatisthis

        # parameters frame (pf)
        row = 0
        pf = Tkinter.Frame(parent)
        pf.grid(row = row, column = 0, sticky = 'w',padx=8,pady=8)
        self._make_parameters_panel(pf)

        # checkbox to show relative coord
        row = row + 1
        relative_text = ' Show coord relative to open model '
        rm = Hybrid.Checkbutton(parent,  relative_text, 0)
        rm.button.grid(row=row, column=0, sticky='w',padx=8)
        self.relative_xyz = rm.variable

        # menu frame
        row = row + 1
        from chimera.widgets import ModelOptionMenu
        self.menu = ModelOptionMenu(parent, command=self.menu_cb,
                                    labelpos='w', label_text='Model:')
        self.menu.grid(row=row, sticky='w', padx=8, pady=2)

    # ---------------------------------------------------------------------
    # Panels
    # ---------------------------------------------------------------------

    def _make_parameters_panel(self, frame):
        """_make_parameters_panel(frame)

        Make a panel in the GUI for parmeters
        (distance and atom location).
        """
        
        row = 0

        # distance
        dfL = Tkinter.Label(frame, text=' Distance ')
        dfL.grid(row=row, column=0, sticky='w')
        dfE = Hybrid.Entry(frame, ' ', 7, '0.0')
        dfE.frame.grid(row=row, column=1, columnspan=3, sticky='w')
        dfE.entry['state'] = 'readonly'
        self.distance_value = dfE.variable

        # atom 1 location
        row = row + 1
        self.marker1_xyz = []
        a1L = Tkinter.Label(frame, text=' XYZ 1    ')
        a1L.grid(row=row, column=0, sticky='w',pady=2)
        for a in range(3):
            a1E = Hybrid.Entry(frame, ' ', 7, '0.0')
            a1E.frame.grid(row=row, column=a+1, sticky='w')
            a1E.entry['state'] = 'readonly'
            self.marker1_xyz.append(a1E.variable)

        # atom 2 location
        row = row + 1
        self.marker2_xyz = []
        a2L = Tkinter.Label(frame, text=' XYZ 2    ')
        a2L.grid(row=row, column=0, sticky='w',pady=2)
        for a in range(3):
            a2E = Hybrid.Entry(frame, ' ', 7, '0.0')
            a2E.frame.grid(row=row, column=a+1, sticky='w')
            a2E.entry['state'] = 'readonly'
            self.marker2_xyz.append(a2E.variable)

        return
    
    def menu_cb(self, val):

        return

    # ---------------------------------------------------------------------
    # Distance and Location functions
    # ---------------------------------------------------------------------

    def get_parameters_value(self):
        """get_parameters_value():

        Output:
            dist        distance
            marker1d    marker 1 location
            marker2d    marker 2 location

        Get parameters - distance and location of markers.
        """

        if self.volume_path_dialog == None:
            msg = 'No marker set present!\n'
            self.status(msg, color='red', blankAfter=15)
            replyobj.warning(msg)
            return None,None,None
        
        linked_list = self.volume_path_dialog.selected_links()
        if len(linked_list) == 0:
            msg = 'No links present/selected!\n'
            self.status(msg, color='red', blankAfter=15)
            replyobj.warning(msg)
            return None, None, None
        
        link = linked_list[0]

        dist = self.find_link_distance(link)
        marker1d, marker2d = self.find_marker_location(link)
        
        return dist, marker1d, marker2d

    def find_link_distance(self, link):
        """find_link_distance(link)

        Input:
            link    markerset link

        Output:
            dist    distance or None if link is None
            
        Find distance of link.
        """

        if link == None:
            return None

        from VolumePath import markerset
        distance = markerset.distance
        dist = distance(link.marker1.xyz(), link.marker2.xyz())
        
        return dist

    def find_marker_location(self, link):
        """find_marker_location(link)

        Input:
            link    markerset link

        Output:
            marker1d    marker 1 location
            marker2d    marker 2 location

        Find marker location.
        """

        if link == None:
            return None,None

        from VolumePath import markerset
        distance = markerset.distance
        dist = distance(link.marker1.xyz(), link.marker2.xyz())
        marker1d = link.marker1.xyz()
        marker2d = link.marker2.xyz()

        if self.relative_xyz.get():
            marker1d, marker2d = self.find_marker_relative(link)

        # show labels for marker 1 and 2
        if not link.marker1.note():
            link.marker1.set_note('1')
            link.marker1.show_note(1)
        if not link.marker2.note():
            link.marker2.set_note('2')
            link.marker2.show_note(1)
        
        return marker1d, marker2d

    def find_marker_relative(self, link):
        """find_marker_relative(link)

        Input:
            link    markerset link

        Output:
            marker1d    marker 1 location relative to model
            marker2d    marker 2 location relative to model

        Find marker location relative to model.
        """
        
        from VolumeViewer import slice

        # open model and marker set
        om = self.menu.getvalue()
        ms = link.marker1.marker_set

        # xform of open model and marker set 
        xf_om = om.openState.xform
        xf_ms = ms.transform()

        # get marker object coordinates
        m1_xyz = link.marker1.xyz()
        m2_xyz = link.marker2.xyz()

        # get object coordinates relative to model
        marker1d = self.transform_coord(m1_xyz, xf_ms, xf_om)
        marker2d = self.transform_coord(m2_xyz, xf_ms, xf_om)

        return marker1d, marker2d

    def transform_coord(self, from_xyz, from_xform, to_xform):
        """transform_coord(from_xyz, from_xform, to_xform)

        Input:
            from_xyz    from object coordinates
            from_xform  from object's transform
            to_xform    to objcet's transform

        Output:
            to_xyz      to object coordinates

        Convert coordinates from 'from object' to 'to object'
        """
        
        import VolumePath
        to_xyz = VolumePath.transform_coordinates(from_xyz,
                                    from_xform,to_xform)
        return to_xyz
    
    def update_parameters_value(self):
        """update_parameters_value()
        """
        
        dist, marker1d, marker2d = self.get_parameters_value()

        if (dist != None and marker1d != None and marker2d != None):
            msg = 'Measured in Angstrom units\n'
            self.status(msg, color='blue', blankAfter=10)
            replyobj.info(msg)

        if dist == None: dist = 0.0
        if marker1d == None: marker1d = 0.0,0.0,0.0
        if marker2d == None: marker2d = 0.0,0.0,0.0

        self.distance_value.set('%6.3f' % dist)
        for a in range(3):
            self.marker1_xyz[a].set('%6.3f' % marker1d[a])
            self.marker2_xyz[a].set('%6.3f' % marker2d[a])

        return
    
    def Compute(self):
        """Compute parameters
        """

        if self.volume_path_dialog == None:
            import VolumePath
            self.volume_path_dialog = VolumePath.volume_path_dialog()

        self.update_parameters_value()

# -------------------------------------------------------------------------
# Looks for dialog. If create=1, new dialog is created if an old one does
# not exist.
# 
def simple_distance_dialog(create=0):
    """Looks for Measure Stick dialog.

    simple_distance_dialog(create=0)

    If create = 1, then creates a new dialog if dialog does not exist.
    """
    
    from chimera import dialogs
    return dialogs.find(Measure_Stick.name, create=create)

# -------------------------------------------------------------------------
# Main dialog.
#
def show_simple_distance_dialog():
    """Shows the Measure Stick dialog.

    show_simple_distance_dialog()
    """
    
    from chimera import dialogs
    return dialogs.display(Measure_Stick.name)

# -------------------------------------------------------------------------
# Register dialog with Chimera.
# 
from chimera import dialogs
dialogs.register(Measure_Stick.name,Measure_Stick,replace=1)

# -------------------------------------------------------------------------
