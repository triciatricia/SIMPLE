# -------------------------------------------------------------------------
# SegmentWrite/__init__.py
#
# Segment Volume package - Segment Write module
#
# Author:
#       Lavu Sridhar, Baylor College of Medicine (BCM)
#
# Files in module:
#       __init__.py         GUI
#       ChimeraExtension.py
#       mrc_write.py        MRC command-line
#       mrc_header.py       MRC header
#       mrc_specs.py        MRC specs and interpretation
#
# Help files:
#       init.html, init.png
#
# Revisions:
#       2005.01.22: Lavu Sridhar, BCM
#       2005.02.15: Lavu Sridhar, BCM
#       2005.09.06: Lavu Sridhar, BCM (VU 1.2129 Chimera)
#
# To Do:
#       See comments marker with # @
#
"""GUI to save Chimera's VolumeData data objects
(grid data object) in different volume data formats.

Supports writing:
(1) MRC data format - specs are in the file (mrc_specs.py).
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

class Segment_Write(ModelessDialog):
    """Class: Segment_Write() - dialog for saving volume data.

    Main dialog for saving volume data.
    """

    title = 'Segment Write'
    name  = 'segment write'
    buttons = ('Close',)

    # @ help = 'ContributedSoftware/SegmentWrite/init.html'
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

        self.write_dialog = seg_write_dialog()
        self.open_dialog = None 

        parent.columnconfigure(0, weight = 1)
        self.toplevel_widget = parent.winfo_toplevel() # @ whatisthis
        self.toplevel_widget.withdraw() # @ whatisthis

        # data menu frame (dmf)
        row = 0
        import SegmentMenu
        from SegmentMenu import datamenuseg
        dmf = datamenuseg.Segment_Open_Data(self, parent,
                                            self.data_status_cb)
        dmf.frame.grid(row = row, column = 0, sticky = 'nw', pady = 8)
        self.data_panel = dmf

        # save formats frame (sff)
        row = row + 1
        sff = Tkinter.Frame(parent, padx=8, pady=8)
        sff.grid(row = row, column = 0, sticky = 'nw')
        self.save_buttons = self._make_save_formats_panel(sff)

        # output frame (omf)
        row = row + 1
        from SegmentMenu import datamenuseg
        omf = datamenuseg.Segment_Open_Output(self, parent,
                                             self.output_status_cb)
        omf.frame.grid(row = row, column = 0, sticky = 'nw', pady=8)
        self.output_panel = omf

        # create initial data menu list
        self.data_panel.data_items_refresh()

        # @ do we need to do stuff before closing Chimera session
        #   or this segmentation dialog

    # ---------------------------------------------------------------------
    # Additional panels
    # ---------------------------------------------------------------------

    def _make_save_formats_panel(self, frame):
        """_make_save_formats_panel(frame)

        Output:
            buttons         dictionary of Save and Save As buttons

        Make a panel in the GUI to save files, and return buttons
        as a dictionary with keys corresponding to the different
        save formats.
        """

        row = 0

        # save formats label
        sfL = Tkinter.Label(frame, text='Output file format ')
        sfL.grid(row = row, column = 0, sticky = 'w')

        data_output = {}
        save_button = {}

        # mrc format
        row = row + 1

        # save as mrc entry (samE)
        samE = Hybrid.Entry(frame, 'MRC ', '16', 'temp.mrc')
        samE.frame.grid(row = row, column = 0, sticky = 'w', padx=40)
        data_output['mrc'] = samE
        # @ how to update entry - callback

        # save as mrc button (samB)
        samB = Hybrid.Button_Row(frame, '',
                               (('Save', self.save_mrc_cb),
                                ('Save As', self.save_as_mrc_cb)))
        samB.frame.grid(row = row, column = 1, sticky = 'w')
        save_button['mrc'] = samB.buttons

        self.data_output = data_output
        
        return save_button
        
    # ---------------------------------------------------------------------
    # Data menu related functions
    # ---------------------------------------------------------------------

    def data_status_cb(self, data_item, data_status):
        """data_status_cb(data_item, data_status) - callback.

        Callback function for data status, used by datamenuseg's
        Data menu. Activates and deactivates Save buttons.
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

        # activate/deactivate save and save as buttons
        if data_status == self.data_panel.DATA_NOT_SHOWN:
            self._set_save_buttons_state('normal')
        elif data_status == self.data_panel.DATA_SHOWN:
            self._set_save_buttons_state('normal') 
        else:
            self._set_save_buttons_state('disabled')
            
        return

    def _set_save_buttons_state(self, button_state):
        """_set_save_buttons_state(button_state) - button state

        Input:
            button_state        'normal' or 'disabled'

        Change state of all Save and Save As buttons to state
        specified by button_state.
        """

        if not (button_state == 'normal' or
                button_state == 'disabled'):

            msg = 'Invalid state specified for Save buttons!\n'
            self.status(msg, color='red', blankAfter=15)
            replyobj.error(msg)
            return

        self.save_buttons['mrc'][0]['state'] = button_state
        self.save_buttons['mrc'][1]['state'] = button_state
        
        return        
    
    # ---------------------------------------------------------------------
    #  Output menu related functions
    # ---------------------------------------------------------------------

    def output_status_cb(self, output_item, output_status):
        """output_status_cb(output_item, output_status) - callback
        
        Callback function for output status, used by datamenuseg's
        Output menu.
        """

        self.output_shown = output_status
        self.output_item = output_item

        # display a message
        if output_status == self.output_panel.DATA_NOT_SHOWN:
            msg = 'Output item %s not shown\n' % (output_item.full_name)
        elif output_status == self.output_panel.DATA_SHOWN:
            msg = 'Output item %s shown\n'% (output_item.full_name)
        else:
            msg = 'No output items present\n'

        # self.status(msg, color='blue', blankAfter=15)
        # if output_status == self.output_panel.DATA_EMPTY:
        #    replyobj.info(msg)

        return

    # ---------------------------------------------------------------------
    #  MRC Save related functions.
    # ---------------------------------------------------------------------

    def save_mrc_cb(self):
        """save_mrc_cb() - callback for save mrc button.
        """

        self.save_as_file(file_format='mrc', ask_path=0)

        return

    def save_as_mrc_cb(self):
        """save_as_mrc_cb() - callback for save as mrc button.
        """

        self.save_as_file(file_format='mrc', ask_path=1)

        return

    # ---------------------------------------------------------------------
    #  Main save function.
    # ---------------------------------------------------------------------

    def save_as_file(self, file_format, ask_path=1):
        """save_as_file(ask_path=1) - save menu data item.

        Saves data item on data menu to file_format. Prompts the user
        for a path if ask_path is set to 1. Checks if output file
        and path are valid.
        """
        
        # check input data exists
        if self.data_item == None:
            name = '%s' % (self.data_panel.data_menu.variable.get())
            msg = 'Input data %s not found!\n' % name 
            self.status(msg, color='red', blankAfter=15)
            replyobj.error(msg)
            return

        # get input file path
        infile = str(self.data_item.path)

        # @ create and use a dictionary in future
        # just check to be on safe side
        if file_format == 'mrc':
            file_ext = '.mrc'
            file_filters = [('MRC Files', '*.mrc','')]
        else:
            msg = 'Output format %s not recognized!\n' % file_format 
            self.status(msg, color='red', blankAfter=15)
            replyobj.error(msg)
            return
        
        # get output file path (return if none)
        if ask_path:
            first_part, last_part = self.name_and_dot_suffix(infile)
            default_path = first_part + file_ext
            outfile = self._get_file_path(default_path, file_filters)
            if outfile == None:
                msg = 'Save cancelled!\n'
                self.status(msg, color='blue', blankAfter=5)
                return
            outfile_name = os.path.basename(outfile)
            self.data_output[file_format].variable.set(outfile_name)

        # get output file name
        outfile_name = str(self.data_output[file_format].variable.get())
        # if not ask_path, then set output path to current directory
        if not ask_path:
            outfile = os.path.join(os.path.curdir, outfile_name)
            
        # If ask path, then it should have already asked for
        # permission to overwrite if infile == outfile.
        
        # check if valid output name and path and if overwriting
        if (outfile_name == '' or (ask_path == 0 and outfile == infile)):
            first_part, last_part = self.name_and_dot_suffix(infile)
            outfile = '%s-2%s' % (first_part, file_ext)
            outfile_name = os.path.basename(outfile)
            msg = 'Using default output file %s\n'% outfile
            replyobj.info(msg)
        self.data_output[file_format].variable.set(outfile_name)

        self.output_item = None

        # save 
        if file_format == 'mrc':
            # save as mrc
            import mrc_write
            if mrc_write.save_mrc(self.data_item.data, path=outfile):
                save_success = 1
            else:
                save_success = 0
        else:
            pass

        # message
        if save_success:
            msg = 'Written %s\n' % outfile
            self.status(msg, color='blue', blankAfter=10)
            replyobj.info(msg)
        else:
            msg = 'Writing %s failed!\n' % outfile
            self.status(msg, color='red', blankAfter=10)
            replyobj.error(msg)
            
        if save_success:
            # create output data item, show the dialog
            self.open_output_data_items('', [outfile])
            self.enter()
        
    def _get_file_path(self, default_path, filters):
        """_get_file_path(default_path) - prompt for a file path.

        Input:
            default_path    default for initial directory/file
            filters         eg: [('MRC Files', '*.mrc', '')]
            
        Output:
            path            valid path or None
            
        Prompts user for file path starting with default_path. If
        no path found, then returns None.
        """

        # @ deal with Cancel button
        
        if default_path:
            initialdir, initialfile = os.path.split(default_path)
        else:
            initialdir, initialfile = None, None
        
        import OpenSave
        d = OpenSave.SaveModal(title='Save volume data file',
                               initialdir = initialdir,
                               initialfile = initialfile,
                               filters = filters)
        paths_and_types = d.run(self.toplevel_widget)
        if paths_and_types and len(paths_and_types) == 1:
            path = paths_and_types[0][0]
        else:
            path = None

        return path

    # ---------------------------------------------------------------------
    #  Output functions.
    # ---------------------------------------------------------------------

    def open_output_data_items(self, outdir, outfiles):
        """open_output_data_items(outdir, outfiles) - output menu.

        Input:
            outdir      output file directory
            outfiles    output file
            
        Add output data items in outfiles in outdir directory, to
        output data menu.
        """

        if len(outfiles) == 0:
            return
        
        filepaths = map(lambda outfile: os.path.join(outdir, outfile),
                        outfiles)
        filepaths_valid = filter(lambda p: os.path.isfile(p), filepaths)
        self.output_panel.data_open_cb(filepaths_valid)

        if len(filepaths_valid) < len(outfiles):
            msg = 'Some or all output files not found!\n'
            self.status(msg, color='red', blankAfter=10)
            replyobj.error(msg)
        
        return

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
        
def seg_write_dialog(create=0):
    """seg_write_dialog(create=0) - look for Segment Write dialog.

    If create = 1, then creates a new dialog if dialog does not exist.
    """
    
    from chimera import dialogs
    return dialogs.find(Segment_Write.name, create=create)

def show_seg_write_dialog():
    """show_seg_write_dialog() - shows the Segment Write dialog.
    """
    
    from chimera import dialogs
    return dialogs.display(Segment_Write.name)

# -------------------------------------------------------------------------
# Register dialog with Chimera.
# -------------------------------------------------------------------------
 
from chimera import dialogs
dialogs.register(Segment_Write.name,Segment_Write,replace=1)

# -------------------------------------------------------------------------
