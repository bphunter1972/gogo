"""
Contains all of the global variables.
"""

import os
from vkit import Vkit

# Keys is the guideline by how Vars will be created. Each key is the variable name and has the default value, the type, and a comment on its purpose.
# Vars is a dictionary of values, to be filled in with values by setup-files like project.py and tb.py.
# Setup files do not assign to Vars directly, rather, they assign to variables with the same name as the keys of Vars.
__DEFAULT_VAL__, __TYPES__, __COMMENT__ = range(3)
Keys = {
    # Testbench-related variables
    'VKITS'           : ([], (list,),   "Vkits that this testbench relies upon, in order"),
    'STATIC_VKITS'    : ([], (list,),   "Vkits that should be considered static for the purposes of partition compilation"),
    'FLISTS'          : ([], (list,),   "Testbench FLISTs to include"),
    'TB_TOP'          : ("", (str,),    "The module name of the top-level of the testbench"),
    
    # Build-related
    'BLD_PARTITION'   : ("", (str,),    "When 'auto', compiles and creates a vcs_partition_config.file. If 'custom', runs in partition-compile mode with file named 'partition.cfg'. Otherwise, 'off'."),
    'BLD_PARALLEL'    : (0, (int,),     "The number of cores on which to compile in parallel (partition-compile only)"),
    'BLD_TOOL'        : ("", (str,),    "Command needed to run a build"),
    'BLD_MODULES'     : ([], (list,),   "Added to runmod for all builds"),
    'BLD_OPTIONS'     : ("", (str,),    "Additional build options"),
    'BLD_TAB_FILES'   : ([], (list,),   "PLI files that should also be added to the build command-line (-P <name>)"),
    'BLD_SO_FILES'    : ([], (list,),   "Shared Objects that will be added to the build command-line (-LDFLAGS '<all>')"),
    'BLD_ARC_LIBS'    : ([], (list,),   ".a/.o archive libraries that will be added to the build command-line"),
    'BLD_VCOMP_DIR'   : ("", (str,),    "The name of the compile directory"),
    'BLD_DEFINES'     : ([], (list,),   "All +defines as needed"),
    
    # Simulation-related
    'SIM_MODULES'     : ([], (list,),   "List of modules, added to runmod for all sims"),
    'SIM_GUI'         : ("", (str,),    "Add this to simulation command-line when you want to run in GUI mode"),
    'SIMOPTS'         : ("", (str,),    "Added to the simulation command-line (not overridden by --simopts)"),
    'SIM_PLUSARGS'    : ([], (list,),   "Added to the simulation command-line (all preceded by +)"),
    'SIM_WAVE_OPTIONS': ("", (str,),    "Run-time options"),
    
    # LSF-related
    'LSF_BLD_LICS'    : ([], (list,),   "Additional licenses used for building"),
    'LSF_SIM_LICS'    : ([], (list,),   "Additional licences used for simulation"),
    
    # Cleaning-related
    'CLEAN_DIRS'      : ([], (list,),   "Names of directories to delete"),
    'CLEAN_FILES'     : ([], (list,),   "Names of files to delete"),
    
    # Miscellaneous
    'UVM_REV'         : ("1_1d", (str,), "UVM Revision to use"),
}

Vars = {}

# These keys do NOT need to be specified
OptionalKeys = ('STATIC_VKITS', 'SIMOPTS', 'SIM_PLUSARGS', 'BLD_OPTIONS', 'BLD_PARTITION', 'BLD_PARALLEL', 
    'BLD_SO_FILES', 'BLD_TAB_FILES', 'BLD_ARC_LIBS', 'BLD_DEFINES', 'LSF_SIM_LICS', 'LSF_BLD_LICS')

# All of the command-line options from parse_args
Options = None

# the Logger
Log = None

# The Vkit and StaticVkit arrays of Vkit classes
Vkits = StaticVkits = None

########################################################################################
def setup_globals():
    """
    Set up the Vars dictionary with imported information from project and the local tb.py
    """

    global Vars, Vkits, StaticVkits

    # The names of all the library files that will be imported
    libraries = ('project', Options.tb)

    # Initialize Vars with default values from Keys
    for key in Keys:
        Vars[key] = Keys[key][__DEFAULT_VAL__]

    def import_lib(mod_name):
        try:
            lib = __import__(mod_name)
        except ImportError:
            import sys
            path_str = 'PYTHONPATH = '
            for p in sys.path:
                path_str += '\n\t%s' % p
            Log.critical("'%s.py' file not found! Modify your PYTHONPATH?\n%s" % (mod_name, path_str))

        lib_dict = lib.__dict__
        for key in Vars:
            if key in lib_dict:
                # check that the type is correct
                if type(lib_dict[key]) not in Keys[key][__TYPES__]:
                    Log.critical("Expected type(s) %s for %s, but saw %s instead.", 
                        Keys[key][__TYPES__], key, type(lib_dict[key]))

                if type(Vars[key]) == str:
                    # concatenate with a space if it's already set to something
                    Vars[key] = Vars[key] + ' ' + lib_dict[key] if (Vars[key] != "" and lib_dict[key] != Vars[key]) else lib_dict[key]
                else:
                    Vars[key] += lib_dict[key]

    map(import_lib, libraries)

    Vars['VKITS_DIR'] = '../vkits'
    Vars['UVM_DIR']   = os.path.join(Vars['VKITS_DIR'], 'uvm', Vars['UVM_REV'])

    # TODO: Fix this checker
    # for key in Vars:
    #     if Vars[key] is None and key not in OptionalKeys:
    #         Log.error("%s is not defined in any of %s." % (key, ','.join(["%s.py" % it for it in libraries])))

    # check that some dictionary items only contain correct values
    if Vars['BLD_PARTITION'] and Vars['BLD_PARTITION'] not in ('custom', 'auto', 'off'):
        Log.critical("BLD_PARTITION value '%s' must be one of 'custom', 'auto', or 'off'" % Vars['BLD_PARTITION'])

    # build the Vkits and StaticVkits arrays
    Vkits = [Vkit(it) for it in Vars['VKITS']]
    uvm_flist = os.path.join(Vars['UVM_DIR'], 'uvm.flist')
    uvm_vkit = Vkit(uvm_flist)
    Vkits.insert(0, uvm_vkit)
    StaticVkits = [Vkit(it) for it in Vars['STATIC_VKITS']]
    StaticVkits.insert(0, uvm_vkit)

########################################################################################
def print_keys():
    from textwrap import wrap
    print """
Assign variables with the following names in either project.py or tb.py.

project.py : There should be one of these per-project.
tb.py      : There should be one (or more) of these per-testbench.

If more than 1 tb.py are created, select which tb.py to use with the --tb 
command-line option.
"""

    for key in sorted(Keys.keys()):
        txt = wrap(Keys[key][__COMMENT__], 60)
        print("%-18s%s" % (key, txt[0]))

        for line in txt[1:]:
            print("%-18s%s" % (' ', line))


########################################################################################
# These variables supply gogo with extendability. Add your own gadgets to these lists.
pre_build_gadgets = []
post_build_gadgets = []
