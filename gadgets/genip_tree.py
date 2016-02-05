"""
A gadget that prints the genip tree.
"""

import gadget
import gvars
import depends
from utils import order_vkits
from utils import sort_vkits

Log = depends.Log = gvars.Log

class GenipTreeGadget(gadget.Gadget):
    def __init__(self):
        super(GenipTreeGadget, self).__init__()

        self.schedule_phase = 'pre_build'
        Log.info("Genip Tree:")
        self.print_genip_tree(gvars.Vkits)

    #--------------------------------------------
    def print_genip_tree(self, all_vkits):
        "Returns the tree of vkits as a string"

        ordered = order_vkits(all_vkits)
        depends.print_ordered_deps(ordered)
        sorted_vkits = sort_vkits(all_vkits)
        print(sorted_vkits)

    #--------------------------------------------
    def genCmdLine(self):
        return []


