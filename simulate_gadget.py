"""
An gadget class that executes the simulation
"""

import gadget
import gvars
import os

Log = gvars.Log

class SimulateGadget(gadget.Gadget):
    """
    A Job that executes the simulation
    The test to run is contained in gvars.Options.test
    """

    #--------------------------------------------
    def __init__(self):
        super(SimulateGadget, self).__init__()
        
        self.name = gvars.Options.dir if gvars.Options.dir else gvars.Options.test
        self.resources = gvars.Vars['LSF_SIM_LICS']
        self.queue = 'verilog'

        # if verbosity is 0 or --interactive is on the command-line, then run interactively
        if gvars.Options.verb == 0 or gvars.Options.interactive:
            self.interactive = True
        else:
            self.interactive = False

        self.quiet = False
        self.runmod_modules = gvars.Vars['SIM_MODULES']

        self.sim_dir = os.path.join('sim', self.name)

        Log.info("waves = %s" % gvars.Options.wave)

    #--------------------------------------------
    def create_cmds(self):
        """
        Returns the commands as a list of strings.
        """

        Log.info("Simulating...%s" % self.name)

        sim_cmd = os.path.join(gvars.Vars['BLD_VCOMP_DIR'], 'simv')
        sim_cmd += " +UVM_TESTNAME=%s_test_c" % gvars.Options.test

        sim_cmd += " -l %s/logfile" % self.sim_dir

        if gvars.Options.seed == 0:
            import random
            gvars.Options.seed = random.getrandbits(32)
        sim_cmd += " +seed=%d" % gvars.Options.seed

        if not os.path.exists(self.sim_dir):
            try:
                os.makedirs(self.sim_dir)
            except OSError:
                import sys
                Log.critical("Unable to create %s" % self.sim_dir)
                sys.exit(254)

        # OPTIONS
        sim_cmd += " +UVM_VERBOSITY=%s" % gvars.Options.verb

        if gvars.Options.topo:
            sim_cmd += " +UVM_TOPO_DEPTH=%d" % gvars.Options.topo

        if gvars.Options.wdog:
            sim_cmd += " +wdog=%d" % gvars.Options.wdog

        if gvars.Options.gui:
            sim_cmd += gvars.Vars['SIM_GUI']

        if gvars.Options.wave == 'vpd':
            wave_script_name = os.path.join(self.sim_dir, '.wave_script')
            sim_cmd += " +vpdon +vpdfile+%s/waves.vpd " % (self.sim_dir)
            sim_cmd += " -ucli -do %s +vpdupdate +vpdfilesize+2048" % wave_script_name
            self.create_wave_script(wave_script_name)
        elif gvars.Options.wave == 'fsdb':
            sim_cmd += self.handle_verdi()

        if gvars.Options.svfcov:
            sim_cmd += " +svfcov"

        # add simulation command-line options
        if gvars.Vars['SIMOPTS']:
            sim_cmd += " " + gvars.Vars['SIMOPTS']
        if gvars.Options.simopts:
            sim_cmd += " " + gvars.Options.simopts

        if gvars.Vars['SIM_PLUSARGS']:
            sim_cmd += " " + ' '.join(['+%s' % it for it in gvars.Vars['SIM_PLUSARGS']])

        return [sim_cmd]

    #--------------------------------------------
    def create_wave_script(self, wave_script_name):
        "Create the .wave_script file that VCS will do."
        with open(wave_script_name, 'w') as file:
            print >>file, "set d [string map {logfile waves.vpd} [senv logFilename] ]"
            print >>file, "dump -file $d -type vpd"
            print >>file, "dump -add %s -depth 0" % gvars.Vars['TB_TOP']
            print >>file, "run"

    #--------------------------------------------
    def handle_verdi(self):
        Log.info("Handling verdi")

        self.runmod_modules.append(gvars.Vars['VERDI_MODULE'])
        str =  " +fsdb_siglist=%s/.signal_list" % self.sim_dir
        str += " +fsdb_outfile=%s/verilog.fsdb" % self.sim_dir
        str += " +fsdb_trace +memcbk +fsdb+trans_begin_callstack +sps_enable_port_recording"

        # make a file with the tb_top in it, call it .signal_list
        with open(os.path.join(self.sim_dir, '.signal_list'), 'w') as file:
            print >>file, "0 %s" % gvars.Vars['TB_TOP']

        return str
