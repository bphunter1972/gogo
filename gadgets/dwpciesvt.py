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
        self.runmod_modules = gvars.PROJ.MODULES["synopsys-designware"]

        # make the obj/unit directory if it doesn't already exist
        self.cwd = os.path.abspath(os.path.join(gvars.PROJ.VKITS_DIR, "designware"))
        self.unit_dir = os.path.join(self.cwd, "obj/unit")
        try:
            os.makedirs(self.unit_dir)
        except OSError:
            pass

    #--------------------------------------------     
    def create_cmds(self):
        "Prepend the commands with a call to dw_vip_setup, if necessary."

        cmd_line = "dw_vip_setup -p obj/unit -a pcie_device_agent_svt -svlog"
        return gadget.GadgetCommand(comment="Running dw_vip_setup in %s" % self.cwd, command=cmd_line)

    #--------------------------------------------
    def check_dependencies(self):
        "Return True if the svt_pcie.uvm.pkg does not exist."

        svt_pcie_uvm_pkg = os.path.join(self.unit_dir, 'include/sverilog/svt_pcie.uvm.pkg')
        return not os.path.exists(svt_pcie_uvm_pkg)

