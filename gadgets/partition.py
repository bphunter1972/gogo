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

        self.schedule_phase = 'pre_vlog'
        
        static_vkits = gvars.StaticVkits
        vkits = [it for it in gvars.Vkits if it not in static_vkits]
        cells = gvars.Vars['PARTITION_CELLS']
        part_cfg_name = '.partition.cfg'
        self.turds.append(part_cfg_name)
        
        with open(part_cfg_name, 'w') as pfile:
            if static_vkits:
                static_vkit_pkgs = ' '.join([it.get_pkg_name() for it in static_vkits])
                print >>pfile, "partition package %s ;" % static_vkit_pkgs
            for cell in cells:
                print >>pfile, "partition cell %s ;" % cell
            for vkit in vkits:
                print >>pfile, "partition package %s ;" % vkit.get_pkg_name()
