# -------------------------------------------------------------------------
# SegmentTrack/trackxform.py
#
# Segment Volume package - Segment Track module
# 
# Author:
#       Lavu Sridhar, Baylor College of Medicine (BCM)
#
# Revisions:
#       2005.01.17: Lavu Sridhar, BCM
#       2005.02.15: Lavu Sridhar, BCM
#
# To Do:
#       See comments marked with # @
#
"""Module to track and apply transforms in Chimera camera
coordinates.
"""

# -------------------------------------------------------------------------

import os

import chimera
from chimera.baseDialog import ModelessDialog
from CGLtk import Hybrid

import Tkinter

# -------------------------------------------------------------------------

class TrackXformDialog(ModelessDialog):
    """Class TrackXformDialog()

    Dialog for tracking transforms in Chimera's camera coordinates.
    """

    title= 'Track Model Transfom'
    name = 'track model transformation'
    buttons = ('Close',)

    # @ help = 'ContributedSoftware/SegmentTrack/trackxform.html'
    dir_pkg = os.path.dirname(__file__)
    help_path = os.path.join(dir_pkg, 'trackxform.html')
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
        self.track_xform = None

        # menu frame
        row = 0
        from chimera.widgets import ModelOptionMenu
        self.menu = ModelOptionMenu(parent, command=self.menu_cb,
                                    labelpos='w', label_text='Model:')
        self.menu.grid(row=row, sticky='w', padx=8, pady=8)

        # initial transform frame (itf)
        row = row + 1
        itf = Tkinter.Frame(parent,padx=8,pady=8)
        itf.grid(row=row, column=0, sticky='nw')

        # record initial
        itfg = Hybrid.Button_Row(itf, 'Record transform  ',
                                 (('Record',self.record_initial_cb),))
        itfg.frame.grid(row=0, column=0, columnspan=3, sticky='w')

        # parameters
        itfp = Tkinter.Frame(itf, padx=16)
        itfp.grid(row=1, column=0, sticky='w')
        self.init_trans, self.init_rot, self.init_ang = \
                         self._make_param_panel(itfp)

        # current transform frame (ctf)
        row = row + 1
        ctf = Tkinter.Frame(parent, padx=8, pady=8)
        ctf.grid(row=row, column=0, sticky='nw')

        # get current
        ctfg = Hybrid.Button_Row(ctf, 'Current transform  ',
                                 (('Get',self.record_current_cb),))
        ctfg.frame.grid(row=0, column=0, sticky='w')

        # parameters
        ctfp = Tkinter.Frame(ctf, padx=16)
        ctfp.grid(row=1, column=0, sticky='w')
        self.curr_trans, self.curr_rot, self.curr_ang = \
                         self._make_param_panel(ctfp)
        
        # listbox frame
        row = row+1
        from chimera.widgets import ModelScrolledListBox
        self.listbox = ModelScrolledListBox(parent,
                                            labelpos='w',
                                            label_text='Model List:')
        self.listbox.component('listbox')['selectmode'] = 'extended'
        self.listbox.grid(row=row, sticky='w', padx=8, pady=8)
        
        # apply frame (af)
        row = row + 1
        af = Tkinter.Frame(parent, padx=8, pady=8)
        af.grid(row=row, column=0, sticky='nw')

        # apply
        afg = Hybrid.Button_Row(af, '',
                                (('Apply',self.apply_initial_cb),))
        afg.frame.grid(row=0, column=0, sticky='w')
        text = ' recorded transform to models\n'
        text = text + ' selected in above model list '
        afgL = Tkinter.Label(af, text = text)
        afgL.grid(row=0, column=1, sticky='w')

        # reset
        afr = Hybrid.Button_Row(af, '',
                                (('Reset',self.reset_initial_cb),))
        afr.frame.grid(row=1, column=0, sticky='w')
        text = ' initial transform'
        afrL = Tkinter.Label(af, text = text)
        afrL.grid(row=1, column=1, sticky='w')
   
    def Close(self):
        """Close() - close dialog.
        """
        
        ModelessDialog.Close(self)

    def menu_cb(self, val):

        return

    # ---------------------------------------------------------------------
    # Paramaters panel
    # ---------------------------------------------------------------------

    def _make_param_panel(self, frame):
        """_make_param_panel(frame)

        Input:
            frame

        Output:
            translation     translation text entry
            rotation        rotation text entry
            angle           angle text entry
            
        Makes the parameters panel. 
        """

        row = 0
        
        # translation
        transL = Tkinter.Label(frame, text='Translation:    ')
        transL.grid(row=row, column=0, sticky='w')
        trans = Tkinter.Label(frame, text='')
        trans.grid(row=row, column=1, sticky='w')

        # rotation axis
        row = row + 1
        rotL = Tkinter.Label(frame, text='Rotation Axes:  ')
        rotL.grid(row=row, column=0, sticky='w')
        rot = Tkinter.Label(frame, text='')
        rot.grid(row=row, column=1, sticky='w')

        # rotation angle
        row = row + 1
        angL = Tkinter.Label(frame, text='Rotation Angle: ')
        angL.grid(row=row, column=0, sticky='w')
        ang = Tkinter.Label(frame, text='')
        ang.grid(row=row, column=1, sticky='w')
        
        return trans, rot, ang

    # ---------------------------------------------------------------------
    # Call back functions
    # ---------------------------------------------------------------------

    def record_initial_cb(self):
        """record_initial_cb() - callback func for record transform.
        """

        model = self.menu.getvalue()
        self.record_initial(model)

    def record_current_cb(self):
        """record_current_cb() - callback func for current transform.
        """

        model = self.menu.getvalue()
        self.record_current(model)

    def apply_initial_cb(self):
        """apply_initial_cb() - callback function for apply button.
        """

        models = self.listbox.getvalue()
        for model in models:
            self.update_current(model)
        model = self.menu.getvalue()
        self.record_current(model)

    def reset_initial_cb(self):
        """reset_initial_cb() - callback function for reset button.
        """

        self.reset_initial()
        
    # ---------------------------------------------------------------------
    # Command line (for GUI) functions
    # ---------------------------------------------------------------------
    
    def set_model(self, model):
        """set_model(model) - set menu to model.
        """
        
        self.menu.setvalue(model)

    def record_initial(self, model):
        """record_initial(model) - record and display model transform.
        """

        if not model:
            msg = 'No initial model'
            self.status(msg, color='blue', blankAfter=5)
            
        self.track_xform = get_xform(model)
        self._display_param_initial(self.track_xform)

    def record_current(self, model):
        """record_current(model) - display current model transform.
        """
    
        if not model:
            msg = 'No current model'
            self.status(msg, color='blue', blankAfter=5)

        self._display_param_current(model)

    def update_current(self, model):
        """update_current(model) - apply recorded transform to model.
        """

        if not model:
            msg = 'No current model'
            self.status(msg, color='blue', blankAfter=5)
        if not self.track_xform:
            msg = 'No starting transform'
            self.status(msg, color='blue', blankAfter=5)

        update_xform(model, self.track_xform)

    def reset_initial(self):
        """reset_initial() - reset all parameters
        """

        self.track_xform = None
        self._display_param_initial(None)
        self._display_param_current(None)
        
    # ---------------------------------------------------------------------
    # GUI functions for parameters
    # ---------------------------------------------------------------------
    
    def _display_param_initial(self, xform):
        """_display_param_initial(xform) - display initial transform.
        """

        vx, ax, an = self.get_param(xform=xform)
        self.init_trans['text'] = vx
        self.init_rot['text'] = ax
        self.init_ang['text'] = an

    def _display_param_current(self, model):
        """_display_param_current(model) - display current transform.
        """

        vx, ax, an = self.get_param(model=model)
        self.curr_trans['text'] = vx
        self.curr_rot['text'] = ax
        self.curr_ang['text'] = an

    def get_param(self, xform=None, model=None):
        """get_param(xform=None, model=None) - transform parameters.

        Input:
            xform=None
            model=None

        Output:
            translation     
            rotation vector
            rotation angle
            
        Get transform parameters as text strings, one each for
        translation vector, rotation vector, and rotation angle.
        Return empty text strings for no model and no xform.
        """

        if not xform:
            if model:
                xform = model.openState.xform
            else:
                return '','',''

        vx = xform.getTranslation()
        ax, an = xform.getRotation()

        vx_text = '(%7.3f, %7.3f, %7.3f)' % (vx.x, vx.y, vx.z)
        ax_text = '(%8.4f, %8.4f, %8.4f)' % (ax.x, ax.y, ax.z)
        an_text = '%7.3f' % (an)

        return vx_text, ax_text, an_text

