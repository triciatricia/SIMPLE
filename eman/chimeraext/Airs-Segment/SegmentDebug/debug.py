LB = '\n' # line break
TXT = ''
DBG = ''

def append_text(TXT, TXT_TMP, SB, EB):
    TXT = TXT + SB + TXT_TMP + EB
    return TXT

def prompt_message(DBG, TXT_TMP, SB, EB):
    DBG = DBG + SB + TXT_TMP + EB

    from chimera import replyobj
    replyobj.error(TXT_TMP)

    return DBG

TXT_TMP = 'Debug analysis'
DBG = append_text(DBG, TXT_TMP, LB, LB)

TXT_TMP = 'Debug log for EMAN\'s Chimera modules'
TXT = append_text(TXT, TXT_TMP, LB, LB)

TXT_TMP = 'Lavu Sridhar'
TXT = append_text(TXT, TXT_TMP, LB, LB)
DBG = append_text(DBG, TXT_TMP, LB, LB)

TXT_TMP = 'Chimera version = -%s-' % (chimera.version.version)
TXT = append_text(TXT, TXT_TMP, LB, '')
TXT_TMP = 'Chimera build   = -%s-' % (chimera.version.release)
TXT = append_text(TXT, TXT_TMP, LB, '')

import os
import sys

# check for OS platform
TXT_TMP = 'Platform = -%s-' % (sys.platform)
TXT = append_text(TXT, TXT_TMP, LB, '')
TXT_TMP = 'OS name = -%s-' % (chimera.operating_system())
TXT = append_text(TXT, TXT_TMP, LB, '')

# check for Python version
TXT_TMP = 'Python = -%s-' % (sys.version)
TXT = append_text(TXT, TXT_TMP, LB, '')

# check for current directory
TXT_TMP = 'Working dir = -%s-' % os.getcwd()
TXT = append_text(TXT, TXT_TMP, LB, '')

# check for EMANDIR environment varaible
TXT_TMP = 'Searching for EMANDIR environment variable...'
TXT = append_text(TXT, TXT_TMP, LB + LB, '')
if os.environ.has_key('EMANDIR'):
    TXT_TMP = 'EMANDIR value = -%s-' % (os.environ['EMANDIR'])
    TXT = append_text(TXT, TXT_TMP, LB, '')
else:
    TXT_TMP = 'Did not find EMANDIR environment variable!'
    TXT = append_text(TXT, TXT_TMP, LB, '')
    TXT_TMP = 'Add EMANDIR to environment variables'
    TXT = append_text(TXT, TXT_TMP, LB, '')

    DBG = prompt_message(DBG, TXT_TMP, LB, '')

# check for PYHTONPATH environment variable
TXT_TMP = 'Searching for PYTHONPATH Chimera varaible..'
TXT = append_text(TXT, TXT_TMP, LB + LB, '')
if os.environ.has_key('PYTHONPATH'):
    TXT_TMP = 'Default PYTHONPATH in Chimera = -%s-' % (os.environ['PYTHONPATH'])
    TXT = append_text(TXT,TXT_TMP, LB, '')
else:
    TXT_TMP = 'PYHTONPATH not found in Chimera'
    TXT = append_text(TXT,TXT_TMP, LB, '')
    
    # DBG = prompt_message(DBG, TXT_TMP, LB, '')

# first try to import EMAN
TXT_TMP = 'First attempt to import EMAN...'
TXT = append_text(TXT, TXT_TMP, LB + LB, '')
try:
    import EMAN
    TXT_TMP = 'EMAN import successfful'
    TXT = append_text(TXT, TXT_TMP, LB, '')
        
