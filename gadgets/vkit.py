"""
A class that represents a Vkit, with common faculties
"""

from __future__ import print_function

import os.path
import gvars
import gadget
from os_utils import touch
import utils

Log = gvars.Log

class VkitGadget(gadget.Gadget):
    """
    Represents a vkit

    entry: (string) Either the relative path to a vkit configuration file; or
                    the name of a regular vkits directory. Such a vkit cannot be used for genip.
           (dict)   A dictionary containing the vkit parameters found in a vcfg.py file
    """
    def __init__(self, entry):
        super(VkitGadget, self).__init__()

        # ensure that check_dependencies must only run once
        self.checked_dependencies = None

        # The vkit is either a dictionary, or a vcfg.py file located in the specified path from vkits_dir, 
        # or it's simply a name that can be applied to a default dictionary
        config = {}
        if type(entry) == dict:
            config = entry
        elif type(entry) == str:
            if entry.endswith('.py') and os.path.exists(entry):
                config = self.load_vcfg(entry)
            else:
                # create a simple default vkit
                config = {'NAME':entry, 'DIR':entry, 'FLIST':entry}

        self.make_assignments(config, entry)

        # these variables are necessary when running in genip mode
        self.schedule_phase  = 'genip'
        self.resources       = gvars.PROJ.LSF_VLOG_LICS
        self.queue           = 'build'
        self.interactive     = False
        try:
            self.runmod_modules = [gvars.PROJ.MODULES[key] for key in gvars.VLOG.MODULES]
        except KeyError:
            Log.critical("Unknown module in VLOG.MODULES: {}".format(gvars.vlog.MODULES))

        self.cwd             = self.dir_name
        self.lib_name        = '{}_LIB'.format(self.name.upper())
        Log.debug("name={}, dir_name={}, lib_name={}".format(self.name, self.dir_name, self.lib_name))
        self.stdoutPath      = utils.get_filename(os.path.join(self.dir_name, '{}.stdout'.format(self.lib_name)))
        self.mergeStderr     = True
        self.genip_done_file = utils.get_filename(os.path.join(self.dir_name, '{}.genip_done'.format(self.lib_name)))
        self.genip_completed = False
        self.pkg_dir         = os.path.join(self.dir_name, self.pkg_name)
        Log.debug("Sending to pkg_dir: {}".format(self.pkg_dir))

        # ensures that the "...waiting for..." message is only printed once per vkit
        self.printed_waiting_for = False

        # in genip mode, run as a gadget, add the ssim gadget to
        # ensure that the synopsys_sim.setup file is created.
        if gvars.VLOG.COMPTYPE == 'genip':
            import schedule
            import gadgets.ssim
            schedule.add_gadget(gadgets.ssim.SsimGadget(self))

    #--------------------------------------------
    def make_assignments(self, config, entry):
        """
        Assigns to local variables based on configurations supplied
        """
        vkits_dir = gvars.PROJ.VKITS_DIR

        try:
            self.name = config['NAME']
            Log.debug("Loaded config for {}".format(self.name))
        except KeyError:
            Log.critical("config for {} has no NAME attribute.".format(entry))

        try:
            self.dir_name = config['DIR']
            if not isinstance(self.dir_name, str):
                Log.critical("Directory specified for {} is not a string.".format(entry))
            if self.dir_name.startswith('project'):
                self.dir_name = self.dir_name.replace('project', gvars.RootDir)
            elif not self.dir_name.startswith(vkits_dir):
                self.dir_name = os.path.join(vkits_dir, self.dir_name)
        except KeyError:
            self.dir_name = os.path.join(vkits_dir, self.name)
        self.dir_name = os.path.abspath(self.dir_name)

        try:
            self.flist_name = config['FLIST']
        except KeyError:
            self.flist_name = os.path.join(self.dir_name, "{}.flist".format(self.name))
        if not self.flist_name.startswith(self.dir_name):
            self.flist_name = os.path.join(self.dir_name, self.flist_name)
        if not self.flist_name.endswith(".flist"):
            self.flist_name += '.flist'

        try:
            self.pkg_name = config['PKG_NAME']
        except KeyError:
            self.pkg_name = "{}_pkg".format(self.name)
        if not self.pkg_name.endswith("_pkg"):
            self.pkg_name += "_pkg"

        try:
            self.dependencies = config['DEPENDENCIES']
        except KeyError:
            self.dependencies = []

        if 'VLOG' in config:
            self.VLOG = config['VLOG']
        else:
            from vkit_config import Vlog
            self.VLOG = Vlog()

    #--------------------------------------------
    def load_vcfg(self, entry):
        """
        The entry represents a vcfg.py file. Import it and use its dictionary to get 
        values for this vkit.
        """

        import imp
        import sys

        mod_name,ext = os.path.splitext(os.path.basename(entry))
        try:
            mod = imp.load_source(mod_name , entry)
        except ImportError:
            if gvars.Options.dbg:
                raise
            else:
                Log.critical("Unable to import {} from {}".format((mod_name)))

        result = mod.__dict__.copy()
        del sys.modules[mod_name]
        Log.debug("Loaded cfg:\n{}".format(result))
        return result

    #--------------------------------------------
    def __repr__(self):
        return self.get_pkg_name()

    #--------------------------------------------
    def get_pkg_name(self):
        return "DEFAULT.{}".format(self.pkg_name)

    #--------------------------------------------
    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)

    #--------------------------------------------
    def __ne__(self, other):
        return not self.__eq__(other)

    #--------------------------------------------
    def get_all_sources(self, patterns=['.sv', '.v', '.svh']):
        """
        Returns a list of ALL files in the vkit directory.
        """

        from pymake import glob_files
        patterns = ['*{}'.format(it) for it in patterns]
        srcs = glob_files([self.dir_name], patterns, recursive=True)

        # remove any sv files that VCS creates during genip 
        srcs = [it for it in srcs if not it.startswith(self.pkg_dir)]

        return srcs

    #--------------------------------------------
    def create_cmds(self):
        """
        Create vlogan and vcs commands.
        """

        cmds = []

        # the vkits of our dependencies
        Log.debug("Getting the vkits for: {} with dependencies: {}".format((self.lib_name, self.dependencies)))
        self.libs = gvars.get_vkits(self.dependencies, False)

        import vlog
        vlog_warnings = vlog.get_warnings(self.VLOG.IGNORE_WARNINGS)
        vlog_defines  = vlog.get_defines(self.VLOG.DEFINES + gvars.VLOG.DEFINES)
        flists        = vlog.get_flists([self.flist_name])
        tab_files     = vlog.get_tab_files(gvars.VLOG.TAB_FILES + self.VLOG.TAB_FILES)
        so_files      = vlog.get_so_files(self.VLOG.SO_FILES)
        arc_libs      = vlog.get_arc_libs(self.VLOG.ARC_LIBS)
        parallel      = vlog.get_parallel()
        work_arg      = '-work {}' % self.lib_name
        sharedlib     = '-sharedlib={}' % ':'.join([it.pkg_dir for it in self.libs]) if self.libs else ''
        vcs_dir       = '-dir={}' % self.pkg_name
        genip_cmd     = '-genip {}.{} -lca' % (self.lib_name, self.pkg_name) 

        # set env variables for VCS
        # setenv SYNOPSYS_SIM_SETUP name.setup
        cmds.append(gadget.GadgetCommand(command="setenv SYNOPSYS_SIM_SETUP {}.setup".format(self.name, check_after=False, no_modules=True)))
        cmds.append(gadget.GadgetCommand(command="setenv VCS_UVM_HOME project/verif/vkits/uvm/{}/src".format(gvars.PROJ.UVM_REV, check_after=False, no_modules=True)))

        # create vlogan command
        vlogan_args   = [vlog_warnings, gvars.VLOG.OPTIONS, self.VLOG.OPTIONS, '-nc +vcsd', gvars.VLOG.VLOGAN_OPTIONS, 
                        self.VLOG.VLOGAN_OPTIONS, vlog_defines, flists, work_arg, '-ntb_opts uvm']
        vlogan_cmd    = 'vlogan ' + ' '.join(vlogan_args)
        cmds.append(gadget.GadgetCommand(comment='Running vlogan...', command=vlogan_cmd))

        # create VCS command
        vcs_args      = [vlog_warnings, gvars.VLOG.OPTIONS, gvars.VLOG.VCS_OPTIONS, self.VLOG.OPTIONS, 
                        self.VLOG.VCS_OPTIONS, tab_files, so_files, arc_libs, parallel, sharedlib, vcs_dir, 
                        genip_cmd, '-ntb_opts uvm']
        vcs_cmd       = gvars.VLOG.TOOL + ' ' + ' '.join(vcs_args)
        cmds.append(gadget.GadgetCommand(comment='Running vcs...', command=vcs_cmd))

        return cmds

    #--------------------------------------------
    def pauseJob(self):
        "Return true if any dependent libs are not yet done."

        dependent_libs = [it for it in self.libs if not (it.doNotLaunch or it.genip_completed)]
        if dependent_libs:
            if not self.printed_waiting_for:
                # ensure that these things only get printed once
                Log.info("{} waiting for {}".format((self.name, dependent_libs)))
                self.printed_waiting_for = True
            return True
        else:
            return False

    #--------------------------------------------
    def preLaunchCallback(self):

        # ensure that the project link exists
        try:
            os.symlink(gvars.RootDir, os.path.join(self.dir_name, 'project'))
        except OSError:
            pass

        # If there are any libraries that this vkit depends on, then wait until they have completed
        Log.info("{} Launching!".format(self.name))

    #--------------------------------------------
    def completedCallback(self):
        # ensure that this does not get launched again by waitForSomeJobs call in another vkit's preLaunchCallback
        self.genip_completed = True;

        # if this job did not actually launch, then don't call getExitStatus
        if self.doNotLaunch:
            return

        Log.info("{} genip completed!".format(self.name))
        exit_status = self.getExitStatus()
        if exit_status != 0:
            import sync_nfs
            Log.info("{} We are going down because of me! exit_status=%0d".format((self.name, exit_status)))
            try:
                with sync_nfs.sync_open(self.stdoutPath) as f:
                    lines = f.readlines()
            except IOError:
                Log.critical("Unable to read stdout file {}".format(self.stdoutPath))
            for line in lines:
                print(line, end="")
            if os.path.exists(self.genip_done_file):
                os.remove(self.genip_done_file)
            raise gadget.GadgetFailed("genip of {} failed with exit status %0d. See {}".format((self.name, exit_status, self.stdoutPath)))
        else:
            try:
                touch(self.genip_done_file)
            except IOError:
                Log.critical("Unable to touch file {}".format(self.genip_done_file))

    #--------------------------------------------
    def check_dependencies(self):
        if self.checked_dependencies is not None:
            return self.checked_dependencies

        import pymake
        targets = self.genip_done_file
        sources = self.get_all_sources()
        answer = pymake.pymake(targets, sources, get_cause=True)
        Log.debug("dependencies of {} say {} because {}".format(self.name, answer.result, answer.cause))
        result = answer.result

        # also check any of our dependency libraries
        if not result:
            self.libs = gvars.get_vkits(self.dependencies)
            for lib in self.libs:
                if lib.check_dependencies():
                    result = True
                    Log.debug("{} will be built because of {}".format((self.name, lib.name)))
                    break

        # this ensures that any job that calls waitForSomeJobs() will not try to launch this
        if result == False:
            self.doNotLaunch = True
        self.checked_dependencies = result
        return result

    #--------------------------------------------
    def cleanup(self):
        "Report back any directories and/or files that should be cleaned up from this vkit."

        files = [self.genip_done_file, 
                 self.stdoutPath, 
                 # things that VCS creates automatically
                 os.path.join(self.dir_name, '.vlogansetup.args'),
                 os.path.join(self.dir_name, '.vcs_lib_lock'),
                ] 

        dirs = [self.pkg_dir,]

        return (dirs, files)
