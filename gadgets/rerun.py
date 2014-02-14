"Creates the rerun/qrun scripts after simulation completes"

from __future__ import print_function

import gadget
import os
import gvars

Log = gvars.Log

class RerunGadget(gadget.Gadget):
    """Creates rerun/qrun scripts after sim completes"""
    def __init__(self, sim_dir):
        super(RerunGadget, self).__init__()
        self.sim_dir = sim_dir
        self.schedule_phase = 'pre_simulate'

    #--------------------------------------------
    def make_script(self, name, cmd_line):
        with open(name, 'w') as sfile:
            print("#!/usr/bin/env csh", file=sfile)
            print("", file=sfile)
            print(cmd_line + " $*", file=sfile)
            print("", file=sfile)
        os.chmod(name, 0o777)

    #--------------------------------------------
    def create_cmds(self):
        r_name = os.path.join(self.sim_dir, 'rerun')
        q_name = os.path.join(self.sim_dir, 'qrun')

        cmd_line = "gogo sim" #% (gvars.SIM.TEST, gvars.SIM.SEED)
        cmd_args = list(set(['TEST=%s' % gvars.SIM.TEST, 'SEED=%d' % gvars.SIM.SEED] + gvars.CommandLineVariables))
        cmd_line += " %s" % ' '.join(cmd_args)

        # create qrun script
        self.make_script(q_name, cmd_line)

        # add debug & waves to create rerun script
        wave = gvars.SIM.WAVE if gvars.SIM.WAVE else 'fsdb'
        cmd_line += " DBG=UVM_HIGH WAVE=%(wave)s" % locals()
        self.make_script(r_name, cmd_line)

        # there is nothing to spawn off from this gadget
        return []