except:
    TXT_TMP = 'EMAN import failed...'
    TXT = append_text(TXT, TXT_TMP, LB, '')

    # adding EMAN lib to PYHTONPATH
    TXT_TMP = 'Adding EMAN lib to PYTHONPATH ...'
    TXT = append_text(TXT, TXT_TMP, LB + LB, LB)
    if os.environ.has_key('EMANDIR'):
        # add directory (EMAN lib) to python path
        emandir = os.environ['EMANDIR']
        emanpy = os.path.join(emandir, 'lib')
        if sys.platform == 'win32':
            sep = ';' # Windows separator
        else:
            sep = ':' # Unix separator

        if (os.environ.has_key('PYTHONPATH') and
            os.environ['PYTHONPATH'] != ''):
            pypath = os.environ['PYTHONPATH'] + sep + emanpy
            TXT_TMP = '...Adding ENAN lib = -%s- ' % (emanpy)
            TXT = append_text(TXT, TXT_TMP, LB, '')
            TXT_TMP = '...to PYTHONPATH in Chimera = -%s-' % (os.environ['PYTHONPATH'])
            TXT = append_text(TXT, TXT_TMP, LB, '')
        else:
            pypath = emanpy
            TXT_TMP = '...Setting PYTHONPATH in Chimera'
            TXT = append_text(TXT, TXT_TMP, LB, '')
            TXT_TMP = '...to ENAN lib = -%s- ' % (emanpy)
            TXT = append_text(TXT, TXT_TMP, LB, '')
        os.environ['PYTHONPATH'] = pypath
        sys.path.append(emanpy)
        TXT_TMP = 'Final PYTHONPATH in Chimera = -%s-' % (os.environ['PYTHONPATH'])
        TXT = append_text(TXT, TXT_TMP, LB, '')

    else:
        TXT_TMP = 'EMANDIR enviroment variable not found!'
        TMP = append_text(TXT, TXT_TMP, LB, '')
        
        TXT_TMP = 'Add EMANDIR environment variable!\n'
        TMP = append_text(TXT, TXT_TMP, LB, '')

        DBG = prompt_message(DBG, TXT_TMP, LB, '')

# second try to import EMAN
TXT_TMP = 'Second attempt to import EMAN...'
TXT = append_text(TXT, TXT_TMP, LB + LB, '')
try:
    import EMAN
    TXT_TMP = 'EMAN import succefful'
    TXT = append_text(TXT, TXT_TMP, LB, '')

except:
    TXT_TMP = 'EMAN import failed!'
    TXT = append_text(TXT, TXT_TMP, LB, '')

    DBG = prompt_message(DBG, TXT_TMP, LB, '')

# check if Segment modules can be imported
TXT_TMP = 'Try to import Segment modules...'
TXT = append_text(TXT, TXT_TMP, LB + LB, '')
try:
    import SegmentMask
    TXT_TMP = 'module import successful'
    TXT = append_text(TXT, TXT_TMP, LB, '')
    
except:
    TXT_TMP = 'module import failed!'
    TXT = append_text(TXT, TXT_TMP, LB, '')

    import sys
    TXT_TMP = 'System path = -%s-' % (sys.path)
    TXT = append_text(TXT, TXT_TMP, LB, '')
    
    TXT_TMP = 'add Segment directory to Chimera Tools path'
    TXT = append_text(TXT, TXT_TMP, LB, '')

    DBG = prompt_message(DBG, TXT_TMP, LB, '')

# try import 1st sample program
TXT_TMP = 'Try to import sample program (maskmain)...'
TXT = append_text(TXT, TXT_TMP, LB + LB, '')
try:
    from SegmentMask import maskmain
    TXT_TMP = 'maskmain import successful!'
    TXT = append_text(TXT, TXT_TMP, LB, '')

except:
    TXT_TMP = 'maskmain import failed!'
    TXT = append_text(TXT, TXT_TMP, LB, '')

    DBG = prompt_message(DBG, TXT_TMP, LB, '')
    
# try import 2nd sample program
TXT_TMP = 'Try to import sample program (maskedit)...'
TXT = append_text(TXT, TXT_TMP, LB + LB, '')
try:
    from SegmentMask import maskedit
    TXT_TMP = 'maskedit import successful!'
    TXT = append_text(TXT, TXT_TMP, LB, '')

except:
    TXT_TMP = 'maskedit import failed!'
    TXT = append_text(TXT, TXT_TMP, LB, '')

    DBG = prompt_message(DBG, TXT_TMP, LB, '')

# try opening sample dialog (mask dialog - mg)
TXT_TMP = 'Attempting to display dialog...'
TXT = append_text(TXT, TXT_TMP, LB + LB, '')
try:
    mg = maskmain.seg_mask_dialog(1)
    TXT_TMP = 'mask dialog open successful!'
    TXT = append_text(TXT, TXT_TMP, LB, '')

