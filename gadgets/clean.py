"""
Cleans a testbench tree.
"""

import gadget
import gvars
from shutil import rmtree
import os

Log = gvars.Log

class CleanGadget(gadget.Gadget):
    """Clean up!"""

    #--------------------------------------------
    def __init__(self):
        super(CleanGadget, self).__init__()

        self.schedule_phase = 'clean'
        clean_dirs = gvars.PROJ.CLEAN_DIRS + [gvars.GogoDir]

        gvars.Log.info("Cleaning...")
        for dname in clean_dirs:
            Log.debug("Removing...%s" % dname)
            try:
                rmtree(dname)
                Log.info("Removed dir %s" % dname)
            except:
                pass

        for fname in gvars.PROJ.CLEAN_FILES:
            Log.debug("Removing...%s" % fname)
            try:
                os.remove(fname)
                Log.info("Removed file %s" % fname)
            except:
                pass

