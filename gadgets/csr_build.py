"Runs csr3 during pre_build phase."

import gadget
import gvars
from utils import get_filename
from pymake import pymake
import os.path

Log = gvars.Log

class CsrBuildGadget(gadget.Gadget):

    #--------------------------------------------
    def __init__(self):
        super(CsrBuildGadget, self).__init__()

        self.schedule_phase = 'pre_build'
        self.name = 'csr3'
        self.queue = 'build'
        self.interactive = False
        dir = os.path.join(gvars.RootDir, "verif/vkits/csr")
        self.stdoutPath = get_filename(os.path.join(dir, '.csr3_stdout'))
        self.mergeStderr = True
        self.done_file = get_filename(os.path.join(dir, ".csr3_done"))

    #--------------------------------------------
    def create_cmds(self):
        """
        Run csr3 verif

        TODO: This is an *extremely over-simplified* version of what regs/Makefile does. 
        """

        cmd_line = "csr3 verif"
        return [("Running csr3", cmd_line)]

    #--------------------------------------------
    def check_dependencies(self):
        "Returns True if .csr3_done happened before any of the target CSR files"

        pymake.Log = Log
        answer = pymake(self.done_file, gvars.TB.CSR_FILES, get_cause=True)

        return answer.result

    #--------------------------------------------
    def completedCallback(self):
        exit_status = self.getExitStatus()
        if exit_status == 0:
            f = open(self.done_file, "w")
            f.close()
        else:
            Log.error("csr3 Failure. See %s" % self.stdoutPath)
            raise gadget.GadgetFailed("csr3")
