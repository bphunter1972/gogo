"""
An Action class representing the Build action.
"""

import action
import gvars
import os

Log = gvars.Log

class BuildAction(action.Action):
    """Builds the simulation executable"""

    #--------------------------------------------
    def __init__(self):
        super(BuildAction, self).__init__()

        self.name = 'build'
        self.resources = [gvars.Vars['LSF_BLD_LICS']]
        self.queue = 'build'
        self.interactive = True
        self.quiet = True
        self.runmod_modules = gvars.Vars['BLD_MODULES']

    #--------------------------------------------
    def create_cmds(self):
        """
        Returns the commands as a list of strings.
        """

        run_partition = gvars.Vars['BLD_PARTITION']

        # determine all of the vkits and flists
        vkits = [os.path.join(gvars.Vars['VKITS_DIR'], it, "%s.flist" % it) for it in gvars.Vars['VKITS']]
        flists = [gvars.Vars['UVM_FLIST']] + vkits + gvars.Vars['FLISTS']

        # create vcomp directory if it does not already exist
        if not os.path.exists(gvars.Vars['BLD_VCOMP_DIR']):
            try:
                os.makedirs(gvars.Vars['BLD_VCOMP_DIR'], 0777)
            except OSError:
                Log.critical("Unable to create directory %s" % gvars.Vars['BLD_VCOMP_DIR'])
                sys.exit(255)

        uvm_dpi = " %s/src/dpi/uvm_dpi.cc" % gvars.Vars['UVM_DIR']
        flists = ' -f ' + ' -f '.join(flists)

        tab_files = so_files = arc_libs = bld_defines = cmpopts = bld_options = ""
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

        # create vlogan command if running partition compile
        if run_partition:
            vlogan_cmd = 'vlogan'
            vlogan_cmd += uvm_dpi
            vlogan_cmd += flists
            vlogan_cmd += bld_options
            vlogan_cmd += bld_defines

        # create build command
        bld_cmd = gvars.Vars['BLD_TOOL']
        bld_cmd += ' -o %s -Mupdate' % (os.path.join(gvars.Vars['BLD_VCOMP_DIR'], 'sim.exe'))
        bld_cmd += uvm_dpi
        bld_cmd += flists
        bld_cmd += bld_options
        if run_partition:
            bld_cmd += ' -partcomp +optconfigfile+vcs_partition_config.file'
        bld_cmd += tab_files
        bld_cmd += so_files
        bld_cmd += arc_libs
        bld_cmd += bld_defines
        bld_cmd += cmpopts

        cmds = []
        if run_partition:
            cmds.append("echo '++ Running vlogan'")
            cmds.append(vlogan_cmd)
        cmds.append("echo '++ Running vcs'")
        cmds.append(bld_cmd)

        return cmds
