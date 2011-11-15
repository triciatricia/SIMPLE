# general modules

import os
import Tkinter
import Pmw

# chimera related modules

import chimera
from chimera.baseDialog import ModelessDialog

class AIRS_Dialog(ModelessDialog):

    title='AIRS'
    name = 'AIRS'
    buttons = ('Close',)

    # help = 'ContributedSoftware/Airs/airs.html'
    dir_pkg = os.path.dirname(__file__)
    help_path = os.path.join(dir_pkg, 'airs.html')
    help_url = 'file://' + help_path
    help = help_url

    # ---------------------------------------------------------------------
    # Fill in UI
    # ---------------------------------------------------------------------
    
    def fillInUI(self, parent):
        """fillInUI(parnet)
        """

        row = 0

        # airs frame
	af = Tkinter.Frame(parent, bd=2, padx=5, pady=10, relief='flat')
	af.grid(row=row, column=0, sticky='ew')

	# airs button
##	afb = Tkinter.Button(af, text="   AIRS   ",
##                             font=('Tempus Sans ITC', '36', 'bold'),
##                             background='black', foreground='white',
##                             activebackground='black',
##                             activeforeground='red',
##                             command=self.airs_info)
##	afb.grid(row=0, column=0, sticky='ew')

        # airs icon
        from chimera import chimage
        import os.path
        thisfile = os.path.abspath(__file__)
        thisdir  = os.path.dirname(thisfile)
        icon = chimage.get(os.path.join(thisdir, 'airs-small.gif'),parent)

        row = row + 1
        afi = Tkinter.Label(parent, image=icon, borderwidth=10)
        afi.__image = icon
        afi.grid(row=1, column=0, sticky='ew')
        
        # notebooks frame
        row = row + 1        
        nbf = Tkinter.Frame(parent)
        nbf.grid(row=row, column=0, sticky='nw')
        
        nb = Pmw.NoteBook(nbf)
        nb.pack(expand=1, fill=Tkinter.BOTH)
        self.notebook = nb
        
        nb.add('filters', tab_text='Filters')
        self.filtersFrame = nb.page('filters')

        nb.add('docking', tab_text='Docking')
        self.dockingFrame = nb.page('docking')

        nb.add('analysis', tab_text='Analysis')
        self.analysisFrame = nb.page('analysis')

        nb.add('segment', tab_text = 'Segment')
        self.segmentFrame = nb.page('segment')

        nb.add('segmisc', tab_text = 'Segment Misc')
        self.segmentMiscFrame = nb.page('segmisc')

        nb.add('misc', tab_text='Misc.')
        self.miscFrame = nb.page('misc')
        
        # filters page

        fp = Tkinter.Frame(self.filtersFrame)
        fp.pack(side=Tkinter.TOP, fill=Tkinter.X, expand=1)

        rowfp = 0
        fpfilter = Tkinter.Button(fp, text='EMAN Filters',
                                  command=self.filters_dialog)
        fpfilter.grid(row=rowfp,column=0,sticky='nsew')

        # segment page

        sp = Tkinter.Frame(self.segmentFrame)
        sp.pack(side=Tkinter.TOP, fill=Tkinter.X, expand=1)

        rowsp = 0
        spsimple = Tkinter.Button(sp, text='Segment Simple',
                                  command=self.seg_simple_dialog)
        spsimple.grid(row=rowsp,column=0,sticky='nsew')

        rowsp = rowsp + 1
        spmarker = Tkinter.Button(sp, text='Segment Markers',
                                  command=self.seg_marker_dialog)
        spmarker.grid(row=rowsp,column=0,sticky='nsew')

        rowsp = rowsp + 1
        spmask = Tkinter.Button(sp, text='Segment Mask',
                                command=self.seg_mask_dialog)
        spmask.grid(row=rowsp,column=0,sticky='nsew')
        
        rowsp = rowsp + 1
        spread = Tkinter.Button(sp, text='Segment Read',
                                command=self.seg_read_dialog)
        spread.grid(row=rowsp,column=0,sticky='nsew')
        
        rowsp = rowsp + 1
        spwrite = Tkinter.Button(sp, text='Segment Write',
                                 command=self.seg_write_dialog)
        spwrite.grid(row=rowsp,column=0,sticky='nsew')
        
        # segment misc page

        smp = Tkinter.Frame(self.segmentMiscFrame)
        smp.pack(side=Tkinter.TOP, fill=Tkinter.X, expand=1)

        rowsmp = 0
        smpmeasurestick = Tkinter.Button(smp, text='Measure Stick',
                                command=self.measure_stick_dialog)
        smpmeasurestick.grid(row=rowsmp,column=0,sticky='nsew')


        rowsmp = rowsmp + 1
        smptrackxf = Tkinter.Button(smp, text='Segment Track',
                                command=self.track_xform_dialog)
        smptrackxf.grid(row=rowsmp,column=0,sticky='nsew')

        # docking page

        dp = Tkinter.Frame(self.dockingFrame)
        dp.pack(side=Tkinter.TOP, fill=Tkinter.X, expand=1)

        rowdp = 0
        dpfh = Tkinter.Button(dp, text='Foldhunter',
                              command=self.foldhunter_dialog)
        dpfh.grid(row=rowdp,column=0,sticky='nsew')

        rowdp = rowdp + 1
        dpffh = Tkinter.Button(dp, text='Flexible Foldhunter',
                               command=self.flex_foldhunter_dialog)
        dpffh.grid(row=rowdp,column=0,sticky='nsew')

        rowdp = rowdp + 1
        dpmanual = Tkinter.Button(dp, text='Manual Docking',
                                  command=self.dock_manual_dialog)
        dpmanual.grid(row=rowdp,column=0,sticky='nsew')

        # analysis page

        ap = Tkinter.Frame(self.analysisFrame)
        ap.pack(side=Tkinter.TOP, fill=Tkinter.X, expand=1)

        rowap = 0
        aphh = Tkinter.Button(ap, text='Classic Helixhunter',
                              command=self.helixhunter_dialog)
        aphh.grid(row=rowap,column=0,sticky='nsew')

        rowap = rowap + 1
        apsseh = Tkinter.Button(ap, text='SSE Hunter',
                                command=self.ssehunter_dialog)
        apsseh.grid(row=rowap,column=0,sticky='nsew')

        rowap = rowap + 1
        apsseb = Tkinter.Button(ap, text='SSE Builder',
                                command=self.ssebuilder_dialog)
        apsseb.grid(row=rowap,column=0,sticky='nsew')

        # misc. page

        mp = Tkinter.Frame(self.miscFrame)
        mp.pack(side=Tkinter.TOP, fill=Tkinter.X, expand=1)

        rowmp = 0
        mpmodeview = Tkinter.Button(mp, text='Mode Viewer',
                                    command=self.modeviewer_dialog)
        mpmodeview.grid(row=rowmp,column=0,sticky='nsew')

        rowmp = rowmp + 1
        mprt = Tkinter.Button(mp, text='Rotate n Translate',
                              command=self.rot_trans_dialog)
        mprt.grid(row=rowmp,column=0,sticky='nsew')