except:
    TXT_TMP = 'mask dialog open failed!'
    TXT = append_text(TXT, TXT_TMP, LB, '')

    DBG = prompt_message(DBG, TXT_TMP, LB, '')

# create some dummy mask data:
TXT_TMP = 'Attempting to create dummy data...'
TXT = append_text(TXT, TXT_TMP, LB + LB, '')
# data 64x64x64 with cube 20x20x20
mask_dir = os.getcwd()
mask_files = ['debugTestFile.mrc',]
mask_file = mask_files[0]

mst = mg.mask_type_choices[0]   # cube
p0, p1, p2 = [20,20,20]         # size 20
mask_path = os.path.join(mask_dir, mask_file)
mask_origin = (0.,0.,0.)        # data origin
mask_size = (64,64,64)          # data size
mask_step = (1.,1.,1.)          # ang per pix
talign = (0.,0.,0.)             # translate
ralign = (0.,0.,0.)             # rotate (EMAN Euler)
radial = 0                      # step function

msg = maskedit.create_mask(mst, p0,p1,p2, mask_path,
                           mask_origin, mask_size, mask_step,
                           talign, ralign, radial)

TXT_TMP = msg
TXT = append_text(TXT, TXT_TMP, LB, '')

# check if dummy data created
TXT_TMP = 'Checking for mask output file...'
TXT = append_text(TXT, TXT_TMP, LB + LB, '')
try:
    os.path.isfile(mask_path)
    TXT_TMP = 'mask output file found'
    TXT = append_text(TXT, TXT_TMP, LB, '')

except:
    TXT_TMP = 'mask out file missing!'
    TXT = append_text(TXT, TXT_TMP, LB, '')

    DBG = prompt_message(DBG, TXT_TMP, LB, '')

# open dummy data with Chiemra
TXT_TMP = 'Attempt to open file with Chimera...'
TXT = append_text(TXT, TXT_TMP, LB + LB, '')
try:
    cms = chimera.openModels.open(mask_path)
    TXT_TMP = 'mask output file opened'
    TXT = append_text(TXT, TXT_TMP, LB, '')

except:
    TXT_TMP = 'file unreadable or missing!'
    TXT = append_text(TXT, TXT_TMP, LB, '')

    DBG = prompt_message(DBG, TXT_TMP, LB, '')

# open dummy data with dialog
TXT_TMP = 'Attempt to open file with dialog...'
TXT = append_text(TXT, TXT_TMP, LB + LB, '')
try:
    mg.open_output_data_items(mask_dir, mask_files)
    TXT_TMP = 'mask output file opened'
    TXT = append_text(TXT, TXT_TMP, LB, '')

except:
    TXT_TMP = 'mask out file unreadable or error!'
    TXT = append_text(TXT, TXT_TMP, LB, '')

    DBG = prompt_message(DBG, TXT_TMP, LB, '')

# show dummy data
TXT_TMP = 'Attempt to display data from dialog...'
TXT = append_text(TXT, TXT_TMP, LB + LB, '')
try:
    mg.output_panel.data_show_cb()
    TXT_TMP = 'mask file display successful'
    TXT = append_text(TXT, TXT_TMP, LB, '')

except:
    TXT_TMP = 'mask file display failed!'
    TXT = append_text(TXT, TXT_TMP, LB, '')

    DBG = prompt_message(DBG, TXT_TMP, LB, '')

TXT_TMP = LB + '-'*30 + LB + LB + \
          'Do you see a 20x20x20 mask cube at the ' + LB + \
          'center of a 64x64x64 data file?' + LB + '-'*30 + LB

print TXT_TMP
          
TXT_TMP = 'If you check Model Panel under Favorites menu ' + LB + \
          'Chimera, there should be 2 models with file ' + LB + \
          'name debugTestFile.mrc' + LB + '-'*30 + LB

print TXT_TMP

TXT_TMP = 'If NOT, pleae type "print TXT" and send us ' + LB + \
          'the output along with any other error messages' + LB + \
          '-'*30 + LB

print TXT_TMP

