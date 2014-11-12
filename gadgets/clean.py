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

        clean_files = gvars.PROJ.CLEAN_FILES
        clean_dirs = gvars.PROJ.CLEAN_DIRS + [gvars.GogoDir]

        for vkit in gvars.Vkits:
            dirs,files = vkit.cleanup()
            clean_dirs += dirs
            clean_files += files

        gvars.Log.info("Cleaning...")
        for dname in clean_dirs:
            try:
                rmtree(dname)
                Log.info("Removed dir %s" % dname)
            except:
                pass


        for fname in clean_files:
            try:
                os.remove(fname)
                Log.info("Removed file %s" % fname)
            except:
                pass


