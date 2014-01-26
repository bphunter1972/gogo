"""
A class that represents a Vkit, with common faculties
"""

import os.path
import gvars
import gadget

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

        Log.debug("Creating vkit %s" % entry)
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

        # in genip mode, run as a gadget
        if gvars.VLOG.COMPTYPE == 'genip':
            self.handle_genip()

    #--------------------------------------------
    def make_assignments(self, config, entry):
        """
        Assigns to local variables based on configurations supplied
        """
        vkits_dir = gvars.PROJ.VKITS_DIR

        try:
            self.name = config['NAME']
            Log.debug("Loaded config for %s" % self.name)
        except KeyError:
            Log.critical("config for %s has no NAME attribute." % entry)

        try:
            self.dir_name = config['DIR']
            if not isinstance(self.dir_name, str):
                Log.critical("Directory specified for %s is not a string." % entry)
            if not self.dir_name.startswith(vkits_dir):
                self.dir_name = os.path.join(vkits_dir, self.dir_name)
        except KeyError:
            self.dir_name = os.path.join(vkits_dir, self.name)
            Log.info("Set self.dir_name=%s" % self.dir_name)
        self.dir_name = os.path.abspath(self.dir_name)

        try:
            self.flist_name = config['FLIST']
        except KeyError:
            self.flist_name = os.path.join(self.dir_name, "%s.flist" % self.name)
        if not self.flist_name.startswith(self.dir_name):
            self.flist_name = os.path.join(self.dir_name, self.flist_name)
        if not self.flist_name.endswith(".flist"):
            self.flist_name += '.flist'

        try:
            self.pkg_name = config['PKG_NAME']
        except KeyError:
            self.pkg_name = "%s_pkg" % self.name
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
                Log.critical("Unable to import %s from %s" % (mod_name))

        result = mod.__dict__.copy()
        del sys.modules[mod_name]
        return result

    #--------------------------------------------
    def __repr__(self):
        return self.get_pkg_name()

    #--------------------------------------------
    def get_pkg_name(self):
        return "DEFAULT.%s" % self.pkg_name

    #--------------------------------------------
    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)

    #--------------------------------------------
    def __ne__(self, other):
        return not self.__eq__(other)

    #--------------------------------------------
    def get_all_sources(self, patterns=['.sv', '.v']):
        """
        Returns a list of ALL files in the vkit directory.
        """

        from pymake import glob_files
        patterns = ['*%s' % it for it in patterns]
        srcs = glob_files([self.dir_name], patterns, recursive=True)
        return srcs

    #--------------------------------------------
    def handle_genip(self):
        self.schedule_phase = 'genip'
        self.resources = gvars.PROJ.LSF_VLOG_LICS
        self.queue = 'build'
        self.interactive = False
        self.runmod_modules = gvars.VLOG.MODULES
        self.cwd = self.dir_name
        self.lib_name = '%s_LIB' % self.name.upper()

        import schedule
        import gadgets.ssim
        schedule.add_gadget(gadgets.ssim.SsimGadget(self))

    #--------------------------------------------
    def create_cmds(self):
        """
        echo "Running vlogan"
        runmod -m synopsys-vcs_mx/H-2013.06-SP1 vlogan ../vkits/uvm/1_1d/src/dpi/uvm_dpi.cc -nc -q -notice -unit_timescale=1ns/1ps -sverilog +define+PROJ_INCLUDES_UVM+VCS+HAVE_VERDI_WAVE_PLI+RANDOM_SYNC_DELAY+TBV+BEHAVE+USE_ASSERTIONS+UVM_NO_DEPRECATED+UVM_OBJECT_MUST_HAVE_CONSTRUCTOR +libext+.v+.sv -full64 +warn=noISALS,noULSU,noIDTS,noLCA_FEATURES_ENABLED -sv_pragma +lint=noPCTIO-L,noPCTI-L +vcsd -f swi.flist -work SWI_LIB

        echo "Running vcs"
        runmod -m synopsys-vcs_mx/H-2013.06-SP1 vcs -lca +warn=noLCA_FEATURES_ENABLED,noACC_CLI_ON -genip SWI_LIB.swi_pkg ../vkits/uvm/1_1d/src/dpi/uvm_dpi.cc -CFLAGS -DVCS +vpi -P /nfs/cadtools/synopsys/Verdi-201309/share/PLI/VCS/LINUX64/novas.tab -P project/verif/vpi/vpi_msg.tab
        """     

        cmds = []

        # the vkits of our dependencies
        self.libs = gvars.get_vkits(self.dependencies)

        import vlog
        vlog_warnings = vlog.get_warnings(self.VLOG.IGNORE_WARNINGS)
        vlog_defines = vlog.get_defines(self.VLOG.DEFINES)
        flists = vlog.get_flists([self.flist_name])
        tab_files = vlog.get_tab_files(gvars.VLOG.TAB_FILES + self.VLOG.TAB_FILES)
        so_files = vlog.get_so_files(self.VLOG.SO_FILES)
        arc_libs = vlog.get_arc_libs(self.VLOG.ARC_LIBS)
        parallel = vlog.get_parallel()
        if self.libs:
            v_libs = ' -v ' + ' -v '.join(["%s.%s" % (it.lib_name, it.pkg_name) for it in self.libs])
        else:
            v_libs = ''

        # create vlogan command
        vlogan_args = [vlog_warnings, gvars.VLOG.OPTIONS, self.VLOG.OPTIONS, '-nc +vcsd', gvars.VLOG.VLOGAN_OPTIONS, 
                        self.VLOG.VLOGAN_OPTIONS, vlog_defines, v_libs, flists]                        
        vlogan_cmd = 'vlogan ' + ' '.join(vlogan_args)
        vlogan_cmd += ' -work %s' % self.lib_name
        cmds.append(('Running vlogan...',vlogan_cmd))

        # create VCS command
        vcs_cmd = gvars.VLOG.TOOL
        vcs_cmd += ' -genip %s.%s +vpi -lca' % (self.lib_name, self.pkg_name) 
        vcs_args = [vlog_warnings, self.VLOG.OPTIONS, self.VLOG.VCS_OPTIONS, tab_files, so_files, arc_libs, 
            vlog_defines, parallel]
        vcs_cmd += ' ' + ' '.join(vcs_args)
        cmds.append(('Running vcs...', vcs_cmd))

        return cmds

    #--------------------------------------------
    def preLaunchCallback(self):
        import sge_tools as sge

        # ensure that the project link exists
        try:
            os.symlink(gvars.RootDir, os.path.join(self.dir_name, 'project'))
        except OSError:
            pass

        if self.dependencies:
            Log.info("%s waiting for %s" % (self.name, self.dependencies))
            sge.waitForSomeJobs(self.libs, pollingMode=False)
            Log.info("%s Launching!" % self.name)

    #--------------------------------------------     
    # def genCmdLine(self):
    #     """
    #     Parallel partition compiles on a multi-core machine 
    #     """

    #     cmdLine = super(VkitGadget, self).genCmdLine()
    #     if gvars.VLOG.PARALLEL:
    #         cmdLine += ' -pe smp_pe %d' % int(    #     return cmdLine

