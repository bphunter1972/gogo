"""
A gadget that runs simrpt during post_simulate phase
"""

import gadget
import sys

class SimrptGadget(gadget.Gadget):
    """
    """

    #--------------------------------------------
    def __init__(self, sim_dir):
        super(SimrptGadget, self).__init__()

        self.schedule_phase = 'post_simulate'
        self.name = 'simrpt'
        self.runLocally = True
        self.sim_dir = sim_dir

        self.stdoutPath = sys.stdout
        self.mergeStderr = True

    #--------------------------------------------
    def create_cmds(self):
        self.turds.append('.simrpt.stdout')
        return ['simrpt %s/logfile' % self.sim_dir]
