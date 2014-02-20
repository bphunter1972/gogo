"Runs csr3 during pre_build phase."

import gadget
import gvars
from utils import get_filename
from pymake import pymake

Log = gvars.Log

class CsrBuildGadget(gadget.Gadget):

    #--------------------------------------------
    def __init__(self):
        super(CsrBuildGadget, self).__init__()

        self.schedule_phase = 'pre_build'
        self.name = 'csr3'
        self.queue = 'build'
        self.interactive = False

        self.done_file = get_filename(".csr3_done")

    #--------------------------------------------
    def create_cmds(self):
        "Run csr3 verif"

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
        Log.info("Received exit_status=%d" % exit_status)
        if exit_status == 0:
            f = open(self.done_file, "w")
            f.close()
        else:
            from os import remove
            try:
                remove(self.done_file)
            except OSError:
                pass
