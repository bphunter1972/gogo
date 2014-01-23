"""
Contains all of the global variables.
"""

import sys
import var_type

# Keys is the guideline by how Vars will be created. Each key is the variable name and has the default value, the type, and a comment on its purpose.
# Vars is a dictionary of values, to be filled in with values by setup-files like project.py and tb.py.
# Setup files do not assign to Vars directly, rather, they assign to variables with the same name as the keys of Vars.
VTYPES = {
    # How to compile and run with VCS
    'VLOG' : {
        # Name             (default, possible types)   Help
        'COMPTYPE'       : ['p', (str,),      "The compile type for this testbench: (p)artition, (g)enip, (n)ormal 2-step."],
        'PART_CFG'       : ['.partition.cfg', (str,), "The name of the partition compile configuration file, when COMPTYPE is 'p'"],
        'PARALLEL'       : [0, (int,),        "The number of cores on which to compile in parallel (partition-compile only)"],
        'TOOL'           : ["", (str,),       "Command needed to run a build"],
        'MODULES'        : [[], (list,),      "Added to runmod for all builds"],
        'OPTIONS'        : ["", (str,),       "Build options for both VCS and VLOGAN"],
        'VCS_OPTIONS'    : ["", (str,),       "Build options for VCS only"],
        'VLOGAN_OPTIONS' : ["", (str,),       "Build options for VLOGAN only"],
        'TAB_FILES'      : [[], (list,),      "PLI files that should also be added to the build command-line (-P <name>)"],
        'SO_FILES'       : [[], (list,),      "Shared Objects that will be added to the build command-line (-LDFLAGS '<all>')"],
        'ARC_LIBS'       : [[], (list,),      ".a/.o archive libraries that will be added to the build command-line"],
        'VCOMP_DIR'      : ["", (str,),       "The name of the compile directory"],
        'DEFINES'        : [[], (list,),      "All +defines as needed"],
        'IGNORE_WARNINGS': [[], (list,),      "Warnings that should be ignored by VCS during vlog."],
        'GUI'            : ["", (str,),       "Add this to simulation command-line when you want to run in GUI mode"],
    },

    # Simulation Options
    'SIM' : {
        'OPTS'           : ["", (str,),       "Added to the simulation command-line"],
        'PLUSARGS'       : [[], (list,),      "Added to the simulation command-line (all preceded by +)"],
        'TEST'           : ["basic", (str,),  "The name of the test to be run."],
        'SEED'           : [1, (int,),        "The seed to use for the simulation, or 0 for random (TODO)"],
        'DBG'            : [0, (int,str),     "Debug level of simulation"],
        'INTERACTIVE'    : [0, (int,bool),    "Turn interactive on (1) or off (0)"],
        'WDOG'           : [0, (int,),        "Time (in ns) at which the testbench will watchdog timeout (or zero for no watchdog)."], 
        'GUI'            : [0, (int,bool),    "Run VCS in GUI mode with DVE"],
        'DIR'            : ['', (str,),       "Specify alternate directory for results."],
        'TOPO'           : [0, (int,),        "Print UVM topology at this depth."],
        'SVFCOV'         : [0, (int,bool),    "Run with SV Functional Coverage"],
        'WAVE'           : [None, (str,),     "Dump waves to 'fsdb' or 'vpd' file."]
    },

    # Testbench Options
    'TB' : {
        'VKITS'          : [[], (list,),      "Vkits that this testbench relies upon, in order"],
        'STATIC_VKITS'   : [[], (list,),      "Vkits that should be considered static for the purposes of partition compilation"],
        'PARTITION_CELLS': [[], (list,),      "Cells that should be separate partitions for partition compilation"],
        'FLISTS'         : [[], (list,),      "Testbench FLISTs to include"],
        'TOP'            : ["", (str,),       "The module name of the top-level of the testbench"],
        'INCDIRS'        : [[], (list,),      "The list of +incdirs to create for this testbench"],
        'LIBRARIES'      : [[], (list,),      "The list of library directories to create for this testbench"],
    },

    # Miscellaneous Project settings
    'PROJ' : {
        'RUNMOD_MODULES'   : [[], (list,),      "List of modules, added to runmod for all sims"],
        'LSF_VLOG_LICS'    : [[], (list,),      "Additional licenses used for building"],
        'LSF_SIM_LICS'     : [[], (list,),      "Additional licences used for simulation"],
        'CLEAN_DIRS'       : [[], (list,),      "Names of directories to delete"],
        'CLEAN_FILES'      : [[], (list,),      "Names of files to delete"],
        'UVM_REV'          : ["1_1d", (str,),   "UVM Revision to use"],
        'VERDI_MODULE'     : ["", (str,),       "Module to load for Verdi usage."],
        'VKITS_DIR'        : ["", (str,),       "The location of all vkits directories"],
    }
}

