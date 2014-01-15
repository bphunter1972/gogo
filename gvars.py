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
    },

    'SIM' : {
        'MODULES'        : [[], (list,),      "List of modules, added to runmod for all sims"],
        'GUI'            : ["", (str,),       "Add this to simulation command-line when you want to run in GUI mode"],
        'OPTS'           : ["", (str,),       "Added to the simulation command-line (not overridden by --simopts)"],
        'PLUSARGS'       : [[], (list,),      "Added to the simulation command-line (all preceded by +)"],
        'WAVE_OPTIONS'   : ["", (str,),       "Run-time options"],
    },

    'TB' : {
        'VKITS'          : [[], (list,),      "Vkits that this testbench relies upon, in order"],
        'STATIC_VKITS'   : [[], (list,),      "Vkits that should be considered static for the purposes of partition compilation"],
        'PARTITION_CELLS': [[], (list,),      "Cells that should be separate partitions for partition compilation"],
        'FLISTS'         : [[], (list,),      "Testbench FLISTs to include"],
        'TOP'            : ["", (str,),       "The module name of the top-level of the testbench"],
        'INCDIRS'        : [[], (list,),      "The list of +incdirs to create for this testbench"],
        'LIBRARIES'      : [[], (list,),      "The list of library directories to create for this testbench"],
    },

    'PROJ' : {
        'LSF_VLOG_LICS'    : [[], (list,),      "Additional licenses used for building"],
        'LSF_SIM_LICS'     : [[], (list,),      "Additional licences used for simulation"],
        'CLEAN_DIRS'       : [[], (list,),      "Names of directories to delete"],
        'CLEAN_FILES'      : [[], (list,),      "Names of files to delete"],
        'UVM_REV'          : ["1_1d", (str,),   "UVM Revision to use"],
        'VERDI_MODULE'     : ["", (str,),       "Module to load for Verdi usage."],
        'VKITS_DIR'        : ["", (str,),       "The location of all vkits"],
    }
}

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

# A list of all the verilog sources (fore dependency checking)
AllVerilogSources = None

# # ########################################################################################
# # def print_keys():
# #     from textwrap import wrap
# #     print("""
# # Assign variables with the following names in either project.py or tb.py.

# # project.py : There should be one of these per-project.
# # tb.py      : There should be one (or more) of these per-testbench.

# # If more than 1 tb.py are created, select which tb.py to use with the --tb 
# # command-line option.
# # """)

# #     for key in sorted(Keys.keys()):
# #         txt = wrap(Keys[key][__COMMENT__], 60)
# #         print("%-18s%s" % (key, txt[0]))

# #         for line in txt[1:]:
# #             print("%-18s%s" % (' ', line))

########################################################################################
def get_all_sources(source_type='verilog'):
    """
    Returns a list of all of the sources of the given type.
    source_type : (str) Currently only 'verilog' is supported
    =>          : (list of str) The list of all of the source files.
    """

    global AllVerilogSources
    import os.path
    from pymake import glob_files

    # only ever do this once
    if AllVerilogSources is None:
        AllVerilogSources = []
        for vkit in Vkits:
            AllVerilogSources.extend(vkit.get_all_sources())

        for flist in TB.FLISTS:
            fname = os.path.abspath(flist)
            dirname = os.path.dirname(fname)
            all_flist_sources = glob_files([dirname], ['*.v', '*.sv', '*.vh', '*.svh'])
            AllVerilogSources.extend(all_flist_sources)

    return AllVerilogSources
