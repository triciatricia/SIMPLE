# -------------------------------------------------------------------------
# SegmentSimple/simple.py
# 
# Segment Volume package - Segment Simple module
#
# Author:
#       Lavu Sridhar, Baylor College of Medicine (BCM)
#
# Revisions:
#       2004.12.15: Lavu Sridhar, BCM
#       2005.02.15: Lavu Sridhar, BCM
#       2005.09.06: Lavu Sridhar, BCM (VU 1.2129 Chimera)
#       2005.10.10: Lavu Sridhar, BCM (VU 1.2176 Chimera)
#       2005.11.15: Lavu Sridhar, BCM (VU 1.2179 Chimera)
#       2006.03.06: Lavu Sridhar, BCM (VU 1.2179 Chimera) Part2
#       2006.05.24: Lavu Sridhar, BCM (VU Circle Mask)
#
# To Do:
#       See comments marked with # @
# 
# Key:
#       VU: Version Upgrade
#
"""Segmentation of MRC density maps using simple regions.

GUI to perform segmentation of MRC density maps, using simple regions:
(1) Cuboid regions
(2) Spherical regions
(3) ...
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

class Segment_Simple(ModelessDialog):
    """Class: Segment_Simple()

    The main GUI dialog for simple segmentation.
    """
    
    title = 'Segment Simple'
    name = 'segment simple'
    buttons = ('Close',)

    # @ help = 'ContributedSoftware/SegmentSimple/simple.html'
    dir_pkg = os.path.dirname(__file__)
    help_path = os.path.join(dir_pkg, 'simple.html')
    help_url = 'file://' + help_path
    help = help_url

    provideStatus = True
    statusPosition = 'above'
    statusResizing = False
    statusWidth = 40

    output_choices = {0: 'Segment region ',  1: 'Original region',
                      2: 'Custom region  '}
    
    segment_choices = {0: 'Box.....', 1: 'Circle..'}

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
            
        self.seg_dialog = seg_simple_dialog()

        self.box_region_selector = None
        self.circle_region_selector = None
        
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
        
        # selection region frame (srf)
        row = row + 1
        srf = Tkinter.Frame(parent, padx=8, pady=8)
        srf.grid(row = row, column = 0, sticky = 'nw')
        self._make_selection_region_panel(srf)

        # selection parameters frame
        row = row + 1
        spf = Tkinter.Frame(parent, padx=8, pady=8)
        spf.grid(row = row, column = 0, sticky = 'nw')
        self._make_selection_parameters_panel(spf)

        # output region parameters (orp)
        row = row + 1
        orp = Tkinter.Frame(parent, padx=8, pady=8)
        orp.grid(row = row, column = 0, sticky = 'nw')
        self._make_output_region_panel(orp)

        # segmentation info frame (sif)
        row = row + 1
        sif = Tkinter.Frame(parent, padx=8, pady=8)
        sif.grid(row = row, column = 0, sticky = 'nw')
        self._make_segmentation_panel(sif)

        # output menu frame
        row = row + 1
        import SegmentMenu
        from SegmentMenu import datamenuseg
        omf = datamenuseg.Segment_Open_Output(self, parent,
                                              self.output_status_cb)
        omf.frame.grid(row = row, column = 0, sticky = 'nw', pady = 8)
        self.output_panel = omf

        #  create initial data menu list
        self.data_panel.data_items_refresh()

        # defaults
        self.output_region_menu.variable.set(self.output_choices[0])
        self.segment_type.set(self.segment_choices[0])

        # @ do we need to do stuff before closing Chimera session
        #   or this segmentation dialog

    # ---------------------------------------------------------------------
    # Selection panels
    # ---------------------------------------------------------------------

    def _make_selection_region_panel(self, frame):
        """_make_selection_region_panel(frame)

        Make a panel in the GUI for selection region.
        """
        
        row = 0

        # selection region label (srL)
        srL = Tkinter.Label(frame, text = 'Selection Region ')
        srL.grid(row = row, column = 0, columnspan=2, sticky = 'w')

        row = row + 1
        mbgap = Tkinter.Label(frame, text = ' ')
        mbgap.grid(row = row, column = 0, sticky = 'w',padx=16)

        # mouse button (mb)
        mb = Hybrid.Checkbutton(frame, ' Use mouse ',0)
        mb.button.grid(row = row, column = 1, sticky = 'w')
        self.sel_mouse_button = mb.button
        self.selection_mouse  = mb.variable
        mb.callback(self.selection_mouse_cb)
 
        # mouse button menu (mbm)
        mbm = Hybrid.Option_Menu(frame, '', 'button 1', 'button 2',
                                 'button 3', 'ctrl button 1',
                                 'ctrl button 2', 'ctrl button 3')
        mbm.variable.set('button 2')
        mbm.frame.grid(row = row, column = 2, sticky = 'w')
        mbm.add_callback(self.selection_button_cb)
        self.selection_button = mbm.variable

        # buttons (srB)
        srB = Hybrid.Button_Row(frame, '',
                                (('Delete ', self.selection_delete_cb),
                                 ('Show ',   self.selection_show_cb),
                                 ('Hide ',   self.selection_hide_cb)))
        srB.frame.grid(row = row, column = 3, sticky = 'w', padx=32)
        
        self.sel_delete_button = srB.buttons[0]
        self.sel_show_button   = srB.buttons[1]
        self.sel_hide_button   = srB.buttons[2]

        return

    def _make_selection_parameters_panel(self, frame):
        """_make_selection_parameters_panel(frame)

        Make a panel in the GUI for selection parameters.
        """
        
        row = 0

        # selection parmaeters label (spL)
        spL = Tkinter.Label(frame, text = 'Selection Region Parameters ')
        spL.grid(row = row, column = 0, sticky = 'w')
        
        # choose region type (crt)
        row = row + 1
        crt = Hybrid.Checkbutton_Row(frame, 'Choose region ',
                                     ('Box   ','Circle   '))
        crt.frame.grid(row = row, column = 0, sticky = 'nw', padx=32) 
        (box_button, circle_button) = crt.checkbuttons

        # allow resize
        for r in crt.checkbuttons:
            r.callback(self.allow_toplevel_resize_cb)
        # @ where exactly and where all should it be?

        # popup box parameters (pbp)
        row = row + 1
        pbp = Tkinter.Frame(frame, padx=32)
        box_button.popup_frame(pbp, row=row, column=0, sticky = 'nw')
        self._make_box_parameters_panel(pbp)

        box_button.variable.set(1) # default active panel

        # popup circle parameters (pcp)
        row = row + 1
        pcp = Tkinter.Frame(frame, padx=32)
        circle_button.popup_frame(pcp, row=row, column=0, sticky = 'nw')
        self._make_circle_parameters_panel(pcp)

        return
    
    def _make_output_region_panel(self, frame):
        """_make_output_region_panel(frame)

        Make a panel on the GUI for specifying output region type.
        """

        row = 0

        rt = Tkinter.Frame(frame, padx=8)
        rt.grid(row = row, column = 0, sticky = 'nw')

        # output region label (orL)
        orL = Tkinter.Label(frame, text = 'Output Region ')
        orL.grid(row = row, column = 0, sticky = 'w')
        
        # choose region type (crt)
        row = row + 1
        crt = Hybrid.Option_Menu(frame, 'Choose output region : ',
                                 self.output_choices[0],
                                 self.output_choices[1],
                                 self.output_choices[2])
        crt.frame.grid(row = row, column = 0, sticky = 'nw', padx=32)
        crt.add_callback(self.output_region_type_cb)
        self.output_region_menu = crt

        # output region message (orm)
        row = row + 1
        orm = Tkinter.Label(frame)
        orm.grid(row = row, column = 0, sticky = 'w', padx=64, pady=2)
        orm['font'] = non_bold_font(frame)
        self.output_region_message = orm

        # output region parameters (orp)
        row = row + 1
        orp = Tkinter.Frame(frame, padx=32)
        orp.grid(row = row, column = 0, sticky = 'nw')
        self._make_output_parameters_panel(orp)
    
        return

    def _make_segmentation_panel(self, frame):
        """_make_segmentation_panel(frame)

        Make a plane in the GUI for segmentation and output file info.
        """

        row = 0

        # segmentation info label (siL)
        siL = Tkinter.Label(frame, text = 'Segmentation Info ')
        siL.grid(row = row, column = 0, sticky = 'w')

        # choose segmentation type (cst)
        row = row + 1
        cst = Hybrid.Radiobutton_Row(frame, 'Choose type ',
                                     (self.segment_choices[0],
                                      self.segment_choices[1]),
                                     self.seg_type_cb)
        cst.frame.grid(row = row, column = 0, columnspan=2,
                       sticky = 'nw', padx=32)
        self.segment_type = cst.variable

        # output data file entry (odfE)
        row = row + 1
        odfE = Hybrid.Entry(frame, 'File MRC ', '16', 'temp.mrc')
        odfE.frame.grid(row = row, column = 0, sticky = 'w', padx=32)
        self.data_output = odfE
        # @ how to update entry - callback
        
        # buttons
        sb = Hybrid.Button_Row(frame, '',
                               (('Apply', self.segment_apply_cb),))
        sb.frame.grid(row = row, column = 1, sticky = 'w')

        return

    # ---------------------------------------------------------------------
    # Parameters panels
    # ---------------------------------------------------------------------

    def _make_box_parameters_panel(self, frame):
        """_make_box_parameters_panel(frame)

        Make a panel in the GUI for box parameters.
        """

        row = 0
        
        # box labels (bL)
        bL = Tkinter.Label(frame, text = 'Box    ')
        bL.grid(row = row, column = 0, sticky = 'w')

        bLp = Tkinter.Label(frame, text = '   In Pixels ')
        bLp.grid(row = row, column = 1, sticky = 'w')

        bLa = Tkinter.Label(frame, text = '   In Angstroms ')
        bLa.grid(row = row, column = 2, sticky = 'w')

        row = row + 1
        
        # box entry labels (beL)
        beL = Tkinter.Frame(frame, padx=16)
        beL.grid(row = row, column = 0, sticky = 'w')
         
        # box ijk (box_ijk)
        box_ijk = Tkinter.Frame(frame, padx=4)
        box_ijk.grid(row = row, column = 1, sticky = 'w')

        # box xyz (box_xyz)
        box_xyz = Tkinter.Frame(frame, padx=4)
        box_xyz.grid(row = row, column = 2, sticky = 'w')

        # box entries
        box_param = self._make_size_center_parameters_panel(beL,
                        box_ijk, box_xyz, 'Size   ', 'Center ', 
                        entry_cb=self.parameters_to_selection_cb)

        self.box_size = box_param[0]
        self.box_center = box_param[1]
        self.box_size_xyz = box_param[2]
        self.box_center_xyz = box_param[3]

        return

    def _make_circle_parameters_panel(self, frame):
        """_make_circle_parameters_panel(frame)

        Make a panel in the GUI for circle parameters.
        """

        row = 0

        # circle labels (cL)
        cL = Tkinter.Label(frame, text = 'Circle ')
        cL.grid(row = row, column = 0, sticky = 'w')
        cLp = Tkinter.Label(frame, text = '   In Pixels ')
        cLp.grid(row = row, column = 1, sticky = 'w')
        cLa = Tkinter.Label(frame, text = '   In Angstroms ')
        cLa.grid(row = row, column = 2, sticky = 'w')

        row = row + 1
        
        # circle entry labels (ceL)
        ceL = Tkinter.Frame(frame, padx=16)
        ceL.grid(row = row, column = 0, sticky = 'w')
         
        # circle ijk (circle_ijk)
        circle_ijk = Tkinter.Frame(frame, padx=4)
        circle_ijk.grid(row = row, column = 1, sticky = 'w')

        # circle xyz (circle_xyz)
        circle_xyz = Tkinter.Frame(frame, padx=4)
        circle_xyz.grid(row = row, column = 2, sticky = 'w')

        # circle entries
        circle_param = self._make_size_center_parameters_panel(ceL,
                        circle_ijk, circle_xyz, 'Size   ', 'Center ',
                        entry_cb=self.parameters_to_selection_cb)

        self.circle_size = circle_param[0]
        self.circle_center = circle_param[1]
        self.circle_size_xyz = circle_param[2]
        self.circle_center_xyz = circle_param[3]

        return

    def _make_output_parameters_panel(self, frame):
        """_make_output_parameters_panel(frame)

        Make a panel in the GUI for output parameters.
        """

        row = 0

        # output labels (oL)
        oL = Tkinter.Label(frame, text = 'Output ')
        oL.grid(row = row, column = 0, sticky = 'w')
        oLp = Tkinter.Label(frame, text = '   In Pixels ')
        oLp.grid(row = row, column = 1, sticky = 'w')
        oLa = Tkinter.Label(frame, text = '   In Angstroms ')
        oLa.grid(row = row, column = 2, sticky = 'w')

        row = row + 1

        # output entry labels (oeL)
        oeL = Tkinter.Frame(frame, padx=16)
        oeL.grid(row = row, column = 0, sticky = 'w')
         
        # output ijk (output_ijk)
        output_ijk = Tkinter.Frame(frame, padx=4)
        output_ijk.grid(row = row, column = 1, sticky = 'w')

        # output xyz (output_xyz)
        output_xyz = Tkinter.Frame(frame, padx=4)
        output_xyz.grid(row = row, column = 2, sticky = 'w')

        # output entries
        output_param = self._make_size_center_parameters_panel(oeL,
                        output_ijk, output_xyz, 'Size   ', 'Center ', 
                        entry_cb=self.parameters_to_selection_cb)

        self.output_size = output_param[0]
        self.output_center = output_param[1]
        self.output_size_xyz = output_param[2]
        self.output_center_xyz = output_param[3]

        return
    
    def _make_size_center_parameters_panel(self, frame_label, frame_ijk,
            frame_xyz=None, size_label  ='Size   ',
            center_label='Center ', entry_cb=None):
        """_make_size_center_parameters_panel(frame_label, frame_ijk,
                frame_xyz=None, size_label='Size   ',
                center_label='Center ', entry_cb=None)

        Input:
            frame_label     frame for labels
            frame_ijk       frame for ijk parameters
            frame_xyz       frame for xyz parameters, defualt=None
            size_label      default='Size   '
            center_label    default='Center '
            entry_cb        callback for <KeyPress-Return>,
                               default=None

        Output (if frame_xyz != None):
            [size_ijk, center_ijk, size_xyz, center_xyz]

        Output (if frame_xyz == None):
            [size_ijk, center_ijk]        

        where:
            size_ijk        entry variable list (pixels)
            center_ijk      entry variable list (pixels)
            size_xyz        entry variable list (angstroms, readonly)
            center_xyz      entry variable list (angstroms, readonly)

        Here an entry is of class Hybrid.Entry
        """
        
        # labels
        
        sizeL = Tkinter.Label(frame_label, text=size_label)
        sizeL.grid(row = 0, column = 0, sticky = 'w')

        centerL = Tkinter.Label(frame_label, text=center_label)
        centerL.grid(row = 1, column = 0, sticky = 'w')

        # pixel parameters
        
        size_ijk = []
        for a in range(3):
            size_e = Hybrid.Entry(frame_ijk, '', 5)
            size_e.frame.grid(row = 0, column = a, sticky = 'w')
            if entry_cb:
                size_e.entry.bind('<KeyPress-Return>', entry_cb)
            size_ijk.append(size_e) 

        center_ijk = []
        for a in range(3):
            center_e = Hybrid.Entry(frame_ijk, '', 5)
            center_e.frame.grid(row = 1, column = a, sticky = 'w')
            if entry_cb:
                center_e.entry.bind('<KeyPress-Return>', entry_cb)
            center_ijk.append(center_e) 

        # if only pixel paramaeters requested, then return
        if frame_xyz == None:
            return [size_ijk, center_ijk]
        
        # angstrom parameters
        
        size_xyz = []
        for a in range(3):
            size_e = Hybrid.Entry(frame_xyz,'', 7)
            size_e.frame.grid(row = 0, column = a, sticky = 'w')
            size_e.entry['state'] = 'readonly'
            size_xyz.append(size_e)

        center_xyz = []
        for a in range(3):
            center_e = Hybrid.Entry(frame_xyz, '', 7)
            center_e.frame.grid(row = 1, column = a, sticky = 'w')
            center_e.entry['state'] = 'readonly'
            center_xyz.append(center_e)

        return [size_ijk, center_ijk, size_xyz, center_xyz]

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
        if data_status == self.data_panel.DATA_NOT_SHOWN:
            self.selection_hide_cb()
            self.sel_mouse_button['state'] = 'disabled'
        elif data_status == self.data_panel.DATA_SHOWN:
            self.selection_show_cb()
            self.sel_mouse_button['state'] = 'normal'
        elif data_status == self.data_panel.DATA_EMPTY:
            self.selection_delete_cb()
            self.sel_mouse_button['state'] = 'disabled'
        else:
            # should not be here
            pass

        self.output_region_type_cb()
        
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
    # Selection functions
    # ---------------------------------------------------------------------

    def selection_delete_cb(self):
        """selection_delete_cb() - callback to delete selection
        """

        if self.box_region_selector:
            self.box_region_selector.unbind_mouse_button()
            self.box_region_selector.box_model.delete_box()
        if self.circle_region_selector:
            self.circle_region_selector.unbind_mouse_button()
            self.circle_region_selector.circle_model.delete_circle()
        self.selection_mouse_cb()

        return

    def selection_show_cb(self):
        """selection_show_cb() - callback to show selection
        """

        seg_type = self.segment_type.get()
        
        if   seg_type == self.segment_choices[0]:
            if self.box_region_selector:
                if not self.box_region_selector.box_model.box_shown():
                    self.box_region_selector.box_model.display_box(1)
        elif seg_type == self.segment_choices[1]:
            if self.circle_region_selector:
                #VU Circle Mask
                # self.no_feature('circle')
                if not self.circle_region_selector.circle_model.circle_shown():
                    self.circle_region_selector.circle_model.display_circle(1)

        return

    def selection_hide_cb(self):
        """selection_hide_cb() - callback to hide selection
        """

        seg_type = self.segment_type.get()
        
        if   seg_type == self.segment_choices[0]:
            if self.box_region_selector:
                if self.box_region_selector.box_model.box_shown():
                    self.box_region_selector.box_model.display_box(0)
        elif seg_type == self.segment_choices[1]:
            if self.circle_region_selector:
                #VU Circle Mask
                # self.no_feature('circle')
                if self.circle_region_selector.circle_model.circle_shown():
                    self.circle_region_selector.circle_model.display_circle(0)
                
        return

    # ---------------------------------------------------------------------
    #  Mouse functions.
    # ---------------------------------------------------------------------

    def selection_mouse_cb(self):
        """selection_mouse_cb() - callback for mouse selection

        Enable/disable mouse to select regions.
        """

        # If 'Use mouse' box is checked, create a selection region
        # corresponding to the segment type, else, if there are any
        # selection regions currently active, unbind mouse buttons.

        seg_type = self.segment_type.get()

        if self.selection_mouse.get():
            if   seg_type == self.segment_choices[0]:
                self.mouse_box_region_cb()
            elif seg_type == self.segment_choices[1]:
                self.mouse_circle_region_cb()
        else:
            if self.box_region_selector:
                self.box_region_selector.unbind_mouse_button()
            if self.circle_region_selector:
                self.circle_region_selector.unbind_mouse_button()

    def mouse_box_region_cb(self):
        """mouse_box_regions_cb()

        Allows mouse to select box regions.
        """

        if self.box_region_selector == None:
            import selectregion
            self.box_region_selector = \
                    selectregion.Select_Box(self.seg_dialog)
        button, modifiers = self.selection_button_spec()
        self.box_region_selector.bind_mouse_button(button, modifiers)

    def mouse_circle_region_cb(self):
        """mouse_circle_region_cb()

        Allows mouse to select circle regions.
        """

        if self.circle_region_selector == None:
            import selectregion
            self.circle_region_selector = \
                    selectregion.Select_Circle(self.seg_dialog)
        button, modifiers = self.selection_button_spec()
        self.circle_region_selector.bind_mouse_button(button, modifiers)

    def selection_button_cb(self):
        """selection_button_cb() - callback for mouse button menu.

        Update button used for selection.
        """

        if not self.selection_mouse.get():
            return
        
        # @ later: carefully check if any errors while switching
        #   between seg types under diff scenarios...

        if self.box_region_selector:
            button, modifiers = self.selection_button_spec()
            self.box_region_selector.bind_mouse_button(button,
                                                       modifiers)
        if self.circle_region_selector:
            button, modifiers = self.selection_button_spec()
            self.circle_region_selector.bind_mouse_button(button,
                                                          modifiers)

        return
    
    def selection_button_spec(self):
        """selection_button_spec() - return mouse button.

        Output:
            mouse_button
        """

        name = self.selection_button.get()
        name_to_button = {'button 1':('1', []), 
                          'button 2':('2', []),
                          'button 3':('3', []),
                          'ctrl button 1':('1',['Ctrl']),
                          'ctrl button 2':('2',['Ctrl']),
                          'ctrl button 3':('3',['Ctrl'])}
        button = name_to_button[name]
        return button

    # ---------------------------------------------------------------------
    #  Parameters to selection functions.
    # ---------------------------------------------------------------------

    def parameters_to_selection_cb(self, event=None):
        """parameters_to_selection_cb(event=None) - draw regoin

        Input:
            event       For <KeyPress-Return> in parameter
                            entries, default = None
        
        If data item on menu is dispalyed, then draw appropriate
        selection region.
        """

        seg_type = self.segment_type.get()
        self.parameters_to_output_xyz_cb()
        
        if   seg_type == self.segment_choices[0]:
            self.parameters_to_box_xyz_cb()
            if self.data_shown == self.data_panel.DATA_SHOWN:
                self.parameters_to_box()
        elif seg_type == self.segment_choices[1]:
            self.parameters_to_circle_xyz_cb()
            if self.data_shown == self.data_panel.DATA_SHOWN:
                self.parameters_to_circle()
            # @ upgrade later
        else:
            pass

        return

    def parameters_to_box(self):
        """parameters_to_box() - draw box from parameters

        Draw box selection region after checking if all appropriate
        parameters entered.
        """

        if not (self.data_shown == self.data_panel.DATA_SHOWN):
            return

        size_value, center_value = \
                    self.check_parameters_box(mild=1, warn=0)

        # if no valid parameters, then can't draw box
        if (size_value == None or center_value == None):
            return

        # box region in terms of ijk_in and ijk_out
        size_half = map(lambda a:a/2, size_value)
        ijk_in  = map(lambda a,b: int(a-b), center_value, size_half)
        ijk_out = map(lambda a,b: int(a+b), center_value, size_half)

        # box region in terms of xyz_in and xyz_out
        data = self.data_item.data
        xyz_in  = data.ijk_to_xyz(ijk_in)
        xyz_out = data.ijk_to_xyz(ijk_out)

        # transform and box
        #VU 1.2129
        # xform = self.data_panel.focus_region.transform()
        import SegmentMenu
        from SegmentMenu import datamenuseg
        data_region = self.data_panel.focus_region
        #VU 1.2179
        # xform = datamenuseg.get_data_region_xform(data_region)
        xform, tf = datamenuseg.get_data_region_xform(data_region)
        #VU 1.2179
        # for newer versions rather, bbox is ijk rather than xyz
        if tf == None: # implies older versions
            bbox  = (xyz_in,xyz_out)
            import PDBmatrices
            tf = PDBmatrices.identity_matrix()
        else:
            bbox = (ijk_in, ijk_out)

        # create a box region if one does not exist
        if self.box_region_selector == None:
            import selectregion
            self.box_region_selector = \
                        selectregion.Select_Box(self.seg_dialog)

        # if box exists and shown, delete it, else reshape it
        self.box_region_selector.toggle_box()

        # reshape box to occupy current box
        #VU 1.2179
        # self.box_region_selector.box_model.reshape_box(bbox, xform)
        self.box_region_selector.box_model.reshape_box(bbox, tf, xform)

        msg = 'Selection region shown in red!\n'
        self.status(msg, color='blue', blankAfter=10)
        # replyobj.info(msg)
        
        return

    def parameters_to_circle(self):
        """parameters_to_circle() - draw circle from parameters
        
        Draw circle selection region after checking if all appropriate
        parameters entered.
        """

        if not (self.data_shown == self.data_panel.DATA_SHOWN):
            return

        #VU Circle Mask
        # self.no_feature('circle')

        size_value, center_value = \
                    self.check_parameters_circle(mild=1, warn=0)

        # if no valid parameters, then can't draw circle
        if (size_value == None or center_value == None):
            return

        # circle region in terms of ijk_in and ijk_out
        size_half = map(lambda a:a/2, size_value)
        ijk_in  = map(lambda a,b: int(a-b), center_value, size_half)
        ijk_out = map(lambda a,b: int(a+b), center_value, size_half)

        # circle region in terms of xyz_in and xyz_out
        data = self.data_item.data
        xyz_in  = data.ijk_to_xyz(ijk_in)
        xyz_out = data.ijk_to_xyz(ijk_out)

        # transform and box
        #VU 1.2129
        # xform = self.data_panel.focus_region.transform()
        import SegmentMenu
        from SegmentMenu import datamenuseg
        data_region = self.data_panel.focus_region
        #VU 1.2179
        # xform = datamenuseg.get_data_region_xform(data_region)
        xform, tf = datamenuseg.get_data_region_xform(data_region)
        #VU 1.2179
        # for newer versions rather, bbox is ijk rather than xyz
        if tf == None: # implies older versions
            bbox  = (xyz_in,xyz_out)
            import PDBmatrices
            tf = PDBmatrices.identity_matrix()
        else:
            bbox = (ijk_in, ijk_out)

        # create a circle region if one does not exist
        if self.circle_region_selector == None:
            import selectregion
            self.circle_region_selector = \
                        selectregion.Select_Circle(self.seg_dialog)

        # if circle exists and shown, delete it, else reshape it
        self.circle_region_selector.toggle_circle()

        # reshape circle to occupy current circle
        #VU 1.2179
        # self.circle_region_selector.circle_model.reshape_circle(bbox, xform)
        self.circle_region_selector.circle_model.reshape_circle(bbox, tf, xform)

        msg = 'Selection region shown in red!\n'
        self.status(msg, color='blue', blankAfter=10)
        # replyobj.info(msg)
        
        return

    # ---------------------------------------------------------------------
    # Parameters to xyz
    # ---------------------------------------------------------------------
    
    def parameters_to_xyz(self, size_ijk, center_ijk,
                          size_var_xyz, center_var_xyz):
        """parameters_to_xyz(size_ijk, center_ijk,
                             size_var_xyz, center_var_xyz)

        Input:
            size_ijk        list of size values (pixels)
            ceneter_ijk     list of center values (pixels)
            size_var_xyz    list of szie variables (xyz)
            center_var_xyz  list of cener variables (xyz) 
            
        Update xyz parameters for input size and center variables.
        """

        if size_ijk == None or self.data_item == None:
            for a in range(3):
                size_var_xyz[a].variable.set('')
        else:
            # Compute size_xyz as difference of zero_ijk and size_ijk
            # as data.ijk_to_xyz does real coordinate transformation.
            zero_ijk = [0,0,0]
            data = self.data_item.data
            xyz_in  = data.ijk_to_xyz(zero_ijk)
            xyz_out = data.ijk_to_xyz(size_ijk)

            size_xyz  = map(lambda a,b: b-a, xyz_in, xyz_out)
            for a in range(3):
                size_var_xyz[a].variable.set('%5.2f' % (size_xyz[a]))

        if center_ijk == None or self.data_item == None:
            for a in range(3):
                center_var_xyz[a].variable.set('')
        else:
            data = self.data_item.data
            center_xyz = data.ijk_to_xyz(center_ijk)
            for a in range(3):
                center_var_xyz[a].variable.set('%5.2f' % (center_xyz[a]))
        
        return        

    def parameters_to_box_xyz_cb(self):
        """parameters_to_box_xyz_cb() - callback for xyz parameters

        Update xyz parameters for box.
        """

        if (self.data_shown == self.data_panel.DATA_EMPTY):
            self.parameters_to_xyz(None, None,
                            self.box_size_xyz, self.box_center_xyz)
            return
                
        size_value, center_value = \
                    self.check_parameters_box(mild=1, warn=0)
        self.parameters_to_xyz(size_value, center_value,
                            self.box_size_xyz, self.box_center_xyz)

        return

    def parameters_to_circle_xyz_cb(self):
        """parameters_to_circle_xyz_cb() - callback for xyz parameters

        Update xyz parameters for circle.
        """

        # @ upgrade later
        #VU Circle Mask
        if (self.data_shown == self.data_panel.DATA_EMPTY):
            self.parameters_to_xyz(None, None,
                            self.circle_size_xyz, self.circle_center_xyz)
            return
                
        size_value, center_value = \
                    self.check_parameters_circle(mild=1, warn=0)
        self.parameters_to_xyz(size_value, center_value,
                            self.circle_size_xyz, self.circle_center_xyz)
        
        return

    def parameters_to_output_xyz_cb(self):
        """parameters_to_output_xyz_cb() - callback for xyz parameters

        Update xyz parameters for output.
        """

        if (self.data_shown == self.data_panel.DATA_EMPTY):
            self.parameters_to_xyz(None, None,
                            self.output_size_xyz, self.output_center_xyz)
            return
                
        size_value, center_value = \
                    self.check_parameters_output(mild=1, warn=0)
        self.parameters_to_xyz(size_value, center_value,
                            self.output_size_xyz, self.output_center_xyz)

        return

        
    # ---------------------------------------------------------------------
    # Check box parameters
    # ---------------------------------------------------------------------
    
    def check_parameters_box(self, mild=1, warn=0):
        """check_parameters_box(mild=1, warn=0)

        Input:
            mild        1 - check for integers (and +ve for size)
                        0 - check with data's size/center parameters
            warn        0 - quit
                        1 - warn (or update)
        Output:
            size_value      list of box size values (integers)
            center_value    list of box center values (integers)

        Check if parameters are integers (and +ve fr box size).
        If mild is set to 0, also check if box center within
        data region.
        """

        size_value   = self.check_parameters_box_size(warn)
        center_value = self.check_parameters_box_center(warn)
        
        if mild == 1:
            return size_value, center_value

        # perform further checks, check for more stringent conditions
        size_value, center_value = \
            self.check_parameters_box_strict(size_value, center_value)

        return size_value, center_value

    def check_parameters_box_size(self, warn):
        """check_parameters_box_size(warn)

        Input:
            warn            1/0
            
        Output:
            size_value      list of box size values (integers)
            
        Check box size parameters. If warn=1, inform about bad
        parameters.
        """

        size = []
        for a in range(3):
            size.append(self.box_size[a].variable.get())

        # check if box size values are +ve integers
        size_value = []
        for a in range(3):
            if size[a].strip().isdigit():
                size_value.append(int(size[a]))
                self.box_size[a].variable.set('%s' % (size_value[a]))
            elif warn == 1:
                msg = 'Use +ve integer box dimensions!\n'
                self.status(msg, color='red', blankAfter=10)
                replyobj.error(msg)
                return None
            else:
                return None

        return size_value

    def check_parameters_box_center(self, warn):
        """check_parameters_box_center(warn)

        Input:
            warn            1/0

        Output:
            center_value    list of box center values (integers)

        Check box center parameters. If warn=1, inform about bad
        parameters.
        """
        
        center = []
        for a in range(3):
            center.append(self.box_center[a].variable.get())

        input_size = self.data_item.size
        center_value = map(lambda a: a/2, input_size)

        # check if box center values are integers,
        # if not set them to half of data size
        for a in range(3):
            if center[a].strip().lstrip('-').isdigit():
                center_value[a] = int(center[a])
                self.box_center[a].variable.set('%s' % (center_value[a]))
            elif warn == 1:
                # use data center for coordinate 'a'
                msg = 'Updating box center...\n'
                self.status(msg, color='blue', blankAfter=10)
                replyobj.warning(msg)
                msg = 'Output center coord %d set to data center' % (a)
                replyobj.warning(msg)
                self.box_center[a].variable.set('%s' % (center_value[a]))
            else:
                return None

        return center_value

    def check_parameters_box_strict(self, size_ijk, center_ijk):
        """check_parameters_box_strict(self, size_ijk, center_ijk)

        Input:
            size_ijk
            center_ijk
            warn                1 - warn or update

        Output:
            size_ijk             list, None if not satisfied
            center_ijk           list, None if not satisfied

        Check box parameters against data size and data center.
        Return 0 if conditions not satisfied.
        """

        if size_ijk == None or center_ijk == None:
            return None, None
        
        size_half_ijk = map(lambda a:a/2, size_ijk)
        ijk_in  = map(lambda a,b: a-b, center_ijk, size_half_ijk)
        ijk_out = map(lambda a,b: a+b, center_ijk, size_half_ijk)

        input_size = self.data_item.size
            
        # quit if non-positive size
        if ((size_half_ijk < [0,0,0]) or (size_half_ijk[0] == 0) or
            (size_half_ijk[1] == 0)   or (size_half_ijk[2] == 0)):
            msg = 'Box dimensions should be at least 2x2x2!\n'
            self.status(msg, color='red', blankAfter=10)
            replyobj.error(msg)
            return None, None

        # quit if completely outside
        if (ijk_in  > input_size) or (ijk_out < [0,0,0]):
            msg = 'Box completely outside data!\n'
            self.status(msg, color='red', blankAfter=10)
            replyobj.error(msg)
            return None, None

        # quit if box center outside (EMAN requirement)
        for a in range(3):
            if (center_ijk[a] <0 ) or (center_ijk[a] > input_size[a]):
                msg = 'Ensure box center inside data!\n'
                self.status(msg, color='red', blankAfter=10)
                replyobj.error(msg)
                return None, None
            
        # warn if padding
        if (ijk_in  < [0,0,0]) or (ijk_out > input_size):
            msg = 'Box lies partially outside data, using padding...\n'
            replyobj.warning(msg)

        # warn if MRC origin would be = (0,0,0)
        if not sum(map(lambda a,b: a-2*b, input_size, ijk_in)):
            msg = 'Output may not be displayed with correct center.\n'
            replyobj.warning(msg)

        return size_ijk, center_ijk

    # ---------------------------------------------------------------------
    # Check circle parameters (VU Circle Mask)
    # ---------------------------------------------------------------------
    
    def check_parameters_circle(self, mild=1, warn=0):
        """check_parameters_circle(mild=1, warn=0)

        Input:
            mild        1 - check for integers (and +ve for size)
                        0 - check with data's size/center parameters
            warn        0 - quit
                        1 - warn (or update)
        Output:
            size_value      list of circle size values (integers)
            center_value    list of circle center values (integers)

        Check if parameters are integers (and +ve fr box size).
        If mild is set to 0, also check if box center within
        data region.
        """

        size_value   = self.check_parameters_circle_size(warn)
        center_value = self.check_parameters_circle_center(warn)
        
        if mild == 1:
            return size_value, center_value

        # perform further checks, check for more stringent conditions
        size_value, center_value = \
            self.check_parameters_circle_strict(size_value, center_value)

        return size_value, center_value

    def check_parameters_circle_size(self, warn):
        """check_parameters_circle_size(warn)

        Input:
            warn            1/0
            
        Output:
            size_value      list of circle size values (integers)
            
        Check circle size parameters. If warn=1, inform about bad
        parameters.
        """

        size = []
        for a in range(3):
            size.append(self.circle_size[a].variable.get())

        # check if circle size values are +ve integers
        size_value = []
        for a in range(3):
            if size[a].strip().isdigit():
                size_value.append(int(size[a]))
                self.circle_size[a].variable.set('%s' % (size_value[a]))
            elif warn == 1:
                msg = 'Use +ve integer circle dimensions!\n'
                self.status(msg, color='red', blankAfter=10)
                replyobj.error(msg)
                return None
            else:
                return None

        return size_value

    def check_parameters_circle_center(self, warn):
        """check_parameters_circle_center(warn)

        Input:
            warn            1/0

        Output:
            center_value    list of circle center values (integers)

        Check circle center parameters. If warn=1, inform about bad
        parameters.
        """
        
        center = []
        for a in range(3):
            center.append(self.circle_center[a].variable.get())

        input_size = self.data_item.size
        center_value = map(lambda a: a/2, input_size)

        # check if circle center values are integers,
        # if not set them to half of data size
        for a in range(3):
            if center[a].strip().lstrip('-').isdigit():
                center_value[a] = int(center[a])
                self.circle_center[a].variable.set('%s' % (center_value[a]))
            elif warn == 1:
                # use data center for coordinate 'a'
                msg = 'Updating circle center...\n'
                self.status(msg, color='blue', blankAfter=10)
                replyobj.warning(msg)
                msg = 'Output center coord %d set to data center' % (a)
                replyobj.warning(msg)
                self.circle_center[a].variable.set('%s' % (center_value[a]))
            else:
                return None

        return center_value

    def check_parameters_circle_strict(self, size_ijk, center_ijk):
        """check_parameters_circle_strict(self, size_ijk, center_ijk)

        Input:
            size_ijk
            center_ijk
            warn                1 - warn or update

        Output:
            size_ijk             list, None if not satisfied
            center_ijk           list, None if not satisfied

        Check circle parameters against data size and data center.
        Return 0 if conditions not satisfied.
        """

        if size_ijk == None or center_ijk == None:
            return None, None
        
        size_half_ijk = map(lambda a:a/2, size_ijk)
        ijk_in  = map(lambda a,b: a-b, center_ijk, size_half_ijk)
        ijk_out = map(lambda a,b: a+b, center_ijk, size_half_ijk)

        input_size = self.data_item.size
            
        # quit if non-positive size
        if ((size_half_ijk < [0,0,0]) or (size_half_ijk[0] == 0) or
            (size_half_ijk[1] == 0)   or (size_half_ijk[2] == 0)):
            msg = 'Circle dimensions should be at least 2x2x2!\n'
            self.status(msg, color='red', blankAfter=10)
            replyobj.error(msg)
            return None, None

        # quit if completely outside
        if (ijk_in  > input_size) or (ijk_out < [0,0,0]):
            msg = 'Circle completely outside data!\n'
            self.status(msg, color='red', blankAfter=10)
            replyobj.error(msg)
            return None, None

        # quit if circle center outside (EMAN requirement)
        for a in range(3):
            if (center_ijk[a] <0 ) or (center_ijk[a] > input_size[a]):
                msg = 'Ensure circle center inside data!\n'
                self.status(msg, color='red', blankAfter=10)
                replyobj.error(msg)
                return None, None
            
        # warn if padding
        # @ CHECK PADDING DONE?
        if (ijk_in  < [0,0,0]) or (ijk_out > input_size):
            msg = 'Circle lies partially outside data, using padding...\n'
            replyobj.warning(msg)

        # warn if MRC origin would be = (0,0,0)
        if not sum(map(lambda a,b: a-2*b, input_size, ijk_in)):
            msg = 'Output may not be displayed with correct center.\n'
            replyobj.warning(msg)

        return size_ijk, center_ijk

    # ---------------------------------------------------------------------
    # Check output parameters
    # ---------------------------------------------------------------------

    # These are mild condition checks for output parameters.
    # More stringent tests (checks against segment region
    # parameters) are done when the Apply button is pressed.
    # That way, the ouput region is checked only against the
    # correct segmentation type (box, etc.).
    
    def check_parameters_output(self, mild=1, warn=0):
        """check_parameters_output(mild=1, warn=0)

        Input:
            mild        1 - check for integers (and +ve for size)
                        0 - current does same as 1
            warn        0 - quit
                        1 - warn (or update)
        Output:
            size_value      list of output size values (integers)
            center_value    list of output center values (integers)

        Check if parameters are integers (and +ve fr box size).
        If mild is set to 0, does not do anything more.
        """

        size_value   = self.check_parameters_output_size(warn)
        center_value = self.check_parameters_output_center(warn)
        
        if mild == 1:
            return size_value, center_value

        # perform further checks, check for more stringent conditions
        # size_value, center_value = \
        #    self.check_parameters_output_strict(size_value, center_value)

        return size_value, center_value

    def check_parameters_output_size(self, warn):
        """check_parameters_output_size(warn)

        Input:
            warn            1/0
            
        Output:
            size_value      list of box size values (integers)
            
        Check output size parameters. If warn=1, inform about bad
        parameters.
        """

        size = []
        for a in range(3):
            size.append(self.output_size[a].variable.get())

        # check if output size values are +ve integers
        size_value = []
        for a in range(3):
            if size[a].strip().isdigit():
                size_value.append(int(size[a]))
                self.output_size[a].variable.set('%s' % (size_value[a]))
            elif warn == 1:
                msg = 'Use +ve integer output dimensions!\n'
                self.status(msg, color='red', blankAfter=10)
                replyobj.error(msg)
                return None
            else:
                return None

        return size_value

    def check_parameters_output_center(self, warn):
        """check_parameters_output_center(warn)

        Input:
            warn            1/0

        Output:
            center_value    list of output center values (integers)

        Check output center parameters. If warn=1, inform about bad
        parameters.
        """
        
        center = []
        for a in range(3):
            center.append(self.output_center[a].variable.get())

        input_size = self.data_item.size
        center_value = map(lambda a: a/2, input_size)

        # check if box center values are integers,
        # if not set them to half of data size
        for a in range(3):
            if center[a].strip().lstrip('-').isdigit():
                center_value[a] = int(center[a])
                self.output_center[a].variable.set('%s' %
                                                   (center_value[a]))
            elif warn == 1:
                # use data center for coordinate 'a'
                msg = 'Updating output center... \n'
                self.status(msg, color='blue', blankAfter=10)
                replyobj.warning(msg)
                msg = 'Output center coord %d set to data center\n' % (a)
                replyobj.warning(msg)
                self.output_center[a].variable.set('%s' %
                                                   (center_value[a]))
            else:
                return None

        return center_value

    # ---------------------------------------------------------------------
    # Selection to parameters
    # ---------------------------------------------------------------------

    #VU 1.2179
    # def selection_to_parameters_cb(self, xyz_in, xyz_out):
    #    """selection_to_parameters_cb(self, xyz_in, xyz_out)
    #
    #    Input:
    #        xyz_in
    #        xyz_out
    #
    #    Output:
    #        ijk_in
    #        ijk_out
    #        
    #    Get xyz parameters from selection and convert them to pixels,
    #    then call an update parameters function.
    #    """
    def selection_to_parameters_cb(self, xyz_in, xyz_out, ijk=None):
        """selection_to_parameters_cb(self, xyz_in, xyz_out, ijk=None)

        Input:
            xyz_in
            xyz_out
            ijk = None  if true, then xyz_in and xyz_out are ijk

        Output:
            ijk_in
            ijk_out
            
        Get xyz parameters from selection and convert them to pixels,
        then call an update parameters function.
        """

        if xyz_in == None or xyz_out == None:
            if self.data_panel.focus_region == None:
                msg = 'No data region!\n'
                self.status(msg, color='red', blankAfter=15)
                replyobj.error(msg)
            else:
                print "hello!" # @
            return

        data_region = self.data_panel.focus_region
        if data_region == None:
            return

        #VU 1.2129
        # data = data_region.data_set.data
        import SegmentMenu
        from SegmentMenu import datamenuseg
        data = datamenuseg.find_data_from_data_region(data_region)

        #VU 1.2179
        # ijk_in  = data.xyz_to_ijk(xyz_in)
        # ijk_out = data.xyz_to_ijk(xyz_out)
        if ijk == None:
            ijk_in  = data.xyz_to_ijk(xyz_in)
            ijk_out = data.xyz_to_ijk(xyz_out)
        else:
            ijk_in  = xyz_in
            ijk_out = xyz_out
        
        seg_type = self.segment_type.get()
        if   seg_type == self.segment_choices[0]:
            self.box_to_parameters(ijk_in, ijk_out)
        elif seg_type == self.segment_choices[1]:
            self.circle_to_parameters(ijk_in, ijk_out)
        else:
            pass

        return

    def box_to_parameters(self, ijk_in, ijk_out):
        """box_to_parameters(ijk_in, ijk_out)

        Input:
            ijk_in
            ijk_out

        Update entries for box selection region from selection.
        """

        center_ijk = map(lambda a,b: int((a+b)/2), ijk_in, ijk_out)
        size_ijk   = map(lambda a,b: int((b-a)  ), ijk_in, ijk_out)

        for a in range(3):
            self.box_center[a].variable.set(center_ijk[a])
            self.box_size[a].variable.set(  size_ijk[a])
            
        self.parameters_to_xyz(size_ijk, center_ijk,
                        self.box_size_xyz, self.box_center_xyz)

        return 

    def circle_to_parameters(self, ijk_in, ijk_out):
        """circle_to_parameters(ijk_in, ijk_out)

        Input:
            size_ijk
            center_ijk

        Update entries for circle selection region from selection.
        """

        # @ upgrade later
        center_ijk = map(lambda a,b: int((a+b)/2), ijk_in, ijk_out)
        size_ijk   = map(lambda a,b: int((b-a)  ), ijk_in, ijk_out)

        for a in range(3):
            self.circle_center[a].variable.set(center_ijk[a])
            self.circle_size[a].variable.set(  size_ijk[a])

        self.parameters_to_xyz(size_ijk, center_ijk,
                        self.circle_size_xyz, self.circle_center_xyz)

        return

    # ---------------------------------------------------------------------
    # Output region functions
    # ---------------------------------------------------------------------

    def output_region_type_cb(self):
        """output_region_type_cb() - callback for output region type

        Displays a message and activates/decativates output
        parameters panel.
        """

        ort = self.output_region_menu.variable.get()
        if not (ort in self.output_choices.values()):
            ort = self.output_choices.values()[0]
            self.output_region_menu.variable.set(ort)
            self.choose_region_type_cb()
            print 'unknow region type'
            return
            
        if   ort == self.output_choices[0]:
            # segment volume
            msg = 'Output region is same as segmented volume!\n'
        elif ort == self.output_choices[1]:
            # original volume
            msg = 'Output region is same as original volume!\n'
        elif ort == self.output_choices[2]:
            # custom volume
            msg = 'Specify output region size and center!\n'
        else:
            region_choice = None
            
        self.output_region_message['text'] = msg
        self.output_region_parameters_cb()
        
        return

    def output_region_parameters_cb(self):
        """output_region_parameters_cb() - callback

        Sets default values for output region parameters.
        """

        ort = self.output_region_menu.variable.get()
        if self.data_item:
            data_size = self.data_item.size
            data_center = map(lambda a: a/2, data_size)
            ds = map(lambda a: '%d' % (a),   data_size)
            dc = map(lambda a: '%d' % (a), data_center)
        else:
            data_size = None
            data_center = None
            ds = ['', '', '']
            dc = ['', '', '']
        
        if ort == self.output_choices[0]:
            # segment volume
            for a in range(3):
                self.output_size[a].variable.set('')
                self.output_center[a].variable.set('')
                self.output_size[a].entry['state'] = 'disabled'
                self.output_center[a].entry['state'] = 'disabled'
        elif ort == self.output_choices[1]:
            # original volume
            for a in range(3):
                self.output_size[a].variable.set(ds[a])
                self.output_center[a].variable.set(dc[a])
                self.output_size[a].entry['state'] = 'readonly'
                self.output_center[a].entry['state'] = 'readonly'
            self.parameters_to_xyz(data_size, data_center,
                        self.output_size_xyz, self.output_center_xyz)
        elif ort == self.output_choices[2]:
            # custom volume
            for a in range(3):
                self.output_size[a].entry['state'] = 'normal'
                self.output_center[a].entry['state'] = 'normal'

        return

    # ---------------------------------------------------------------------
    #  Segmentation related functions
    # ---------------------------------------------------------------------

    def seg_type_cb(self):
        """seg_type_cb() - callback for segment type.
        """

        # @ Really no need for this function later...

        # @ For some reason, when a choice is set, the
        #   button does not get updated automatically,
        #   until the mouse is brought over the button.
        
        seg_type = self.segment_type.get()
       
        if   seg_type == self.segment_choices[0]:
            pass
        elif seg_type == self.segment_choices[1]:
            #VU Circle Mask
            # for now, no circle feature
            # self.no_feature('circle')
            # self.segment_type.set(self.segment_choices[0],
            #                      invoke_callbacks = 0)
            pass
        else:
            self.segment_type.set(self.segment_choices[0],
                                  invoke_callbacks = 0)
            
        return

    def segment_apply_cb(self):
        """segment_apply_cb() - callback for Apply button.
        """

        self.segment_apply()
        
        return

    def segment_apply(self):
        """segment_apply()- applies appropriate segmentation 

        Applies appropriate segmentation after Apply button
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

        seg_type = self.segment_type.get()

        # get input file path, name, and size in pixels
        infile_path = str(self.data_item.path)
        infile      = str(self.data_item.name)
        infile_size = self.data_item.size

        # check and set output name
        self.output_item = None
        outfile = str(self.data_output.variable.get())
        if (outfile == '') or (outfile == infile):
            if   seg_type == self.segment_choices[0]:
                first_part, last_part = self.name_and_dot_suffix(infile)
                outfile = '%s-box%s' % (first_part, last_part)
            elif seg_type == self.segment_choices[1]:
                first_part, last_part = self.name_and_dot_suffix(infile)
                outfile = '%s-cir%s' % (first_part, last_part)
            msg = 'Using default output file %s\n'% outfile
            replyobj.info(msg)
        self.data_output.variable.set(outfile)

        # apply segmentation
        if   seg_type == self.segment_choices[0]:
            print 'segmenting out box region'
            seg_success = self.segment_apply_box(infile_path,
                                        outfile, infile_size)
        elif seg_type == self.segment_choices[1]:
            print 'segmenting out circle region'
            seg_success = self.segment_apply_circle(infile_path,
                                        outfile, infile_size)
        else:
            seg_success = 0
            pass

        # add to menu
        if seg_success:
            self.open_output_data_items(os.getcwd(),[outfile])
            self.enter()

    # ---------------------------------------------------------------------
    # Box segmentation
    # ---------------------------------------------------------------------

    def segment_apply_box(self, inputfile,outputfile,input_size):
        """segment_apply_box(self, inputfile,outputfile,input_size)

        Input:
            inputfile       input file path
            outputfile      output file name
            input_size      input data size (tuple)

        Apply box segmentation after checking for input data,
        box parameters and output parameters.

        Assumes that the input parameters are all valid.
        """

        msg = 'Applying box segmentation on %s\n' % inputfile
        replyobj.info(msg)

        # get box size - check if appropriate
        size_value, center_value = \
                    self.check_parameters_box(mild=0,warn=1)
        self.parameters_to_xyz(size_value, center_value,
                            self.box_size_xyz, self.box_center_xyz)
        if (size_value == None or center_value == None):
            return 0

        # Note: The box conditions above take care of most of the
        # exceptions, when we compare output size with box size.

        # get output size - check if acceptable.
        ort = self.output_region_menu.variable.get()
        if   ort == self.output_choices[0]:
            output_size = size_value
        elif ort == self.output_choices[1]:
            output_size = self.data_item.size
        elif ort == self.output_choices[2]:
            # custom
            output_size = self.check_output_size(size_value)
        else:
            return 0

        if output_size == None:
            return 0

        # get output center - check if acceptable
        if   ort == self.output_choices[0]:
            output_center = center_value
        elif ort == self.output_choices[1]:
            output_center = map(lambda a: a/2, self.data_item.size)
        elif ort == self.output_choices[2]:
            # custom
            output_center = self.check_output_center(output_size,
                                        size_value, center_value)
        else:
            return 0
        
        if output_center == None:
            return 0

        # @ assuming boxes in same directory as this class
        dir = os.path.dirname(__file__)
        cmd0 = os.path.join(dir, 'boxes.py')

        cmd0 = cmd0 + ' "%s" "%s" clip=' %(inputfile,outputfile)
        cmd0 = cmd0 + '%d,%d,%d' %(tuple(size_value))
        cmd0 = cmd0 + ',%d,%d,%d' % (tuple(center_value))
        cmd0 = cmd0 + ' pad=%d,%d,%d' % (tuple(output_size))
        cmd0 = cmd0 + ',%d,%d,%d' % (tuple(output_center))

        # @ windows seems to require the command python
        cmd0 = 'python ' + cmd0

        print cmd0
        os.system(cmd0)

        msg = 'Applied box segmentation on %s\n' \
              % os.path.basename(inputfile)
        self.status(msg, color='blue', blankAfter=10)
        replyobj.info(msg)

        return 1

    def check_output_size(self, box_size):
        """check_output_size(box_size)

        Input:
            box_size        list of box size integers (tuple)
            
        Output:
            size_value      list of size integers (tuple)
                            default=None

        Check if output size valid integers and larger than
        box size. If not, return None.

        Assumes box parmaeters are valid.   
        """
        
        size = []
        for a in range(3):
            size.append(self.output_size[a].variable.get())

        # check if output size values are +ve integers
        size_value = []
        for a in range(3):
            if size[a].strip().isdigit():
                size_value.append(int(size[a]))
                self.output_size[a].variable.set('%s' % (size_value[a]))
            else:
                msg = 'Use +ve integer box dimensions!\n'
                self.status(msg, color='red', blankAfter=10)
                replyobj.error(msg)
                return None

        # quit if output size smaller than box
        for a in range(3):
            if size_value[a] < box_size[a]:
                msg = 'Custom output size smaller than box size!\n'
                self.status(msg, color='red', blankAfter=10)
                replyobj.error(msg)
                return None

        return size_value

    def check_output_center(self, size_value, box_size, box_center, warn=1):
        """check_output_center(size_value, box_size, box_center,warn=1)

        Input:
            size_value      list of size (integers)
            box_size        list of box size (integers)
            box_center      list of box size (integers)
            warn=1          warn if making changes, else return None
            
        Output:
            center_value    list of size integers (tuple)
                            default=None

       Check if output center valid. If not, return None.

       Assumes that box parameters are valid.
        """
        
        center = []
        for a in range(3):
            center.append(self.output_center[a].variable.get())

        center_value = map(lambda a: a/2, size_value)

        # check if box center values are integers,
        # if not set them to half of output size
        for a in range(3):
            if center[a].strip().lstrip('-').isdigit():
                center_value[a] = int(center[a])
                self.output_center[a].variable.set('%s' %
                                                   (center_value[a]))
            elif warn == 1:
                # use data center for coordinate 'a'
                msg = 'Updating output center...\n'
                self.status(msg, color='blue', blankAfter=10)
                replyobj.warning(msg)
                msg = 'Using data center as output center coord %d\n' % (a)
                replyobj.warning(msg)
                self.output_center[a].variable.set('%s' %
                                                   (center_value[a]))
            else:
                return None

        size_half = map(lambda a  : a/2, size_value)
        ijk_in    = map(lambda a,b: a-b, center_value, size_half)
        ijk_out   = map(lambda a,b: a+b, center_value, size_half)

        box_half  = map(lambda a  : a/2, box_size)
        box_in    = map(lambda a,b: a-b, box_center, box_half)
        box_out   = map(lambda a,b: a+b, box_center, box_half)

        # quit if segment box not inside output box
        for a in range(3):
            if ijk_in[a] > box_in[a] or ijk_out[a] < box_out[a]:
                msg = 'Custom output size does not include entire box!\n'
                self.status(msg, color='red', blankAfter=10)
                replyobj.error(msg)
                return None

        return center_value
    
    # ---------------------------------------------------------------------
    # Circle segmentation
    # ---------------------------------------------------------------------

    def segment_apply_circle(self, inputfile,outputfile,input_size):
        """segment_apply_circle(self, inputfile,outputfile,input_size)

        Input:
            inputfile       input file path
            outputfile      output file name
            input_size      input data size (tuple)

        Apply circle segmentation after checking for input data,
        box parameters and output parameters.
        """

        #VU Circle Mask
        # self.no_feature('circle')

        msg = 'Applying circle segmentation on %s\n' % inputfile
        replyobj.info(msg)

        # get circle size - check if appropriate
        size_value, center_value = \
                    self.check_parameters_circle(mild=0,warn=1)
        self.parameters_to_xyz(size_value, center_value,
                            self.circle_size_xyz, self.circle_center_xyz)
        if (size_value == None or center_value == None):
            return 0

        # Note: The circle conditions above take care of most of the
        # exceptions, when we compare output size with circle size.

        # get output size - check if acceptable.
        ort = self.output_region_menu.variable.get()
        if   ort == self.output_choices[0]:
            output_size = size_value
        elif ort == self.output_choices[1]:
            output_size = self.data_item.size
        elif ort == self.output_choices[2]:
            # custom
            output_size = self.check_output_size(size_value)
        else:
            return 0

        if output_size == None:
            return 0

        # get output center - check if acceptable
        if   ort == self.output_choices[0]:
            output_center = center_value
        elif ort == self.output_choices[1]:
            output_center = map(lambda a: a/2, self.data_item.size)
        elif ort == self.output_choices[2]:
            # custom
            output_center = self.check_output_center(output_size,
                                        size_value, center_value)
        else:
            return 0
        
        if output_center == None:
            return 0

        # @ assuming boxes in same directory as this class
        dir = os.path.dirname(__file__)
        cmd0 = os.path.join(dir, 'boxes.py')

        cmd0 = cmd0 + ' "%s" "%s" circle=' %(inputfile,outputfile)
        cmd0 = cmd0 + '%d,%d,%d' %(tuple(size_value))
        cmd0 = cmd0 + ',%d,%d,%d' % (tuple(center_value))
        cmd0 = cmd0 + ' pad=%d,%d,%d' % (tuple(output_size))
        cmd0 = cmd0 + ',%d,%d,%d' % (tuple(output_center))

        # @ windows seems to require the command python
        cmd0 = 'python ' + cmd0

        print cmd0
        os.system(cmd0)

        msg = 'Applied circle segmentation on %s\n' \
              % os.path.basename(inputfile)
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

def seg_simple_dialog(create=0):
    """seg_simple_dialog(create=0) - look for Segment Simple dialog.

    If create = 1, then creates a new dialog if dialog does not exist.
    """
    
    from chimera import dialogs
    return dialogs.find(Segment_Simple.name, create=create)

def show_seg_simple_dialog():
    """show_seg_simple_dialog() - Shows the Segment Simple dialog.
    """
    
    from chimera import dialogs
    return dialogs.display(Segment_Simple.name)

# -------------------------------------------------------------------------
# Register dialog with Chimera.
# -------------------------------------------------------------------------

from chimera import dialogs
dialogs.register(Segment_Simple.name,Segment_Simple,replace=1)

# -------------------------------------------------------------------------
