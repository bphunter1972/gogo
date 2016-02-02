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
PROJ.CLEAN_DIRS = ['sim', 'csrc', 'DVEfiles', 'AN.DB', 'partitionlib', 'work']
PROJ.CLEAN_FILES = ['ucli.key', 'vc_hdrs.h', 'vcs_partition_config.file', 'pc_autopart.txt', 'project', '.vcs_lib_lock']

# Runmod module for VCS
# VCS_VERSION = 'H-2013.06-SP1'
VCS_VERSION = 'J-2014.12-SP2'
# VCS_VERSION = 'J-2014.12-BETA'
VC_VERSION = 'J-2014.12'

PROJ.MODULES['vcs'] = 'synopsys-vcs_mx/%s' % VCS_VERSION
PROJ.MODULES['verdi'] = 'synopsys-vc-verdi/%s' % VC_VERSION
PROJ.MODULES['synopsys-designware'] = 'synopsys-designware/20140815'

# Miscellaneous
VERDI_HOME = get_env_variable('VERDI_HOME', PROJ.MODULES['verdi'])

#--------------------------------------------
# Verilog Variables
VLOG.MODULES = ["vcs"]
VLOG.TOOL = 'vcs'
VLOG.VCOMP_DIR  = 'sim/.vcomp'

# .tab files
VLOG.TAB_FILES = ['project/verif/uvm_common/explicit/vpi_msg.tab',
                 'project/verif/uvm_common/explicit/cn_rand.tab',
                 '%s/share/PLI/VCS/LINUX64/novas.tab' % (VERDI_HOME),
                 'project/verif/common/explicit/cn_bist_mon.tab',
                 'project/verif/uvm_common/explicit/fake_vcsTBV.tab',
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
VLOG.ARC_LIBS = ['%s/share/PLI/VCS/LINUX64/pli.a' % (VERDI_HOME), ]

# VCS/VLOGAN Options
VLOG.OPTIONS = ' -notice -unit_timescale=1ns/1fs -ntb_opts uvm -sverilog -full64 %s/uvm/%s/src/dpi/uvm_dpi.cc -bc=cb_extended_behavior' % (PROJ.VKITS_DIR, PROJ.UVM_REV)
VLOG.VLOGAN_OPTIONS = ' -sv_pragma +libext+.v'
VLOG.VCS_OPTIONS = ' -CFLAGS -DVCS -lca -debug_pp'
VLOG.IGNORE_WARNINGS = ['ISALS', 'ULSU', 'IDTS', 'LCA_FEATURES_ENABLED', 'LCA_FEATURES_WARN_OPTION', 
                        'PC_SKIP_FULLDR', 'UII-L']
VLOG.DEFINES = ['VCS', 'PROJ_INCLUDES_UVM', 'RANDOM_SYNC_DELAY', 'TBV', 'BEHAVE', 'USE_ASSERTIONS', 'HAVE_VERDI_WAVE_PLI', 
                'UVM_NO_DEPRECATED', 'UVM_NO_RELNOTES', 'UVM_OBJECT_MUST_HAVE_CONSTRUCTOR']

#--------------------------------------------
# Various Simulation Flags
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
