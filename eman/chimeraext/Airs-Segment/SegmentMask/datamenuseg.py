#!/usr/bin/env python
# -------------------------------------------------------------------------
# SegmentMenu/datamenuseg.py
#
# Segment Volume package - Segment Menu module
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
"""Input and output menus used in Segment Volume package.

Data Item menu tracks open volume data models and keeps the
input and output menus up to date. 
"""

# -------------------------------------------------------------------------

# general modules
import Tkinter

# chimera related modules

import chimera
from chimera import replyobj
from CGLtk import Hybrid

# -------------------------------------------------------------------------
# Class Segment_Open_Data: Input Data Menu for Segment Volume package
# 
class Segment_Open_Data:
    """Class: Segment_Open_Data(dialog, parent,
                        data_status_dialog_cb) - input menu

    Input:
        dialog      dialog where menu is added
        parent
        data_status_dialog_cb
                    callback when data status changes
                    
    Input data menu for Segment Volume package.
    """

    DATA_SHOWN =     'Yes'
    DATA_NOT_SHOWN = 'No'
    DATA_EMPTY =     'NA'

    def __init__(self, dialog, parent, data_status_dialog_cb,
                 menu_label='Input  '):
        """__init__(dialog, parent, data_status_dialog_cb,
                    menu_label='Input  ') - input menu

        Input:
            dialog      dialog where menu is added
            parent
            data_status_dialog_cb
                        callback when data status changes
            menu_label  label for the menu (default = 'Input  ')
                    
        Input data menu for Segment Volume package.
        """

        self.dialog = dialog
        self.data_status_dialog_cb = data_status_dialog_cb
        
        self.data_items = []
        self.focus_region = None # current selection
        
        self.data_shown = self.DATA_EMPTY
        
        self.refresh_in_progress = 0

        frame = Tkinter.Frame(parent)
        frame.columnconfigure(0, weight = 1)
        self.frame = frame

        # self.toplevel_widget = parent.winfo_toplevel()

        # frame data (fd)
        fd = Tkinter.Frame(frame, padx=8)
        fd.grid(row = 0, column = 0, sticky = 'nw')
        row = 0

        fdL = Tkinter.Label(fd, text = menu_label)
        fdL.grid(row = row, column = 0, sticky = 'w')

        # frame data menu (fdm)
        fdm = Hybrid.Option_Menu(fd, 'Data file : ')
        fdm.frame.grid(row = row, column = 1, columnspan=4, sticky = 'w')
        
        fdm.add_callback(self.data_menu_cb)
        self.data_menu = fdm

        # frame data size (fds)
        row = row + 1
        fdsL = Tkinter.Label(fd, text = 'Size in Pixels : ')
        fdsL.grid(row = row, column = 1, sticky = 'w')

        fds = Tkinter.Frame(fd)
        fds.grid(row = row, column = 2, sticky = 'w')
        
        self.data_size = []
        for a in range(3):
            size_v = Hybrid.StringVariable(fds)
            size_e = Tkinter.Entry(fds, width=5,
                                   textvariable = size_v.tk_variable)
            size_e.grid(row = 0, column = a, sticky = 'w')
            size_e['state'] = 'readonly'
            self.data_size.append(size_v)
        
        # frame data region (fdr)
        fdrL = Tkinter.Label(fd, text = 'Displayed : ')
        fdrL.grid(row = row, column = 3, sticky = 'w', padx=4)

        fdr = Tkinter.Label(fd)
        fdr.grid(row = row, column = 4, sticky = 'w')

        fdr['font'] = non_bold_font(fd)
        self.data_region_name = fdr

        # frame data  buttons (fdb)
        row = row + 1
        fdb = Hybrid.Button_Row(fd, '',
                                (('Open', self.data_open_cb),
                                 ('Refresh menu',
                                  self.data_items_refresh_cb)))
        fdb.frame.grid(row = row, column = 1, columnspan=4,
                       sticky = 'w',pady=4)

        self.data_open_button = fdb.buttons[0]
        self.data_refresh_button = fdb.buttons[1]

        # set trigger for OpenModels
        chimera.triggers.addHandler('OpenModels',
                                    self.data_refresh_cb, None)
        
        # @ do we need to add unmap with the remove handler part?

    # ---------------------------------------------------------------------
    # Open files, close files related functions
    # ---------------------------------------------------------------------
    
    def data_open_cb(self):
        """data_open_cb() - callback for Open button

        Opens new files, using Volume Viewer's open dialog box.
        Opens Volume Viewer and its OpenSave file browser.
        """

        from VolumeViewer.volumedialog import volume_dialog
        vvd = volume_dialog(create = True)
        vvd.open_cb()

        # @ Updating the data items now would not work, as the user
        #   will take time to select files in the open dialog box.
        #   So, the user has to hit the refresh button if the model
        #   is not displayed automatically by Volume Viewer.
        #
        # @ Prompt the user to hit the refresh button?

    # ---------------------------------------------------------------------
    # @ File handling is done internally via add_grid_data function,
    #   rather than via Volume Viewer. Adding the files to Volume
    #   Viewer should be done separately using the internal function:
    #   add_data_sets_volume_viewer(grid_objects)

    def data_open_dialog_cb(self):
        """data_open_dialog_cb() - callback that opens dialog
                                    box to open new files.

        File handling is done internally via add_grid_data function,
        rather than via Volume Viewer. Adding the files to Volume
        Viewer should be done separately using the internal
        function: add_data_sets_volume_viewer(grid_objects).
        """

        def open_grid_objects(grid_objects, s = self):
            s.add_grid_data(grid_objects)

        from VolumeData.opendialog import select_files
        select_files('Open Volume Data', open_grid_objects)

    # ---------------------------------------------------------------------
    # This function adds data items to main data items list, but not
    # to the Volume Viewer data sets list. To add to the Volume Viewer
    # data sets list, make a separate call using the internal function:
    # add_data_sets_volume_viewer(grid_objects)

    def add_grid_data(self, grid_objects):
        """add_grid_data(grid_objects) - add data to menu

        Input:
            grid_objects    list of VolumeData grid data objects

        Output:
            data_items      list of Data_Item items

        Get data items from open files grid, and add new ones from them.
        Then set first opened file to data menu.

        This function adds data items to main data items list, but
        not to the Volume Viewer data sets list. To add to the
        Volume Viewer data sets list, make a separate call using the
        internal function: add_data_sets_volume_viewer(grid_objects).
        """

        # find current data item on menu
        data_item = self.data_item_from_menu()
        
        # if no open objects, then set current menu item to menu again
        if len(grid_objects) == 0:
            self.data_menu_set(data_item)
            return None

        # get data items from models, and add the new ones
        import dataitem
        data_items = map(dataitem.data_item_from_data, grid_objects)
        self.add_data_items(data_items)

        # set first opened data item to menu
        for d in data_items:
            if d:
                data_item = d
                self.data_menu_set(data_item)
                return data_items

        # if no valid item, then set current menu item to menu again
        self.data_menu_set(data_item)
        return data_items

    # ---------------------------------------------------------------------
    # Add grid objects (from an open files grid) to Volume Viewer. Does
    # not really alter anything within the class. Mainly used if this
    # class opens grid objects internally, and then wants to add them
    # to Volume Viewer.

    def add_data_sets_volume_viewer(self, grid_objects):
        """add_data_sets_volume_viewer(grid_objects)

        Add data sets corresponding to grid objects, to Volume Viewer.
        """
    
        from VolumeViewer import volume_from_grid_data
        for g in grid_objects:
            volume_from_grid_data(g)

    # ---------------------------------------------------------------------
    # Refresh menu related functions
    # ---------------------------------------------------------------------
    
    def data_items_refresh_cb(self):
        """data_items_refresh_cb() - callback to refresh menu

        Callback to refresh list of data items with data regions
        in Volume Viewer and Chimera's open models list.
        """

        self.data_items_refresh()
        
    def data_items_refresh(self):
        """data_items_refresh() - refresh menu

        Refresh list of data items using data regions in
        Volume Viewer and open models in Chimera.
        """

        data_item = self.data_item_from_menu()

        self.update_data_items()
        self.update_data_regions()

        self.update_data_menu(data_item)
        
    def update_data_items(self):
        """update_data_items()

        Update data items list from data regions in Volume Viewer.
        Remove data items not in the list of data regions and add
        data items for any new data regions.
        """

        data_item_initial = self.data_item_from_menu()

        data_regions = data_regions_volume_viewer_list()

        # if no data regions and then just flush the data items list
        if (data_regions == None or len(data_regions) == 0):
            self.remove_data_items(self.data_items)
            return

        # if there are existing data items, and if they are not
        # open in data regions list, remove them
        if len(self.data_items) > 0:
            for data_item in self.data_items:
                if not find_region_volume_viewer(data_item):
                    self.remove_data_item(data_item)

        import dataitem
        
        # add any new data regions from Volume Viewer
        for data_region in data_regions:
            data = data_region.data_set.data
            data_item = dataitem.data_item_from_data(data, data_region)
            if not data_item.find_data_item_in_items(self.data_items):
                self.add_data_item(data_item)

        # set menu to initial data item after updating it or
        # to the first valid data item in list
        self.update_data_menu(data_item_initial)
                
        return

    # ---------------------------------------------------------------------
    # Add/remove data items related functions
    # ---------------------------------------------------------------------
    
    def add_data_items(self, data_items):
        """add_data_items(data_items)

        Add data items in data_items after checking for duplicates.
        """

        if (data_items == None or len(data_items) == 0):
            return
        
        for data_item in data_items:
            self.add_data_item(data_item)

        return

    def add_data_item(self, data_item):
        """add_data_item(data_item)

        Add data item if it is new.
        """

        if data_item == None:
            return

        if data_item.find_data_item_in_items(self.data_items):
            return

        self.data_items.append(data_item)
        name = data_item.full_name
        self.data_menu.add_entry(name)

        return

    def remove_data_items(self, data_items):
        """remove_data_items(data_items)

        Remove data items in data_items if in main data items list.
        """

        if (data_items == None or len(data_items) == 0):
            return

        if len(self.data_items) == 0:
            return
        
        for data_item in data_items:
            self.remove_data_item(data_item)

        return

    def remove_data_item(self, data_item):
        """remove_data_item(data_item)

        Remove data item if it is in main data items list.
        """

        if (data_item == None or len(self.data_items) == 0):
            return

        if data_item.find_data_item_in_items(self.data_items):
            index = self.data_items.index(data_item)
            self.data_menu.remove_entry(index)
            del self.data_items[index]

        return

    def update_data_regions(self):
        """update_data_regions()

        Update data regions with information indicating if the
        data region is displaed in Chimera or not. Checks
        Chimera for all open models of class Volume Viewer.
        """

        open_models = open_models_list()

        if len(self.data_items) == 0:
            return

        if (open_models == None or len(open_models) == 0):
            for data_item in self.data_items:
                data_item.remove_region()
            return

        for data_item in self.data_items:
            if data_item.region:
                if not find_model_data_region(data_item.region,
                                              open_models):
                    data_item.remove_region()
            else:
                data_region = find_region_volume_viewer(data_item)
                data_item.add_region(data_region)

        return

    # ---------------------------------------------------------------------
    # Data menu related functions
    # ---------------------------------------------------------------------
            
    def data_menu_cb(self):
        """data_menu_cb() - callback for menu

        Callback for data menu when a data item is selected.
        Uses the data item name on the data menu to get its
        properties, etc
        """

        # find current data item on menu
        data_item = self.data_item_from_menu()

        # show its size and if it is displayed
        ds = get_data_size(data_item)
        for a in range(3):
            self.data_size[a].set(ds[a])
        self.show_data_status(data_item)
        self.data_status_cb()
        
        return

    def show_data_status(self, data_item):
        """show_data_status(data_item)

        Get data item region display status and set as focus region
        if there is a region. 
        """

        self.data_shown = self.DATA_NOT_SHOWN
        self.data_region_name['text'] = ' No.'
        self.focus_region = None

        if data_item == None:
            self.data_shown = self.DATA_EMPTY
            self.data_region_name['text'] = '    '
            return

        for d in self.data_items:
            if d.find_data_item_in_items([data_item]):
                if d.region:
                    self.data_shown = self.DATA_SHOWN
                    self.data_region_name['text'] = 'Yes.'
                    self.focus_region = d.region
                    return
                    
        return

    def data_status_cb(self):
        """data_status_cb() - callback for data status change

        Callback for data status. Use to display a message,
        activate or deactivate buttons and menus.
        """

        # find current data item on menu
        data_item = self.data_item_from_menu()

        data_status = self.data_shown
        focus_region = self.focus_region

        # activate/deactivate data buttons if any

        # call dialog's data status cb
        self.data_status_dialog_cb(data_item, data_status)

        return

    def data_menu_set(self, data_item=None):
        """data_menu_set(data_item=None) - set menu to data item.
        """

        if data_item == None:
            name = ''
            self.data_menu.variable.set(name)
        else:
            name = data_item.full_name
            self.data_menu.variable.set(name)

    def update_data_menu(self, data_item=None):
        """update_data_menu(data_item=None)

        Update data menu with data item. If no input data item, set
        menu to first data item in list of data items.
        """

        if data_item != None:
            d = data_item.find_data_item_in_items(self.data_items)
        else:
            d = None
        
        if d:
            self.data_menu_set(d)
        else:
            for data_item in self.data_items:
                if data_item:
                    self.data_menu_set(data_item)
                    return

        self.data_menu_set(d)
        return

    def data_item_from_menu(self):
        """data_item_from_menu()

        Output:
            data_item
            
        Return data item from menu.
        """
        
        # find current data item on menu
        name = '%s' % (self.data_menu.variable.get())
        data_item = self.find_data_item_by_name(name)

        return data_item

    def find_data_item_by_name(self, full_name):
        """find_data_item_by_name(full_name)

        Output:
            data_item
            
        Return the data item corresponding to full_name.
        """

        if full_name == '':
            return None

        if len(self.data_items) == 0:
            return None
        
        for data_item in self.data_items:
            if data_item.full_name == full_name:
                return data_item

        return None

    # ---------------------------------------------------------------------
    # Callback function for trigger OpenModels when a new model is
    # added or removed in Chimera.
    # ---------------------------------------------------------------------

    # ---------------------------------------------------------------------
    # @ What is ideal is to trigger when data regions list in Volume
    #   Viewer is modified rather than the list of open models. By
    #   using OpenModels, we have a problem when a data region is
    #   opened in Volume Viewer and not displayed or when a unshown
    #   data region is removed from Volume Viewer.

    def data_refresh_cb(self, *triggerArgs, **kw):
        """data_refresh_cb(*triggerArgs, **kw) - callback

        Updates data display status in Segment Volume package.

        When models are opened or closed in Chimera, data display 
        status is updated.
        """
        
        if self.refresh_in_progress == 0:
            self.refresh_in_progress = 1
            if ('model list change' in triggerArgs[-1].reasons):
                self.data_items_refresh()
            self.refresh_in_progress = 0

        return None

