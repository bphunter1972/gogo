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
    """Builds the simulation executable for a testbench."""

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

        self.run_partition = gvars.VLOG.COMPTYPE == 'partition'
        self.run_genip = gvars.VLOG.COMPTYPE == 'genip'
        self.run_normal = gvars.VLOG.COMPTYPE == 'normal'

        # create the partition configuration file in auto mode
        if self.run_partition:
            # note that this does not actually go to the schedule yet (everything runs in init(), 
            # we still will add it to the schedule in case that changes someday)
            import partition
            schedule.add_gadget(partition.PartitionGadget())
            Log.info("Running in partition mode.")
        elif self.run_genip:
            import ssim
            schedule.add_gadget(ssim.SsimGadget())
            self.turds.append('csrc')
            self.turds.append('work')
            Log.info("Running in genip mode.")

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
        if self.run_partition:
            partition_cfg_name = gvars.VLOG.PART_CFG
            partition_cfg_name = get_filename(partition_cfg_name)
            if not check_files_exist(partition_cfg_name):
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
        flists =  [get_filename('.flist')]
        if not self.run_genip:
            flists   = [it.flist_name for it in gvars.Vkits] + flists
        flists       = get_flists(flists)
        tab_files    = get_tab_files(gvars.VLOG.TAB_FILES)
        so_files     = get_so_files(gvars.VLOG.SO_FILES)
        vlog_defines = get_defines(gvars.VLOG.DEFINES)
        arc_libs     = get_arc_libs(gvars.VLOG.ARC_LIBS)
        parallel     = '-fastpartcomp=j%d' % gvars.VLOG.PARALLEL if gvars.VLOG.PARALLEL else ""
        if gvars.VLOG.IGNORE_WARNINGS:
            vlog_warnings = get_warnings(gvars.VLOG.IGNORE_WARNINGS)
        else:
            vlog_warnings = ""
        if gvars.SIM.WAVE != None:
            gvars.VLOG.VCS_OPTIONS += ' -debug_pp'

        #--------------------------------------------
        # set environment variable here in genip mode
        if self.run_genip:
            cmds.append(gadget.GadgetCommand(command="setenv VCS_UVM_HOME project/verif/vkits/uvm/%s/src" % gvars.PROJ.UVM_REV, check_after=False, no_modules=True))
            
        #--------------------------------------------
        # create vlogan command if running partition compile
        if self.run_partition or self.run_genip:
            vlogan_args = [vlog_warnings, gvars.VLOG.OPTIONS, gvars.VLOG.VLOGAN_OPTIONS, vlog_defines, flists]
            if self.run_genip:
                vlogan_args.append('-work WORK')
            vlogan_cmd = 'vlogan ' + ' '.join(vlogan_args)
            cmds.append(gadget.GadgetCommand(comment='Running vlogan...', command=vlogan_cmd))

        #--------------------------------------------
        # create vcs command
        simv_file = os.path.join(gvars.VLOG.VCOMP_DIR, 'simv')
        vcs_args = [gvars.VLOG.TOOL, ' -o %s -Mupdate' % (simv_file), 
                    vlog_warnings, gvars.VLOG.OPTIONS, gvars.VLOG.VCS_OPTIONS, 
                    tab_files, so_files, arc_libs, parallel
                    ]

        if self.run_genip:
            sharedlib = '-sharedlib=%s' % ':'.join([it.pkg_dir for it in gvars.Vkits])
            vcs_args.append(sharedlib)
            vcs_args.append('-integ work.%s' % gvars.TB.TOP)

        if self.run_partition:
            vcs_args.append(' -partcomp +optconfigfile+%s' % partition_cfg_name)
            vcs_args.append(gvars.TB.TOP)

        vcs_cmd = ' ' + ' '.join(vcs_args)
        cmds.append(gadget.GadgetCommand(comment='Running vcs...', command=vcs_cmd))

        return cmds

########################################################################################
# Externally Available Functions
########################################################################################

# TODO: Put this in a vcs_utils file?

########################################################################################
def get_warnings(warnings):
    if warnings:
        return "+warn=" + ','.join(['no%s' % it for it in warnings])
    else:
        return ""

########################################################################################
def get_defines(defs):
    if defs:
        return '+define+' + '+'.join(defs)
    else:
        return ""

########################################################################################
def get_flists(flists):
    # all the flist files in total
    flists = gvars.TB.FLISTS + flists
    return '-f ' + ' -f '.join(flists)

########################################################################################
def get_tab_files(tab_files):
    if tab_files:
        for t_file in tab_files:
            if not check_files_exist(t_file):
                raise gadget.GadgetFailed("%s does not exist from %s" % (t_file, os.getcwd()))
        return '-P ' + ' -P '.join(tab_files)
    else:
        return ""

########################################################################################
def get_so_files(so_files):
    if so_files:
        # check first that they exist
        if not check_files_exist(so_files):
            raise gadget.GadgetFailed("%s does not exist." % so_files)
        so_files = [os.path.abspath(it) for it in so_files]
        return " -LDFLAGS '%s'" % (' '.join(so_files))
    else:
        return ""

########################################################################################
def get_arc_libs(arcs):
    return ' '.join(arcs)

########################################################################################
def get_parallel():
    return '-fastpartcomp=j%d' % gvars.VLOG.PARALLEL if gvars.VLOG.PARALLEL else ""
