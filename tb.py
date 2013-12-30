# Add vkit dependencies *in order*
VKITS = ['cn', 'global', 'credits', 'gmem', 'swi']
STATIC_VKITS = ['cn', 'global', 'credits']

# Add testbench flists
FLISTS = ['ut_swi.flist', ]

# Testbench Top-level
TB_TOP = 'ut_swi_tb_top'

VLOG_DEFINES = ['SYS_TB_PATH=ut_swi_tb_top', 'UT_SWI_TB']

VLOG_PARTITION = 'custom'
