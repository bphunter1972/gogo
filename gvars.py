"""
Contains all of the global variables.
"""

import os

# Vars is a dictionary of values, to be filled in with values by setup-files like project.py and tb.py.
# Setup files do not assign to Vars directly, rather, they assign to variables with the same name as the keys of Vars.
Vars = {
    # Testbench-related variables
    'VKITS'           : None,   # (list of strings) Vkits that this testbench relies upon, in order
    'STATIC_VKITS'    : None,   # (list of strings) Vkits that should be considered static for the purposes of partition compilation
    'FLISTS'          : None,   # (list of strings) Testbench FLISTs to include
    'TB_TOP'          : None,   # (string) The module name of the top-level of the testbench
    
    # Build-related
    'BLD_PARTITION'   : None,   # (string) When 'auto', compiles and creates a vcs_partition_config.file. 
                                #          If 'custom', runs in partition-compile mode with file named 'partition.cfg'.
    'BLD_TOOL'        : None,   # (string) Command needed to run a build
    'BLD_MODULES'     : None,   # (list of strings) Added to runmod for all builds
    'BLD_OPTIONS'     : None,   # (string) Additional build options
    'BLD_TAB_FILES'   : None,   # (list of strings) PLI files that should also be added to the build command-line (-P <name>)
    'BLD_SO_FILES'    : None,   # (list of strings) Shared Objects that will be added to the build command-line (-LDFLAGS '<all>')
    'BLD_ARC_LIBS'    : None,   # (list of strings) .a archive libraries that will be added to the build command-line
    'BLD_VCOMP_DIR'   : None,   # (string) The name of the compile directory
    'BLD_DEFINES'     : None,   # (list of strings) All +BLD_defines as needed
    
    # Simulation-related
    'SIM_MODULES'     : None,   # (list of string) List of modules, added to runmod for all sims
    'SIM_GUI'         : None,   # (string) Add this to simulation command-line when you want to run in GUI mode
    'SIMOPTS'         : None,   # (string) Added to the simulation command-line (not overridden by --simopts)
    'SIM_PLUSARGS'    : None,   # (list of string) Added to the simulation command-line (all preceded by +)
    'SIM_WAVE_OPTIONS': None,   # (string) Run-time options
    
    # LSF-related
    'LSF_SUBMIT_TOOL' : None,   # (string) The LSF tool to call
    'LSF_BLD_LICS'    : None,   # (string) Additional licenses used for building
    'LSF_SIM_LICS'    : None,   # (string) Additional licences used for simulation
    
    # Cleaning-related
    'CLEAN_DIRS'      : None,   # (list of strings) Names of directories to delete
    'CLEAN_FILES'     : None,   # (list of strings) Names of files to delete

    # Miscellaneous
    'UVM_REV'         : None,   # (string) UVM Revision to use
}

# These keys do NOT need to be specified
OptionalKeys = ('STATIC_VKITS', 'SIMOPTS', 'SIM_PLUSARGS', 'BLD_OPTIONS', 'BLD_PARTITION', 'BLD_SO_FILES', 'BLD_TAB_FILES', 
    'BLD_ARC_LIBS', 'BLD_DEFINES', 'LSF_SIM_LICS', 'LSF_BLD_LICS')

# All of the command-line options from parse_args
Options = None

# the Logger
Log = None

########################################################################################
def setup_globals():
    """
    Set up the Vars dictionary with imported information from project and the local tb.py
    """

    global Vars

    # The names of all the library files that will be imported
    libraries = ('project', 'tb')

    def import_lib(mod_name):
        try:
            lib = __import__(mod_name)
        except ImportError:
            Log.critical("%s.py file not found! Ensure that your PYTHONPATH variable includes '.'" % mod_name)

        lib_dict = lib.__dict__
        for key in Vars:
            if key in lib_dict:
                try:
                    if type(Vars[key]) == str:
                        Vars[key] = Vars[key] + ' ' + lib_dict[key]
                    else:
                        Vars[key] += lib_dict[key]
                except:
                    Vars[key] = lib_dict[key]

    map(import_lib, libraries)

    Vars['VKITS_DIR'] = '../vkits'
    Vars['UVM_DIR']   = os.path.join(Vars['VKITS_DIR'], 'uvm/%s' % Vars['UVM_REV'])
    Vars['UVM_FLIST'] = os.path.join(Vars['UVM_DIR'], 'uvm.flist')

    for key in Vars:
        if Vars[key] is None and key not in OptionalKeys:
            Log.error("%s is not defined in any of %s." % (key, ','.join(["%s.py" % it for it in libraries])))

    # check that some dictionary items only contain correct values
    if Vars['BLD_PARTITION'] and Vars['BLD_PARTITION'] not in ('custom', 'auto'):
        Log.critical("BLD_PARTITION value '%s' must be one of 'custom' or 'auto'" % Vars['BLD_PARTITION'])
