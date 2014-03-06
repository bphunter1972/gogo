"""
Calls build.pl. 
Currently, this is over-simplistic and needs to actually take over what build.pl does.
Also, it's not working yet, so don't run this gadget.
"""

import gadget
import gvars
import os

Log = gvars.Log

class BuildGadget(gadget.Gadget):

    #--------------------------------------------
    def __init__(self):
        super(BuildGadget, self).__init__()

        self.schedule_phase = 'build'

        self.name = 'build'
        self.queue = 'build'
        self.interactive = True

        # create a symbolic link called 'project'. 
        try:
            os.symlink('../..', 'project')
        except OSError:
            pass

        # add the CSR gadget to pre_build phase
        import gadgets.csr_build
        import schedule
        schedule.add_gadget(gadgets.csr_build.CsrBuildGadget())

    #--------------------------------------------
    def create_cmds(self):
        """
        Just run build.pl for now.        
        """

        cmd_line = "build.pl -libdir=lib -initlocal -bsubblds -blddep -64bit -sim=VCS"
        return gadget.GadgetCommand(command=cmd_line, comment="Running build.pl")