# -------------------------------------------------------------------------

class Segment_Open_Output:
    """Class: Segment_Open_Output(dialog, parent,
                        data_status_dialog_cb) - output menu

    Input:
        dialog      dialog where menu is added
        parent
        data_status_dialog_cb
                    callback when data status changes
                    
    Output data menu for Segment Volume package.
    """

    DATA_SHOWN =     'Yes'
    DATA_NOT_SHOWN = 'No'
    DATA_EMPTY =     'NA'

    def __init__(self, dialog, parent, data_status_dialog_cb,
                 menu_label='Output '):
        """__init__(dialog, parent, data_status_dialog_cb,
                    menu_label='Output ') - output menu

        Input:
            dialog      dialog where menu is added
            parent
            data_status_dialog_cb
                    callback when data status changes
            menu_label  label for the menu (default = 'Output ')
                    
        Output data menu for Segment Volume package.
        """

        self.dialog = dialog
        self.data_status_dialog_cb = data_status_dialog_cb
        
        self.data_items = []
        self.focus_region = None # current selection
        
        self.data_shown = self.DATA_EMPTY
        
        self.refresh_in_progress = 0

        frame = Tkinter.Frame(parent)
        frame.columnconfigure(0, weight = 1)
        self.frame = frame

        # self.toplevel_widget = parent.winfo_toplevel()

        # frame data (fd)
        fd = Tkinter.Frame(frame, padx=8)
        fd.grid(row = 0, column = 0, sticky = 'nw')
        row = 0

        fdL = Tkinter.Label(fd, text = menu_label)
        fdL.grid(row = row, column = 0, sticky = 'w')

        # frame data menu (fdm)
        fdm = Hybrid.Option_Menu(fd, 'Data File : ')
        fdm.frame.grid(row = row, column = 1, columnspan=4, sticky = 'w')
        
        fdm.add_callback(self.data_menu_cb)
        self.data_menu = fdm

        # frame data size (fds)
        row = row + 1
        fdsL = Tkinter.Label(fd, text = 'Size in Pixels : ')
        fdsL.grid(row = row, column = 1, sticky = 'w')
        
        fds = Tkinter.Frame(fd)
        fds.grid(row = row, column = 2, sticky = 'w')
        
        self.data_size = []
        for a in range(3):
            size_v = Hybrid.StringVariable(fds)
            size_e = Tkinter.Entry(fds, width=5,
                                   textvariable = size_v.tk_variable)
            size_e.grid(row = 0, column = a, sticky = 'w')
            size_e['state'] = 'readonly'
            self.data_size.append(size_v)
        
        # frame data region (fdr)
        fdrL = Tkinter.Label(fd, text = 'Displayed : ')
        fdrL.grid(row = row, column = 3, sticky = 'w', padx=4)

        fdr = Tkinter.Label(fd)
        fdr.grid(row = row, column = 4, sticky = 'w')

        fdr['font'] = non_bold_font(fd)
        self.data_region_name = fdr
        
        # frame data buttons (fdb)
        row = row + 1
        fdb = Hybrid.Button_Row(fd, '',
                                (('Show', self.data_show_cb),
                                 ('Hide', self.data_hide_cb),
                                 ('Show All', self.data_show_all_cb),
                                 ('Hide All', self.data_hide_all_cb),
                                 ('Remove All', self.data_remove_all_cb)))
        fdb.frame.grid(row = row, column = 1, columnspan=4,
                       sticky = 'w', pady=4)

        self.data_show_button = fdb.buttons[0]
        self.data_hide_button = fdb.buttons[1]
        self.data_show_all_button = fdb.buttons[2]
        self.data_hide_all_button = fdb.buttons[3]

        # set trigger for OpenModels
        chimera.triggers.addHandler('OpenModels',
                                    self.data_refresh_cb, None)
        
        # @ do we need to add unmap with the remove handler part?

    # ---------------------------------------------------------------------
    # Open files, close files related functions
    # ---------------------------------------------------------------------
    
    def data_open_cb(self, filepaths):
        """data_open_cb(filepaths)

        Input:
            filepaths       list of files to be opened

        Output
            data_items      list of data items opened

        Open the files in filepaths and add to menu. This function
        is typically called when an Apply button is pressed.
        """

        data_item = self.data_item_from_menu()

        # if empty files list, then set current menu to menu again
        if len(filepaths) == 0:
            self.data_menu_set(data_item)
            return None

        # get data items from files list, and add them
        import dataitem
        data_items = map(dataitem.data_item_from_file, filepaths)
        self.add_data_items(data_items)

        # set first opened data item to menu
        for d in data_items:
            if d:
                data_item = d
                self.data_menu_set(data_item)
                return

        # if no valid item, then set current menu item to menu again
        self.data_menu_set(data_item)
        return data_items
        
    # ---------------------------------------------------------------------
    # Add/remove data items related functions
    # ---------------------------------------------------------------------
    
    def add_data_items(self, data_items):
        """add_data_items(data_items)

        Add data items in data_items to list and menu after
        checking for duplicates.
        """

        if (data_items == None or len(data_items) == 0):
            return
        
        for data_item in data_items:
            self.add_data_item(data_item)

        return

    def add_data_item(self, data_item):
        """add_data_item(data_item)

        Add data item to list and menu if it is new.
        """

        if data_item == None:
            return

        for d in self.data_items:
            if d.find_data_item_in_items([data_item]):
                return

        self.data_items.append(data_item)
        name = data_item.full_name
        self.data_menu.add_entry(name)

        return

    # ---------------------------------------------------------------------
    # Data menu refresh functions
    # ---------------------------------------------------------------------
    
    def data_items_refresh_cb(self):
        """data_items_refresh_cb() - callback to refresh menu

        Callback to refresh list of data items. Update list of
        data items with data regions in Volume Viewer and open
        models in Chimera.
        """

        self.data_items_refresh()
    
    def data_items_refresh(self):
        """data_items_refresh() - refresh menu

        Refresh data items list using open models from Chimera.
        Get data items from Chimera open volume data models, and
        check if any of regions associated with our data items
        have been closed. If any region has been removed, update
        the menu.
        """

        self.update_data_regions()

    def update_data_regions(self):
        """update_data_regions() 

        Checks if data regions associated with data items are
        still open or if they have been removed by Volume Viewer
        or Chimera.
        """

        open_models = open_models_list()

        # find current data item on menu
        data_item = self.data_item_from_menu()

        # find the region in vvd. if not found, remove region
        # set current menu item to menu again. if found, check 
        # if model open
        for d in self.data_items:
            if d.region:
                # find region in vvd
                dr = find_region_volume_viewer(d)
                if dr:
                    # region found in vvd, check if model open,
                    # if not, remove region, remove region from vvd
                    if not find_model_data_region(dr, open_models):
                        d.remove_region()
                        # if find_region_volume_viewer(d):
                        #    self.remove_region_volume_viewer(d)
                else:
                    # region not found, remove region
                    d.remove_region()

        self.data_menu_set(data_item)
        return

    # ---------------------------------------------------------------------
    # @ Not a polite thing to do.

    def remove_region_volume_viewer(self, data_item):
        """remove_region_volume_viewer(data_item)

        Remove data region in Volume Viewer corresponding to
        data item.
        """

        if data_item == None:
            return

        data_region = find_region_volume_viewer(data_item)
        if data_region:
            msg = 'Segment Volume dialog region -'
            msg = msg + '%s %s' % (dr.data_set.name, dr.name)
            msg = msg + '- ...being removed...\n'
            replyobj.info(msg)
            dr.close()
            msg = '...removed from Volume Viewer\n'
            replyobj.info(msg)

        return
        
    # ---------------------------------------------------------------------
    # Buttons related functions
    # ---------------------------------------------------------------------

    def data_remove_cb(self):
        """data_remove_cb() - callback for remove data

        Remove data item on menu after removing region from
        Volume Viewer (if any), and update the data menu to
        first entry on data menu list.
        """

        # find current data item on menu
        data_item = self.data_item_from_menu()

        # first hide the correspond region if any
        self.data_hide_cb()
        
        # delete data item from data items list and data menu list
        index = self.data_items.index(data_item)
        self.data_menu.remove_entry(index)
        del self.data_items[index]

        # update data menu to next item on data items list
        self.update_data_menu()

        return

    def data_remove_all_cb(self):
        """data_remove_all_cb() - callback for remove all data

        Remove all data items on menu after removing regions
        from Volume Viewer (if any).
        """

        # find current data item on menu
        data_item = self.data_item_from_menu()

        while len(self.data_items) > 0:
            # remove first data item
            d = self.data_items[0]
            self.data_menu_set(d)
            self.data_remove_cb()

        return

    def data_show_cb(self):
        """data_show_cb() - callback for show button
        
        Displays the data item on menu, using Volume Viewer.
        """

        # find current data item on menu
        data_item = self.data_item_from_menu()

        if data_item == None:
            self.data_items_refresh()
            return

        # check if there is a data region associated with data item
        if data_item.region == None:
            from VolumeViewer import volume_from_grid_data
            volume_from_grid_data(data_item.data)
            data_item.update_region_name()
            self.update_data_menu_entry(data_item)

        # display
        data_item.region.show()
        
        self.data_menu_set(data_item)
        return
            
    def data_hide_cb(self):
        """data_hide_cb() - callback for hide button

        Removes the data region from Volume Viewer (if any)
        corresponding to data item on menu.
        """

        # find current data item on menu
        data_item = self.data_item_from_menu()

        # check if there is a data item, and if there is a data region
        # associated with that data item
        if (data_item == None) or (data_item.region == None):
            self.data_items_refresh()
            return

        # remove from display
        data_region = data_item.region
        data_item.remove_region()
        data_region.close()

        self.data_menu_set(data_item)
        return
 
    def data_show_all_cb(self):
        """data_show_all_cb() - callback for show all button

        Displays all data items on menu, using Volume Viewer.
        """

        # find current data item on menu
        data_item = self.data_item_from_menu()

        if data_item == None:
            self.data_items_refresh()
            return

        # set each data item to menu and then call data_show_cb
        for d in self.data_items:
            self.data_menu_set(d)
            self.data_show_cb()
            
        self.data_menu_set(data_item)
        return
            
    def data_hide_all_cb(self):
        """data_hide_all_cb() - callback for hide all button

        Removes data regions from Volume Viewer (if any) 
        corresponding to all data items on menu.
        """

        # find current data item on menu
        data_item = self.data_item_from_menu()

        # set each data item to menu and then call data_hide_cb
        for d in self.data_items:
            self.data_menu_set(d)
            self.data_hide_cb()

        self.data_menu_set(data_item)
        return
 
    # ---------------------------------------------------------------------
    # Data menu related functions
    # ---------------------------------------------------------------------
            
    def data_menu_cb(self):
        """data_menu_cb() - callback for menu 

        Callback for data menu. Uses the data item name
        on the data menu to get its properties, etc
        """

        # find current data item on menu
        data_item = self.data_item_from_menu()

        # show its size and if it is displayed
        ds = get_data_size(data_item)
        for a in range(3):
            self.data_size[a].set(ds[a])
        self.show_data_status(data_item)
        self.data_status_cb()

        return

    def show_data_status(self, data_item):
        """show_data_status(data_item)

        Get data item region display status and set as focus region
        if there is a region. 
        """

        self.data_shown = self.DATA_NOT_SHOWN
        self.data_region_name['text'] = ' No.'
        self.focus_region = None

        if data_item == None:
            self.data_shown = self.DATA_EMPTY
            self.data_region_name['text'] = '    '
            return

        for d in self.data_items:
            if d.find_data_item_in_items([data_item]):
                if d.region:
                    self.data_shown = self.DATA_SHOWN
                    name = '%s %s' % (d.name, d.region.name)
                    self.data_region_name['text'] = 'Yes.'
                    self.focus_region = d.region
                    return

        return None

    def data_status_cb(self):
        """data_status_cb() - callback for data status change

        Callback for data status. Use to display a message,
        activate or deactivate buttons and menus.
        """

        # find current data item on menu
        data_item = self.data_item_from_menu()

        data_status = self.data_shown
        focus_region = self.focus_region

        # activate/deactivate data buttons
        if data_status == self.DATA_NOT_SHOWN:
            self.data_show_button['state'] = 'normal'
            self.data_hide_button['state'] = 'disabled'
        elif data_status == self.DATA_SHOWN:
            self.data_show_button['state'] = 'disabled'
            self.data_hide_button['state'] = 'normal'
        else:
            self.data_show_button['state'] = 'disabled'
            self.data_hide_button['state'] = 'disabled'

        self.data_status_dialog_cb(data_item, data_status)

        return

    def data_menu_set(self, data_item=None):
        """data_menu_set(data_item=None) - set menu to data item.
        """

        if data_item == None:
            name = ''
            self.data_menu.variable.set(name)
        else:
            name = data_item.full_name
            self.data_menu.variable.set(name)

    def update_data_menu(self, data_item=None):
        """update_data_menu(data_item=None)

        Update data menu with data item. If no input data item, set
        menu to first data item in list of data items.
        """

        if data_item != None:
            d = data_item.find_data_item_in_items(self.data_items)
        else:
            d = None
        
        if d:
            self.data_menu_set(d)
        else:
            for data_item in self.data_items:
                if data_item:
                    self.data_menu_set(data_item)
                    return

        self.data_menu_set(d)
        return

    def data_item_from_menu(self):
        """data_item_from_menu()

        Output:
            data_item

        Return data item from menu.
        """
        
        # find current data item on menu
        name = '%s' % (self.data_menu.variable.get())
        data_item = self.find_data_item_by_name(name)

        return data_item
    
    def find_data_item_by_name(self, full_name):
        """find_data_item_by_name(full_name)

        Output:
            data_item
            
        Return the data item correspond to name.
        """

        if full_name == '':
            return None

        if len(self.data_items) == 0:
            return None
        
        for data_item in self.data_items:
            if data_item.full_name == full_name:
                return data_item

        return None

    def update_data_menu_entry(self, data_item):
        """update_data_menu_entry(data_item)

        Update data menu entry name with data item's new full_name.
        """

        try:
            index = self.data_items.index(data_item)
            new_name = data_item.full_name
            self.data_menu.remove_entry(index)
            self.data_menu.insert_entry(index, new_name)
        except:
            msg = 'While updating output data menu entry name,\n' + \
                  'could not find data item in data items list!\n'
            replyobj.warning(msg)

        return

    # ---------------------------------------------------------------------
    # Callback function for trigger OpenModels when a new model is
    # added or removed in Chimera.
    # ---------------------------------------------------------------------

    # @ see note at input menu's data_refresh_cb function
    
    def data_refresh_cb(self, *triggerArgs, **kw):
        """data_refresh_cb(*triggerArgs, **kw) - callback

        Updates data display status in Segment Volume package.

        When models are opened or closed in Chimera, data display 
        status is updated.
        """
        
        if self.refresh_in_progress == 0:
            self.refresh_in_progress = 1
            if ('model list change' in triggerArgs[-1].reasons):
                self.data_items_refresh()
            self.refresh_in_progress = 0

        return None

