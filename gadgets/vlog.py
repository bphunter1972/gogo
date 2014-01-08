"""
An Gadget class representing the verilog-compile gadget.
"""

import gadget
import gvars
import os

Log = gvars.Log

class VlogGadget(gadget.Gadget):
    """Builds the simulation executable"""

    #--------------------------------------------
    def __init__(self):
        super(VlogGadget, self).__init__()

        self.schedule_phase = 'vlog'

        self.name = 'vlog'
        self.resources = gvars.Vars['LSF_VLOG_LICS']
        self.queue = 'build'
        self.interactive = True
        self.runmod_modules = gvars.Vars['VLOG_MODULES']

        # create a symbolic link called 'project'. 
        try:
            os.symlink('../..', 'project')
        except OSError:
            pass

        # create the partition file if one does not already exist
        if gvars.Vars['VLOG_PARTITION'] == 'custom' and not os.path.exists('partition.cfg'):
            # note that this does not actually go to the schedule yet (everything runs in init(), 
            # we still will add it to the schedule in case that changes someday)
            import partition
            import schedule
            schedule.add_gadget(partition.PartitionGadget())

    #--------------------------------------------     
    def genCmdLine(self):
        """
        Parallel partition compiles on a multi-core machine 
        """

        cmdLine = super(VlogGadget, self).genCmdLine()
        if gvars.Vars['VLOG_PARALLEL']:
            cmdLine += ' -pe smp_pe %d' % int(gvars.Vars['VLOG_PARALLEL'])
        return cmdLine

    #--------------------------------------------
    def create_cmds(self):
        """
        Returns the commands as a list of strings.
        """

        cmds = []

        vlog_partition = gvars.Vars['VLOG_PARTITION'] 
        run_partition = vlog_partition in ('auto', 'custom')

        # check that partition.cfg file exists, else emit a warning
        if vlog_partition == 'custom' and not os.path.exists('partition.cfg'):
            Log.warning("Unable to find file 'partition.cfg'.  Setting to run in auto mode instead.")
            vlog_partition = 'auto'

        # create vcomp directory if it does not already exist
        if not os.path.exists(gvars.Vars['VLOG_VCOMP_DIR']):
            try:
                os.makedirs(gvars.Vars['VLOG_VCOMP_DIR'], 0o777)
            except OSError:
                Log.critical("Unable to create directory %s" % gvars.Vars['VLOG_VCOMP_DIR'])

        uvm_dpi = " %s/src/dpi/uvm_dpi.cc" % gvars.Vars['UVM_DIR']
        flists = get_flists() 

        tab_files = so_files = arc_libs = vlog_defines = cmpopts = vlog_options = parallel = vlog_warnings = ""
        tab_files = get_tab_files()
        so_files = get_so_files()
        vlog_defines = get_defines()
        if gvars.Vars['VLOG_ARC_LIBS']:
            arc_libs = ' ' + ' '.join(gvars.Vars['VLOG_ARC_LIBS'])
        if gvars.Options.cmpopts:
            cmpopts += " " + gvars.Options.cmpopts
        vlog_options = " %s" % gvars.Vars['VLOG_OPTIONS']
        if gvars.Vars['VLOG_PARALLEL']:
            parallel = ' -fastpartcomp=j%d' % gvars.Vars['VLOG_PARALLEL']
        if gvars.Vars['VLOG_IGNORE_WARNINGS']:
            vlog_warnings = "+warn+" + ','.join(['no%s' % it for it in vlog_warnings])

        # create vlogan command if running partition compile
        if run_partition:
            vlogan_cmd = 'vlogan'
            vlogan_cmd += uvm_dpi
            vlogan_cmd += vlog_options
            vlogan_cmd += vlog_defines
            vlogan_cmd += flists
            for not_in in ('-DVCS', "+vpi"):
                vlogan_cmd = vlogan_cmd.replace(not_in, '')
            cmds.append(vlogan_cmd)

        # create vlog command
        simv_file = os.path.join(gvars.Vars['VLOG_VCOMP_DIR'], 'simv')
        vlog_cmd = gvars.Vars['VLOG_TOOL']
        vlog_cmd += ' -o %s -Mupdate' % (simv_file)
        vlog_cmd += uvm_dpi
        vlog_cmd += vlog_options
        vlog_cmd += vlog_warnings
        vlog_cmd += ' -fastcomp=1 -lca -rad'

        try:
            part = {
                'auto'  : ' -partcomp=autopartdbg',
                'custom': ' -partcomp +optconfigfile+partition.cfg',
                'off'   : '',
            }[vlog_partition]
            vlog_cmd += part
        except KeyError:
            Log.critical("The VLOG_PARTITION variable %s must be set to (auto, custom, or off)." % vlog_partition)

        vlog_cmd += tab_files
        vlog_cmd += so_files
        vlog_cmd += arc_libs
        vlog_cmd += vlog_defines
        vlog_cmd += cmpopts
        vlog_cmd += parallel
        vlog_cmd += flists
        cmds.append(vlog_cmd)

        return cmds

########################################################################################
def get_defines():
    if gvars.Vars['VLOG_DEFINES']:
        return ' +define+' + '+'.join(gvars.Vars['VLOG_DEFINES'])
    else:
        return ""

########################################################################################
def get_flists():
    # determine all of the vkits and flists
    vkits = [it.flist_file() for it in gvars.Vkits]

    # all the flist files in total
    flists = vkits + gvars.Vars['FLISTS']

    return ' -f ' + ' -f '.join(flists)

########################################################################################
def get_tab_files():
    if gvars.Vars['VLOG_TAB_FILES']:
        return ' -P ' + ' -P '.join(gvars.Vars['VLOG_TAB_FILES'])
    else:
        return ""

########################################################################################
def get_so_files():
    if gvars.Vars['VLOG_SO_FILES']:
        so_files = [os.path.abspath(it) for it in gvars.Vars['VLOG_SO_FILES']]
        return " -LDFLAGS '%s'" % (' '.join(so_files))
    else:
        return ""
