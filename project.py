#--------------------------------------------
# UVM Options

# Select UVM_REV
UVM_REV   = '1_1d'

#--------------------------------------------
# How to build with VCS
VCS_VERSION = 'H-2013.06-SP1'
VLOG_MODULES = ["synopsys-vcs_mx/%s" % VCS_VERSION]
VLOG_TOOL = 'vcs'
VLOG_VCOMP_DIR  = 'sim/.vcomp'

# .tab files
VLOG_TAB_FILES = ['../../verif/uvm_common/explicit/vpi_msg.tab',
             '../../verif/uvm_common/explicit/cn_rand.tab',
             '/nfs/cacadtools/synopsys/Verdi-201309/share/PLI/VCS/LINUX64/novas.tab',
             '../../verif/common/explicit/cn_bist_mon.tab',
             '../../verif/uvm_common/explicit/fake_vcsTBV.tab',
             ]

# .so files
VLOG_SO_FILES = ['obj/VCS/vpi_msg.so',
                 'obj/VCS/cn_rand.so',
                 'obj/VCS/cn_gate.so',
                 'obj/VCS/fake_vcsTBV.so',
                 'obj/VCS/cn_bist_mon.so',
                 'obj/VCS/libVkit.so',
            ]

# .a files
VLOG_ARC_LIBS = ['/nfs/cacadtools/synopsys/Verdi-201309/share/PLI/VCS/LINUX64/pli.a', ]

# VCS VLOG Options
VLOG_OPTIONS = '-q -debug_pp -notice -unit_timescale=1ns/1ps -sverilog +libext+.v+.sv'
VLOG_OPTIONS += '  -CFLAGS -DVCS -full64 +warn=noISALS,noULSU,noIDTS,noLCA_FEATURES_ENABLED -sv_pragma'

VLOG_DEFINES = ['VCS', 'HAVE_VERDI_WAVE_PLI', 'RANDOM_SYNC_DELAY', 'TBV', 'BEHAVE', 'USE_ASSERTIONS', 
            'UVM_NO_DEPRECATED', 'UVM_OBJECT_MUST_HAVE_CONSTRUCTOR']

#--------------------------------------------
# Various Simulation Flags
SIM_GUI = ' -gui'
SIM_MODULES = ['synopsys-vcs_mx/%s' % VCS_VERSION]
SIM_PLUSARGS = ['bug_file=../../verif/bugs.bdf',
                'verrtime=0',
                'projmode=uvm',
                'showlev',
                'dbglen=75',
                'filelen=30',
                'fsdbLogOff',
                'rand_sync',
                'ntb_random_seed=1',
                'ntb_solver_opt=bs',
                'chip_pass=1.0',
                'err=10',
                'UVM_MAX_QUIT_COUNT=10,0'
                ]

#--------------------------------------------
# Simulation options
SIM_WAVE_OPTIONS = ''

#--------------------------------------------
# LSF Command

# VLOG Licenses
LSF_VLOG_LICS = ['lic_cmp_vcs']

# Simulation Licenses
LSF_SIM_LICS = ['lic_sim_vcs']

#--------------------------------------------
# How to Clean Up
CLEAN_DIRS = ['sim', 'csrc', 'DVEfiles', 'AN.DB', 'partitionlib']
CLEAN_FILES = ['ucli.key', 'vc_hdrs.h', 'vcs_partition_config.file', 'pc_autopart.txt', 'project']

#--------------------------------------------
# Miscellaneous
VERDI_MODULE = 'synopsys-verdi'

