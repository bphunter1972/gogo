import gvars
import gadget
import os

class DWPciesvtGadget(gadget.Gadget):
    "Build the designware component"
    
    def __init__(self):
        super(DWPciesvtGadget, self).__init__()
      
        self.schedule_phase = 'pre_vlog'
        
        self.name = 'DWPciesvt'
        self.queue = 'build'
        self.interactive = True
        self.runmod_modules = ["synopsys-designware"]

    #--------------------------------------------     
    def create_cmds(self):
        "Prepend the commands with a call to dw_vip_setup, if necessary."

        # make the obj/unit directory if it doesn't already exist
        self.dw_dir = os.path.join(gvars.Vars['VKITS_DIR'], "designware")
        self.unit_dir = os.path.join(self.dw_dir, "obj/unit")
        try:
            os.makedirs(self.unit_dir)
        except OSError:
            pass

        self.create_dw = os.path.exists('%s/include/sverilog/svt_pcie.uvm.pkg' % self.unit_dir) == False
        self.cwd = os.path.abspath(self.dw_dir)

        # if we must, prepend this command
        if self.create_dw:
            gvars.Log.info("Running dw_vip_setup in %s" % self.cwd)
            return ["dw_vip_setup -p obj/unit -a pcie_device_agent_svt -svlog"]
        else:
            return []

