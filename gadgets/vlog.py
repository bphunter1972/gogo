"""
Compiles the verilog for a testbench.
"""

import gadget
import gvars
import os
import schedule
from utils import check_files_exist, get_filename

Log = gvars.Log

class VlogGadget(gadget.Gadget):
    """Builds the simulation executable"""

    #--------------------------------------------
    def __init__(self):
        super(VlogGadget, self).__init__()

        self.schedule_phase = 'vlog'

        self.name = 'vlog'
        self.resources = gvars.PROJ.LSF_VLOG_LICS
        self.queue = 'build'
        self.interactive = True
        self.runmod_modules = gvars.VLOG.MODULES

        # create a symbolic link called 'project'. 
        try:
            os.symlink('../..', 'project')
        except OSError:
            pass

        # create the flist file for the testbench
        import flist
        schedule.add_gadget(flist.FlistGadget())

        # create the partition configuration file in auto mode
        if gvars.Options.part == 'auto':
            # note that this does not actually go to the schedule yet (everything runs in init(), 
            # we still will add it to the schedule in case that changes someday)
            import partition
            schedule.add_gadget(partition.PartitionGadget())

    #--------------------------------------------     
    def genCmdLine(self):
        """
        Parallel partition compiles on a multi-core machine 
        """

        cmd_line = super(VlogGadget, self).genCmdLine()
        if gvars.VLOG.PARALLEL:
            cmd_line += ' -pe smp_pe %d' % int(gvars.VLOG.PARALLEL)
        return cmd_line

    #--------------------------------------------
    def create_cmds(self):
        """
        Returns the commands as a list of strings.
        """

        cmds = []

        #--------------------------------------------
        # partitioning
        vlog_partition = gvars.Options.part
        run_partition = vlog_partition != 'off'
        if run_partition:
            partition_cfg_name = '.partition.cfg' if vlog_partition == 'auto' else vlog_partition
            partition_cfg_name = get_filename(partition_cfg_name)
            if check_files_exist(partition_cfg_name) == 0:
                raise gadget.GadgetFailed("%s does not exist." % partition_cfg_name)

        #--------------------------------------------
        # create vcomp directory if it does not already exist
        if not os.path.exists(gvars.VLOG.VCOMP_DIR):
            try:
                os.makedirs(gvars.VLOG.VCOMP_DIR, 0o777)
            except OSError:
                raise gadget.GadgetFailed("Unable to create directory %s" % gvars.VLOG.VCOMP_DIR)

        #--------------------------------------------
        # get common command-line arguments
        flists       = get_flists() 
        tab_files    = get_tab_files()
        so_files     = get_so_files()
        vlog_defines = get_defines()
        arc_libs     = ' '.join(gvars.VLOG.ARC_LIBS)
        parallel     = '-fastpartcomp=j%d' % gvars.VLOG.PARALLEL if gvars.VLOG.PARALLEL else ""
        if gvars.VLOG.IGNORE_WARNINGS:
            vlog_warnings = "+warn=" + ','.join(['no%s' % it for it in gvars.VLOG.IGNORE_WARNINGS])
        else:
            vlog_warnings = ""
        if gvars.SIM.WAVE != None:
            gvars.VLOG.VCS_OPTIONS += ' -debug_pp'

        #--------------------------------------------
        # create vlogan command if running partition compile
        if run_partition:
            vlogan_args = [vlog_warnings, gvars.VLOG.OPTIONS, gvars.VLOG.VLOGAN_OPTIONS, vlog_defines, flists]
            vlogan_cmd = 'vlogan ' + ' '.join(vlogan_args)
            cmds.append(gadget.GadgetCommand(comment='Running vlogan...', command=vlogan_cmd))

        #--------------------------------------------
        # create vcs command
        simv_file = os.path.join(gvars.VLOG.VCOMP_DIR, 'simv')
        vcs_args = [gvars.VLOG.TOOL, ' -o %s -Mupdate' % (simv_file), 
                    vlog_warnings, gvars.VLOG.OPTIONS, gvars.VLOG.VCS_OPTIONS, 
                    tab_files, so_files, arc_libs, parallel
                    ]

        if run_partition:
            vcs_args.append(' -partcomp +optconfigfile+%s' % partition_cfg_name)
            vcs_args.append(gvars.TB.TOP)

        vcs_cmd = ' ' + ' '.join(vcs_args)
        cmds.append(gadget.GadgetCommand(comment='Running vcs...', command=vcs_cmd))

        return cmds

########################################################################################
# Externally Available Functions
########################################################################################

########################################################################################
def get_defines():
    if gvars.VLOG.DEFINES:
        return '+define+' + '+'.join(gvars.VLOG.DEFINES)
    else:
        return ""

########################################################################################
def get_flists():
    # determine all of the vkits and flists
    vkits = [it.flist_name for it in gvars.Vkits]

    # all the flist files in total
    flists = gvars.TB.INIT_FLISTS + vkits + gvars.TB.FLISTS + [get_filename('.flist')]
    return '-f ' + ' -f '.join(flists)

########################################################################################
def get_tab_files():
    if gvars.VLOG.TAB_FILES:
        if check_files_exist(gvars.VLOG.TAB_FILES) == 0:
            raise gadget.GadgetFailed("%s does not exist." % gvars.VLOG.TAB_FILES)
        return '-P ' + ' -P '.join(gvars.VLOG.TAB_FILES)
    else:
        return ""

########################################################################################
def get_so_files():
    if gvars.VLOG.SO_FILES:
        # check first that they exist
        if check_files_exist(gvars.VLOG.SO_FILES) == 0:
            raise gadget.GadgetFailed("%s does not exist." % gvars.VLOG.SO_FILES)
        so_files = [os.path.abspath(it) for it in gvars.VLOG.SO_FILES]
        return " -LDFLAGS '%s'" % (' '.join(so_files))
    else:
        return ""