##        rowmp = rowmp + 1
##        mpskeleton = Tkinter.Button(mp, text='Skeleton',
##                                    command=self.skeleton_dialog)
##        mpskeleton.grid(row=rowmp,column=0,sticky='nsew')

        rowmp = rowmp + 1
        mppdb2mrc = Tkinter.Button(mp, text='PDB to MRC',
                                   command=self.pdb2mrc_dialog)
        mppdb2mrc.grid(row=rowmp,column=0,sticky='nsew')

        rowmp = rowmp + 1
        mpcmm2pdb = Tkinter.Button(mp, text='CMM to PDB',
                                   command=self.cmm2pdb_dialog)
        mpcmm2pdb.grid(row=rowmp,column=0,sticky='nsew')

        rowmp = rowmp + 1
        mppdb2cmm = Tkinter.Button(mp, text='PDB to CMM',
                                   command=self.pdb2cmm_dialog)
        mppdb2cmm.grid(row=rowmp,column=0,sticky='nsew')

        # self.notebook.setnaturalsize()

    # ---------------------------------------------------------------------
    # General Page buttons
    # ---------------------------------------------------------------------

    def airs_info(self):

        print 'AIRS' #>
        
    # ---------------------------------------------------------------------
    # Filter Page buttons
    # ---------------------------------------------------------------------
    
    def filters_dialog(self):

        import Airs.filters
        Airs.filters.gui()

    # ---------------------------------------------------------------------
    # Segment Page buttons
    # ---------------------------------------------------------------------
    
    def seg_simple_dialog(self):

        import SegmentSimple.simple
        SegmentSimple.simple.show_seg_simple_dialog()
        
    def seg_marker_dialog(self):

        import SegmentSimple.marker
        SegmentSimple.marker.show_seg_marker_dialog()
        
    def seg_mask_dialog(self):

        import SegmentMask.maskmain
        SegmentMask.maskmain.show_seg_mask_dialog()

    def seg_read_dialog(self):

        import SegmentRead
        SegmentRead.show_seg_read_dialog()
        
    def seg_write_dialog(self):

        import SegmentWrite
        SegmentWrite.show_seg_write_dialog()
        
    # ---------------------------------------------------------------------
    # Segment Misc Page buttons
    # ---------------------------------------------------------------------
    
    def measure_stick_dialog(self):

        import MeasureStick
        MeasureStick.show_simple_distance_dialog()
        
    def track_xform_dialog(self):

        import SegmentTrack.trackxform
        SegmentTrack.trackxform.show_track_xform_dialog()

    # ---------------------------------------------------------------------
    # Docking Page buttons
    # ---------------------------------------------------------------------
    
    def foldhunter_dialog(self):

        import Airs.fhc
        Airs.fhc.gui()

    def flex_foldhunter_dialog(self):

        import Airs.flexible
        Airs.flexible.gui()

    def dock_manual_dialog(self):

        import DockManual.dockmanual
        DockManual.dockmanual.dock_manual_dialog(create=1)

    # ---------------------------------------------------------------------
    # Analysis Page buttons
    # ---------------------------------------------------------------------
    
    def helixhunter_dialog(self):

        import Airs.hhc
        Airs.hhc.gui()

    def ssehunter_dialog(self):

        import Airs.ssc
        Airs.ssc.gui()

    def ssebuilder_dialog(self):

        import Airs.ssebuilder
        Airs.ssebuilder.gui()

    # ---------------------------------------------------------------------
    # Misc. Page buttons
    # ---------------------------------------------------------------------
    
    def modeviewer_dialog(self):

        import Airs.modeviewer
        Airs.modeviewer.gui()
        
    def rot_trans_dialog(self):

        import Airs.rt
        Airs.rt.gui()
        
    def skeleton_dialog(self):

        import Airs.ssesk
        Airs.ssesk.gui()
        
    def pdb2mrc_dialog(self):

        import Airs.pdb2mrc
        Airs.pdb2mrc.gui()
        
    def cmm2pdb_dialog(self):

        import Airs.c2p
        Airs.c2p.gui()
        
    def pdb2cmm_dialog(self):

        import Airs.p2c
        Airs.p2c.gui()
        
# -------------------------------------------------------------------------
# Main dialog
# -------------------------------------------------------------------------

def airs_dialog(create=0):
    """airs_dialog(create=0) - look for AIRS dialog.

    If create = 1, then creates a new dialog if dialog does not exist.
    """
    
    from chimera import dialogs
    return dialogs.find(AIRS_Dialog.name, create=create)

def show_airs_dialog():
    """show_airs_dialog() - shows the AIRS dialog.
    """
    
    from chimera import dialogs
    return dialogs.display(AIRS_Dialog.name)

# -------------------------------------------------------------------------
# Register dialog with Chimera.
# -------------------------------------------------------------------------
 
from chimera import dialogs
dialogs.register(AIRS_Dialog.name,AIRS_Dialog,replace=1)

# -------------------------------------------------------------------------
