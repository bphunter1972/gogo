"Compiles a vkit as a piece of IP"

import gadget

class GenipGadget(gadget.Gadget):
    """Runs vlogan/vcs on a particular vkit"""
    def __init__(self, vkit):
        super(GenipGadget, self).__init__()
        self.vkit = vkit
    
    #--------------------------------------------
    def genCmdLine(self):
        pass
