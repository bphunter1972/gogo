"""
Calls build.pl. 
Currently, this is over-simplistic and needs to actually take over what build.pl does.
Also, it's not working yet, so don't run this gadget.
"""

import gadget
import gvars
import os
from utils import get_filename

Log = gvars.Log

class BuildGadget(gadget.Gadget):

    #--------------------------------------------
    def __init__(self):
        super(BuildGadget, self).__init__()

        self.schedule_phase = 'build'

        self.name = 'build'
        self.queue = 'build'
        self.interactive = True

        # create a symbolic link called 'project'. 
        try:
            os.symlink('../..', 'project')
        except OSError:
            pass

        # add the CSR gadget to pre_build phase
        import gadgets.csr_build
        import schedule
        schedule.add_gadget(gadgets.csr_build.CsrBuildGadget())

    #--------------------------------------------
    def create_cmds(self):
        """
            $(ECHO) mkdir -m 777 -p $(TB_LIB_DIR)
            $(ECHO) $(AR) p $(_EXP_LIB) $(notdir $(basename $@)).o > $(basename $@).o
            $(ECHO) if [ ! -f $(basename $@).o ]; then echo "***ERROR: $(_EXP_LIB) does not contain $(basename $@).o!"; exit 1; fi
            $(ECHO) $(LD) -o $@ $(LDOPTS) $(basename $@).o
            $(ECHO) rm -f $(basename $@).o
        """

        cmds = []
        libraries = ['vpi_msg', 'cn_rand', 'cn_gate', 'fake_VCStbv', 'cn_bist_mon']
        for lib in libraries:
            libdir = get_filename(os.path.join(gvars.RootDir, "verif/lib/commonVCS.a"))
            cmd = "mkdir -m 777 -p obj/VCS; ar p %(libdir)s %(lib)s.o > obj/VCS/%(lib)s.o" % locals()
            cmds.append(gadget.GadgetCommand(command=cmd, no_modules=True, comment="Making %s" % lib))
            cmd = "g++ -o obj/VCS/%(lib)s.so -fPIC -shared --export-dynamic -Wl,--fatal-warnings -ggdb -m64 obj/VCS/%(lib)s.o; rm -f obj/VCS/%(lib)s.o " % locals()
            cmds.append(gadget.GadgetCommand(command=cmd, no_modules=True))

        return cmds
