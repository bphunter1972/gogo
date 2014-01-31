"""
A gadget that calls build.pl.
Currently, this is over-simplistic and needs to actually take over what build.pl does.
Also, it's not working yet.
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

    #--------------------------------------------
    def create_cmds(self):
        """
        Just run build.pl for now.        
        """

        cmd_line = "build.pl -libdir=lib -initlocal -bsubblds -blddep -64bit -sim=VCS"
        return [cmd_line]
