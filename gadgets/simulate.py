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

        self.runmod_modules = gvars.PROJ.RUNMOD_MODULES
        self.tb_top         = gvars.TB.TOP
        self.sim_dir        = os.path.join('sim', self.name)
        self.vcomp_dir      = gvars.VLOG.VCOMP_DIR
        self.sim_exe        = os.path.join(self.vcomp_dir, 'simv')

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
        if utils.check_files_exist(self.sim_exe) == 0:
            raise gadget.GadgetFailed("Simulation Executable %s does not exist." % self.sim_exe)

        sim_cmd = self.sim_exe
        sim_cmd += " +UVM_TESTNAME=%s_test_c" % gvars.SIM.TEST
        sim_cmd += " -l %s/logfile" % self.sim_dir
        sim_cmd += " +seed=%d" % gvars.SIM.SEED
        sim_cmd += " +sim_dir=%s" % self.sim_dir

        # options
        sim_cmd += " +UVM_VERBOSITY=%s" % gvars.SIM.DBG

        if gvars.SIM.TOPO:
            sim_cmd += " +UVM_TOPO_DEPTH=%d" % gvars.SIM.TOPO

        if gvars.SIM.WDOG:
            sim_cmd += " +wdog=%d" % gvars.SIM.WDOG

        if gvars.SIM.GUI:
            sim_cmd += gvars.SIM.GUI

        if gvars.SIM.WAVE == 'vpd':
            wave_script_name = os.path.join(self.sim_dir, '.wave_script')
            sim_cmd += " +vpdon +vpdfile+%s/waves.vpd " % (self.sim_dir)
            sim_cmd += " -ucli -do %s +vpdupdate +vpdfilesize+2048" % wave_script_name
            self.handle_vpd(wave_script_name)
        elif gvars.SIM.WAVE == 'fsdb':
            sim_cmd += " +fsdb_trace +memcbk +fsdb+trans_begin_callstack +sps_enable_port_recording"
            sim_cmd += " +fsdb_siglist=%(sim_dir)s/.signal_list +fsdb_outfile=%(sim_dir)s/verilog.fsdb" % self.__dict__

        if gvars.SIM.SVFCOV:
            cm_name = gvars.SIM.DIR + "." + str(utils.get_time_int())
            sim_cmd += " +svfcov=%0d -covg_dump_range -cm_dir coverage/coverage -cm_name %s" % (gvars.SIM.SVFCOV, cm_name)

        # add simulation command-line options
        if gvars.SIM.OPTS:
            sim_cmd += " " + gvars.SIM.OPTS

        if gvars.SIM.PLUSARGS:
            sim_cmd += " " + ' '.join(['+%s' % it for it in gvars.SIM.PLUSARGS])

        return [sim_cmd]
        
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
        self.runmod_modules.append(gvars.PROJ.VERDI_MODULE)

        # Run vericom gadget during pre_simulate
        import gadgets.vericom
        import gadgets.fsdb
        import schedule
        vericom = gadgets.vericom.VericomGadget(self.sim_dir)
        schedule.add_gadget(vericom)

        fsdb = gadgets.fsdb.FsdbGadget(self.sim_dir)
        schedule.add_gadget(fsdb)
