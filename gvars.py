"""
Contains all of the global variables.
"""

import sys
import var_type

# Keys is the guideline by how Vars will be created. Each key is the variable name and has the default value, the type, and a comment on its purpose.
# Vars is a dictionary of values, to be filled in with values by setup-files like project.py and tb.py.
# Setup files do not assign to Vars directly, rather, they assign to variables with the same name as the keys of Vars.
__DEFAULT_VAL__, __TYPES__, __COMMENT__ = range(3)

VTYPES = {
    # How to compile and run with VCS
    'VLOG' : {
        # Name             (default, possible types)   Help
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
        'OPTS'           : ["", (str,),       "Added to the simulation command-line (not overridden by --simopts)"],
        'PLUSARGS'       : [[], (list,),      "Added to the simulation command-line (all preceded by +)"],
        'TEST'           : ("basic", (str,),  "The name of the test to be run.")
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

########################################################################################
def get_vtype(vtype):
    return getattr(sys.modules[__name__], vtype)

