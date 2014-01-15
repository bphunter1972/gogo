from gvars import *
import os.path

#--------------------------------------------
# Project Variables

# Select UVM_REV
PROJ.UVM_REV   = '1_1d'
PROJ.VKITS_DIR = os.path.join(RootDir, 'verif/vkits')

# VLOG Licenses
PROJ.LSF_VLOG_LICS = ['lic_cmp_vcs']

# Simulation Licenses
PROJ.LSF_SIM_LICS = ['lic_sim_vcs']

# How to Clean Up
PROJ.CLEAN_DIRS = ['sim', 'csrc', 'DVEfiles', 'AN.DB', 'partitionlib']
PROJ.CLEAN_FILES = ['ucli.key', 'vc_hdrs.h', 'vcs_partition_config.file', 'pc_autopart.txt', 'project']

# Miscellaneous
PROJ.VERDI_MODULE = 'synopsys-verdi'


#--------------------------------------------
# Verilog Varialbes
VCS_VERSION = 'H-2013.06-SP1'
VLOG.MODULES = ["synopsys-vcs_mx/%s" % VCS_VERSION]
VLOG.TOOL = 'vcs'
VLOG.VCOMP_DIR  = 'sim/.vcomp'

# .tab files
VLOG.TAB_FILES = ['../../verif/uvm_common/explicit/vpi_msg.tab',
             '../../verif/uvm_common/explicit/cn_rand.tab',
             '/nfs/cacadtools/synopsys/Verdi-201309/share/PLI/VCS/LINUX64/novas.tab',
             '../../verif/common/explicit/cn_bist_mon.tab',
             '../../verif/uvm_common/explicit/fake_vcsTBV.tab',
             ]

# .so files
VLOG.SO_FILES = ['obj/VCS/vpi_msg.so',
                 'obj/VCS/cn_rand.so',
                 'obj/VCS/cn_gate.so',
                 'obj/VCS/fake_vcsTBV.so',
                 'obj/VCS/cn_bist_mon.so',
                 'obj/VCS/libVkit.so',
            ]

# .a files
VLOG.ARC_LIBS = ['/nfs/cacadtools/synopsys/Verdi-201309/share/PLI/VCS/LINUX64/pli.a', ]

# VCS/VLOGAN Options
VLOG.OPTIONS = '-q -debug_pp -notice -unit_timescale=1ns/1ps -sverilog +libext+.v+.sv -fastcomp=1 -full64 -sv_pragma %s/uvm/%s/src/dpi/uvm_dpi.cc' % (PROJ.VKITS_DIR, PROJ.UVM_REV)
VLOG.VCS_OPTIONS = '-CFLAGS -DVCS -lca -rad'
VLOG.IGNORE_WARNINGS = ['ISALS', 'ULSU', 'IDTS', 'LCA_FEATURES_ENABLED', 'LCA_FEATURES_WARN_OPTION', 'PC_SKIP_FULLDR']
VLOG.DEFINES = ['VCS', 'HAVE_VERDI_WAVE_PLI', 'RANDOM_SYNC_DELAY', 'TBV', 'BEHAVE', 'USE_ASSERTIONS', 'UVM_NO_DEPRECATED', 'UVM_NO_RELNOTES', 'UVM_OBJECT_MUST_HAVE_CONSTRUCTOR']

#--------------------------------------------
# Various Simulation Flags
SIM.GUI = ' -gui'
SIM.MODULES = ['synopsys-vcs_mx/%s' % VCS_VERSION]
SIM.PLUSARGS = ['bug_file=../../verif/bugs.bdf',
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
SIM.WAVE_OPTIONS = ''

#--------------------------------------------
# LSF Command

