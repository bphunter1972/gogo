"Launches all of the vkits during the vkit phase"

import gadget
import schedule
import gvars

Log = gvars.Log

class GenipGadget(gadget.Gadget):
    """Runs vlogan/vcs on a particular vkit"""
    def __init__(self):
        super(GenipGadget, self).__init__()

        self.name = 'genip'
        self.schedule_phase = 'genip'

        for vkit in gvars.Vkits:
            Log.info("genip adding %s" % vkit.name)
            schedule.add_gadget(vkit)
            
    #--------------------------------------------
    def create_cmds(self):
        return None
        

