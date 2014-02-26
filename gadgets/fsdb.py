"""
A gadget that creates the fsdb.sh file.
"""

from __future__ import print_function

import gadget
import gvars
import os
import utils

Log = gvars.Log

class FsdbGadget(gadget.Gadget):
    """Creates the fsdb.sh file"""
    def __init__(self, sim_dir):
        super(FsdbGadget, self).__init__()

        self.schedule_phase = 'pre_simulate'
        self.sim_dir        = sim_dir
        self.name           = 'fsdb'
        self.runLocally     = True
        self.fsdb_name      = os.path.join(self.sim_dir, 'fsdb.sh')
        self.tb_top         = gvars.TB.TOP
        self.vcomp_dir      = gvars.VLOG.VCOMP_DIR

    #--------------------------------------------
    def create_cmds(self):
        self.turds.append(self.fsdb_name)

        with open(self.fsdb_name, 'w') as fsdb_file:
            print("runmod verdi -rcFile ~/.novas.rc -ssf %(sim_dir)s/verilog.fsdb -logdir %(sim_dir)s/verdiLog -top %(tb_top)s -nologo -lib %(vcomp_dir)s $*" % self.__dict__, file=fsdb_file)
        os.chmod(self.fsdb_name, 0o777)

        return None
        
    #--------------------------------------------
    def check_dependencies(self):
        """
        Returns true if vericom needs to be run because the vericomLog/compiler.log file does not exist.
        """

        return not os.path.exists(self.fsdb_name)
