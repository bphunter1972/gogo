"Prints out the latest source file that may cause a compile."

import gadget
import pymake
import utils
import gvars

Log = gvars.Log

class LatestGadget(gadget.Gadget):
    def __init__(self):
        super(LatestGadget, self).__init__()

        self.schedule_phase = 'pre_clean'

        srcs = utils.get_all_sources() 
        answer = pymake.get_extreme_mtime(srcs, old=False, get_file=True)
        Log.info("Latest source is %s" % answer[1])

    def genCmdLine(self):
        return []
