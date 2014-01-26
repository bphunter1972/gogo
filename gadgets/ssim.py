"Creates a Synopsys-sim setup file"

from __future__ import print_function

import gadget
import os.path
import gvars

Log = gvars.Log

class SsimGadget(gadget.Gadget):
    """Creates the synopsys_sim.setup file for the given vkit, during the pre_genip phase"""
    def __init__(self, vkit):
        super(SsimGadget, self).__init__()
        self.vkit = vkit

        self.name = 'ssim_%s' % self.vkit.name
        self.schedule_phase = 'pre_genip'

    #--------------------------------------------
    def create_cmds(self):
        # create synopsys_sim.setup file that looks like this:
        # CN_LIB : project/verif/vkits/cn/cn_pkg
        # GLOBAL_LIB : project/verif/vkits/global/global_pkg
        # UVM_LIB : project/verif/vkits/uvm/1_1d/uvm_pkg
        # GMEM_LIB : project/verif/vkits/gmem/gmem_pkg
        # CREDITS_LIB : project/verif/vkits/credits/credits_pkg
        # SWI_LIB : swi_pkg

        # write out synopsys_sim.setup file if one does not already exist
        setup_file_name = os.path.join(self.vkit.dir_name, 'synopsys_sim.setup')
        Log.info("Creating %s" % setup_file_name)

        with open(setup_file_name, 'w') as sfile:
            print("%s : %s" % (self.vkit.lib_name, self.vkit.pkg_name), file=sfile)
            Log.info("%s dependencies: %s" % (self.name, self.vkit.dependencies))
            libs = gvars.get_vkits(self.vkit.dependencies)
            Log.info("%s libs: %s" % (self.name, [it.name for it in libs]))

            for lib in libs:
                print("%s : %s" % (lib.lib_name, os.path.join(lib.dir_name, lib.pkg_name)), file=sfile)

        self.turds.append(setup_file_name)
        
        # there are no jobs to farm out from this
        return None
