# -------------------------------------------------------------------------
# SegmentRead/__init__.py
#
# Segment Volume package - Segment Read module
# 
# Author:
#       Lavu Sridhar, Baylor College of Medicine (BCM)
#
# Files in module:
#       __init__.py         Main dialog
#       rawiv_read.py       RawIV command-line
#       rawiv_format.py     RawIV header related
#       rawiv_grid.py       RawIV data
#       rawiv_specs.py      RawIV specs and interpretation
#
# Help files:
#       init.html, init.png
#
# Revisions:
#       2005.02.12: Lavu Sridhar, BCM
#       2005.02.15: Lavu Sridhar, BCM
#       2005.09.06: Lavu Sridhar, BCM (VU 1.2129 Chimera)
#
# To Do:
#       See comments marked with # @
#
"""GUI to read additional data formats used with Segment Volume
package, and wrap the data as a Chimera grid data object (see
the Volume Data module in Chimera).

Supports reading:
(1) Chimera's VolumeData data types
(2) RawIV data format - file specs are in rawiv_specs.py

Requires Segment Menu module from Segment Volume package.
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

class Segment_Read(ModelessDialog):
    """Class: Segment_Read() - dialog for reading volume data.

    Dialog for reading volume data
    """

    title = 'Segment Read'
    name  = 'segment read'
    buttons = ('Close',)

    # @ help = 'ContributedSoftware/SegmentRead/init.html'
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
        self.output_item = None

        self.read_dialog = seg_read_dialog()
        self.open_dialog = None 

        parent.columnconfigure(0, weight = 1)
        self.toplevel_widget = parent.winfo_toplevel() # @ whatisthis

        # data menu frame (dmf)
        row = 0
        import SegmentMenu
        from SegmentMenu import datamenuseg
        dmf = datamenuseg.Segment_Open_Data(self, parent,
                                            self.data_status_cb)
        dmf.frame.grid(row = row, column = 0, sticky = 'nw', pady = 8)
        self.data_panel = dmf

        # additional formats frame (aff)
        row = row + 1
        aff = Tkinter.Frame(parent, padx=8, pady=8)
        aff.grid(row = row, column = 0, sticky = 'nw')
        self._make_additional_formats_panel(aff)

        # create initial data menu list
        self.data_panel.data_items_refresh()

        # @ do we need to do stuff before closing Chimera session
        #   or this segmentation dialog

        msg = 'Hit Refresh button if menu not automatically updated!\n'
        self.status(msg, color='blue', blankAfter=15)
        replyobj.info(msg)

    # ---------------------------------------------------------------------
    # Additional panels
    # ---------------------------------------------------------------------
    
    def _make_additional_formats_panel(self, frame):
        """_make_additional_formats_panel(frame)

        Make a panel in the GUI for adding additional formats
        not directly support by the VolumeData module of Chimera.
        """

        row = 0

        # additional formats label
        afL = Tkinter.Label(frame, text='Additional data formats ')
        afL.grid(row = row, column = 0, sticky = 'w')

        # rawiv format
        row = row + 1
        afr = Hybrid.Button_Row(frame, 'RawIV format ',
                                (('Open', self.rawiv_open_cb),))
        afr.frame.grid(row = row, column = 0, sticky = 'w', padx = 32)

    # ---------------------------------------------------------------------
    # Data menu related functions
    # ---------------------------------------------------------------------

    def data_status_cb(self, data_item, data_status):
        """data_status_cb(data_item, data_status) - callback.

        Callback function for data status, used by datamenuseg's
        Data menu.
        """

        self.data_shown = data_status
        self.data_item = data_item

        # display a message
        if data_status == self.data_panel.DATA_NOT_SHOWN:
            msg = 'Data item %s not shown\n' % (data_item.full_name)
        elif data_status == self.data_panel.DATA_SHOWN:
            msg = 'Data item %s shown\n'% (data_item.full_name)
        else:
            msg = 'No data items present\n'
       
        # self.status(msg, color='blue', blankAfter=15)
        # if data_status == self.data_panel.DATA_EMPTY:
        #    replyobj.info(msg)

        # activate/deactivate buttons
        if data_status == self.data_panel.DATA_NOT_SHOWN:
            pass
        elif data_status == self.data_panel.DATA_SHOWN:
            pass
        else:
            pass
        
        return
    
    # ---------------------------------------------------------------------
    #  RawIV format related functions.
    # ---------------------------------------------------------------------

    def rawiv_open_cb(self):
        """rawiv_open_cb() - callback for opening RawIV files.
        """

        if self.open_dialog == None:
            import OpenSave
            d = OpenSave.OpenModeless(title='Open RawIV Data',
                                      filters = [('RawIV Data',
                                                  '*.rawiv')],
                                      defaultFilter=0,
                                      command = self.rawiv_open_file_cb)
            self.open_dialog = d
        else:
            self.open_dialog.enter()
    
    def rawiv_open_file_cb(self, apply, dialog):
        """rawiv_open_file_cb() - callback to open RawIV files.

        Callback function passed on to OpenSave dialog. Opens the
        grid objects from the OpenSave dialog and adds them to main
        data items list and to the Volume Viewer data sets list.
        """

        if not apply:
            return        # User pressed Cancel

        import rawiv_read
        grid_objects = []
        for path in dialog.getPaths():
            grid_object = rawiv_read.open_rawiv(path)
            grid_objects.append(grid_object)

        self.data_panel.add_grid_data(grid_objects)
        self.data_panel.add_data_sets_volume_viewer(grid_objects)

    # ---------------------------------------------------------------------
    #  Misc functions.
    # ---------------------------------------------------------------------

    # ---------------------------------------------------------------------
    # After user resizes dialog by hand it will not resize automatically
    # when panels are added or deleted. This allows the automatic resize
    # to happen
    # 
    def allow_toplevel_resize_cb(self):

        self.toplevel_widget.geometry('')

    def name_and_dot_suffix(self, name):
        """name_and_dot_suffix(name)

        Input:
            name        file name or path
            
        Output:
            first_part  left part of name before last period
            last_part   right part of name after last period
                        including the period

        Returns first part and dot suffix from file name or path.
        Suffix includes the last '.' If no period, then simply
        returns the name as first_part and '' as last_part.
        """

        try:
            dot_position = name.rindex('.')
        except ValueError:
            return name, ''
            
        first_part = name[:dot_position]
        last_part  = name[dot_position:]

        return first_part, last_part
        
    def no_feature(self, name=None):
        """no_feature(name=None) - message for missing feature.

        Displays a message saying that feature='name' is not
        avaialable.
        """
        
        if name == None:
            name = ''
        msg = 'Feature %s not available!\n' % (name) 
        self.status(msg, color='blue', blankAfter=3)
        replyobj.info(msg)
        return
    
# -------------------------------------------------------------------------
# Misc functions
# -------------------------------------------------------------------------

nbfont = None
def non_bold_font(frame):

    global nbfont
    if nbfont == None:
        e = Tkinter.Entry(frame)
        nbfont = e['font']
        e.destroy()
    return nbfont

# -------------------------------------------------------------------------
# Main dialog
# -------------------------------------------------------------------------

def seg_read_dialog(create=0):
    """seg_read_dialog(create=0) - look for Segment Read dialog.

    If create = 1, then creates a new dialog if dialog does not exist.
    """
    
    from chimera import dialogs
    return dialogs.find(Segment_Read.name, create=create)

def show_seg_read_dialog():
    """show_seg_read_dialog() - shows the Segment Read dialog.
    """
    
    from chimera import dialogs
    return dialogs.display(Segment_Read.name)

# -------------------------------------------------------------------------
# Register dialog with Chimera.
# -------------------------------------------------------------------------
 
from chimera import dialogs
dialogs.register(Segment_Read.name,Segment_Read,replace=1)

# -------------------------------------------------------------------------
