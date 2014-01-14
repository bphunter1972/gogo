"""
A gadget that creates the flist file for an SV testbench directory.
"""

from __future__ import print_function

import gadget
import gvars
import glob


class FlistGadget(gadget.Gadget):
    """Creates the .flist file for a testbench"""
    def __init__(self):
        super(FlistGadget, self).__init__()

        self.schedule_phase = 'pre_vlog'

    #--------------------------------------------
    def create_cmds(self):
        "Create the flist file for this testbench."

        import os
        tb_name = os.path.split(os.getcwd())[1]
        tb_dir = 'project/verif/%(tb_name)s' % locals()
        root_dir = gvars.RootDir

        with open('.flist', 'w') as ffile:
            # print +incdirs
            print("+incdir+%(tb_dir)s" % locals(), file=ffile)
            for incdir in gvars.Vars['TB_INCDIRS']:
                print("+incdir+%(incdir)s" % locals(), file=ffile)

            # print testbench sv files
            for svfile in glob.glob('*.sv'):
                print("project/verif/%(tb_name)s/%(svfile)s" % locals(), file=ffile)

            # print tests
            for test in glob.glob('tests/*.sv'):
                print("project/verif/%(tb_name)s/%(test)s" % locals(), file=ffile)

            # print -y libraries
            for libdir in gvars.Vars['TB_LIBRARIES']:
                print("-y %(libdir)s" % locals(), file=ffile)

        self.turds.append('.flist')
        
        return []