# This code creates the variables PROJ, VLOG, SIM, etc.
SIM = TB = VLOG = PROJ = None # these just get rid of any lint errors
for key in VTYPES.keys():
    setattr(sys.modules[__name__], key, var_type.VarType(VTYPES[key], key))

# All of the command-line options from parse_args
Options = None

# the Logger
Log = None

# The Vkit and StaticVkit arrays of Vkit classes
Vkits = StaticVkits = None

# The root directory of the project
RootDir = None

# Variables that were Culled from the Command Line
CommandLineVariables = None

########################################################################################
def get_vtype(vtype):
    return getattr(sys.modules[__name__], vtype)

########################################################################################
def command_line_assignment(vars):
    "Assign variables based on the command-line arguments that look like assignments"

    var_type.Log = Log

    # perform work on any SIM.TEST first, then check rest of command-line work to be done
    test_work = None
    cl_work = []

    #--------------------------------------------
    def parse_var(var):
        if '+=' in var:
            (vname, value) = var.split('+=', 1)
            use_incr = True
        elif '=' in var:
            (vname, value) = var.split('=', 1)
            use_incr = False

        try:
            (vtype_name, var_name) = vname.split('.')
        except ValueError:
            (vtype_name, var_name) = ('SIM', vname)

        # check that vtype_name is legal
        if vtype_name not in VTYPES.keys():
            Log.critical("Illegal vtype name: '%s'" % vtype_name)
        vtype = get_vtype(vtype_name)

        # either append to or set the value
        func = vtype.incr_value if use_incr else vtype.set_value
        return (var_name, value, func)

    #--------------------------------------------
    for var in vars:
        var_name, value, func = parse_var(var)
        if var_name == 'TEST':
            test_work = [var_name, value, func]
        else:
            cl_work.append([var_name, value, func])

    # assign test-name first
    if test_work:
        test_work[2](test_work[0], test_work[1])

    # assign test-name to directory
    SIM.DIR = SIM.TEST

    # perform all other assignements
    for work in cl_work:
        work[2](work[0], work[1])

########################################################################################
def setup_globals():
    """
    Set up the variables in gvars by importing all of the import files for this testbench
    """

    import var_type
    import gadget
    from area_utils import calcRootDir
    global RootDir

    var_type.Log = Log
    gadget.Log = Log
    RootDir = calcRootDir()

    # The names of all the library files that will be imported
    libraries = ('project', Options.tb)

    #--------------------------------------------
    def import_lib(mod_name):
        try:
            __import__(mod_name)
        except ImportError:
            Log.critical("'%s.py' file not found. Make sure you are in a testbench directory and that your PYTHONPATH is set correctly." % mod_name)

    # import each of the libraries
    map(import_lib, libraries)

    # now, handle the variables that were on the command-line
    try:
        command_line_assignment(CommandLineVariables)
    except Exception as ex:
        if Options.dbg:
            raise
        Log.critical("Unable to parse command-line: %s" % ex)

    # check that all global variables are ok
    check_vars()

########################################################################################
def check_vars():
    if VLOG.COMPTYPE.lower() in ('p', 'part', 'partition'):
        VLOG.COMPTYPE = 'partition'
    elif VLOG.COMPTYPE.lower() in ('g', 'gen', 'genip'):
        VLOG.COMPTYPE = 'genip'
    elif VLOG.COMPTYPE.lower() in ('n', 'norm', 'normal'):
        VLOG.COMPTYPE = 'normal'
    else:
        Log.critical("VLOG.COMPTYPE value of %s is not recognized." % VLOG.COMPTYPE)

    Log.info("Running with VLOG.COMPTYPE value of %s" % VLOG.COMPTYPE)

########################################################################################
def setup_vkits():
    "Set up the vkits in gvars"

    global Vkits, StaticVkits    
    from vkit import Vkit

    Vkits = [Vkit(it) for it in TB.VKITS]
    uvm_vkit = Vkit({'NAME':'uvm', 'DEPENDENCIES':[], 'DIR':'uvm/1_1d'})
    Vkits.insert(0, uvm_vkit)

    try:
        StaticVkits = [it for it in Vkits if it.name in TB.STATIC_VKITS]
    except AttributeError:
        Log.critical("A Vkit below has no name:\n%s" % Vkits)
