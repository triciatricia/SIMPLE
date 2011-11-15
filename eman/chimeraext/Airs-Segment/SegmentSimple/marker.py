# -------------------------------------------------------------------------
# SegmentSimple/marker.py
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
#       2006.03.06: Lavu Sridhar, BCM (VU 1.2179 Chimera) Part2
#
# To Do:
#       See comments marked with # @
# 
# Key:
#       VU: Version Upgrade
#
"""Segmentation of MRC density maps using markers.

GUI to perform segmentation of MRC density maps, using Markers and:
(1) Boxes Regions
(2) Nearest Neigbhorhood Regions
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

class Segment_Marker(ModelessDialog):
    """Class: Segment_Marker()

    The main GUI dialog for marker based segmentation.
    """

    title='Segment Marker'
    name = 'segment marker'
    buttons = ('Close',)

    # @ help = 'ContributedSoftware/SegmentSimple/marker.html'
    dir_pkg = os.path.dirname(__file__)
    help_path = os.path.join(dir_pkg, 'marker.html')
    help_url = 'file://' + help_path
    help = help_url

    provideStatus = True
    statusPosition = 'above'
    statusResizing = False
    statusWidth = 40

    segment_choices = {0: 'Box  ', 1: 'Near '}
    output_choices = {0: 'single', 1: 'multiple'}
    
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

        self.seg_dialog = seg_marker_dialog()

        self.marker_dialog = None
        self.marker_set = None
        self.marker_boxes = []

        self.refresh_in_progress = 0
        
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

        # parameters frame (pf)
        row = row + 1
        pf = Tkinter.Frame(parent, padx=8, pady=8)
        pf.grid(row = row, column = 0, sticky = 'nw')
        self._make_parameters_panel(pf)

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
        omf.frame.grid(row = row, column = 0, sticky = 'nw', pady=8)
        self.output_panel = omf

        # create initial data menu list
        self.data_panel.data_items_refresh()

        # default values
        self.segment_type.set(self.segment_choices[0],
                              invoke_callbacks=0)
        self.output_type.set(self.output_choices[0])

        # set trigger for OpenModels
        chimera.triggers.addHandler('OpenModels',
                                    self.marker_set_refresh_cb, None)

        self.marker_refresh_cb()
        
        # @ do we need to do stuff before closing Chimera session
        #   or this segmentation dialog

    # ---------------------------------------------------------------------
    # Panels
    # ---------------------------------------------------------------------

    def _make_parameters_panel(self, frame):
        """_make_parameters_panel(frame)

        Make a panel in the GUI for parameters (marker set, box size).
        """

        row = 0

        # parameters label (pL)
        pL = Tkinter.Label(frame, text = 'Parameters ')
        pL.grid(row = row, column = 0, sticky = 'w')

        # marker set menu (msm)
        row = row + 1
        msm = Hybrid.Option_Menu(frame, 'Marker Set : ')
        msm.frame.grid(row = row, column = 0, sticky = 'w', padx=32)
        msm.add_callback(self.marker_menu_cb)
        self.marker_menu = msm

        # marker set buttons (msb)
        row = row + 1
        msb = Hybrid.Button_Row(frame, '',
                                  (('Open', self.marker_open_cb),
                                   ('Refresh List',
                                    self.marker_refresh_cb)))
        msb.frame.grid(row=row, column=0, sticky='w', padx=32, pady=2)

        # box size (bxs)
        row = row + 1
        bxs = Hybrid.Entry(frame, 'Box Size (Angstroms)  ', '8', '')
        bxs.frame.grid(row=row, column=0, sticky='w', padx=32, pady=2)
        self.box_size = bxs
        # @ how to update entry - callback


        # marker boxes (mbx)
        row = row + 1
        mbx = Hybrid.Button_Row(frame, 'Boxes ',
                                (('Show',self.marker_boxes_show_cb),
                                 ('Hide',self.marker_boxes_hide_cb)))
        mbx.frame.grid(row=row, column=0, sticky='w', padx=32, pady=2)

        return

    def _make_segmentation_panel(self, frame):
        """_make_segmentation_panel(frame)

        Make a panel on the GUI for segmentation and output file info.
        """

        row = 0
        
        # segment info label (siL)
        siL = Tkinter.Label(frame, text = 'Segmentation Info ')
        siL.grid(row = row, column = 0, sticky = 'w')

        # chosoe segment type (cst)
        row = row + 1
        cst = Hybrid.Radiobutton_Row(frame, 'Choose type ',
                                     (self.segment_choices[0],
                                      self.segment_choices[1]),
                                     self.seg_type_cb)
        cst.frame.grid(row = row, column = 0, columnspan=2,
                       sticky = 'nw', padx=32)
        self.segment_type = cst.variable

        # choose number of outputs (cno)
        row = row + 1
        cno = Hybrid.Radiobutton_Row(frame, 'Output files ',
                                     (self.output_choices[0],
                                      self.output_choices[1]),
                                     self.output_type_cb)
        cno.frame.grid(row = row, column = 0, columnspan=2,
                       sticky = 'nw', padx=32)
        self.output_type = cno.variable

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
    #  Marker related functions.
    # ---------------------------------------------------------------------

    def marker_open_cb(self):
        """marker_open_cb() - callback for marker set open buton

        Calls the Volume Path Dialog and its open dialog.
        """

        # @  Better way?

        if self.marker_dialog == None:
            import VolumePath
            self.marker_dialog = VolumePath.volume_path_dialog(1)

        self.marker_dialog.ImportXML()
        self.marker_dialog.enter()
        self.marker_dialog.open_dialog.enter()

        return
    
    def marker_menu_cb(self):
        """marker_menu_cb() - callback for marker set menu
        """

        name = self.marker_menu.variable.get()
        self.marker_set = self.find_marker_set_by_name(name)
        if self.marker_set:
            name = self.marker_set.name
        else:
            name = ''
        self.marker_menu.variable.set(name, invoke_callbacks = 0)

        # adjust markers opacity
        self.marker_set_opaque_cb()

        return

    def marker_set_opaque_cb(self):
        """marker_set_opaque_cb()

        Set markers to 0.5 opacity if fully opaqe.
        """

        if not self.marker_set:
            return

        for marker in self.marker_set.markers():
            r,g,b,a = marker.rgba()
            if a == 1:
                a = 0.5
                marker.set_rgba((r,g,b,a))
                marker.show_note(1)

        return
    
    def marker_refresh_cb(self):
        """marker_refresh_cb()

        Refresh markers list whenever models are opened or closed in
        Chimera.
        """

        # @ Need to update menu with Listbox in VolumePath
        #   whenever that listbox changes. Any better ways?

        if self.marker_dialog == None:
            import VolumePath
            vpd = VolumePath.volume_path_dialog()
            if vpd == None:
                return
            self.marker_dialog = vpd

        # flush out all entries, get open models list, populate menu
        self.marker_menu.remove_all_entries()
        open_models = chimera.openModels.list()
        for ms in self.marker_sets():
            self.marker_menu.add_entry(ms.name)

        # if previous entry still in current marker sets list,
        # then reset else, set to top most entry
        ms = self.marker_set
        if ms and self.find_marker_set_by_name(ms.name):
            self.marker_menu.variable.set(ms.name)
        elif len(self.marker_sets()) > 0:
            ms = self.marker_sets()[-1]
            self.marker_menu.variable.set(ms.name)
        else:
            self.marker_menu.variable.set('')
            
    # ---------------------------------------------------------------------
    #  Marker boxes related functions.
    # ---------------------------------------------------------------------

    def marker_boxes_show_cb(self):
        """marker_boxes_show_cb()

        Show boxes around selected markers, with box center at
        marker center and box size equal to marker diameter,
        with a transform matching data size.
        """

        self.marker_boxes_hide_cb()

        ms = self.marker_set
        if ms == None:
            return

        mssm = ms.selected_markers()
        # check if any markers selected
        if len(mssm) == 0:
            msg = 'No selected markers!\n'
            self.status(msg, color='red', blankAfter=15)
            replyobj.warning(msg)
            return

        # check input data exists
        if self.data_item == None:
            msg = 'Input data not found!\n'
            self.status(msg, color='red', blankAfter=15)
            replyobj.warning(msg)
            return

        #VU 1.2129
        # xform = self.data_item.region.transform()
        import SegmentMenu
        from SegmentMenu import datamenuseg
        data_region = self.data_item.region
        #VU 1.2179
        # xform = datamenuseg.get_data_region_xform(data_region)
        xform, tf = datamenuseg.get_data_region_xform(data_region)
        xyz_to_ijk = self.data_item.data.xyz_to_ijk
        #VU 1.2179
        #for im in mssm:
        #    self.marker_boxes.append(self.marker_box_create(im,xform))
        for im in mssm:
            self.marker_boxes.append(
                self.marker_box_create(im,tf,xform, xyz_to_ijk))
            
        return
    
    def marker_boxes_hide_cb(self):
        """marker_boxes_hide_cb()

        Hide any boxes shown around markers.
        """

        if len(self.marker_boxes) == 0:
            return

        # open_models = chimera.openModels.list()
        for marker_box in self.marker_boxes:
            # if marker_box in open_models:
            marker_box.delete_box()

        self.marker_boxes = []
        
        return

    #VU 1.2179
    #def marker_box_create(self, marker, xform):
    #    """marker_box_create(marker,xform)
    def marker_box_create(self, marker,tf,xform,xyz_to_ijk):
        """marker_box_create(marker,tf,xform,xyz_to_ijk)

        Create a box around marker center and of size equal to
        marker diameter, with a transform matching data size.
        """

        #VU 1.2179
        # use box size if given
        size_value = 0
        size = str(self.box_size.variable.get())
        if size.strip().lstrip('-').isdigit():
            size_value = int(size)
            self.box_size.variable.set('%d' % size_value)
        # else using marker radius instead of box size
        if size_value > 0:
            radius = size_value
        else:
            radius = marker.radius()

        #VU 1.2179
        # radius = marker.radius()
        center = marker.xyz()

        ms = marker.marker_set
        ms_xf = ms.transform()

        # convert marker center to data xform
        center_xyz = self.transform_coord(center,ms_xf,xform)

        #VU 1.2179
        # just making a copy
        #bbox = []
        #bbox.append(map(lambda a, b=radius: a-b, center_xyz))
        #bbox.append(map(lambda a, b=radius: a+b, center_xyz))
        bbox_xyz = []
        bbox_xyz.append(map(lambda a, b=radius: a-b, center_xyz))
        bbox_xyz.append(map(lambda a, b=radius: a+b, center_xyz))

        #VU 1.2179
        bbox_ijk = []
        bbox_ijk.append(map(lambda a: float(round(a)),
                            xyz_to_ijk(bbox_xyz[0])))
        bbox_ijk.append(map(lambda a: float(round(a)),
                            xyz_to_ijk(bbox_xyz[1])))

        #VU 1.2179
        # for newer versions rather, bbox is ijk rather than xyz
        bbox = []
        if tf == None:
            bbox.append(bbox_xyz[0])
            bbox.append(bbox_xyz[1])
            import PDBmatrices
            tf = PDBmatrices.identity_matrix()
        else:
            bbox.append(bbox_ijk[0])
            bbox.append(bbox_ijk[1])
            
        import selectregion
        box_model = selectregion.Box_Model()
        #VU 1.2179
        #box_model.reshape_box(bbox, xform)
        box_model.reshape_box(bbox, tf, xform)

        return box_model

    def transform_coord(self, from_xyz, from_xform, to_xform):

        import VolumePath
        to_xyz = VolumePath.transform_coordinates(from_xyz,
                                        from_xform, to_xform)

        return to_xyz
    
    # ---------------------------------------------------------------------
    # Callback function for trigger OpenModels when a new model is
    # added or removed in Chimera. 
    # ---------------------------------------------------------------------
    
    def marker_set_refresh_cb(self, *triggerArgs, **kw):
        """marker_set_refresh_cb(*triggerArgs, **kw)

        Updates marker set menu.
        """

        if self.refresh_in_progress == 0:
            self.refresh_in_progress = 1
            if ('model list change' in triggerArgs[-1].reasons):
                self.marker_refresh_cb()
            self.refresh_in_progress = 0

        return None
    
    def find_marker_set_by_name(self, name):
        """find_marker_set_by_name(name) -

        Input:
            name            marker set name, different from its
                            file name
        Output:
            marker_set      marker set that matches name,
                            defualt = None
                            
        Find marker set from Volume Path.
        """

        if not self.marker_dialog:
            return None

        return self.marker_dialog.find_marker_set_by_name(name)

    def marker_sets(self):
        """makrer_sets() - list of marker sets from Volume Path.

        Output:
            marker_sets     a list of marker sets or empty list
        """

        if not self.marker_dialog:
            return []

        return self.marker_dialog.marker_sets
    
    # ---------------------------------------------------------------------
    #  Segmentation related functions.
    # ---------------------------------------------------------------------

    def seg_type_cb(self):
        """seg_type_cb() - callback for segment type.

        If NN mode, then no use having single output file.
        """

        seg_type = self.segment_type.get()
        output_type = self.output_type.get()
        
        if   seg_type == self.segment_choices[0]:
            pass
        elif seg_type == self.segment_choices[1]:
            if output_type == self.output_choices[0]:
                self.output_type.set(self.output_choices[1],
                                     invoke_callbacks=0)
        else:
            self.segment_type.set(self.segment_choices[0])
            
        return 

    def output_type_cb(self):
        """output_type_cb() - callback for output type.

        If NN mode, then no use having single output file.
        """

        output_type = self.output_type.get()
        seg_type = self.segment_type.get()
        
        if   output_type == self.output_choices[0]:
            if seg_type == self.segment_choices[1]:
                self.output_type.set(self.output_choices[1],
                                     invoke_callbacks=0)
        elif output_type == self.output_choices[1]:
            pass
        else:
            self.output_type.set(self.output_choices[0])

        return
    
    def segment_apply_cb(self):
        """segment_apply_cb() - callback for Apply button.
        """

        self.segment_apply()

        return

    def segment_apply(self):
        """segment_apply() - applies appropriate segmentation

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

        # check marker set exists
        if self.marker_set == None:
            name = '%s' % (self.marker_menu.variable.get())
            msg = 'Marker set %s not found!\n' % name 
            self.status(msg, color='red', blankAfter=15)
            replyobj.error(msg)
            return

        # get input marker file path, name, and size
        markerfile_path = str(self.marker_set.file_path)
        markerfile      = os.path.basename(markerfile_path)
        markerfile_size = len(self.marker_set.markers())

        # check if markers exist
        if markerfile_size  == 0:
            name = '%s' % (self.marker_menu.variable.get())
            msg = 'Marker set %s empty!\n' % name 
            self.status(msg, color='red', blankAfter=15)
            replyobj.error(msg)
            return            

        # check and set output name
        self.output_item = None
        outfile = str(self.data_output.variable.get())
        if (outfile == '') or (outfile == infile):
            first_part, last_part = self.name_and_dot_suffix(infile)
            outfile = '%s-m%s' % (first_part, last_part)
            msg = 'Using default output file %s\n'% outfile
            replyobj.info(msg)
        self.data_output.variable.set(outfile)

        # for each marker, create a output file name
        first_part, last_part = self.name_and_dot_suffix(outfile)
        outfiles = []
        markers = self.marker_set.markers()
        for i_m in range(len(markers)):
            name = first_part + '-%d' % (i_m)
            name = name + last_part
            outfiles.append('%s' % name)

        # check marker parameters and write them to file, else quit
        marker_success = 0
        centers, radii = self.get_marker_parameters(markers)
        if centers == None or radii == None:
            return
        paramfile = outfile + '.temp.cmm'
        if not self.write_marker_parameters(centers, radii, paramfile):
            msg = 'Failed to write a temp marker file!\n'
            self.status(msg, color='red', blankAfter=15)
            replyobj.error(msg)
            return

        # check multiple or single output file
        output_type = self.output_type.get()
        if   output_type == self.output_choices[0]:
            msg = ' into single file\n'
            outfiles = [outfile]
        elif output_type == self.output_choices[1]:
            msg = ' info multiple files\n'

        # apply segmentation
        if   seg_type == self.segment_choices[0]:
            msg = 'segmenting box regions' + msg
            replyobj.info(msg)
            seg_success = self.segment_apply_boxes(infile_path,
                                paramfile, outfile)
        elif seg_type == self.segment_choices[1]:
            msg = 'segmenting NN regions' + msg
            replyobj.info(msg)
            seg_success = self.segment_apply_near(infile_path,
                                paramfile, outfile)
        else:
            seg_succes = 0
            pass

        # delete parameter file
        os.remove(paramfile)
        
        # add to menu
        if seg_success:
            self.open_output_data_items(os.getcwd(),outfiles)
            self.enter()

    # ---------------------------------------------------------------------
    # Boxes segmentation
    # ---------------------------------------------------------------------
    
    def segment_apply_boxes(self, inputfile, paramfile, outputfile):
        """segment_apply_boxes(inputfile, paramfile, outputfile)

        Input:
            inputfile
            paramfile       parameter file path (a temp file)
            outputfiles     list of output file paths
        
        Output:
            1/0             success
            
        Apply marker based box segmentation.

        Assumes that the input parmaeters are all valid.
        """

        msg = 'Applying boxes segmentation on %s\n' % inputfile
        replyobj.info(msg)

        output_type = self.output_type.get()
        
        # @ assuming boxes in same directory as this class
        dir = os.path.dirname(__file__)
        cmd0 = os.path.join(dir, 'boxes.py')

        cmd0 = cmd0 + ' "%s" "%s" ' % (inputfile, outputfile)
        cmd0 = cmd0 + ' boxes=%s ' % (paramfile)
        cmd0 = cmd0 + ' num=%s' % (output_type)

        # @ windows seems to require the command python'
        cmd0 = 'python ' + cmd0

        print cmd0
        os.system(cmd0)

        msg = 'Applied boxes segmentation on %s\n' \
              % os.path.basename(inputfile)
        self.status(msg, color='blue', blankAfter=10)
        replyobj.info(msg)

        return 1

    # ---------------------------------------------------------------------
    # Nearest neighborhood segmentation
    # ---------------------------------------------------------------------
    
    def segment_apply_near(self, inputfile, paramfile, outputfile):
        """segment_apply_near(inputfile, paramfile, outputfile)

        Input:
            inputfile
            paramfile       parameter file path (a temp file)
            outputfiles     list of output file paths
        
        Output:
            1/0             success
            
        Apply marker based box segmentation.

        Assumes that the input parmaeters are all valid.
        """

        msg = 'Applying NN segmentation on %s\n' % inputfile
        replyobj.info(msg)

        output_type = self.output_type.get()
        
        # @ assuming boxes in same directory as this class
        dir = os.path.dirname(__file__)
        cmd0 = os.path.join(dir, 'boxes.py')

        cmd0 = cmd0 + ' %s %s ' % (inputfile, outputfile)
        cmd0 = cmd0 + ' near=%s ' % (paramfile)
        cmd0 = cmd0 + ' num=%s' % (output_type)

        # @ windows seems to require the command python'
        cmd0 = 'python ' + cmd0

        print cmd0
        os.system(cmd0)

        msg = 'Applied NN segmentation on %s\n' \
              % os.path.basename(inputfile)
        self.status(msg, color='blue', blankAfter=10)
        replyobj.info(msg)

        return 1

    # ---------------------------------------------------------------------
    # Marker parameters
    # ---------------------------------------------------------------------
    
    def get_marker_parameters(self, markers):
        """get_marker_parameters(markers)

        Input:
            markers

        Output:
            ijk_center_values   box centers in pixels
            ijk_radius_values   box radii in pixels (size/2)

        Check the marker parameters, and return the markers
        parameters in terms of pixels: location and radius.

        Note: Marker radius will be used as size of cube,
        and if -ve, that box region will be set to zero.
        """
        
        xyz_to_ijk = self.data_item.data.xyz_to_ijk
        #VU 1.2129
        # xyz_origin = self.data_item.data.xyz_origin
        xyz_origin = self.data_item.origin
        
        # box size if given
        size_value = 0
        size = str(self.box_size.variable.get())
        if size.strip().lstrip('-').isdigit():
            size_value = int(size)
            self.box_size.variable.set('%d' % size_value)
        # else using marker radius instead of box size

        # get parameters from markers
        center_values = []
        radius_values = []
        for marker in markers:

            # marker location in pixels
            xyz = xyz_to_ijk(tuple(marker.xyz()))
            x, y, z = map(lambda a: int(a), xyz)
            center_ijk = [x,y,z]
            
            # if size value not given, use marker radius
            if size_value == 0: radius = [marker.radius(),0,0]
            else: radius = [size_value*0.5,0,0]

            # adjust for origin and convert to pixels
            radius[0] = radius[0] + xyz_origin[0]
            radius_ijk = int(xyz_to_ijk(radius)[0])
            if marker.note() == '-': radius_ijk = -radius_ijk

            center_values.append(center_ijk)
            radius_values.append(radius_ijk)

        centers_ijk, radii_ijk =  \
            self.check_marker_parameters(center_values, radius_values)

        return centers_ijk, radii_ijk
    
    def check_marker_parameters(self, centers, radii):
        """check_maker_parameters(centers, radii)

        Input:
            centers
            radii

        Output:
            centers_ijk     list of centers, default = None
            radii_ijk       list of radii, default = None

        Check if marker parameters are valid. Quit if not.
        """

        input_size = self.data_item.size
        centers_ijk = []
        radii_ijk = []
        
        for i_m in range(len(radii)):

            ijk_center = centers[i_m]
            ijk_radius = radii[i_m]
            ijk_min = map(lambda a: a - abs(ijk_radius), ijk_center)
            ijk_max = map(lambda a: a + abs(ijk_radius), ijk_center)

            # quit if completely outside
            if (ijk_min > input_size) or (ijk_max < [0,0,0]):
                msg = 'Found marker completely outside data!\n'
                self.status(msg, color='red', blankAfter=10)
                replyobj.error(msg)
                return None, None

            # quit if marker center outside (EMAN constraint)
            for a in range(3):
                if (ijk_center[a] < 0) or (ijk_center[a] > input_size[a]):
                    msg = 'Ensure marker center inside data!\n'
                    self.status(msg, color='red', blankAfter=10)
                    replyobj.error(msg)
                    return None, None

            centers_ijk.append(ijk_center)
            radii_ijk.append(ijk_radius)
            
        return centers_ijk, radii_ijk

    def write_marker_parameters(self, centers, radii, paramfile):
        """write_marker_parameters(centers, radii, paramfile)

        Input:
            centers     marker centers
            radii       radii of makers (+ve or -ve integers)
            paramfile   file to write parameters to

        Output:
            paramfile   marker parameter file, default = None
            
        Write marker parameters to file - markerfile, usually
        set to output file name with '.temp.cmm' suffix added.
        This file is deleted after segmentation is complete.
        """

        # @ A better way, instead of writing to a file?
 
        marker_param_lines = []
        for i_m in range(len(radii)):

            line = ' BOX     '
            line = line + '%d %d %d ' % tuple(centers[i_m])
            line = line + '%d\n' % radii[i_m]
            marker_param_lines.append(line)

        # write marker parameters to file
        file_write = open(paramfile,'w')
        file_write.writelines(marker_param_lines)
        file_write.close()

        if not os.path.isfile(paramfile):
            return None
        
        return paramfile

    # ---------------------------------------------------------------------
    #  Output functions.
    # ---------------------------------------------------------------------

    # ---------------------------------------------------------------------
    # After segmentation complete, update output data menu. 
    # 
    def open_output_data_items(self, outdir, outfiles):

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
        
    # ---------------------------------------------------------------------
    # Hides the data region corresponding to the output file.
    #
    def no_feature(self, name=None):

        if name == None:
            name = ''
        msg = 'Feature %s not available!\n' % (name) 
        self.status(msg, color='blue', blankAfter=3)
        replyobj.info(msg)
        return
    
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
def seg_marker_dialog(create=0):
    """Looks for Segment Marker dialog.

    seg_marker_dialog(create=0)

    If create = 1, then creates a new dialog if dialog does not exist.
    """
    
    from chimera import dialogs
    return dialogs.find(Segment_Marker.name, create=create)

# -------------------------------------------------------------------------
# Main dialog.
#
def show_seg_marker_dialog():
    """Shows the Segment Marker dialog.

    show_seg_marker_dialog()
    """
    
    from chimera import dialogs
    return dialogs.display(Segment_Marker.name)

# -------------------------------------------------------------------------
# Register dialog with Chimera.
# 
from chimera import dialogs
dialogs.register(Segment_Marker.name,Segment_Marker,replace=1)

# -------------------------------------------------------------------------