# -------------------------------------------------------------------------
# Common functions
# -------------------------------------------------------------------------

# Font

nbfont = None
def non_bold_font(frame):

  global nbfont
  if nbfont == None:
    e = Tkinter.Entry(frame)
    nbfont = e['font']
    e.destroy()
  return nbfont

def get_data_size(data_item):
    """get_data_size(data_item) - data size strings list

    Input:
        data_item
        
    Output:
        data_size       list of strings of data size in pixels
        
    Retrun data size of data item as a list of strings. Returns
    empty strings ['', '', ''] if no data_item.
    """

    data_size = ['', '', '']
    if data_item:
        data_size = map(lambda a: '%d' % a, data_item.size)
    return data_size

def open_models_list():
    """open_models_list() - models list from Chimera.

    Output:
        open_models     VolumeViewer.surface.SurfaceModel class

    Return a list of open models in Chimera, of class
    VolumeViewer.surface.Surface_Model.
    """

    open_models = filter(lambda x:str(x.__class__) ==
                         'VolumeViewer.surface.Surface_Model',
                         chimera.openModels.list())

    return open_models

def data_regions_volume_viewer_list():
    """data_regions_volume_viewer_list()

    Output:
        data_regions        list of Volume Viewer data regions
        
    Return a list of data regions in Volume Viewer dialog, if it
    is open, else return None.
    """

    from VolumeViewer import volume_list
    return volume_list()

