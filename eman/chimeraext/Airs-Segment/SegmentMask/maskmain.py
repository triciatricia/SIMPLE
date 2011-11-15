# -------------------------------------------------------------------------
# SegmentMask/maskmain.py
#
# Segment Volume package - Segment Mask module
# 
# Author:
#       Lavu Sridhar, Baylor College of Medicine (BCM)
#
# Revisions:
#       2005.07.15: Lavu Sridhar, BCM
#       2005.09.06: Lavu Sridhar, BCM (VU 1.2129 Chimera)
#       2005.11.30: Lavu Sridhar, BCM bug fix
#
# To Do:
#       See comments marked with # @
#
# Key:
#       VU: Version Upgrade
#
"""GUI to create and apply a volume density mask on a
given volume density data. (see the Volume Data module
in Chimera).

Requires Segment Menu module from Segment Volume package
and EMAN.
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

class Segment_Mask(ModelessDialog):
    """Class: Segment_Mask() - dialog for volume data masks.

    Dialog for creating and applying volume data masks.
    """

    title = 'Segment Mask'
    name  = 'segment mask'
    buttons = ('Close',)

    # @ help = 'ContributedSoftware/SegmentMask/maskmain.html'
    dir_pkg = os.path.dirname(__file__)
    help_path = os.path.join(dir_pkg, 'maskmain.html')
    help_url = 'file://' + help_path
    help = help_url

    provideStatus = True
    statusPosition = 'above'
    statusResizing = False
    statusWidth = 40

    mask_type_choices = {0: 'Cuboid      ',
                         1: 'Ellipsoid   ',
                         2: 'Cylindrical ',
                         3: 'Pyramid     ',
                         4: 'Cone        '}
    mask_func_choices = {0: 'Step   ',
                         1: 'Radial '}
    
    # ---------------------------------------------------------------------
    # Fill in UI
    # ---------------------------------------------------------------------
    
    def fillInUI(self, parent):
        """fillInUI(parent)
        """

        self.status('')
        self.output_item = None

        self.mask_dialog = seg_mask_dialog()
        self.open_dialog = None 

        parent.columnconfigure(0, weight = 1)
        self.toplevel_widget = parent.winfo_toplevel() # @ whatisthis

        # panel buttons (pb)
        row = 0
        pb = Hybrid.Checkbutton_Row(parent, 'Panels ',
                                    ('Apply Mask','Create Mask'))
        pb.frame.grid(row = row, column = 0, sticky = 'nw')
        for b in pb.checkbuttons:
            b.callback(self.allow_toplevel_resize_cb)
        (self.mask_apply_panel_button,
         self.mask_selection_panel_button) = pb.checkbuttons

        # data menu frame (dmf)
        row = row + 1
        import SegmentMenu
        from SegmentMenu import datamenuseg
        dmf = datamenuseg.Segment_Open_Data(self, parent,
                                            self.data_status_cb)
        dmf.frame.grid(row = row, column = 0, sticky = 'nw', pady = 8)
        self.data_panel = dmf

        # mask menu frame (mmf)
        row = row + 1
        import SegmentMenu
        from SegmentMenu import datamenuseg
        mmf = datamenuseg.Segment_Open_Data(self, parent,
                                            self.mask_status_cb,
                                            menu_label = 'Mask    ')
        mmf.frame.grid(row = row, column = 0, sticky = 'nw', pady = 8)
        self.mask_panel = mmf

        # mask apply frame (maf)
        row = row + 1
        maf = Tkinter.Frame(parent, padx=8, pady=8)
        maf.grid(row = row, column = 0, sticky = 'nw')
        self._make_mask_apply_panel(maf)
        self.mask_apply_panel_button.popup_frame(maf,
                                    row=row, column=0, sticky='nw')
        self.mask_apply_panel_button.variable.set(1)
        
        # mask selection frame
        row = row + 1
        msf = Tkinter.Frame(parent, padx=8, pady=8)
        msf.grid(row = row, column = 0, sticky = 'nw')
        self._make_mask_selection_panel(msf)
        self.mask_selection_panel_button.popup_frame(msf,
                                    row=row, column=0, sticky='nw')
        self.mask_selection_panel_button.variable.set(0)

        # output menu frame
        row = row + 1
        import SegmentMenu
        from SegmentMenu import datamenuseg
        omf = datamenuseg.Segment_Open_Output(self, parent,
                                              self.output_status_cb)
        omf.frame.grid(row = row, column = 0, sticky = 'nw', pady = 8)
        self.output_panel = omf

        # create initial data menu list
        self.data_panel.data_items_refresh()
        self.mask_panel.data_items_refresh()

        # @ do we need to do stuff before closing Chimera session
        #   or this segmentation dialog

        msg = 'Hit Refresh button if menu not automatically updated!\n'
        self.status(msg, color='blue', blankAfter=15)
        replyobj.info(msg)

    # ---------------------------------------------------------------------
    # Additional panels
    # ---------------------------------------------------------------------
    
    def _make_mask_apply_panel(self, frame):
        """_make_mask_apply_panel(frame)

        Make a panel in the GUI for applying mask.
        """

        row = 0

        # mask apply label (maL)
        maL = Tkinter.Label(frame, text = 'Apply Mask ')
        maL.grid(row = row, column = 0, sticky = 'nw')

        # mask output frame (mof)
        row = row + 1
        mof = Tkinter.Frame(frame, padx=32)
        mof.grid(row=row, column=0, sticky='nw')

        # mask apply button (maB)
        maB = Hybrid.Button_Row(mof, '',
                                ((' Multiply ', self.mask_multiply_cb),
                                 (' Add ', self.mask_add_cb),
                                 (' Add Binary ', self.mask_add_bin_cb),
                                 (' Sub Binary ', self.mask_sub_bin_cb)))
        maB.frame.grid(row=0,column=0,sticky='w')

        # output data file entry (odfE)
        row = row + 1
        odfE = Hybrid.Entry(mof, 'File MRC ', '16', 'temp.mrc')
        odfE.frame.grid(row=1,column=0,sticky='w',pady=2)
        self.data_output = odfE

        return
    
    def _make_mask_selection_panel(self, frame):
        """_make_mask_selection_panel(frame)

        Make a panel in the GUI for mask selection.
        """

        row = 0

        # mask selection label (msL)
        msL = Tkinter.Label(frame,
                            text = 'Create Mask ')
        msL.grid(row = row, column = 0, sticky = 'nw')

        # mask type menu (mtm)
        row = row + 1
        mtm = Hybrid.Option_Menu(frame, 'Mask Type : ',
                                 self.mask_type_choices[0],
                                 self.mask_type_choices[1],
                                 self.mask_type_choices[2],
                                 self.mask_type_choices[3],
                                 self.mask_type_choices[4])
        mtm.frame.grid(row=row, column=0, sticky='nw', padx=32)
        mtm.add_callback(self.mask_type_selection_cb)
        self.mask_type_menu = mtm

        # parameters panel
        row = row + 1
        mpf = Tkinter.Frame(frame, padx=32)
        mpf.grid(row = row, column = 0, sticky = 'nw')
        self._make_mask_parameters_panel(mpf)
    
        # mask type selection
        mts = self.mask_type_choices.values()[0]
        self.mask_type_menu.variable.set(mts)

        # mask create frame (mcf)
        row = row + 1
        mcf = Tkinter.Frame(frame, padx=32)
        mcf.grid(row = row, column = 0, sticky = 'nw')

        # mask data file entry (mdfE)
        mdfE = Hybrid.Entry(mcf, 'Mask MRC File ', '16', 'mask.mrc')
        mdfE.frame.grid(row=0,column=0,sticky='w')
        self.mask_output = mdfE
        
        # mask create button
        mcB = Hybrid.Button_Row(mcf, '',
                                ((' Create Mask ',
                                  self.mask_create_cb),))
        mcB.frame.grid(row=0,column=1,sticky='w')

        return
    
    def _make_mask_parameters_panel(self, frame):
        """_make_mask_parameters_panel(frame)

        Make a panel in the GUI for mask parameters.
        """

        row = 0

        # mask dimensions frame (mdf)
        mdf = Tkinter.Frame(frame)
        mdf.grid(row = row, column = 0, sticky = 'nw')

        # mask parameters label (mpL)
        mdL = Tkinter.Label(mdf, text = 'Dimensions ')
        mdL.grid(row = 0, column=0, sticky = 'w')

        # mask dimensions
        mask_param = []
        size_label = ['p0 ','p1 ','p2 ']
        for a in range(3):
            size_e = Hybrid.Entry(mdf, '%s' % size_label[a], 5)
            size_e.frame.grid(row=0, column=a+1, sticky='w')
            mask_param.append(size_e)
        
        # mask dimensions message (mdm)
        row = row + 1
        mdm = Tkinter.Label(frame)
        mdm.grid(row = row, column = 0, sticky = 'w', padx=40,pady=2)
        mdm['font'] = non_bold_font(frame)
        self.mask_dimensions_message = mdm

        # inherit mask parameters from data (mpd)
        row = row +1
        mpd = Tkinter.Frame(frame)
        mpd.grid(row=row,column=0,sticky='nw')

        mpdL = Tkinter.Label(mpd, text='Mask Parameters ')
        mpdL.grid(row=0, column=0, sticky='w')

        # inherit checbutton
        mpdb = Hybrid.Checkbutton_Row(mpd, '',('Inherit from Input Data',))
        mpdb.frame.grid(row=0, column=1, sticky = 'nw')
        self.mask_inherit = mpdb.checkbuttons[0]
        self.mask_inherit.callback(self.mask_inherit_param_cb)

        # mask size and angstroms per pixel (msapf)
        row = row + 1
        msapf = Tkinter.Frame(frame)
        msapf.grid(row=row, column=0, sticky='nw',padx=32)

        # mask size label (msL)
        msL = Tkinter.Label(msapf, text = 'Size      ')
        msL.grid(row=0, column=0, sticky='w')

        # mask size in pixels
        size_label = ['x','y','z']
        for a in range(3):
            size_e = Hybrid.Entry(msapf, '%s' % size_label[a], 5, '64')
            size_e.frame.grid(row=0,column=a+1,sticky='w',padx=1)
            mask_param.append(size_e)

        # mask size units (msu)
        msu = Tkinter.Label(msapf, text=' pixels ')
        msu.grid(row=0,column=4,sticky='w')
        
        # mask origin label (moL)
        moL = Tkinter.Label(msapf, text = 'Origin    ')
        moL.grid(row=1, column=0, sticky='w')

        # mask origin
        origin_label = ['x','y','z']
        for a in range(3):
            size_e = Hybrid.Entry(msapf, '%s' % origin_label[a], 5, '0')
            size_e.frame.grid(row=1,column=a+1,sticky='w',padx=1)
            mask_param.append(size_e)

        # mask origin units (mou)
        mou = Tkinter.Label(msapf, text=' Angstroms ')
        mou.grid(row=1,column=4,sticky='w')
        
        # mask angstroms per pixel label (mapL)
        mapL = Tkinter.Label(msapf, text = 'Angstroms ')
        mapL.grid(row=2, column=0, sticky='w')

        # mask angstroms per pixel
        app_label = ['x','y','z']
        for a in range(3):
            size_e = Hybrid.Entry(msapf, '%s' % app_label[a], 5, '1.0')
            size_e.frame.grid(row=2,column=a+1,sticky='w',padx=1)
            mask_param.append(size_e)

        # mask angstroms per pixel units (mapu)
        mapu = Tkinter.Label(msapf, text=' per pixel ')
        mapu.grid(row=2,column=4,sticky='w')
        
        # mask translation and rotate frame (mtrf)
        row = row + 1
        mtrf = Tkinter.Frame(frame)
        mtrf.grid(row = row, column = 0, sticky='nw',pady=2)

        # mask translate label (mtL)
        mtL = Tkinter.Label(mtrf, text = 'Translate ')
        mtL.grid(row = 0, column=0, sticky = 'w')

        # translate in pixels
        talign_label = ['tx ','ty ','tz ']
        for a in range(3):
            size_e = Hybrid.Entry(mtrf, '%s' % talign_label[a], 5, '0')
            size_e.frame.grid(row=0, column=a+1, sticky='w',padx=1)
            mask_param.append(size_e)

        # mask translate units (mtu)
        mtu = Tkinter.Label(mtrf, text=' pixels ')
        mtu.grid(row = 0, column=4, sticky = 'w')
        
        # mask rotate label (mrL)
        mrL = Tkinter.Label(mtrf, text = 'Rotate   ')
        mrL.grid(row = 1, column=0, sticky = 'w')

        # rotate in EMAN Euler angles
        ralign_label = ['az ','alt','phi']
        for a in range(3):
            size_e = Hybrid.Entry(mtrf, '%s' % ralign_label[a], 5, '0')
            size_e.frame.grid(row=1, column=a+1, sticky='w',padx=1)
            mask_param.append(size_e)

        # mask rotate units (mru)
        mru = Tkinter.Label(mtrf, text=' EMAN Euler ')
        mru.grid(row = 1, column=4, sticky = 'w')

        self.mask_parameters = mask_param

        # choose function type (cft)
        row = row + 1
        cft = Hybrid.Radiobutton_Row(frame, 'Choose ',
                                     (self.mask_func_choices[0],
                                      self.mask_func_choices[1]),
                                     None)
        cft.frame.grid(row = row, column = 0, sticky = 'nw',pady=2)
        self.mask_function_type = cft.variable

        self.mask_function_type.set(self.mask_func_choices[0],
                                    invoke_callbacks=0)

        return 

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
    
    def mask_status_cb(self, data_item, data_status):
        """mask_status_cb(data_item, data_status) - callback.

        Callback function for data status, used by datamenuseg's
        Data menu.
        """

        self.mask_shown = data_status
        self.mask_item = data_item

        # display a message
        if data_status == self.mask_panel.DATA_NOT_SHOWN:
            msg = 'Mask item %s not shown\n' % (data_item.full_name)
        elif data_status == self.mask_panel.DATA_SHOWN:
            msg = 'Mask item %s shown\n'% (data_item.full_name)
        else:
            msg = 'No data items present\n'
       
        # self.status(msg, color='blue', blankAfter=15)
        # if data_status == self.mask_panel.DATA_EMPTY:
        #    replyobj.info(msg)

        # activate/deactivate buttons
        if data_status == self.mask_panel.DATA_NOT_SHOWN:
            pass
        elif data_status == self.mask_panel.DATA_SHOWN:
            pass
        else:
            pass
        
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
    # Mask type selection functions
    # ---------------------------------------------------------------------

    def mask_type_selection_cb(self):

        mts = self.mask_type_menu.variable.get()
        if not (mts in self.mask_type_choices.values()):
            mts = self.mask_type_choices.values()[0]
            self.mask_type_menu.variable.set(mts)

        if   mts == self.mask_type_choices[0]:
            msg = 'p0 = length_x, p1 = length_y, p2 = length_z'
        elif mts == self.mask_type_choices[1]:
            msg = 'p0 = axis_x, p1 = axis_y, p2 = axis_z'
        elif mts == self.mask_type_choices[2]:
            msg = 'p0 = diameter, p1 = length, p2 = null'
        elif mts == self.mask_type_choices[3]:
            msg = 'p0 = side length, p1 = height, p2 = 3 or 4 sides'
        elif mts == self.mask_type_choices[4]:
            msg = 'p0 = base diameter, p1 = height, p2 = null'
        else:
            print "should not be here" #>

        self.mask_dimensions_message['text'] = msg
        
        return

    def mask_inherit_param_cb(self):

        mip = self.mask_inherit.variable.get()

        if mip:
            for a in range(9):
                self.mask_parameters[a+3].entry['state'] = 'disabled'
        else:
            for a in range(9):
                self.mask_parameters[a+3].entry['state'] = 'normal'

        return
    
    # ---------------------------------------------------------------------
    # Mask create functions
    # ---------------------------------------------------------------------

    def mask_create_cb(self):

        # mask shape type (mst)
        mst = self.mask_type_menu.variable.get()
        if not (mst in self.mask_type_choices.values()):
            return

        # mask function type
        mft = self.mask_function_type.get()
        if   mft == self.mask_func_choices[0]:
            radial = 0
        elif mft == self.mask_func_choices[1]:
            radial = 1
        else:
            return

        # inherit path from data_item or put in default
        if self.data_item:
            data_path = self.data_item.path
            data_item = self.data_item
        else:
            data_path = os.path.curdir
            data_item = None
        
        # mask output file
        mof = self.mask_output.variable.get()
        mask_file = os.path.basename(mof)
        mask_dir  = os.path.dirname(data_path)
        mask_path = os.path.join(mask_dir, mask_file)
        
        mask_files = [mask_file]

        msg = ''

        mip = self.mask_inherit.variable.get()
        if mip:
            if data_item:
                sx,sy,sz = data_item.size
                #VU 1.2129
                # ox,oy,oz = data_item.data.xyz_origin
                # apx,apy,apz = data_item.data.xyz_step
                ox, oy, oz = data_item.origin
                apx, apy, apz = data_item.step
            else:
                self.mask_inherit.variable.set(0)
                msg = 'Cannot inherit parameters from data!\n'
                self.status(msg, color='red', blankAfter=10)
                replyobj.error(msg)
                return
        else:
            sx  = self._read_mask_parameters(3,  'int_type')
            sy  = self._read_mask_parameters(4,  'int_type')
            sz  = self._read_mask_parameters(5,  'int_type')

            ox  = self._read_mask_parameters(6,  'float_type')
            oy  = self._read_mask_parameters(7,  'float_type')
            oz  = self._read_mask_parameters(8,  'float_type')

            apx = self._read_mask_parameters(9,  'float_type')
            apy = self._read_mask_parameters(10, 'float_type')
            apz = self._read_mask_parameters(11, 'float_type')
        
        tx  = self._read_mask_parameters(12, 'float_type')
        ty  = self._read_mask_parameters(13, 'float_type')
        tz  = self._read_mask_parameters(14, 'float_type')
        
        az  = self._read_mask_parameters(15, 'float_type')
        alt = self._read_mask_parameters(16, 'float_type')
        phi = self._read_mask_parameters(17, 'float_type')

        mask_origin = (ox,oy,oz)
        mask_size = (sx,sy,sz)
        mask_step = (apx,apy,apz)
        talign = (tx,ty,tz)
        ralign = (az,alt,phi)

        import maskedit
        if   mst == self.mask_type_choices[0]:
            p0 = self._read_mask_parameters(0, 'int_type')
            p1 = self._read_mask_parameters(1, 'int_type')
            p2 = self._read_mask_parameters(2, 'int_type')
        elif mst == self.mask_type_choices[1]:
            p0 = self._read_mask_parameters(0, 'int_type')
            p1 = self._read_mask_parameters(1, 'int_type')
            p2 = self._read_mask_parameters(2, 'int_type')
        elif mst == self.mask_type_choices[2]:
            p0 = self._read_mask_parameters(0, 'int_type')
            p1 = self._read_mask_parameters(1, 'int_type')
            p2 = 0
        elif mst == self.mask_type_choices[3]:
            p0 = self._read_mask_parameters(0, 'int_type')
            p1 = self._read_mask_parameters(1, 'int_type')
            p2 = self._read_mask_parameters(2, 'int_type')
        elif mst == self.mask_type_choices[4]:
            p0 = self._read_mask_parameters(0, 'int_type')
            p1 = self._read_mask_parameters(1, 'int_type')
            p2 = 0

        if p0 != None and p1 != None and p2!= None:
            msg = maskedit.create_mask(mst, p0,p1,p2,
                                       mask_path, mask_origin,
                                       mask_size, mask_step,
                                       talign, ralign,radial)

        self.status(msg, color='blue', blankAfter=10)
        replyobj.info(msg)

        self.open_output_data_items(mask_dir, mask_files)

        return

    def _read_mask_parameters(self, param_id, param_type):

        if param_id not in range(18):
            return None

        param_tag_set = ['p0 ','p1 ','p2 ',
                         'size - x  ','size - y  ','size - z  ',
                         'origin - x  ','origin - y  ','origin - z  ',
                         'app - x  ','app - y  ','app - z  ',
                         'tx ','ty ','tz ',
                         'az ','alt','phi']
        param_tag = param_tag_set[param_id]
        mask_param = self.mask_parameters[param_id]
        
        try:
            if   param_type == 'float_type':
                param = float(mask_param.variable.get())
            elif param_type == 'int_type':
                param = int(mask_param.variable.get())
        except:
            msg = 'Check parameter %s value!\n' % param_tag
            self.status(msg, color='red', blankAfter=10)
            replyobj.error(msg)
            return None

        return param

    # ---------------------------------------------------------------------
    #  Mask operations callback functions.
    # ---------------------------------------------------------------------

    def mask_multiply_cb(self):
        """mask_multiply_cb() - callback.

        Callback function for multiply mask.
        """

        data_item = self.data_item
        mask_item = self.mask_item
        
        self.mask_multiply(data_item, mask_item)

        return
    
    def mask_add_cb(self):
        """mask_add_cb() - callback.

        Callback function for adding mask.
        """

        data_item = self.data_item
        mask_item = self.mask_item
        
        self.mask_add(data_item, mask_item)

        return
    
    def mask_add_bin_cb(self):
        """mask_add_bin_cb() - callback.

        Callback function for binary addition (AND) of mask.
        """

        data_item = self.data_item
        mask_item = self.mask_item
        
        self.mask_add(data_item, mask_item, bin=1)

        return
    
    def mask_sub_bin_cb(self):
        """mask_sub_bin_cb() - callback.

        Callback function for binary subtraction of mask.
        """

        data_item = self.data_item
        mask_item = self.mask_item
        
        self.mask_add(data_item, mask_item, bin=1,sub=1)

        return
    
    # ---------------------------------------------------------------------
    #  Mask operations functions.
    # ---------------------------------------------------------------------

    def mask_multiply(self, data_item, mask_item):
        """mask_multiply(data_item, mask_item) 

        Multiply data_item and mask_item.
        """

        if data_item == None or mask_item == None:
            return

        dof = self.data_output.variable.get()
        out_file = os.path.basename(dof)
        out_dir  = os.path.dirname(data_item.path)
        out_path = os.path.join(out_dir, out_file)
        
        out_files = [out_file]

        import maskop
        maskop.maskop_multiply(data_item, mask_item, out_path)

        self.open_output_data_items(out_dir, out_files)

        return

    def mask_add(self, data_item, mask_item,bin=0,sub=0):
        """mask_add(data_item, mask_item,bin=0,sub=0) 

        Input:
            data_item   Input data
            mask_item   Mask data
            bin=0       Binary addition if bin=1
            sub=0       Binary subtraction if sub=1 (and bin=1)
            
        Add data_item and mask_item.
        """

        if data_item == None or mask_item == None:
            return

        dof = self.data_output.variable.get()
        out_file = os.path.basename(dof)
        out_dir  = os.path.dirname(data_item.path)
        out_path = os.path.join(out_dir, out_file)
        
        out_files = [out_file]

        import maskop
        if bin == 1:
            maskop.maskop_add_bin(data_item, mask_item, out_path, sub)
        else:
            maskop.maskop_add(data_item, mask_item, out_path)

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

def seg_mask_dialog(create=0):
    """seg_mask_dialog(create=0) - look for Segment Mask dialog.

    If create = 1, then creates a new dialog if dialog does not exist.
    """
    
    from chimera import dialogs
    return dialogs.find(Segment_Mask.name, create=create)

def show_seg_mask_dialog():
    """show_seg_mask_dialog() - shows the Segment Mask dialog.
    """
    
    from chimera import dialogs
    return dialogs.display(Segment_Mask.name)

# -------------------------------------------------------------------------
# Register dialog with Chimera.
# -------------------------------------------------------------------------
 
from chimera import dialogs
dialogs.register(Segment_Mask.name,Segment_Mask,replace=1)

# -------------------------------------------------------------------------
