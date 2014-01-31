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

        def get_sv_path(tb_name, fname):
            return "project/verif/%(tb_name)s/%(fname)s" % locals()

        with open('.flist', 'w') as ffile:
            # print +incdirs
            print("+incdir+%(tb_dir)s" % locals(), file=ffile)
            for incdir in gvars.TB.INCDIRS:
                print("+incdir+%(incdir)s" % locals(), file=ffile)

            # TB_TOP file must go first, because it is the one that imports uvm_pkg
            print(get_sv_path(tb_name, tb_name + '_tb_top.sv'), file=ffile)

            # print testbench sv files
            all_files = glob.glob('*.sv')

            # TODO: I don't know why this should not be there, but it results
            # in tests being declared twice in the factory.
            # if not gvars.VLOG.COMPTYPE == 'genip':
            all_files.extend(glob.glob('tests/*.sv'))

            all_files = [it for it in all_files if not it.endswith('_tb_top.sv')]
            for svfile in all_files:
                print(get_sv_path(tb_name, svfile), file=ffile)

            # print -y libraries
            for libdir in gvars.TB.LIBRARIES:
                print("-y %(libdir)s" % locals(), file=ffile)

        self.turds.append('.flist')
        
        return []