def find_region_volume_viewer(data_item):
    """find_region_volume_viewer(data_item)

    Return the data region in Volume Viewer corresponding to
    data item if any, else return None.

    Used in update_data_regions() and update_data_items().
    """

    if data_item == None:
        return None

    data_regions = data_regions_volume_viewer_list()
    if (data_regions == None or len(data_regions) == 0):
        return None

    for data_region in data_regions:
        if (data_region.data_set.data.path == data_item.path and
            data_region.name == data_item.region_name):
            return data_region

    return None

# -------------------------------------------------------------------------
# @ Note that Chimera release version greater than 1.2065 add an
#   extra space between data set name and data region name.
# -------------------------------------------------------------------------

def find_model_data_region(data_region, open_models):
    """find_model_data_region(data_region, open_models)

    Input:
        data_regions    VolumeViewer data regions
        open_models     VolumeViewer.surface.Surface_Model models
        
    Output:
        model
        
    Return model in open_models that corresponds to data region
    if any, else return None.
    """

    if (data_region == None) or (len(open_models) == 0):
        return None

    # @ For Chimera release version greater than 1.2065,
    #   a space is added between %s and %s in the name, i.e.,
    #   a space between data set name and data region name.

    # for newer versions
    name = '%s %s' %(data_region.data_set.data.name, data_region.name)
    # for older versions
    name2 = '%s%s' %(data_region.data_set.data.name, data_region.name)

    for model in open_models:
        if model:
            if (model.name == name or model.name == name2):
                return model

    return None

# -------------------------------------------------------------------------
