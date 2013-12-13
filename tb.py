# Add vkit dependencies *in order*
VKITS = ['cn', 'global', 'credits', 'gmem', 'swi']

# Add testbench flists
FLISTS = ['ut_swi.flist', ]

# Testbench Top-level
TB_TOP = 'ut_swi_tb_top'

BLD_DEFINES = ['SYS_TB_PATH=ut_swi_tb_top',
               'UT_SWI_TB',
              ]

