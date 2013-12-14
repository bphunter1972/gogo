"""
Creates a new partition file for partition-compile.
"""

import action
import gvars

class PartitionAction(action.Action):
    """Creates a partition file for a testbench"""

    #--------------------------------------------
    def __init__(self):
        super(PartitionAction, self).__init__()

        def pkg_it(kit):
            return "DEFAULT.%s_pkg" % kit

        gvars.Log.info("Creating partition.cfg")

        vkits = gvars.Vars['VKITS']

        # always put uvm here
        static_vkits = ['uvm']

        if gvars.Vars['STATIC_VKITS']:
            static_vkits.extend(gvars.Vars['STATIC_VKITS'])
        static_vkits = ' '.join([pkg_it(it) for it in static_vkits])
        vkits = [pkg_it(it) for it in vkits if it not in static_vkits]

        with open('partition.cfg', 'w') as f:
            if static_vkits:
                print >>f, "partition package %s ;" % static_vkits
            for vkit in vkits:
                print >>f, "partition package %s ;" % vkit

