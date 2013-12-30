"""
A gadget that removes all turd files from other gadgets.
"""

import gadget
import os
import gvars

Log = gvars.Log

class FlushGadget(gadget.Gadget):

    #--------------------------------------------
    def __init__(self):
        super(FlushGadget, self).__init__()

        self.schedule_phase = 'final_cleanup'

    #--------------------------------------------
    def prepare(self):
        import schedule

        all_turds = []

        # collect all turds from scheduled gadgets
        for gadget in schedule.Gadgets:
                all_turds.extend(gadget.turds)

        # remove all turds
        for turd in all_turds:
            Log.debug("Removing turd: '%s'" % turd)
            os.remove(turd)





