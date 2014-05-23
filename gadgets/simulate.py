"""
Runs the simulation.
"""

from __future__ import print_function

import gadget
import gvars
import os
import schedule
import utils

Log = gvars.Log

class SimulateGadget(gadget.Gadget):
    """
    A Job that executes the simulation
    The test to run is contained in gvars.SIM.TEST
    """

    #--------------------------------------------
    def __init__(self):
        super(SimulateGadget, self).__init__()

        self.schedule_phase = 'simulate'

        self.name      = gvars.SIM.DIR
        self.resources = gvars.PROJ.LSF_SIM_LICS
        self.queue     = 'verilog'

        # ensure that the SIM.TEST exists!
        test_file = os.path.join('tests', (gvars.SIM.TEST + '.sv'))
        if utils.check_files_exist(test_file) == 0:
            raise gadget.GadgetFailed("%s is not a legal test." % test_file)

        # if verbosity is 0 or --interactive is on the command-line, then run interactively
        if gvars.SIM.DBG == 0 or gvars.SIM.INTERACTIVE:
            self.interactive = True
        else:
            self.interactive = False

        self.runmod_modules = [gvars.PROJ.MODULES[key] for key in gvars.VLOG.MODULES]
        self.tb_top         = gvars.TB.TOP
        self.sim_dir        = os.path.join('sim', self.name)
        self.vcomp_dir      = gvars.VLOG.VCOMP_DIR
        self.simv_executable = os.path.join(self.vcomp_dir, 'simv')
        if gvars.SIM.GUI != 'verdi':
            self.sim_exe        = self.simv_executable
        else:
            self.sim_exe    = 'verdi'
            self.runmod_modules.append(gvars.PROJ.MODULES['verdi'])

        # if necessary, add Vericom to the list of gadgets, among other things
        if gvars.SIM.WAVE == 'fsdb':
            self.handle_fsdb()

        # set the simulation's seed
        if gvars.SIM.SEED == 0:
            import random
            gvars.SIM.SEED = random.getrandbits(32)

        # create rerun/qrun scripts when we're done
        from gadgets.rerun import RerunGadget
        rerun = RerunGadget(self.sim_dir)
        schedule.add_gadget(rerun)

        # run simrpt when we're done
        from gadgets.simrpt import SimrptGadget
        simrpt = SimrptGadget(self.sim_dir)
        schedule.add_gadget(simrpt)

        if not os.path.exists(self.sim_dir):
            try:
                os.makedirs(self.sim_dir)
            except OSError:
                raise gadget.GadgetFailed("Unable to create %s" % self.sim_dir)

    #--------------------------------------------
    def create_cmds(self):
        """
        Returns the commands as a list of strings.
        """

        # ensure that executable has been built
        if utils.check_files_exist(self.simv_executable) == 0:
            raise gadget.GadgetFailed("Simulation Executable %s does not exist." % self.simv_executable)

        sim_cmd = self.sim_exe
        sim_cmd += " +UVM_TESTNAME=%s_test_c" % gvars.SIM.TEST
        sim_cmd += " -l %s/logfile" % self.sim_dir
        sim_cmd += " +seed=%d" % gvars.SIM.SEED
        sim_cmd += " +sim_dir=%s" % self.sim_dir

        # options
        sim_cmd += " +UVM_VERBOSITY=%s" % gvars.SIM.DBG
        sim_cmd += " +err=%d +UVM_MAX_QUIT_COUNT=%d,0" % (gvars.SIM.ERRBRK, gvars.SIM.ERRBRK)

        if gvars.SIM.TOPO:
            sim_cmd += " +UVM_TOPO_DEPTH=%d" % gvars.SIM.TOPO

        if gvars.SIM.WDOG:
            sim_cmd += " +wdog=%d" % gvars.SIM.WDOG

        if gvars.SIM.GUI == 'dve':
            sim_cmd += ' -gui'
        elif gvars.SIM.GUI == 'verdi':
            sim_cmd += ' -simType vcs -simBin %s' % self.simv_executable

        if gvars.SIM.WAVE == 'vpd':
            wave_script_name = os.path.join(self.sim_dir, '.wave_script')
            sim_cmd += " +vpdon +vpdfile+%s/waves.vpd " % (self.sim_dir)
            sim_cmd += " -ucli -do %s +vpdupdate +vpdfilesize+2048" % wave_script_name
            self.handle_vpd(wave_script_name)
        elif gvars.SIM.WAVE == 'fsdb':
            sim_cmd += " +fsdb_trace +fsdb_outfile=%(sim_dir)s/verilog.fsdb +fsdb_depth=0 " % self.__dict__
            sim_cmd += " +fsdb+trans_begin_callstack +sps_enable_port_recording +fsdbTrans +fsdbLogOff +fsdb+dumpoff+2147483640"

        if gvars.SIM.SVFCOV:
            svfcov_value = self.handle_svfcov(gvars.SIM.SVFCOV)
            if svfcov_value:
                cm_name = gvars.SIM.DIR + "." + str(utils.get_time_int())
                sim_cmd += " +svfcov=%0d -covg_dump_range -cm_dir coverage/coverage -cm_name %s" % (svfcov_value, cm_name)

        # add simulation command-line options
        if gvars.SIM.OPTS:
            if gvars.SIM.GUI == 'verdi':
                sim_cmd += " -simOpt"
            sim_cmd += " " + gvars.SIM.OPTS

        if gvars.SIM.PLUSARGS:
            sim_cmd += " " + ' '.join(['+%s' % it for it in gvars.SIM.PLUSARGS])

            
        return gadget.GadgetCommand(sim_cmd)
        
    #--------------------------------------------
    def handle_vpd(self, wave_script_name):
        "Create the .wave_script file that VCS will do."
        with utils.open(wave_script_name, 'w') as wfile:
            print("""set d [string map {logfile waves.vpd} [senv logFilename] ]
            dump -file $d -type vpd
            dump -add %(tb_top)s -depth 0
            run""" % self.__dict__, file=wfile)
            self.turds.append(os.path.abspath(wfile.name))
            
    #--------------------------------------------
    def handle_fsdb(self):
        self.runmod_modules.append(gvars.PROJ.MODULES['verdi'])

        # Run vericom gadget during pre_simulate
        import gadgets.vericom
        import gadgets.fsdb
        import schedule
        vericom = gadgets.vericom.VericomGadget(self.sim_dir)
        schedule.add_gadget(vericom)

        fsdb = gadgets.fsdb.FsdbGadget(self.sim_dir)
        schedule.add_gadget(fsdb)

    #--------------------------------------------
    def handle_svfcov(self, svfcov):
        "Determine what value to add to the command-line for +svfcov"

        value = 0
        if type(svfcov) is str:
            spl = svfcov.split(',')
            if 'all' in spl:
                value = 15
            else:
                if 'func' in spl:
                    value |= 1
                if 'bits' in spl:
                    value |= 2
                if 'vals' in spl:
                    value |= 8
        elif type(svfcov) is int:
            value = svfcov

        return value

