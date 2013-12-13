"""
Contains all of the global variables.
"""

import os

# All of the global variables in the Vars dictionary
Keys = (
        # Global variables
        'UVM_REV',         # (string) UVM Revision to use
        
        # Testbench-related variables
        'VKITS',           # (list of strings) Vkits that this testbench relies upon, in order
        'FLISTS',          # (list of strings) Testbench FLISTs to include
        'TB_TOP',          # (string) The module name of the top-level of the testbench
        
        # Build-related
        'BLD_PARTITION',   # (bool) When true, runs in partition-compile mode
        'BLD_TOOL',        # (string) Command needed to run a build
        'BLD_MODULES',     # (list of strings) Added to runmod for all builds
        'BLD_OPTIONS',     # (string) Additional build options
        'BLD_TAB_FILES',   # (list of strings) PLI files that should also be added to the build command-line (-P <name>)
        'BLD_SO_FILES',    # (list of strings) Shared Objects that will be added to the build command-line (-LDFLAGS '<all>')
        'BLD_ARC_LIBS',    # (list of strings) .a archive libraries that will be added to the build command-line
        'BLD_VCOMP_DIR',   # (string) The name of the compile directory
        'BLD_DEFINES',     # (list of strings) All +BLD_defines as needed
        
        # Simulation-related
        'SIM_MODULES',     # (list of string) List of modules, added to runmod for all sims
        'SIM_GUI',         # (string) Add this to simulation command-line when you want to run in GUI mode
        'SIMOPTS',         # (string) Added to the simulation command-line (not overridden by --simopts)
        'SIM_PLUSARGS',    # (list of string) Added to the simulation command-line (all preceded by +)
        'SIM_WAVE_OPTIONS',# (string) Run-time options
        
        # LSF-related
        'LSF_SUBMIT_TOOL', # (string) The LSF tool to call
        'LSF_BLD_LICS',    # (string) Additional licenses used for building
        'LSF_SIM_LICS',    # (string) Additional licences used for simulation
        
        # Cleaning-related
        'CLEAN_DIRS',      # (list of strings) Names of directories to delete
        'CLEAN_FILES',     # (list of strings) Names of files to delete
)

# These keys do NOT need to be specified, if you don't want to
OptionalKeys = ('SIMOPTS', 'SIM_PLUSARGS', 'BLD_OPTIONS', 'BLD_PARTITION', 'BLD_SO_FILES', 'BLD_TAB_FILES', 
    'BLD_ARC_LIBS', 'BLD_DEFINES', 'LSF_SIM_LICS', 'LSF_BLD_LICS')

# A dictionary of all the global variables imported from the libraries
Vars = {it : None for it in Keys}

# All of the command-line options from parse_args
Options = None

# the Logger
Log = None

########################################################################################
def setup_globals():
    """
    Set up the Vars dictionary with imported information from project and the local tb.py
    Set up the CmdLineActions dictionary
    """

    global Vars

    # The names of all the library files that will be imported
    libraries = ('project', 'tb')

    def import_lib(mod_name):
        try:
            lib = __import__(mod_name)
        except ImportError:
            Log.critical("%s.py file not found! Ensure that your PYTHONPATH variable includes '.'" % mod_name)
            sys.exit(253)

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
            sys.exit(1)

