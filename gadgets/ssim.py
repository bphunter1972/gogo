"Creates a Synopsys-sim setup file"

from __future__ import print_function

import gadget
import os.path
import gvars

Log = gvars.Log

class SsimGadget(gadget.Gadget):
    """Creates the synopsys_sim.setup file for the given vkit, during the pre_genip phase"""
    def __init__(self, vkit=None):
        super(SsimGadget, self).__init__()
        self.vkit = vkit

        if vkit is not None:
            self.name = 'ssim_%s' % self.vkit.name
        else:
            self.name = 'ssim'
        self.schedule_phase = 'pre_genip'

    #--------------------------------------------
    def create_cmds(self):
        # For VKITS:
        # create synopsys_sim.setup file that looks like this:
        # CN_LIB : project/verif/vkits/cn/cn_pkg
        # GLOBAL_LIB : project/verif/vkits/global/global_pkg
        # UVM_LIB : project/verif/vkits/uvm/1_1d/uvm_pkg
        # GMEM_LIB : project/verif/vkits/gmem/gmem_pkg
        # CREDITS_LIB : project/verif/vkits/credits/credits_pkg
        # SWI_LIB : swi_pkg

        # For testbenches:
        # WORK > DEFAULT
        # DEFAULT : ./work
        # UVM_LIB : project/verif/vkits/uvm/1_1d/uvm_pkg
        # CN_LIB : project/verif/vkits/cn/cn_pkg
        # GLOBAL_LIB : project/verif/vkits/global/global_pkg
        # GMEM_LIB : project/verif/vkits/gmem/gmem_pkg
        # CREDITS_LIB : project/verif/vkits/credits/credits_pkg
        # SPS_LIB : project/verif/vkits/sps/sps_pkg
        # SWI_LIB : project/verif/vkits/swi/swi_pkg


        # write out synopsys_sim.setup file if one does not already exist
        if self.vkit:
            setup_file_name = os.path.join(self.vkit.dir_name, 'synopsys_sim.setup')
        else:
            setup_file_name = 'synopsys_sim.setup'

        with open(setup_file_name, 'w') as sfile:
            if self.vkit:
                libs = gvars.get_vkits(self.vkit.dependencies)
                print("%s : %s" % (self.vkit.lib_name, self.vkit.pkg_name), file=sfile)
            else:
                libs = gvars.Vkits
                print("WORK > DEFAULT", file=sfile)
                print("DEFAULT : ./work", file=sfile)
            for lib in libs:
                print("%s : %s" % (lib.lib_name, os.path.join(lib.dir_name, lib.pkg_name)), file=sfile)

        self.turds.append(setup_file_name)
        
        # there are no jobs to farm out from this
        return None
