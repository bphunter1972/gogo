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

        cmd_line = "gogo vlog sim TEST=%s SEED=%d" % (gvars.SIM.TEST, gvars.SIM.SEED)
        if gvars.SIM.DIR != gvars.SIM.TEST:
            cmd_line += " DIR=%s" % gvars.SIM.DIR
        extras = (('WDOG', gvars.SIM.WDOG), ('TOPO', gvars.SIM.TOPO)) 
        # These are TODO: ('OPTS', gvars.SIM.OPTS), ('PLUSARGS', gvars.SIM.PLUSARGS), 
        for extra in extras:
            if extra[1]:
                cmd_line += " %s=%s" % extra

        # create qrun script
        self.make_script(q_name, cmd_line)

        # add debug & waves to create rerun script
        wave = gvars.SIM.WAVE if gvars.SIM.WAVE else 'fsdb'
        cmd_line += " DBG=UVM_HIGH WAVE=%(wave)s" % locals()
        self.make_script(r_name, cmd_line)

        # there is nothing to spawn off from this gadget
        return []
