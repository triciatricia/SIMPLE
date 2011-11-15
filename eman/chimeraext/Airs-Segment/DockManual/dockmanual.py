# -------------------------------------------------------------------------
# DockManual/dockmanual.py
#
# Segment Volume package - Dock Manual module
# 
# Author:
#       Lavu Sridhar, Baylor College of Medicine (BCM)
#
# Revisions:
#       2005.04.15: Lavu Sridhar, BCM
#       2005.04.25: Lavu Sridhar, BCM
#       2005.10.10: Lavu Sridhar, BCM (VU 1.2176 Chimera)
#
# To Do:
#       See comments marked with # @
#
"""Module to dock PDB structures manually into density maps.
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

class Dock_Manual(ModelessDialog):
    """Class: Dock_Manual()

    The main GUI dialog for docking structures manually. 
    """

    title='Dock Manual'
    name = 'Dock Manual'
    buttons = ('Close',)

    # help = 'ContributedSoftware/DockManual/dockmanual.html'
    dir_pkg = os.path.dirname(__file__)
    help_path = os.path.join(dir_pkg, 'dockmanual.html')
    help_url = 'file://' + help_path
    help = help_url

    provideStatus = True
    statusPosition = 'above'
    statusResizing = False
    statusWidth = 40

    angle_conventions = {0: 'euler   ', 1: 'spin    '}
    angle_units = {0: 'radian ', 1: 'degree '}
    distance_units = {0: 'angstrom', 1: 'pixel   '}
    
    # ---------------------------------------------------------------------
    # Fill in UI
    # ---------------------------------------------------------------------
    
    def fillInUI(self, parent):
        """fillInUI(parnet)
        """

        self.status('')
        self.focus_region = None # current selection
        self.data_item = None
        self.output_item = None
        self.data_shown = None

        self.dock_dialog = dock_manual_dialog()

        self.probe_translate_unit = self.distance_units[0]
        self.probe_rotate_unit = self.angle_units[1]
        self.angle_convention = self.angle_conventions[0]
        
        self.model = None

        parent.columnconfigure(0, weight = 1)
        # parent.rowconfigure(0, weight=1)
        self.toplevel_widget = parent.winfo_toplevel() # @ whatisthis

        # panel buttons (pb)
        row = 0
        pb = Hybrid.Checkbutton_Row(parent, 'Panels ',
                                    ('Units', 'Transform', 'Optimize '))
        pb.frame.grid(row = row, column = 0, sticky = 'nw')
        for b in pb.checkbuttons:
            b.callback(self.allow_toplevel_resize_cb)
        (self.parameter_units_panel_button,
         self.probe_xform_panel_button,
         self.optimize_panels_button) = pb.checkbuttons

        # data menu frame (dmf)
        row = row + 1
        import SegmentMenu
        from SegmentMenu import datamenuseg
        dmf = datamenuseg.Segment_Open_Data(self, parent,
                                            self.data_status_cb)
        dmf.frame.grid(row = row, column = 0, sticky = 'nw', pady = 8)
        self.data_panel = dmf

        # probe menu frame
        row = row + 1
        from chimera.widgets import ModelOptionMenu
        self.probe_menu = ModelOptionMenu(parent,
                                command=self.probe_menu_cb,
                                labelpos='w',
                                label_text='Probe Model:')
        self.probe_menu.grid(row=row, sticky='w', padx=8, pady=8)

        # probe parameters frame
        row = row + 1
        ppf = Tkinter.Frame(parent, padx=8, pady=8)
        ppf.grid(row = row, column = 0, sticky = 'nw')
        self._make_probe_parameters_panel(ppf)

        # parameter units frame
        row = row + 1
        puf = Tkinter.Frame(parent, padx=8, pady=8)
        puf.grid(row = row, column = 0, sticky = 'nw')
        self._make_parameter_units_panel(puf)
        self.parameter_units_panel_button.popup_frame(puf,
                                    row=row, column=0, sticky='nw')
        self.parameter_units_panel_button.variable.set(0)
        
        # probe transform frame
        row = row + 1
        pxf = Tkinter.Frame(parent, padx=8, pady=8)
        pxf.grid(row = row, column = 0, sticky = 'nw')
        self._make_probe_xform_panel(pxf)
        self.probe_xform_panel_button.popup_frame(pxf,
                                    row=row, column=0, sticky='nw')
        self.probe_xform_panel_button.variable.set(0)

        # optimize options frame
        row = row + 1
        oof = Tkinter.Frame(parent, padx=8, pady=8)
        oof.grid(row = row, column = 0, sticky = 'nw')
        self._make_optimize_options_panel(oof)
        self.optimize_panels_button.popup_frame(oof,
                                    row=row, column=0, sticky='nw')
        self.optimize_panels_button.variable.set(0)

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

        self.distance_unit_menu.variable.set(self.distance_units[0])
        self.angle_unit_menu.variable.set(self.angle_units[1])
        self.angle_convention_menu.variable.set(self.angle_conventions[0])

        # @ do we need to do stuff before closing Chimera session
        #   or this segmentation dialog

    # ---------------------------------------------------------------------
    # Panels
    # ---------------------------------------------------------------------

    def _make_probe_parameters_panel(self, frame):
        """_make_probe_parameters_panel(frame)

        Make a panel in the GUI for parameter.
        """

        row = 0

        # parameters label (puL)
        ppL = Tkinter.Label(frame,
                            text = 'Density Parameters ')
        ppL.grid(row = row, column = 0, sticky = 'nw')

        # probe parameters frame
        row = row + 1
        ppf = Tkinter.Frame(frame, padx=40)
        ppf.grid(row = row, column = 0, sticky = 'nw')

        # probe parameter angstroms/pixel
        ppapp_e = Hybrid.Entry(ppf, ' Angstroms per pixel ', '8', '1.0')
        ppapp_e.frame.grid(row=0, column=0, sticky = 'nw')
        self.angstroms_per_pixel = ppapp_e

        # probe parameter resolution
        ppr_e = Hybrid.Entry(ppf, ' Resolution ', '8', '1.0')
        ppr_e.frame.grid(row=0, column=1, sticky = 'nw')
        self.probe_resolution = ppr_e

        return
    
    def _make_parameter_units_panel(self, frame):
        """_make_parameter_units_panel(frame)

        Make a panel in the GUI for parameter units.
        """

        row = 0

        # parameter units label (puL)
        puL = Tkinter.Label(frame,
                            text = 'Parameter Units ')
        puL.grid(row = row, column = 0, sticky = 'nw')

        # parameter units frame
        row = row + 1
        puf = Tkinter.Frame(frame, padx=40)
        puf.grid(row = row, column = 0, sticky = 'nw')

        # parameter units translate (putx)
        putx = Hybrid.Option_Menu(puf, 'Distance units : ',
                                 self.distance_units[0],
                                 self.distance_units[1])
        putx.frame.grid(row = 0, column = 0, sticky = 'nw')
        putx.add_callback(self.distance_unit_type_cb)
        self.distance_unit_menu = putx

        # parameter units rotation (purx)
        purx = Hybrid.Option_Menu(puf, 'Angle units : ',
                                 self.angle_units[0],
                                 self.angle_units[1])
        purx.frame.grid(row = 0, column = 1, sticky = 'nw')
        purx.add_callback(self.angle_unit_type_cb)
        self.angle_unit_menu = purx

        # parameter units angle convention (puax)
        puax = Hybrid.Option_Menu(puf, 'Rotation conventions : ',
                                 self.angle_conventions[0],
                                 self.angle_conventions[1])
        puax.frame.grid(row=1, column=0, sticky = 'nw', columnspan=2)
        puax.add_callback(self.angle_convention_type_cb)
        self.angle_convention_menu = puax

        return

    def _make_probe_xform_panel(self, frame):
        """_make_probe_xform_panel(frame)

        Make a panel in the GUI for probe transform parameters.
        """

        row = 0

        # probe trasform label (pxL)
        pxL = Tkinter.Label(frame,
                            text = 'Probe Transform ')
        pxL.grid(row = row, column = 0, sticky = 'nw')

        row = row + 1
        # probe transform parameters (pxp)
        
        pxp = Tkinter.Frame(frame, padx=40)
        pxp.grid(row = row, column = 0, sticky = 'nw')

        pxtL = Tkinter.Label(pxp, text = 'Translation: ')
        pxtL.grid(row = 0, column = 0, sticky = 'w')

        pxr1L = Tkinter.Label(pxp, text = 'Euler : ')
        pxr1L.grid(row = 1, column = 0, sticky = 'w')

        pxr1L = Tkinter.Label(pxp, text = 'Spin Axis: ')
        pxr1L.grid(row = 2, column = 0, sticky = 'w')

        # probe transform translation
        self.probe_translation_entry = []
        for a in range(3):
            pxt_e = Hybrid.Entry(pxp, '', 8)
            pxt_e.frame.grid(row = 0, column = a+1, sticky = 'w')
            pxt_e.entry.bind('<KeyPress-Return>',
                             self.set_probe_to_xform_cb)
            self.probe_translation_entry.append(pxt_e)
        
        # probe transform rotation euler 
        self.probe_rotation_euler_entry = []
        for a in range(3):
            pxr1_e = Hybrid.Entry(pxp, '', 8)
            pxr1_e.frame.grid(row = 1, column = a+1, sticky = 'w')
            pxr1_e.entry.bind('<KeyPress-Return>',
                             self.set_probe_to_xform_cb)
            self.probe_rotation_euler_entry.append(pxr1_e)

        # probe transform rotation spin axis 
        self.probe_rotation_spin_entry = []
        for a in range(4):
            pxr2_e = Hybrid.Entry(pxp, '', 8)
            pxr2_e.frame.grid(row = 2, column = a+1, sticky = 'w')
            pxr2_e.entry.bind('<KeyPress-Return>',
                             self.set_probe_to_xform_cb)
            self.probe_rotation_spin_entry.append(pxr2_e)

        row = row + 1
        
        # probe transform buttons (pxb)

        pxb = Hybrid.Button_Row(frame, '',
                                ((' Apply Xform ',
                                  self.apply_xform_to_probe_cb),
                                 (' Set Xform ',
                                  self.set_probe_to_xform_cb),
                                 (' Get Xform ',
                                  self.get_xform_of_probe_cb),
                                 (' Reset ',
                                  self.reset_xform_of_probe_cb)))
        pxb.frame.grid(row=row,column=0,sticky='w',padx=40,pady=4)

        row = row+ 1

        # probe transform step

        pxs = Tkinter.Frame(frame, padx=40, pady=4)
        pxs.grid(row = row, column = 0, sticky = 'nw')

        pxsB = Hybrid.Button_Row(pxs, '',
                                 (('Step', self.step_probe_xform_cb),))
        pxsB.frame.grid(row = 0, column = 0, sticky = 'w')

        pxsd_e = Hybrid.Entry(pxs, ' by ', '5', '1.0')
        pxsd_e.frame.grid(row = 0, column = 1, sticky = 'w')
        pxsd_e.entry.bind('<KeyPress-Return>', self.step_probe_xform_cb)
        self.probe_step_xyz_entry = pxsd_e

        pxsdu = Tkinter.Label(pxs, text = ' distance and')
        pxsdu.grid(row = 0, column = 2, sticky = 'w')

        pxsa_e = Hybrid.Entry(pxs, ' by ', '5', '10.0')
        pxsa_e.frame.grid(row = 0, column = 3, sticky = 'w')
        pxsa_e.entry.bind('<KeyPress-Return>', self.step_probe_xform_cb)
        self.probe_step_ang_entry = pxsa_e

        pxsau = Tkinter.Label(pxs, text = ' angle')
        pxsau.grid(row = 0, column = 4, sticky = 'w')
        
        pxstcb = Hybrid.Checkbutton_Row(pxs, 'Translation: ',
                                        ('dx','dy','dz'))
        pxstcb.frame.grid(row=2, column=0, sticky='w', columnspan=5)
        (self.probe_step_dx,  self.probe_step_dy,
         self.probe_step_dz) = pxstcb.checkbuttons

        pxsecb = Hybrid.Checkbutton_Row(pxs, 'Euler      : ',
                                        ('da0','da1','da2'))
        pxsecb.frame.grid(row=3, column=0, sticky='w', columnspan=5)
        (self.probe_step_da0, self.probe_step_da1,
         self.probe_step_da2) = pxsecb.checkbuttons

        pxsscb = Hybrid.Checkbutton_Row(pxs, 'Spin Axis  : ',
                                        ('ds0',))
        pxsscb.frame.grid(row=4, column=0, sticky='w', columnspan=5)
        (self.probe_step_ds0, ) = pxsscb.checkbuttons

        return
        
    def _make_optimize_options_panel(self, frame):
        """_make_optimize_options_panel(frame)

        Make a panel in the GUI for optimize options.
        """

        row = 0

        # optimize values label (ovL)
        ovL = Tkinter.Label(frame,
                            text = 'Optimize Parameters ')
        ovL.grid(row = row, column = 0, sticky = 'nw')

        # mean density parameters
        row = row + 1
        
        opmd = Tkinter.Frame(frame, padx=40, pady=4)
        opmd.grid(row=row, column=0, sticky = 'nw')

        opmd_rL = Tkinter.Label(opmd, text='Euler Range: ')
        opmd_rL.grid(row=0,column=0, sticky='nw')

        self.probe_rotation_range_entry = []
        for a in range(3):
            opmd_e = Hybrid.Entry(opmd, ' ','8','1.0')
            opmd_e.frame.grid(row = 0, column = a+1, sticky = 'w')
            self.probe_rotation_range_entry.append(opmd_e)
            
        opmd_sL = Tkinter.Label(opmd, text='Euler Step : ')
        opmd_sL.grid(row=1,column=0, sticky='nw')
        
        self.probe_rotation_step_entry = []
        for a in range(3):
            opmd_e = Hybrid.Entry(opmd, ' ','8','1.0')
            opmd_e.frame.grid(row = 1, column = a+1, sticky = 'w')
            self.probe_rotation_step_entry.append(opmd_e)

        row = row + 1

        # optimize values label (ooL)
        ooL = Tkinter.Label(frame,
                            text = 'Optimize Options ')
        ooL.grid(row = row, column = 0, sticky = 'nw')

        # mean density option
        row = row + 1
        
        omd = Tkinter.Frame(frame, padx=40, pady=4)
        omd.grid(row = row, column = 0, sticky = 'nw')

        omd_e = Hybrid.Entry(omd, 'Mean density at C-A ', '8', '0.0')
        omd_e.frame.grid(row=0, column=0, sticky = 'nw')
        self.mean_density_entry = omd_e

        omdB = Hybrid.Button_Row(omd, '',
                                 (('Get',
                                   self.get_probe_data_mean_density_cb),
                                  ('Optimize',
                                   self.optimize_probe_locally_cb),
                                  ('Save Probe',
                                   self.save_probe_cb)))
        omdB.frame.grid(row = 0, column = 1, sticky = 'w',padx=2)

        # foldhunter option
        row = row + 1
        
        ofh = Tkinter.Frame(frame, padx=40, pady=2)
        ofh.grid(row = row, column = 0, sticky = 'nw')

        ofhL = Tkinter.Label(ofh, text = 'Foldhunter ')
        ofhL.grid(row=0, column=0, sticky = 'nw')

        ofhB = Hybrid.Button_Row(ofh, '',
                                ((' Apply ',
                                  self.apply_foldhunter_cb),))
        ofhB.frame.grid(row=0,column=1,sticky='w')

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
            # msg = ''
            msg = 'Data item %s not shown\n' % (data_item.name)
        elif data_status == self.data_panel.DATA_SHOWN:
            msg = 'Data item %s shown\n'% (data_item.name)
        else:
            msg = 'No data items present\n'

        # self.status(msg, color='blue', blankAfter=15)
        # if data_status == self.data_panel.DATA_EMPTY:
        #    replyobj.info(msg)

        # activate/deactivate model
        if data_status == self.data_panel.DATA_SHOWN:
            
            import SegmentMenu
            from SegmentMenu import datamenuseg
            
            open_models = datamenuseg.open_models_list()
            dr = self.data_item.region
            model = datamenuseg.find_model_data_region(dr, open_models)
        else:
            model = None
        self.model = model

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
    # Parameter units functions
    # ---------------------------------------------------------------------

    def distance_unit_type_cb(self):
        """distance_unit_type_cb() - callback for distance unit type

        Displays a message and activates/decativates output
        parameters panel.
        """

        dut = self.distance_unit_menu.variable.get()
        if not (dut in self.distance_units.values()):
            dut = self.distance_units.values()[0]
            self.distance_unit_menu.variable.set(dut)
            # self.choose_region_type_cb()
            print 'unknow distance unit'
            return
            
        if   dut == self.distance_units[0]:
            # angstroms
            msg = 'Distance unit is Angstroms!\n'
        elif dut == self.distance_units[1]:
            # pixels
            msg = 'Distance unit is pixels!\n'
        else:
            # unknown distance unit
            pass

        if dut != self.probe_translate_unit:
            self.probe_translate_unit = dut
            self.update_probe_units_cb()
        
        return

    def angle_unit_type_cb(self):
        """angle_unit_type_cb() - callback for angle unit type

        Displays a message and activates/decativates output
        parameters panel.
        """

        aut = self.angle_unit_menu.variable.get()
        if not (aut in self.angle_units.values()):
            aut = self.angle_units.values()[0]
            self.angle_unit_menu.variable.set(aut)
            # self.choose_region_type_cb()
            print 'unknow angle unit'
            return
            
        if   aut == self.angle_units[0]:
            # radians
            msg = 'Angle unit is Radians!\n'
        elif aut == self.angle_units[1]:
            # degrees
            msg = 'Angle unit is Degrees!\n'
        else:
            # unknown angle unit
            pass

        if aut != self.probe_rotate_unit:
            self.probe_rotate_unit = aut
            self.update_probe_units_cb()
        
        return

    def update_probe_units_cb(self):
        """update_probe_units_cb() - callback

        Update probe parameter units.
        """

        # @ maybe automatically convert from one unit to
        #   another unit, but how do you remember the old unit?
        
        return

    def angle_convention_type_cb(self):
        """angle_convention_type_cb() - callback for convention type

        Displays a message and activates/decativates output
        parameters panel.
        """

        act = self.angle_convention_menu.variable.get()
        if not (act in self.angle_conventions.values()):
            aut = self.angle_conventions.values()[0]
            self.angle_convention_menu.variable.set(aut)
            # self.choose_region_type_cb()
            print 'unknow angle convention'
            return

        if   act == self.angle_conventions[0]:
            # EMAN Euler angles
            for a in range(3):
                self.probe_rotation_euler_entry[a].entry['state'] = \
                                                        'normal'
            for a in range(4):
                self.probe_rotation_spin_entry[a].entry['state'] = \
                                                        'readonly'
        elif act == self.angle_conventions[1]:
            # Spin Axis angles
            for a in range(4):
                self.probe_rotation_spin_entry[a].entry['state'] = \
                                                        'normal'
            for a in range(3):
                self.probe_rotation_euler_entry[a].entry['state'] = \
                                                        'readonly'

        if act != self.angle_convention:
            self.angle_convention = act
            # self.update_probe_units_cb()

        return

    # ---------------------------------------------------------------------
    #  Probe Structures related callback functions
    # ---------------------------------------------------------------------

    def probe_menu_cb(self, val):
        """probe_menu_cb(val) - callback for probe menu
        """
        
        return

    def step_probe_xform_cb(self, event=None):

        tx_val, rx_val = self.get_xform_from_entry()
        if tx_val == None or rx_val == None:
            return

        if   self.probe_rotate_unit == self.angle_units[0]:
            angle_factor = 1.0
        elif self.probe_rotate_unit == self.angle_units[1]:
            import math
            angle_factor = math.pi/180.0

        try:
            apix = float(self.angstroms_per_pixel.variable.get())
        except:
            msg = 'Check angstroms/pixel value!\n'
            self.status(msg, color='red', blankAfter=10)
            replyobj.error(msg)
            return
            
        if   self.probe_translate_unit == self.distance_units[0]:
            distance_factor = 1.0
        elif self.probe_translate_unit == self.distance_units[1]:
            distance_factor = apix

        try:
            dxyz_step = float(self.probe_step_xyz_entry.variable.get())
        except:
            msg = 'Check xyz step value!\n'
            self.status(msg, color='red', blankAfter=10)
            replyobj.error(msg)
            return
        
        dxyz_step = dxyz_step*distance_factor
        
        if self.probe_step_dx.variable.get():
            dx = dxyz_step
            tx_val[0] = tx_val[0] + dx
        if self.probe_step_dy.variable.get():
            dy = dxyz_step
            tx_val[1] = tx_val[1] + dy
        if self.probe_step_dz.variable.get():
            dz = dxyz_step
            tx_val[2] = tx_val[2] + dz

        try:
            dang_step = float(self.probe_step_ang_entry.variable.get())
        except:
            msg = 'Check angle step value!\n'
            self.status(msg, color='red', blankAfter=10)
            replyobj.error(msg)
            return
        
        dang_step = dang_step*angle_factor

        if self.angle_convention == self.angle_conventions[0]:
            if self.probe_step_da0.variable.get():
                da0 = dang_step
                rx_val[0] = rx_val[0] + da0
            if self.probe_step_da1.variable.get():
                da1 = dang_step
                rx_val[1] = rx_val[1] + da1
            if self.probe_step_da2.variable.get():
                da2 = dang_step
                rx_val[2] = rx_val[2] + da2
        elif self.angle_convention == self.angle_conventions[1]:
            if self.probe_step_ds0.variable.get():
                ds0 = dang_step
                rx_val[0] = rx_val[0] + ds0
        else:
            # unknow angle convention
            pass
            
        # Also, takes care of rounding effects
        if self.angle_convention == self.angle_conventions[0]:
            self.update_probe_xform_euler_entry(tx_val, rx_val)
        elif self.angle_convention == self.angle_conventions[1]:
            self.update_probe_xform_spin_entry(tx_val, rx_val)
        else:
            # unknow angle convention
            pass

        self.set_probe_to_xform_cb()

        return

    def apply_xform_to_probe_cb(self, event=None):

        model = self.probe_menu.getvalue()

        tx_val, rx_val = self.get_xform_from_entry()
        if tx_val == None or rx_val == None:
            return

        # To take care of rounding effects
        if self.angle_convention == self.angle_conventions[0]:
            self.update_probe_xform_euler_entry(tx_val, rx_val)
        elif self.angle_convention == self.angle_conventions[1]:
            self.update_probe_xform_spin_entry(tx_val, rx_val)
        else:
            # unknow angle convention
            pass
        
        tx_val, rx_val = self.get_xform_from_entry()

        self.set_model_to_xform(model, tx_val, rx_val,overall=0)

        return
        
    def set_probe_to_xform_cb(self, event=None):

        model = self.probe_menu.getvalue()

        tx_val, rx_val = self.get_xform_from_entry()
        if tx_val == None or rx_val == None:
            return

        # To take care of rounding effects
        if   self.angle_convention == self.angle_conventions[0]:
            self.update_probe_xform_euler_entry(tx_val, rx_val)
        elif self.angle_convention == self.angle_conventions[1]:
            self.update_probe_xform_spin_entry(tx_val, rx_val)
        else:
            # unknown angle convention
            pass
        
        tx_val, rx_val = self.get_xform_from_entry()

        self.set_model_to_xform(model, tx_val, rx_val,overall=1)

        return

    def get_xform_of_probe_cb(self):

        model = self.probe_menu.getvalue()

        tx_val, rx_val = self.get_xform_of_model(model)
        if tx_val == None or rx_val == None:
            return

        self.update_probe_xform_spin_entry(tx_val, rx_val)
        rx_val_euler = self.convert_spin_to_euler(rx_val)
        self.update_probe_xform_euler_entry(tx_val, rx_val_euler)
        
        # @ To take care of rounding effects
        if   self.angle_convention == self.angle_conventions[0]:
            rx_val = rx_val_euler
        elif self.angle_convention == self.angle_conventions[1]:
            pass

        self.set_model_to_xform(model, tx_val, rx_val,overall=1)
        
        return

    def reset_xform_of_probe_cb(self):

        model = self.probe_menu.getvalue()
        self.reset_xform_of_model(model)

        self.update_probe_xform_euler_entry()
        self.update_probe_xform_spin_entry()        

        return
        
    # ---------------------------------------------------------------------
    #  Probe Structures related functions
    # ---------------------------------------------------------------------

    def get_xform_from_entry(self):
        """get_xform_from_entry()

        Get probe transform parameters from entry box. 

        Output:
            tx_val      translation (first)
            rx_val      rotation (second)
                            - EMAN Euler convention OR
                            - Spin Axis convention

        Returns None, None if invalid parameters.
        """

        tx_val = []
        rx_val = []

        if   self.probe_rotate_unit == self.angle_units[0]:
            angle_factor = 1.0
        elif self.probe_rotate_unit == self.angle_units[1]:
            import math
            angle_factor = math.pi/180.0

        try:
            apix = float(self.angstroms_per_pixel.variable.get())
        except:
            msg = 'Check angstroms/pixel value!\n'
            self.status(msg, color='red', blankAfter=10)
            replyobj.error(msg)
            return

        if   self.probe_translate_unit == self.distance_units[0]:
            distance_factor = 1.0
        elif self.probe_translate_unit == self.distance_units[1]:
            distance_factor = apix
        
        for a in range(3):
            try:
                ev = float(self.probe_translation_entry[a].variable.get())
            except:
                self.probe_invalid_parameters()
                return None, None
            tx_val.append(ev*distance_factor)

        if self.angle_convention == self.angle_conventions[0]:
            for a in range(3):
                try:
                    ev = self.probe_rotation_euler_entry[a].variable.get()
                    ev = float(ev)
                except:
                    self.probe_invalid_parameters()
                    return None, None
                rx_val.append(ev*angle_factor)
        elif self.angle_convention == self.angle_conventions[1]:
            for a in range(4):
                try:
                    ev = self.probe_rotation_spin_entry[a].variable.get()
                    ev = float(ev)
                except:
                    self.probe_invalid_parameters()
                    return None, None
                if a == 0:
                    rx_val.append(ev*angle_factor)
                else:
                    rx_val.append(ev*distance_factor)
        else:
            # unknown angle convention
            pass
        
        # @ Rectify EMAN Euler angles or Spin Axis angles
        import transrot
        if self.angle_convention == self.angle_conventions[0]:
            rx_val = transrot.euler_rectify(rx_val)
        elif self.angle_convention == self.angle_conventions[1]:
            axis_val, ang_val = \
                      transrot.axis_angle_rectify(rx_val[1:], rx_val[0])
            rx_val[0] = ang_val
            for a in range(3):
                rx_val[a+1] = axis_val[a]

        return tx_val, rx_val

    def probe_invalid_parameters(self):
        """probe_invalid_parameters()

        Warning message stating that the probe parameters are invalid.
        """

        msg = 'Parameters for probe are invalid!\n'
        self.status(msg, color='red', blankAfter=15)
        replyobj.warning(msg)

        return
    
    def update_probe_xform_euler_entry(self, tx_val=None, rx_val=None):
        """update_probe_xform_euler_entry(tx_val=None, rx_val=None)

        Update probe transform info with input parameters. If no
        input parameters are given, then set the values to 0.0.

        The output parameters displayed depend on the units
        selected for the probe rotation angle and the probe
        trnaslation distance, i.e., degrees vs. radians, and
        angstroms vs. pixels. The input parmaeters are, however,
        assumed to be in angstroms/radians units.
        
        Input:
            tx_val      translation (first)
            rx_val      rotation (second) - EMAN Euler convention
        """

        if tx_val == None or rx_val == None:
            translate_val = [0,0,0]
            rotate_val = [0,0,0]
        else:
            translate_val = tx_val
            rotate_val = rx_val

        if   self.probe_rotate_unit == self.angle_units[0]:
            angle_factor = 1.0
        elif self.probe_rotate_unit == self.angle_units[1]:
            import math
            angle_factor = 180.0/math.pi

        try:
            apix = float(self.angstroms_per_pixel.variable.get())
        except:
            msg = 'Check angstroms/pixel value!\n'
            self.status(msg, color='red', blankAfter=10)
            replyobj.error(msg)
            return

        if   self.probe_translate_unit == self.distance_units[0]:
            distance_factor = 1.0
        elif self.probe_translate_unit == self.distance_units[1]:
            distance_factor = 1/apix
        
        for a in range(3):
            ev = '%7.4f' % (translate_val[a]*distance_factor)
            self.probe_translation_entry[a].variable.set(ev)
            ev = '%4.2f' % (rotate_val[a]*angle_factor)
            self.probe_rotation_euler_entry[a].variable.set(ev)

        return

    def update_probe_xform_spin_entry(self, tx_val=None, rx_val=None):
        """update_probe_xform_spin_entry(tx_val=None, rx_val=None)

        Update probe transform info with input parameters. If no
        input parameters are given, then set the values to 0.0.

        The output parameters displayed depend on the units
        selected for the probe rotation angle and the probe
        trnaslation distance, i.e., degrees vs. radians, and
        angstroms vs. pixels. The input parmaeters are, however,
        assumed to be in angstroms/radians units.
        
        Input:
            tx_val      translation (first)
            rx_val      rotation (second) - Spin Axis convention
        """

        if tx_val == None or rx_val == None:
            translate_val = [0.,0.,0.]
            rotate_val = [0.,0.,0.,1.]
        else:
            translate_val = tx_val
            rotate_val = rx_val

        if   self.probe_rotate_unit == self.angle_units[0]:
            angle_factor = 1.0
        elif self.probe_rotate_unit == self.angle_units[1]:
            import math
            angle_factor = 180.0/math.pi

        try:
            apix = float(self.angstroms_per_pixel.variable.get())
        except:
            msg = 'Check angstroms/pixel value!\n'
            self.status(msg, color='red', blankAfter=10)
            replyobj.error(msg)
            return

        if   self.probe_translate_unit == self.distance_units[0]:
            distance_factor = 1.0
        elif self.probe_translate_unit == self.distance_units[1]:
            distance_factor = 1/apix
        
        for a in range(3):
            ev = '%7.4f' % (translate_val[a]*distance_factor)
            self.probe_translation_entry[a].variable.set(ev)
            ev = '%7.4f' % (rotate_val[a+1]*distance_factor)
            self.probe_rotation_spin_entry[a+1].variable.set(ev)
        ev = '%4.2f' % (rotate_val[0]*angle_factor)
        self.probe_rotation_spin_entry[0].variable.set(ev)

        return

    # ---------------------------------------------------------------------
    #  Tranformation related functions
    # ---------------------------------------------------------------------

    def get_xform_of_model(self, model=None):
        """get_xform_of_model(model=None)

        Get transform of model in EMAN Euler angles.

        Input:
            model=None  input model

        Output
            tx_val      translation (first)
            rx_val      rotation (second) - Spin Axis convention

        If no input model, return None, None
        """
        
        if model == None:
            return None, None

        # from SegmentTrack import trackxform
        # xform = trackxform.get_xform(model)
        xf = model.openState.xform
        
        # print xf
        
        # chimera transformation coordinates        
        tx = xf.getTranslation()
        ax, an_deg = xf.getRotation()

        import math
        an_val = an_deg*math.pi/180.0
        
        tx_val = [tx.x, tx.y, tx.z]
        ax_val = [ax.x, ax.y, ax.z]

        rx_val = [an_val, ax.x, ax.y, ax.z]

        return tx_val, rx_val
    
    def convert_spin_to_euler(self, rx_val):
        """convert_spin__to_euler(rx_val)

        Convert Spin Axis convetion to EMAN Euler convention.

        Input:
            rx_val      rotation - Spin Axis convention

        Output:
            rx_val      rotation - EMAN Euler convention
        """

        ax_val = rx_val[1:]
        an_val = rx_val[0]
        
        import transrot
        rot = transrot.cRotation(axis_val=ax_val, ang_val=an_val,
                                 rot_type=2)
        rx_val = rot.get_euler_val()

        return rx_val

    def convert_euler_to_spin(self, rx_val):
        """convert_euler_to_spin(rx_val)

        Convert EMAN Euler convention to Spin Axis convention.

        Input:
            rx_val      rotation - EMAN Euler convention

        Output:
            rx_val      rotation - Spin Axis convention
        """

        import transrot
        rot = transrot.cRotation(euler_val=rx_val, rot_type=3)
        ax_val, an_val = rot.get_axis_angle()

        rx_val = []
        rx_val.append(an_val)
        rx_val = rx_val + ax_val

        return rx_val

    def set_model_to_xform(self, model=None, tx_val=None, rx_val=None,
                           overall=0):
        """set_model_to_xform(model=None, tx_val=None, rx_val=None,
                            overall=0)

        Set transform in Spin Axis or Euler angles to model.

        Input:
            model=None  input model
            tx_val      translation (first)
            rx_val      rotation (second)
                            - Spin Axis or EMAN Euler angles
            overall=0   if overall=0, then add the transform
                            to existing transform, else replace
                            existing transform with current one

        If no model or no translation/rotation parameters, return.
        """
        
        if model == None or tx_val == None or rx_val == None:
            return

        import transrot
        if self.angle_convention == self.angle_conventions[0]:
            rot = transrot.cRotation(euler_val=rx_val, rot_type=3)
            ax_val, an_val = rot.get_axis_angle()
        elif self.angle_convention == self.angle_conventions[1]:
            ax_val = rx_val[1:]
            an_val = rx_val[0]
        else:
            # unknown angle convention
            pass

        import math
        ax = chimera.Vector(ax_val[0],ax_val[1],ax_val[2])
        an = an_val*180.0/math.pi
        tx = chimera.Vector(tx_val[0],tx_val[1],tx_val[2])

        xf = chimera.Xform()
        xf.translate(tx)
        xf.rotate(ax, an)

        # print xf
        
        if overall == 1:
            model.openState.xform = xf
        else:
            # rotaiton about global axis
            model.openState.globalXform(xf)
            # rotaiton about local axis
            # model.openState.localXform(xf)
        
        return 

    def reset_xform_of_model(self, model=None):
        """reset_xform_of_model(model=None)

        Set transform to identity in Chimera coordiantes.

        Input:
            model=None  input model
        """

        # @ For Chimera release version greater than 1.2176,
        #   the Xform_xxx has been changed to Xform.xxx()

        #VU 1.2176
        try:
            xf = chimera.Xform_identity()
        except:
            xf = chimera.Xform.identity()
        model.openState.xform = xf
        
        return

    # ---------------------------------------------------------------------
    #  Correlation related functions
    # ---------------------------------------------------------------------

    def get_probe_data_mean_density_cb(self):

        self.get_probe_data_mean_density()

        return
    
    def get_probe_data_mean_density(self):

        model, data_item = self.get_probe_and_density(pdb_check=1,
                                                 density_check=1)
        if model == None or data_item == None:
            mean1 = 0.0
        else:
            data = data_item.data
            import correl
            mean1 = correl.get_mean_density(model, data)
        self.mean_density_entry.variable.set('%8.5f' % mean1)
        
        return mean1    
            
    def get_probe_and_density(self, pdb_check=1, density_check=1):
        
        model = self.probe_menu.getvalue()
        if self.data_item == None:
            data_item = None
        else:
            data_item = self.data_item

        if density_check == 1 and data_item == None:
            msg = 'Select a density map!\n'
            self.status(msg, color='red', blankAfter=10)
            replyobj.error(msg)
            return None, None
        
        if pdb_check == 1:
            from chimera import Molecule
            if model is None or not isinstance(model, Molecule):
                print model.__class__
                msg = 'Select a PDB model as probe!\n'
                self.status(msg, color='red', blankAfter=10)
                replyobj.error(msg)
                return None, None

        return model, data_item
    
    # ---------------------------------------------------------------------
    #  Optimize locally functions
    # ---------------------------------------------------------------------

    def optimize_probe_locally_cb(self):

        model, data_item = self.get_probe_and_density(pdb_check=1,
                                                 density_check=1)

        if model == None or data_item == None:
            return
        data = data_item.data
        
        self.get_xform_of_probe_cb()

        tx_val, rx_val = self.get_xform_from_entry()
        if tx_val == None or rx_val == None:
            return
        
        if self.angle_convention == self.angle_conventions[0]:
            pass
        elif self.angle_convention == self.angle_conventions[1]:
            rx_val = self.convert_spin_to_euler(rx_val)

        # preform search within delta_xyz and delta_angle here
        a0, a1, a2 = rx_val

        # read values from entry box
        
        if   self.probe_rotate_unit == self.angle_units[0]:
            angle_factor = 1.0
        elif self.probe_rotate_unit == self.angle_units[1]:
            import math
            angle_factor = math.pi/180.0

        d_step = []
        d_range = []
        for a in range(3):
            try:
                ev = self.probe_rotation_step_entry[a].variable.get()
                ev = float(ev)
            except:
                ev = 1.0
            d_step.append(ev*angle_factor)
            try:
                ev = self.probe_rotation_range_entry[a].variable.get()
                ev = float(ev)
            except:
                ev = 2.0
            d_range.append(ev*angle_factor)

        mean1 = []
        mean2 = []
        bang1 = []
        for b0 in frange(-d_range[0], +d_range[0], d_step[0]):
            for b1 in frange(-d_range[1], +d_range[1], d_step[1]):
                for b2 in frange(-d_range[2], +d_range[2], d_step[2]):
                    bt0 = b0 + a0
                    bt1 = b1 + a1
                    bt2 = b2 + a2
                    rx_val_now = [bt0,bt1,bt2]
                    if self.angle_convention == \
                       self.angle_conventions[0]:
                        pass
                    elif self.angle_convention == \
                         self.angle_conventions[1]:
                        rx_val_now = self.convert_euler_to_spin(rx_val_now)
                    self.set_model_to_xform(model, tx_val, rx_val_now,
                                            overall=1)
                    mean1.append(self.get_probe_data_mean_density())
                    bang1.append([bt0,bt1,bt2])
                    print '%f %f %f %f' % (tuple([mean1[-1]]+rx_val_now))

        # find best rx

        ang_ind = mean1.index(max(mean1))
        rx_best = bang1[ang_ind]

        self.set_model_to_xform(model,tx_val, rx_best, overall=1)
        self.get_xform_of_probe_cb()
        self.get_probe_data_mean_density_cb()
        
        return
        
    # ---------------------------------------------------------------------
    #  Prepare for foldhunterP functions
    # ---------------------------------------------------------------------

    def save_probe_cb(self):
        """save_probe_cb()

        Save the probe on menu.
        """

        model = self.probe_menu.getvalue()
        if model == None:
            return

        from ModelPanel import writePDBdialog
        writePDBdialog.WritePDBdialog()

        # model_id = int(model.oslIdent().strip('#'))
        # import Midas
        # Midas.write(model_id, model_id, file_name)

        return

    # ---------------------------------------------------------------------
    #  foldhunterP functions
    # ---------------------------------------------------------------------

    def apply_foldhunter_cb(self):
        """apply_foldhunter_cb()

        Run foldhunterP
        """

        model, data_item = self.get_probe_and_density(pdb_check=1,
                                                 density_check=1)
        if model == None or data_item == None:
            return

        self.get_xform_of_probe_cb()

        tx_val, rx_val = self.get_xform_from_entry()
        if tx_val == None or rx_val == None:
            return
        
        if self.angle_convention == self.angle_conventions[0]:
            pass
        elif self.angle_convention == self.angle_conventions[1]:
            rx_val = self.convert_spin_to_euler(rx_val)

        # preform search within delta_xyz and delta_angle here
        a0, a1, a2 = rx_val

        probe_path = model.openedAs[0]
        target_path = data_item.path

        import os
        probe_name = os.path.basename(probe_path)
        target_name = os.path.basename(target_path)

        # @ first check if EMAN recognized

        # get apix and res
        
        try:
            apix = float(self.angstroms_per_pixel.variable.get())
        except:
            msg = 'Check angstroms/pixel value!\n'
            self.status(msg, color='red', blankAfter=10)
            replyobj.error(msg)
            return

        try:
            res = float(self.probe_resolution.variable.get())
        except:
            msg = 'Check probe resolution value!\n'
            self.status(msg, color='red', blankAfter=10)
            replyobj.error(msg)
            return

        # convert PDB to MRC

        probe_mrc_path = os.path.splitext(probe_path)[0]
        probe_mrc_path = probe_mrc_path + '.mrc'

        boxSize = data_item.size[0]
        cmdpdb2mrc = 'pdb2mrc %s %s apix=%f res=%f box=%d' % \
                     (probe_path, probe_mrc_path, apix, res, boxSize)
        print '%s' % cmdpdb2mrc
        os.system(cmdpdb2mrc)

        # convert to degrees
        if   self.probe_rotate_unit == self.angle_units[0]:
            import math
            angle_factor = 180.0/math.pi
        elif self.probe_rotate_unit == self.angle_units[1]:
            angle_factor = 1.0

        a0 = a0*angle_factor
        a1 = a1*angle_factor
        a2 = a2*angle_factor

        # angle range and step size
        dang_range = []
        dang_step  = []
        for a in range(3):
            try:
                ev = self.probe_rotation_step_entry[a].variable.get()
                ev = float(ev)
            except:
                msg = 'Check angle step value!\n'
                self.status(msg, color='red', blankAfter=10)
                replyobj.error(msg)
                return
            dang_step.append(ev*angle_factor)
            try:
                ev = self.probe_rotation_range_entry[a].variable.get()
                ev = float(ev)
            except:
                msg = 'Check angle range value!\n'
                self.status(msg, color='red', blankAfter=10)
                replyobj.error(msg)
                return
            dang_range.append(ev*angle_factor)

        da0,da1,da2 = dang_step
        ra0,ra1,ra2 = dang_range
        
        # get foldhunterP files
        target_path_sans_ext = os.path.splitext(target_path)[0]
        out_path = target_path_sans_ext + '-fh.mrc'
        log_path = target_path_sans_ext + '-log.txt'
        keep = 1

        # run foldhunterP files
        cmdfhP = 'foldhunterP %s %s %s log=%s da=%f,%f,%f keep=%d startangle=%f,%f,%f range=%f,%f,%f, apix=%f res=%f verbose' % \
                 (target_path, probe_mrc_path, out_path, log_path, da0, da1, da2, keep, a1,a0,a2, ra1, ra0, ra2, apix, res)
        print '%s' % cmdfhP
        os.system(cmdfhP)
        
        # open output
        
        out_dir = os.path.dirname(out_path)
        out_files = [os.path.basename(out_path)]

        self.open_output_data_items(out_dir, out_files)

        return
    
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

# -------------------------------------------------------------------------
#  Misc functions.
# -------------------------------------------------------------------------

def frange(start_val, end_val=None, inc_val=1.0):
    """frange(start_val, end_val=None, inc_val=1.0)

    Returns float values from start_val to end_val in
    increments of inc_val.

    Input:
        start_val       
        end_val=None    
        inc_val=1.0

    Output:
        L       range of values (float)
    """

    if end_val == None:
        end_val = start_val + 0.0
        start_val = 0.0
    else:
        start_val += 0.0 # force it to be a float

    if inc_val == None:
        inc_val = 1.0
    else:
        inc_val += 0.0

    import math
    count = int(math.ceil((end_val - start_val) / inc_val))

    L = [None,] * count
    for i in xrange(count):
        L[i] = start_val + i * inc_val

    return L

# -------------------------------------------------------------------------
# Main dialog
# -------------------------------------------------------------------------

def dock_manual_dialog(create=0):
    """dock_manual_dialog(create=0) - looks for Dock Manual dialog.

    If create = 1, then creates a new dialog if dialog does not exist.
    """
    
    from chimera import dialogs
    return dialogs.find(Dock_Manual.name, create=create)

def show_dock_manual_dialog():
    """show_dock_manual_dialog() - Shows the Dock Manual dialog.
    """
    
    from chimera import dialogs
    return dialogs.display(Dock_Manual.name)

# -------------------------------------------------------------------------
# Register dialog with Chimera.
# -------------------------------------------------------------------------

from chimera import dialogs
dialogs.register(Dock_Manual.name,Dock_Manual,replace=1)

# -------------------------------------------------------------------------

