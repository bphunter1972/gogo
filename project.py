###############
# UVM Options

# Select UVM_REV
UVM_REV   = '1_1d'

###############
# Use runmod
USE_RUNMOD = 1

###############
# How to build with VCS
VCS_VERSION = 'H-2013.06-SP1'
BLD_MODULES = ["synopsys-vcs_mx/%s" % VCS_VERSION]
BLD_TOOL = 'vcs'
BLD_VCOMP_DIR  = 'sim/.vcomp'

# .tab files
BLD_TAB_FILES = ['../../verif/uvm_common/explicit/vpi_msg.tab',
             '../../verif/uvm_common/explicit/cn_rand.tab',
             '/nfs/cacadtools/synopsys/Verdi-201309/share/PLI/VCS/LINUX64/novas.tab',
             '../../verif/common/explicit/cn_bist_mon.tab',
             '../../verif/uvm_common/explicit/fake_vcsTBV.tab',
             ]

# .so files
BLD_SO_FILES = ['/nfs/cadv1/bhunter/t88/t88/verif/ut_swi/obj/VCS/vpi_msg.so',
            '/nfs/cadv1/bhunter/t88/t88/verif/ut_swi/obj/VCS/cn_rand.so',
            '/nfs/cadv1/bhunter/t88/t88/verif/ut_swi/obj/VCS/cn_gate.so',
            '/nfs/cadv1/bhunter/t88/t88/verif/ut_swi/obj/VCS/fake_vcsTBV.so',
            '/nfs/cadv1/bhunter/t88/t88/verif/ut_swi/obj/VCS/cn_bist_mon.so',
            '/nfs/cadv1/bhunter/t88/t88/verif/ut_swi/obj/VCS/libVkit.so',
            ]

# .a files
BLD_ARC_LIBS = ['/nfs/cacadtools/synopsys/Verdi-201309/share/PLI/VCS/LINUX64/pli.a', ]

# VCS Bld Options
BLD_OPTIONS = '-q -debug_pp -notice -unit_timescale=1ns/1ps -sverilog +libext+.v+.sv'
BLD_OPTIONS += ' +define+UVM_NO_DEPRECATED+UVM_OBJECT_MUST_HAVE_CONSTRUCTOR'
BLD_OPTIONS += '  -CFLAGS -DVCS -full64 +warn=noISALS,noULSU,noIDTS,noLCA_FEATURES_ENABLED -sv_pragma'

BLD_DEFINES = ['VCS', 'HAVE_VERDI_WAVE_PLI', 'RANDOM_SYNC_DELAY', 'TBV', 'BEHAVE', 'USE_ASSERTIONS', 
            'UVM_NO_DEPRECATED', 'UVM_OBJECT_MUST_HAVE_CONSTRUCTOR']

###############
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

###############
# Simulation options
SIM_WAVE_OPTIONS = ''

###############
# LSF Command
LSF_SUBMIT_TOOL = 'qrsh'

# Bld Licenses
LSF_BLD_LICS = '-q build -l lic_cmp_vcs'

# Simulation Licenses
LSF_SIM_LICS = '-q verilog -l lic_sim_vcs'

################
# How to Clean Up
CLEAN_DIRS = ('sim', 'csrc', 'DVEfiles')
CLEAN_FILES = ('ucli.key', 'vc_hdrs.h')
