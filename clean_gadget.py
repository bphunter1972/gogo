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

        gvars.Log.info("Cleaning...")
        for dname in gvars.Vars['CLEAN_DIRS']:
            try:
                rmtree(dname)
                Log.info("Removed dir %s" % dname)
            except:
                pass

        for fname in gvars.Vars['CLEAN_FILES']:
            try:
                os.remove(fname)
                Log.info("Removed file %s" % fname)
            except:
                pass

