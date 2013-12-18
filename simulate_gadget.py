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

        self.quiet = True
        self.runmod_modules = gvars.Vars['SIM_MODULES']

    #--------------------------------------------
    def create_cmds(self):
        """
        Returns the commands as a list of strings.
        """

        Log.info("Simulating...%s" % self.name)

        sim_cmd = os.path.join(gvars.Vars['BLD_VCOMP_DIR'], 'sim.exe')
        sim_cmd += " +UVM_TESTNAME=%s_test_c" % gvars.Options.test

        sim_dir = os.path.join('sim', self.name)
        sim_cmd += " -l %s/logfile" % sim_dir

        if gvars.Options.seed == 0:
            import random
            gvars.Options.seed = random.getrandbits(32)
        sim_cmd += " +seed=%d" % gvars.Options.seed

        if not os.path.exists(sim_dir):
            try:
                os.makedirs(sim_dir)
            except OSError:
                import sys
                Log.critical("Unable to create %s" % sim_dir)
                sys.exit(254)

        # OPTIONS
        sim_cmd += " +UVM_VERBOSITY=%s" % gvars.Options.verb

        if gvars.Options.topo:
            sim_cmd += " +UVM_TOPO_DEPTH=%d" % gvars.Options.topo

        if gvars.Options.wdog:
            sim_cmd += " +wdog=%d" % gvars.Options.wdog

        if gvars.Options.gui:
            sim_cmd += gvars.Vars['SIM_GUI']

        if gvars.Options.wave:
            sim_cmd += " +vpdon +vpdfile+%s/waves.vpd " % (sim_dir)
            sim_cmd += " -ucli -do .wave_script +vpdupdate +vpdfilesize+2048"

            # create the waves script
            with open(os.path.join(sim_dir, '.wave_script'), 'w') as file:
                print >>file, "set d [string map {logfile waves.vpd} [senv logFilename] ]"
                print >>file, "dump -file $d -type vpd"
                print >>file, "dump -add %s -depth 0" % gvars.Vars['TB_TOP']
                print >>file, "run"

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

