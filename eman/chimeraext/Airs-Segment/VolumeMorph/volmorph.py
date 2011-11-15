# -------------------------------------------------------------------------
# VolumeMorph/volmorph.py
# 
# Airs-Segment package - Volume Morph module
# 
# Author:
#       Lavu Sridhar, Baylor College of Medicine (BCM)
#
# Revisions:
#       2006.06.21: Lavu Sridhar, BCM
#
# To Do:
#       See comments marked with # @
# 
# Key:
#       VU: Version Upgrade
#
"""Morphing of volume density maps.

GUI to perform morphing of volume density maps, using:
(1) 'Linear deformation'
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

class Volume_Morph(ModelessDialog):
    """Class: Volume_Morph()

    The main GUI dialog for morphing.
    """

    title='Volume Morph'
    name = 'volume morph'
    buttons = ('Close',)

    # @ help = 'ContributedSoftware/VolumeMorph/volmorph.html'
    dir_pkg = os.path.dirname(__file__)
    help_path = os.path.join(dir_pkg, 'volmorph.html')
    help_url = 'file://' + help_path
    help = help_url

    provideStatus = True
    statusPosition = 'above'
    statusResizing = False
    statusWidth = 40
    
    morph_choices = {0: 'Simple', 1: 'Other'}

    # ---------------------------------------------------------------------
    # Fill in UI
    # ---------------------------------------------------------------------

    def fillInUI(self, parent):
        """fillInUI(parent)
        """

        self.status('')
        self.focus_region = None # current selection
        self.data_item = None
        self.output_item = None
        self.data_shown = None

        self.morph_dialog = vol_morph_dialog()

        self.model = None

        self.morph_init  = None
        self.morph_final = None
        
        parent.columnconfigure(0, weight = 1)
        # parent.rowconfigure(0, weight = 1)
        self.toplevel_widget = parent.winfo_toplevel() # @ whatisthis

        # panel buttons (pb)
        row = 0
        pb = Hybrid.Checkbutton_Row(parent, 'Panels ',
                                    ('Simple', ))
        pb.frame.grid(row = row, column = 0, sticky = 'nw')
        for b in pb.checkbuttons:
            b.callback(self.allow_toplevel_resize_cb)
        (self.morph_simple_panel_button,
         ) = pb.checkbuttons

        # data menu frame (dmf)
        row = row + 1
        import SegmentMenu
        from SegmentMenu import datamenuseg
        dmf = datamenuseg.Segment_Open_Data(self, parent,
                                            self.data_status_cb)
        dmf.frame.grid(row = row, column = 0, sticky = 'nw', pady = 8)
        self.data_panel = dmf

        # morph model frame
        row = row + 1
        mmf = Tkinter.Frame(parent, padx=8, pady=8)
        mmf.grid(row = row, column = 0, sticky = 'nw')
        self._make_morph_models_panel(mmf)
        
        # simple morph frame
        row = row + 1
        smf = Tkinter.Frame(parent, padx=8, pady=8)
        smf.grid(row = row, column = 0, sticky = 'nw')
        self._make_morph_simple_panel(smf)
        self.morph_simple_panel_button.popup_frame(smf,
                                    row=row, column=0, sticky='nw')
        self.morph_simple_panel_button.variable.set(1)

        # morph output frame
        row = row + 1
        mof = Tkinter.Frame(parent, padx=8, pady=8)
        mof.grid(row = row, column = 0, sticky = 'nw')
        self._make_morph_output_panel(mof)

        # output menu frame
        row = row + 1
        import SegmentMenu
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
    # Panels
    # ---------------------------------------------------------------------

    def _make_morph_models_panel(self, frame):
        """_make_morph_models_panel(frame)

        Make a panel in the GUI for morph models.
        """

        row = 0

        # morph models label (mmL)
        mmL = Tkinter.Label(frame,
                            text = 'Morph Models ')
        mmL.grid(row = row, column = 0, sticky = 'nw')

        # morph models frame
        row = row + 1
        mmf = Tkinter.Frame(frame, padx=40)
        mmf.grid(row = row, column = 0, sticky = 'nw')

        from chimera.widgets import ModelOptionMenu
                            
        # morph model init menu and label
        self.morph_init_menu = ModelOptionMenu(mmf,
                                command=self.morph_model_menu_cb,
                                labelpos='w',
                                label_text=' Inital model: ')
        self.morph_init_menu.grid(row=0, column=0, sticky='w')

        miL = Tkinter.Label(mmf, text = ' (PDB) ')
        miL.grid(row=0, column=1, sticky = 'nw')

        # morph model final menu and label
        self.morph_final_menu = ModelOptionMenu(mmf,
                                command=self.morph_model_menu_cb,
                                labelpos='w',
                                label_text=' Final model: ')
        self.morph_final_menu.grid(row=1, column=0, sticky='w')

        mfL = Tkinter.Label(mmf, text = ' (PDB) ')
        mfL.grid(row=1, column=1, sticky = 'nw')

        return

    def _make_morph_simple_panel(self, frame):
        """_make_morph_simple_panel(frame)

        Make a panel in the GUI for simple morphing.
        """

        row = 0

        # simple morph label (smL)
        smL = Tkinter.Label(frame,
                            text = 'Simple Morph ')
        smL.grid(row = row, column = 0, sticky = 'nw')

        # simple morph fraction frame
        row = row + 1
        smfrf = Tkinter.Frame(frame, padx=40)
        smfrf.grid(row = row, column = 0, sticky = 'nw')

        # simple morph fraction
        smfr_e = Hybrid.Entry(smfrf, 'Fraction   :', '6', '1.0')
        smfr_e.frame.grid(row=0, column=0, sticky = 'nw')
        self.sm_fraction_value = smfr_e

        # simple morph threshold frame
        row = row + 1
        smtf = Tkinter.Frame(frame, padx=40)
        smtf.grid(row = row, column = 0, sticky = 'nw')

        # simple morph threshold
        smt_c = Hybrid.Checkbutton_Row(smtf, 'Threshold : ',
                                       ('Use  ',))
        smt_c.frame.grid(row=0, column=0, sticky = 'nw')
        (threshold_button,) = smt_c.checkbuttons
        threshold_button.callback(self.sm_threshold_button_cb)
        self.sm_threshold_button = threshold_button

        smt_e = Hybrid.Entry(smtf, '  ', '8', '0.0')
        smt_e.frame.grid(row=0, column=1, sticky = 'nw')
        self.sm_threshold_value = smt_e

        # simple morph filter frame
        row = row + 1
        smff = Tkinter.Frame(frame, padx=40)
        smff.grid(row = row, column = 0, sticky = 'nw')

        # simple morph filter
        smf_c = Hybrid.Checkbutton_Row(smff, 'Filter     : ',
                                       ('Use  ',))
        smf_c.frame.grid(row=0, column=0, sticky = 'nw')
        (filter_button,) = smf_c.checkbuttons
        filter_button.callback(self.sm_filter_button_cb)
        self.sm_filter_button = filter_button
        
        smf_e = Hybrid.Entry(smff, ' lowpass ', '8', '0.0')
        smf_e.frame.grid(row=0, column=1, sticky = 'nw')
        self.sm_filter_value = smf_e

        smfL = Tkinter.Label(smff, text = ' (Ang) ')
        smfL.grid(row=0, column=2, sticky = 'nw')

        # default options
        self.sm_threshold_button.variable.set(0)
        self.sm_filter_button.variable.set(0)
        
        return

    def _make_morph_output_panel(self, frame):
        """_make_morph_output_panel(frame)

        Make a panel in the GUI for output.
        """

        row = 0
        
        # morph output label (moL)
        moL = Tkinter.Label(frame,
                            text = 'Morph Output ')
        moL.grid(row = 0, column = 0, sticky = 'nw')

        # morph output paramters frame (mopf)
        row = row + 1
        mopf = Tkinter.Frame(frame, padx=32)
        mopf.grid(row = 1, column = 0, sticky = 'nw')

        # chose morph type (cmt)
        cmt = Hybrid.Radiobutton_Row(mopf, 'Choose Morph type ',
                                     (self.morph_choices[0],),
                                     self.morph_type_cb)
        cmt.frame.grid(row = 0, column = 0, columnspan = 2,
                       sticky = 'nw', padx=8)
        self.morph_type = cmt

        # output data file entry (odfE)
        odfE = Hybrid.Entry(mopf, 'File MRC ', '16', 'temp.mrc')
        odfE.frame.grid(row = 1, column=0, sticky = 'w', padx=8)
        self.data_output = odfE
        # @ how to update entry - callback

        # buttons
        mb = Hybrid.Button_Row(mopf, '',
                               (('Apply', self.morph_apply_cb),))
        mb.frame.grid(row = 1, column = 1, sticky = 'w', padx=8)

        self.morph_type.variable.set(self.morph_choices[0])
        
        return

    # ---------------------------------------------------------------------
    # Data menu related functions
    # ---------------------------------------------------------------------
            
    def data_status_cb(self, data_item, data_status):
        """data_status_cb(data_item, data_status) - callback.

        Callback function for data status, used by datamenuseg's
        Data menu. Activates and deactivates mouse buttons.
        """

        self.data_shown = data_status
        self.data_item = data_item

        # display a message
        if data_status == self.data_panel.DATA_NOT_SHOWN:
            msg = 'Data item %s not shown\n' % (data_item.name)
        elif data_status == self.data_panel.DATA_SHOWN:
            msg = 'Data item %s shown\n'% (data_item.name)
        else:
            msg = 'No data items present\n'

        # self.status(msg, color='blue', blankAfter=15)
        # if data_status == self.data_panel.DATA_EMPTY:
        #    replyobj.info(msg)

        # activate/deactivate mouse selection
        # if data_status == self.data_panel.DATA_NOT_SHOWN:
        #    self.selection_hide_cb()
        #    self.sel_mouse_button['state'] = 'disabled'
        # elif data_status == self.data_panel.DATA_SHOWN:
        #    self.selection_show_cb()
        #    self.sel_mouse_button['state'] = 'normal'
        # else:
        #    self.selection_delete_cb()
        #    self.sel_mouse_button['state'] = 'disabled'

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
            msg = 'Output item %s not shown\n' % (output_item.name)
        elif output_status == self.output_panel.DATA_SHOWN:
            msg = 'Output item %s shown\n'% (output_item.name)
        else:
            msg = 'No output items present\n'

        # self.status(msg, color='blue', blankAfter=15)
        # if output_status == self.output_panel.DATA_EMPTY:
        #    replyobj.info(msg)

        return

    # ---------------------------------------------------------------------
    #  Morph related callback functions
    # ---------------------------------------------------------------------

    def morph_model_menu_cb(self, val):
        """morph_model_menu_cb(val) - callback for morph model menu
        """
        
        return

    def morph_type_cb(self):
        """morph_type_cb() - callback for morph type
        """
        
        return

    # ---------------------------------------------------------------------
    #  Simple Morph related callback functions
    # ---------------------------------------------------------------------

    def sm_threshold_button_cb(self):
        """sm_threshold_button_cb() - callback for simple morph 

        callback for threshold parameter in simple morph
        """
        if self.sm_threshold_button.variable.get():
            self.sm_threshold_value.entry['state'] = 'normal'
        else:
            self.sm_threshold_value.entry['state'] = 'readonly'
        
        return

    def sm_filter_button_cb(self):
        """sm_filter_button_cb() - callback for simple morph 

        callback for filter parameter in simple morph
        """
        if self.sm_filter_button.variable.get():
            self.sm_filter_value.entry['state'] = 'normal'
        else:
            self.sm_filter_value.entry['state'] = 'readonly'
        
        return

    # ---------------------------------------------------------------------
    #  Morph related functions.
    # ---------------------------------------------------------------------

    def morph_apply_cb(self):
        """morph_apply_cb() - callback for Apply button.
        """

        self.morph_apply()

        return

    def morph_apply(self):
        """morph_apply() - applies appropriate morphing

        Applies appropriate morphing after Apply button
        is specified. Checks values and passes a message if
        incorrect parameters.
        """
        
        # check input data exists
        if self.data_item == None:
            name = '%s' % (self.data_panel.data_menu.variable.get())
            msg = 'Input data %s not found!\n' % name 
            self.status(msg, color='red', blankAfter=15)
            replyobj.error(msg)
            return

        # get input file path, name, and size in pixels
        infile_path = str(self.data_item.path)
        infile      = str(self.data_item.name)
        infile_size = self.data_item.size

        # get morph models
        morph0, morph1 = self.get_morph_models()
        if (morph0 == None or morph1 == None):
            return
        
        # get morph parameters
        morph_type = self.morph_type.variable.get()
        if morph_type == self.morph_choices[0]:
            frac, thr, filt = self.get_simple_morph_param()

        # check and set output name
        self.output_item = None
        outfile = str(self.data_output.variable.get())
        if (outfile == '') or (outfile == infile):
            first_part, last_part = self.name_and_dot_suffix(infile)
            outfile = '%s-m%s' % (first_part, last_part)
            msg = 'Using default output file %s\n'% outfile
            replyobj.info(msg)
        self.data_output.variable.set(outfile)

        # output
        out_dir = os.getcwd()
        out_files = [outfile]

        # run morph command
        seg_sucess = 0
        
        if morph_type == self.morph_choices[0]:
            seg_success = self.morph_apply_simple(self.data_item,
                            morph0, morph1, outfile, frac, thr, filt)

        # open output
        if seg_success:
            self.open_output_data_items(out_dir, out_files)
            self.enter()

        return
    
    def check_morph_model(self, model):
        """check_morph_model(model) - get morph model if valid

        Output:
            model   morph model
        """

        from chimera import Molecule
        if model is None or not isinstance(model, Molecule):
            print model.__class__
            msg = 'Select a PDB model as morph model!\n'
            self.status(msg, color='red', blankAfter=10)
            replyobj.error(msg)
            return None

        return model
        
    def get_morph_models(self):
        """get_morph_models() - get init and final morph models

        Output:
            model0  morph model initial (None if invalid)
            model1  morph model final (None if invalid)
            
        Return the inital and final morph models,
        after checking.
        """

        morph0 = self.morph_init_menu.getvalue()
        morph1 = self.morph_final_menu.getvalue()

        morph0 = self.check_morph_model(morph0)
        morph1 = self.check_morph_model(morph1)

        if morph0 == None or morph1 == None:
            return None, None
        
        morph0_path = morph0.openedAs[0]
        morph1_path = morph1.openedAs[0]
        if morph0_path == morph1_path:
            msg = 'Select 2 different PDB models!\n'
            self.status(msg, color='red', blankAfter=10)
            replyobj.error(msg)
            return None, None

        return morph0, morph1
    
    def get_simple_morph_param(self):
        """get_simple_morph_param() - simple morph parameters

        Output:
            thr
            filt
            frac
            
        Returns parameters to be used for simple morph,
        after checking.
        """

        frac_value = 1.0
        thr_value  = None
        filt_value = None
        
        # read fraction
        frac = str(self.sm_fraction_value.variable.get())
        try:
            frac_value = float(frac)
        except:
            frac_value = 1.0
            msg = 'Reset fraction value!\n'
            self.status(msg, color='red', blankAfter=15)
            replyobj.warning(msg)
        self.sm_fraction_value.variable.set('%5.2f' % frac_value)

        if ((frac_value < 0.1) or (frac_value > 1.0)):
            frac_value = 1.0
            msg = 'Reset fraction value!\n'
            self.status(msg, color='red', blankAfter=15)
            replyobj.warning(msg)
        self.sm_fraction_value.variable.set('%5.2f' % frac_value)
            
        # read threshold
        if self.sm_threshold_button.variable.get():
            thr = str(self.sm_threshold_value.variable.get())
            try:
                thr_value = float(thr)
            except:
                thr_value = 0.0
                msg = 'Reset threshold value!\n'
                self.status(msg, color='red', blankAfter=15)
                replyobj.warning(msg)
            self.sm_threshold_value.variable.set('%5.2f' % thr_value)

        # read filter value
        if self.sm_filter_button.variable.get():
            filt = str(self.sm_filter_value.variable.get())
            try:
                filt_value = float(filt)
            except:
                filt_value = 0.0
                msg = 'Reset filter value!\n'
                self.status(msg, color='red', blankAfter=15)
                replyobj.warning(msg)
            self.sm_filter_value.variable.set('%5.2f' % filt_value)

        return frac_value, thr_value, filt_value
        
    # ---------------------------------------------------------------------
    # Morph simple 
    # ---------------------------------------------------------------------
    
    def morph_apply_simple(self, inputdata, morph0, morph1, outputfile,
                            frac=1.0, thr=None, filt=None):
        """morph_apply_simple(inputdata, morph0, morph1, outputfile,
                               frac=1.0, thr=None, filt=None)

        Input:
            inputdata       input volume data
            morph0          PDB model for morph initial state
            morph1          PDB model for morph final   state
            outputfile      output file path
            frac            fraction of morphing (0.1 to 1)
            thr             threshold, default=None = no thr
            filt            lowpass filter in Angstroms
        
        Output:
            1/0             success
            
        Apply simple morph.

        Assumes that the input parmaeters are all valid.
        """

        infile_path = str(inputdata.path)
        msg = 'Applying simple morph on %s\n' % infile_path
        replyobj.info(msg)

        import morphsimple
        morphsimple.simple_morph(inputdata.data, morph0, morph1,
                                 outputfile, frac, thr, filt)

        msg = 'Applied simple morphing on %s\n' \
              % os.path.basename(infile_path)
        self.status(msg, color='blue', blankAfter=10)
        replyobj.info(msg)

        return 1

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

    # ---------------------------------------------------------------------
    # Returns first part and dot suffix from file name or path.
    # Note that the suffix includes last '.'  
    #
    def name_and_dot_suffix(self, name):

        try:
            dot_position = name.rindex('.')
        except ValueError:
            return name, ''
            
        first_part = name[:dot_position]
        last_part  = name[dot_position:]

        return first_part, last_part
    
# -------------------------------------------------------------------------
#
nbfont = None
def non_bold_font(frame):

    global nbfont
    if nbfont == None:
        e = Tkinter.Entry(frame)
        nbfont = e['font']
        e.destroy()
    return nbfont
  
# -------------------------------------------------------------------------
# Looks for dialog. If create=1, new dialog is created if an old one does
# not exist.
# 
def vol_morph_dialog(create=0):
    """Looks for Volume Morph dialog.

    vol_morph_dialog(create=0)

    If create = 1, then creates a new dialog if dialog does not exist.
    """
    
    from chimera import dialogs
    return dialogs.find(Volume_Morph.name, create=create)

# -------------------------------------------------------------------------
# Main dialog.
#
def show_vol_morph_dialog():
    """Shows the Volume Morph dialog.

    show_vol_morph_dialog()
    """
    
    from chimera import dialogs
    return dialogs.display(Volume_Morph.name)

# -------------------------------------------------------------------------
# Register dialog with Chimera.
# 
from chimera import dialogs
dialogs.register(Volume_Morph.name,Volume_Morph,replace=1)

# -------------------------------------------------------------------------
