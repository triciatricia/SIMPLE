# -------------------------------------------------------------------------
# SegmentMenu/dataitem.py
#
# Segment Volume package - Segment Menu module
# 
# Author:
#       Lavu Sridhar, Baylor College of Medicine (BCM)
#
# Revisions:
#       2004.12.15: Lavu Sridhar, BCM
#       2005.02.15: Lavu Sridhar, BCM
#       2005.09.06: Lavu Sridhar, BCM (VU 1.2129 Chimera)
#
# To Do:
#       See comments marked with # @
# 
# Key:
#       VU: Version Upgrade
#
"""Data Item used in Segment Volume package.
"""

# -------------------------------------------------------------------------

class Data_Item:
    """Class: Data_Item(volume_data, volume_viewer_data_region=None)

    Input:
        data            VolumeData grid data object
        data_region     VolumeViewer data region

    Stores information in Segment Volume dialogs about
    a volume data entry.
    """

    def __init__(self, data, data_region=None):
        """__init__(data, data_region=None)

        Input:
            data            VolumeData grid data object
            data_region     VolumeViewer data region
        """

        self.data = data
        self.name = data.name
        self.size = data.size
        self.path = data.path
        #VU 1.2129 - added origin and step
        self.origin = self.get_origin_from_data(data)
        self.step = self.get_step_from_data(data)
        self.region = None
        if data_region:
            self.region_name = data_region.name
        else:
            self.region_name = ''
        self.full_name = '%s %s' % (self.data.name, self.region_name)

    # ---------------------------------------------------------------------

    def find_data_item_in_items(self, data_items):
        """find_data_item_in_items(data_items)

        Input:
            data_items      list of data items to search in

        Output
            d               data item found in list that matches
            
        Searches for current data item in data items list by matching
        data item path and data item region name. Returns the data
        item that matches. If no match found, returns None.
        """

        if len(data_items) == 0:
            return None
    
        for d in data_items:
            if (d.path == self.path and
                d.region_name == self.region_name):
                return d

        return None

    # ---------------------------------------------------------------------
    # Data region functions
    # ---------------------------------------------------------------------

    def add_region(self, data_region):
        """add_region(data_region) - add/reset region

        Input:
            data_region     VolumeViewer data region

        Add/reset region of current data item to data_region.
        """

        self.region = data_region
        return
    
    def remove_region(self):
        """remove_region() - remove region

        Remove region of current data items.
        """

        self.region = None
        return

    def update_region_name(self):
        """update_region_name() - update region name

        Update region_name and full_name of current data item
        using the data set name and the current region_name...
        full_name = '%s %s' % (self.data.name, self.region_name).
        """

        if self.region == None:
            self.region_name = ''
        else:
            self.region_name = self.region.name
            
        self.full_name = '%s %s' % (self.data.name, self.region_name)
        return

    def get_origin_from_data(self, data):
        """get_origin_from_data(data)

        Input:
            data        VolumeData grid data object

        Output:
            origin      xyz origin for data
            
        Return origin of data. If no input data
        is given, returns None.
        """

        if data == None:
            return None

        # @ For Chimera release version greater than 1.2129,
        #   xyz origin is data.origin() where as for older
        #   versions, it is data.xyz_origin().
        
        try:
            # for newer versions
            origin = data.origin
        except:
            # for older versions
            origin = data.xyz_origin
            
        return origin
  
    def get_step_from_data(self, data):
        """get_step_from_data(data)

        Input:
            data        VolumeData grid data object

        Output:
            step        xyz step for data
            
        Return step size of data. If no input data
        is given, returns None.
        """

        if data == None:
            return None

        # @ For Chimera release version greater than 1.2129,
        #   xyz step is data.step() where as for older
        #   versions, it is data.xyz_step().
        
        try:
            # for newer versions
            step = data.step
        except:
            # for older versions
            step = data.xyz_step
            
        return step
  
# -------------------------------------------------------------------------
# Data item related functions
# -------------------------------------------------------------------------

def data_item_from_file(outfile):
    """data_item_from_file(outfile)

    Input:
        outfile     file to be read

    Output:
        data_item   Data_Item for data in outfile
        
    Create and return a Data_Item from outfile. If no input file,
    returns None.
    """
        
    if outfile == None:
        return None

    from VolumeData import fileformats
    data = fileformats.open_file(outfile)[0]
    data_item = data_item_from_data(data)
        
    return data_item

def data_item_from_data(data, data_region=None):
    """data_item_from_data(data, data_region=None)

    Input:
        data            VolumeData grid data object
        data_region     VolumeViewer data region

    Output:
        data_item       Data_Item for data in data
        
    Create and return a Data_Item from a open file grid object
    or data, and a Volume Viewer data region if available. If
    no input data is given, returns None.
    """

    if data == None:
        return None

    data_item = Data_Item(data, data_region)
    return data_item

# ---------------------------------------------------------------------
