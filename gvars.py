"""
Contains all of the global variables.
"""

import sys
import var_type
import os
import gadget
from area_utils import calcRootDir

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
        'MODULES'        : [[], (list,),      "Keys to PROJ.MODULES used to add to runmod for all builds"],
        'OPTIONS'        : ["", (str,),       "Build options for both VCS and VLOGAN"],
        'VCS_OPTIONS'    : ["", (str,),       "Build options for VCS only"],
        'VLOGAN_OPTIONS' : ["", (str,),       "Build options for VLOGAN only"],
        'TAB_FILES'      : [[], (list,),      "PLI files that should also be added to the build command-line (-P <name>)"],
        'SO_FILES'       : [[], (list,),      "Shared Objects that will be added to the build command-line (-LDFLAGS '<all>')"],
        'ARC_LIBS'       : [[], (list,),      ".a/.o archive libraries that will be added to the build command-line"],
        'VCOMP_DIR'      : ["", (str,),       "The name of the compile directory"],
        'DEFINES'        : [[], (list,),      "All +defines as needed"],
        'IGNORE_WARNINGS': [[], (list,),      "Warnings that should be ignored by VCS during vlog."],
    },

    # Simulation Options
    'SIM' : {
        'OPTS'           : ["", (str,),       "Added to the simulation command-line"],
        'PLUSARGS'       : [[], (list,),      "Added to the simulation command-line (all preceded by +)"],
        'TEST'           : ["basic", (str,),  "The name of the test to be run."],
        'SEED'           : [1, (int,),        "The seed to use for the simulation, or 0 for random (TODO)"],
        'DBG'            : [0, (int,str),     "Debug level of simulation"],
        'MODULES'        : [[], (list,),      "Keys to PROJ.MODULES used to add to runmod for all sims"],
        'INTERACTIVE'    : [0, (int,bool),    "Turn interactive on (1) or off (0)"],
        'WDOG'           : [0, (int,),        "Time (in ns) at which the testbench will watchdog timeout (or zero for no watchdog)."], 
        'GUI'            : ['', (str,),       "Run VCS in GUI mode with (dve) or (verdi)"],
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
        'CSR_FILES'      : [[], (list,),      "The list of .csr files required for this testbench"],
    },

    # Miscellaneous Project settings
    'PROJ' : {
        'MODULES'          : [{}, (dict,),      "Dictionary of modules, with key equal to toolname, added to all runmod commands"],
        'LSF_VLOG_LICS'    : [[], (list,),      "Additional licenses used for building"],
        'LSF_SIM_LICS'     : [[], (list,),      "Additional licences used for simulation"],
        'CLEAN_DIRS'       : [[], (list,),      "Names of directories to delete"],
        'CLEAN_FILES'      : [[], (list,),      "Names of files to delete"],
        'UVM_REV'          : ["1_1d", (str,),   "UVM Revision to use"],
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

# The directory that will be used to store all temporary files
GogoDir = None

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
        elif var_name == 'PLUSARGS':
            # as a list, PLUSARGS is special
            values = value.split(',')
            func(var_name, values)
        else:
            cl_work.append([var_name, value, func])

    # assign test-name first
    if test_work:
        test_work[2](test_work[0], test_work[1])

    # assign test-name to directory
    SIM.DIR = SIM.TEST

    # perform all other assignements
    for name, value, func in cl_work:
        func(name, value)

########################################################################################
def setup_globals():
    """
    Set up the variables in gvars by importing all of the import files for this testbench
    """

    global RootDir
    global GogoDir

    var_type.Log = Log
    gadget.Log = Log
    RootDir = calcRootDir()

    # create a symbolic link called 'project' to the Root directory, if one does not ealready exist
    try:
        os.symlink(RootDir, 'project')
    except OSError:
        pass

    # set the name of the gogo directory where all turd files are kept
    GogoDir = os.path.join(RootDir, '.gogo')

    # The names of all the library files that will be imported
    libraries = ['project', Options.tb]

    # if any end in .py, then strip that
    libraries = [it.replace('.py', '') for it in libraries]
    
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

    # These options are not yet available
    if SIM.GUI == 'verdi':
        Log.critical("SIM.GUI=verdi is not yet supported")
        
########################################################################################
def setup_vkits():
    "Set up the vkits in gvars"

    global Vkits, StaticVkits    
    from gadgets.vkit import VkitGadget

    Log.debug("Running setup_vkits() with %s" % TB.VKITS)
    Vkits = [VkitGadget(it) for it in TB.VKITS]

    try:
        StaticVkits = [it for it in Vkits if it.name in TB.STATIC_VKITS]
    except AttributeError:
        Log.critical("A Vkit below has no name:\n%s" % Vkits)

########################################################################################
def get_vkits(vkit_names, get_all=False):
    """
    Returns the Vkits as named in vkit_names. 
    If get_all is true, returns all of their dependencies, and so on, as well. Then ensures
    uniqueness.
    """

    if not vkit_names:
        return []

    vkits = [it for it in Vkits if it.name in vkit_names]
    if get_all and vkits:
        Log.debug("Here in get_vkits with %s" % vkits)
        all_deps = [it.dependencies for it in vkits if it.dependencies]
        Log.debug("all_deps = %s" % all_deps)
        if all_deps and all_deps != [[]]:
            new_vkits = [get_vkits(it, True) for it in all_deps]
            for it in new_vkits:
                vkits.extend(it)
            Log.debug("Here in get_vkits with %s" % new_vkits)
            vkits = list(set(vkits))
            Log.debug("Now vkits=%s" % vkits)
    return vkits

########################################################################################
def get_env_variable(var, module=None):
    """
    Returns the value of an environment variable. If given the name of a module, loads that module first.
    """

    if module:
        cn_common_dir = os.environ['CN_COMMON_DIR']
        cmd = os.popen('tclsh %s/cad/modulecmd/current/modulecmd.tcl python load %s' % (cn_common_dir, module))
        exec(cmd)

    try:
        Log.debug("Returning for %s: %s" % (var, os.environ[var]))
        return os.environ[var]
    except KeyError:
        Log.critical("Unable to load variable %s with module %s" % (var, module))

