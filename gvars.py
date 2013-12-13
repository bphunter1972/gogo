"""
Contains all of the global variables.
"""

# All of the global variables in the Vars dictionary
Keys = (
        # Global variables
        'UVM_REV',         # (string) UVM Revision to use
        'USE_RUNMOD',      # (bool) When set, build/sim commands will be launched with runmod
        
        # Testbench-related variables
        'VKITS',           # (list of strings) Vkits that this testbench relies upon, in order
        'FLISTS',          # (list of strings) Testbench FLISTs to include
        'TB_TOP',          # (string) The module name of the top-level of the testbench
        
        # Build-related
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
OptionalKeys = ('SIMOPTS', 'SIM_PLUSARGS', 'BLD_OPTIONS', 'BLD_SO_FILES', 'BLD_TAB_FILES', 
    'BLD_ARC_LIBS', 'BLD_DEFINES', 'LSF_SIM_LICS', 'LSF_BLD_LICS')

# A dictionary of all the global variables imported from the libraries
Vars = {it : None for it in Keys}

# All of the command-line options from parse_args
Options = None

# the Logger
Log = None
