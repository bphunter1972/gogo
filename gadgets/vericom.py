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
        self.tb_top         = gvars.Vars['TB_TOP']
        self.interactive    = True
        self.queue          = 'build'
        self.vcomp_dir      = gvars.Vars['VLOG_VCOMP_DIR']
        self.lib_dir        = "%(vcomp_dir)s.lib++" % self.__dict__
        self.runmod_modules.append(gvars.Vars['VERDI_MODULE'])
        
    #--------------------------------------------
    def create_cmds(self):
        """
        First, this function creates the .signal_list and the fsdb.sh executable in the simulation directory.
        Then, it builds and returns the command-line to run vericom. It uses functions in vlog_gadget to do the job.
        """

        import gadgets.vlog as vlogger

        # get all variables
        self.VLOG_defines = vlogger.get_defines()
        self.flists      = vlogger.get_flists()
        self.cmp_opts    = gvars.Options.cmpopts or ''
        self.tab_files   = vlogger.get_tab_files()

        # make a file with the tb_top in it, call it .signal_list
        if not os.path.exists(self.sim_dir):
            try:
                os.makedirs(self.sim_dir)
            except OSError:
                import sys
                Log.critical("Unable to create %s" % self.sim_dir)
                sys.exit(254)

        with open(os.path.join(self.sim_dir, '.signal_list'), 'w') as file:
            print >>file, "0 %s" % self.tb_top
            self.turds.append(os.path.abspath(file.name))

        # create an fsdb.sh executable that people can use to run Verdi
        fsdb_name = os.path.join(self.sim_dir, 'fsdb.sh')
        with open(fsdb_name, 'w') as fsdb_file:
            print >>fsdb_file, "runmod verdi -rcFile ~/.novas.rc -ssf %(sim_dir)s/verilog.fsdb -logdir %(sim_dir)s/verdiLog -top %(tb_top)s -nologo -lib %(vcomp_dir)s $*" % self.__dict__
        os.chmod(fsdb_name, 0o777)

        # create the vericom command

        cmd = "vericom -quiet -lib %(vcomp_dir)s -logdir %(lib_dir)s/vericomLog " % self.__dict__
        cmd += " -smartinc -ssy -ssv -autoalias -sv +libext+.v+.sv+.vh"
        cmd += " %(VLOG_defines)s %(tab_files)s %(cmp_opts)s %(flists)s" % self.__dict__

        # make the vcomp.lib++ directory if necessary
        try:
            os.mkdir(self.lib_dir)
        except OSError:
            pass
            
        # return the command
        return [cmd]

    #--------------------------------------------
    def check_dependencies(self):
        """
        Returns true if vericom needs to be run.
        """

        from pymake import pymake

        all_sources = gvars.get_all_sources('verilog')
        target = os.path.join(self.lib_dir, 'vericomLog/compiler.log')

        answer = pymake(targets=target, sources=all_sources, get_cause=True)
        if answer.result:
            Log.info("vericom does need to run: %s" % answer)
        return answer.result
