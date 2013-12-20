"""
Creates a new partition file for partition-compile.
"""

import gadget
import gvars

Log = gvars.Log

class PartitionGadget(gadget.Gadget):
    """Creates a partition file for a testbench"""

    #--------------------------------------------
    def __init__(self):
        super(PartitionGadget, self).__init__()

        gvars.Log.info("Creating partition.cfg")

        static_vkits = gvars.StaticVkits
        vkits = [it for it in gvars.Vkits if it not in static_vkits]

        with open('partition.cfg', 'w') as f:
            if static_vkits:
                static_vkit_pkgs = ' '.join([it.get_pkg_name() for it in static_vkits])
                print >>f, "partition package %s ;" % static_vkit_pkgs
            for vkit in vkits:
                print >>f, "partition package %s ;" % vkit.get_pkg_name()

