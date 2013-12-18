"""
An Gadget class representing the Build gadget.
"""

import gadget
import gvars
import os

Log = gvars.Log

class BuildGadget(gadget.Gadget):
    """Builds the simulation executable"""

    #--------------------------------------------
    def __init__(self):
        super(BuildGadget, self).__init__()

        self.name = 'build'
        self.resources = gvars.Vars['LSF_BLD_LICS']
        self.queue = 'build'
        self.interactive = True
        self.quiet = True
        self.runmod_modules = gvars.Vars['BLD_MODULES']

        # create a symbolic link called 'project'. 
        try:
            os.symlink('../..', 'project')
        except OSError:
            pass

    #--------------------------------------------     
    def genCmdLine(self):
        """
        Parallel partition compiles on a multi-core machine 
        """

        cmdLine = super(BuildGadget, self).genCmdLine()
        if gvars.Vars['BLD_PARALLEL']:
            cmdLine += ' -pe smp_pe %d' % int(gvars.Vars['BLD_PARALLEL'])
        return cmdLine

    #--------------------------------------------
    def create_cmds(self):
        """
        Returns the commands as a list of strings.
        """

        cmds = []

        bld_partition = gvars.Vars['BLD_PARTITION'] 
        run_partition = bld_partition in ('auto', 'custom')

        # check that partition.cfg file exists, else emit a warning
        if bld_partition == 'custom' and not os.path.exists('partition.cfg'):
            Log.warning("Unable to find file 'partition.cfg'.  Setting to run in auto mode instead.")
            bld_partition = 'auto'

        # determine all of the vkits and flists
        vkits = [it.flist_file() for it in gvars.Vkits]

        # all the flist files in total
        flists = vkits + gvars.Vars['FLISTS']

        # create vcomp directory if it does not already exist
        if not os.path.exists(gvars.Vars['BLD_VCOMP_DIR']):
            try:
                os.makedirs(gvars.Vars['BLD_VCOMP_DIR'], 0777)
            except OSError:
                Log.critical("Unable to create directory %s" % gvars.Vars['BLD_VCOMP_DIR'])
                sys.exit(255)

        uvm_dpi = " %s/src/dpi/uvm_dpi.cc" % gvars.Vars['UVM_DIR']
        flists = ' -f ' + ' -f '.join(flists)

        tab_files = so_files = arc_libs = bld_defines = cmpopts = bld_options = parallel = ""
        if gvars.Vars['BLD_TAB_FILES']:
            tab_files = ' -P ' + ' -P '.join(gvars.Vars['BLD_TAB_FILES'])
        if gvars.Vars['BLD_SO_FILES']:
            so_files = " -LDFLAGS '%s'" % (' '.join(gvars.Vars['BLD_SO_FILES']))
        if gvars.Vars['BLD_ARC_LIBS']:
            arc_libs = ' ' + ' '.join(gvars.Vars['BLD_ARC_LIBS'])
        if gvars.Vars['BLD_DEFINES']:
            bld_defines = ' +define+' + '+'.join(gvars.Vars['BLD_DEFINES'])
        if gvars.Options.cmpopts:
            cmpopts += " " + gvars.Options.cmpopts
        bld_options = " %s" % gvars.Vars['BLD_OPTIONS']
        if gvars.Vars['BLD_PARALLEL']:
            parallel = ' -fastpartcomp=j%d' % gvars.Vars['BLD_PARALLEL']

        # create vlogan command if running partition compile
        if run_partition:
            vlogan_cmd = 'vlogan'
            vlogan_cmd += uvm_dpi
            vlogan_cmd += bld_options
            vlogan_cmd += bld_defines
            vlogan_cmd += flists
            for not_in in ('-DVCS', "+vpi"):
                vlogan_cmd = vlogan_cmd.replace(not_in, '')
            cmds.append("echo '++ Running vlogan'")
            cmds.append(vlogan_cmd)

        # create build command
        simv_file = os.path.join(gvars.Vars['BLD_VCOMP_DIR'], 'simv')
        bld_cmd = gvars.Vars['BLD_TOOL']
        bld_cmd += ' -o %s -Mupdate' % (simv_file)
        bld_cmd += uvm_dpi
        bld_cmd += bld_options

        try:
            part = {
                'auto'  : ' -partcomp=autopartdbg',
                'custom': ' -partcomp +optconfigfile+partition.cfg',
                'off'   : '',
            }[bld_partition]
            bld_cmd += part
        except KeyError:
            Log.critical("The BLD_PARTITION variable %s must be set to (auto, custom, or off)." % bld_partition)

        bld_cmd += tab_files
        bld_cmd += so_files
        bld_cmd += arc_libs
        bld_cmd += bld_defines
        bld_cmd += cmpopts
        bld_cmd += parallel
        bld_cmd += flists
        cmds.append("echo '++ Running vcs'")
        cmds.append(bld_cmd)

        return cmds

########################################################################################
def get_builder():
    return BuildGadget