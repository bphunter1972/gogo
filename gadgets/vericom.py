import gadget
import gvars
import os.path

class VericomGadget(gadget.Gadget):
    """Runs vericom for Verdi usage"""

    def __init__(self, sim_dir):
        super(VericomGadget, self).__init__()

        self.schedule_phase = 'pre_simulate'

        self.name = 'vericom'
        self.runmod_modules.append(gvars.Vars['VERDI_MODULE'])
        self.sim_dir = sim_dir
        self.tb_top = gvars.Vars['TB_TOP']
        self.interactive = True
        self.queue = 'build'
        
    #--------------------------------------------
    def create_cmds(self):
        """
        First, this function creates the .signal_list and the fsdb.sh executable in the simulation directory.
        Then, it builds and returns the command-line to run vericom. It uses functions in build_gadget to do the job.
        """

        import gadgets.build as builder

        # get all variables
        vcomp_dir = gvars.Vars['BLD_VCOMP_DIR']
        bld_defines = builder.get_defines()
        flists = builder.get_flists()
        cmp_opts = gvars.Options.cmpopts or ''
        tab_files = builder.get_tab_files()
        tb_top = gvars.Vars['TB_TOP']
        lib_dir = "%(vcomp_dir)s.lib++" % locals()
        sim_dir = self.sim_dir

        # make a file with the tb_top in it, call it .signal_list
        with open(os.path.join(self.sim_dir, '.signal_list'), 'w') as file:
            print >>file, "0 %s" % self.tb_top

        # create an fsdb.sh executable that people can use to run Verdi
        fsdb_name = os.path.join(self.sim_dir, 'fsdb.sh')
        with open(fsdb_name, 'w') as fsdb_file:
            print >>fsdb_file, "runmod verdi -rcFile ~/.novas.rc -ssf %(sim_dir)s/verilog.fsdb -logdir %(sim_dir)s/verdiLog -top %(tb_top)s -nologo -lib %(vcomp_dir)s" % locals()
        os.chmod(fsdb_name, 0o777)

        # create the vericom command

        cmd = "vericom -quiet -lib %(vcomp_dir)s -logdir %(lib_dir)s/vericomLog " % locals()
        cmd += " -smartinc -ssy -ssv -autoalias -sv +libext+.v+.sv+.vh"
        cmd += " %(bld_defines)s %(tab_files)s %(cmp_opts)s %(flists)s" % locals()

        # make the vcomp.lib++ directory if necessary
        try:
            os.mkdir(lib_dir)
        except OSError:
            pass
            
        # return the command
        return [cmd]