# ---------------------------------------------------------------------
# Command line functions
# ---------------------------------------------------------------------

def get_xform(model):
    """get_xform(model) - get transform of model

    Input:
        model

    Output:
        xform       Transform of model or None if no input model

    Return transform of model if model exists, else return None.
    """
        
    if model: track_xform = model.openState.xform
    else:     track_xform = None
    return track_xform

def update_xform(model, xform):
    """update_xform(model, xform) - set model transform to xform.

    Input:
        model
        xform

    Output:
        model       Model transform set to xform
        
    Set transform of model to xform, and return model.
    """

    if model and xform:
        model.openState.xform = xform
    return model

# -------------------------------------------------------------------------
# Main dialog
# -------------------------------------------------------------------------
        
def track_xform_dialog(create=0):
    """track_xform_dialog(create=0) - look for Track Transform dialog.

    If create = 1, then creates a new dialog if dialog does not exist.
    """
    
    from chimera import dialogs
    return dialogs.find(TrackXformDialog.name, create=create)

def show_track_xform_dialog():
    """show_track_xform_dialog() - shows the Track Transform dialog.
    """
    
    from chimera import dialogs
    return dialogs.display(TrackXformDialog.name)

# -------------------------------------------------------------------------
# Register dialog with Chimera
# -------------------------------------------------------------------------

from chimera import dialogs
dialogs.register(TrackXformDialog.name, TrackXformDialog, replace=1)

# -------------------------------------------------------------------------
