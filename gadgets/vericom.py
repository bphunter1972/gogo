"""
A gadget that runs vericom for Verdi waveform usage.
"""

from __future__ import print_function

import gadget
import gvars
import os.path

Log = gvars.Log

class VericomGadget(gadget.Gadget):
    """Runs vericom for Verdi usage"""

    def __init__(self, sim_dir):
        super(VericomGadget, self).__init__()

        self.schedule_phase = 'pre_simulate'
        self.name           = 'vericom'
        self.sim_dir        = sim_dir
        self.tb_top         = gvars.TB.TOP
        self.interactive    = True
        self.queue          = 'build'
        self.vcomp_dir      = gvars.VLOG.VCOMP_DIR
        self.lib_dir        = "%(vcomp_dir)s.lib++" % self.__dict__
        self.runmod_modules.append(gvars.PROJ.VERDI_MODULE)
        
    #--------------------------------------------
    def create_cmds(self):
        """
        First, this function creates the .signal_list and the fsdb.sh executable in the simulation directory.
        Then, it builds and returns the command-line to run vericom. It uses functions in vlog_gadget to do the job.
        """

        import gadgets.vlog as vlogger

        # get all variables
        self.vlog_defines = vlogger.get_defines(gvars.VLOG.DEFINES)
        self.flists      = vlogger.get_flists([it.flist_name for it in gvars.Vkits] + gvars.TB.FLISTS + ['.flist'])
        self.tab_files   = vlogger.get_tab_files(gvars.VLOG.TAB_FILES)

        # make a file with the tb_top in it, call it .signal_list
        if not os.path.exists(self.sim_dir):
            try:
                os.makedirs(self.sim_dir)
            except OSError:
                raise gadget.GadgetFailed("Unable to create %s" % self.sim_dir)

        with open(os.path.join(self.sim_dir, '.signal_list'), 'w') as sfile:
            print("0 %s" % self.tb_top, file=sfile)
            self.turds.append(os.path.abspath(sfile.name))

        # create the vericom command

        cmd = "vericom -quiet -lib %(vcomp_dir)s -logdir %(lib_dir)s/vericomLog " % self.__dict__
        cmd += " -smartinc -ssy -ssv -autoalias -sv +libext+.v+.sv+.vh"
        cmd += ' ' + ' '.join([self.vlog_defines, self.tab_files, self.flists])

        # make the vcomp.lib++ directory if necessary
        try:
            os.mkdir(self.lib_dir)
        except OSError:
            pass
            
        # return the command
        return gadget.GadgetCommand(cmd)

    #--------------------------------------------
    def check_dependencies(self):
        """
        Returns true if vericom needs to be run because the vericomLog/compiler.log file does not exist.
        """

        target = os.path.join(self.lib_dir, 'vericomLog/compiler.log')
        return not os.path.exists(target)
