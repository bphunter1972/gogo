"""
Defines the base class Gadget.
Commands returned by create_cmds will be concatenated with semicolons and run as a single sge Job.
"""

from __future__ import print_function
import sge_tools as sge
import utils

Log = None

# This is raised by a gadget if its execution was found to have failed
class GadgetFailed(Exception): pass

# This is raised by a gadget if there appears to have been a programming/configuration error
class ProgrammingError(Exception): pass

########################################################################################
# Arrays of these classes are returned by create_cmds
class GadgetCommand(object):
    def __init__(self, command=None, comment=None, no_modules=False, check_after=True):
        self.command = command
        self.comment = comment
        self.no_modules = no_modules
        self.check_after = check_after

    def get_lines(self, modules=None):
        result = []
        if self.comment:
            result.append('echo ">>>> %s"\n' % self.comment)
        if modules and not self.no_modules:
            runmods = "runmod -m %s" % ' -m '.join(modules) + " "
        else:
            runmods = ""
        result.append('%s%s' % (runmods, self.command))
        if self.check_after:
            result.extend(["if($?) then", " exit(-1);", "endif"])
        return result

########################################################################################
class Gadget(sge.Job):
    """The base class gadget."""

    #--------------------------------------------
    def __init__(self):
        super(Gadget, self).__init__()

        self.runmod_modules = []
        self.quiet = True
        self.echo = False

        # descendant classes must set this to one of the schedule phases
        self.schedule_phase = None

        # Any files created by this gadget are called 'turds'.
        # Descendant gadgets should fill in this list with abspath of those files.
        self.turds = []

        self.name = self.__class__.__name__

    #--------------------------------------------
    def create_cmds(self):
        """
        Returns the commands as a list of GadgetCommand objects, or a single object.
        Returning None or an empty list will cause nothing to run on SGE.
        """

        return None

    #--------------------------------------------
    def completedCallback(self):
        """
        If the exit status is bad, raise an error.
        """

        status = self.getExitStatus()

        if status:
            raise GadgetFailed(self.name)

    #--------------------------------------------
    def prepare(self):
        """
        Executes the commands.
        Get the commands to run
        In the event that create_cmds is undefined, then do nothing. Presumably the __init__ function
        did all the work for us.
        """

        import os.path
        self.commands = self.create_cmds()
        if self.commands is None or self.commands == []:
            return

        # make it a list if it's just a string
        if type(self.commands) is GadgetCommand:
            self.commands = [self.commands]

        Log.info("Running %s" % self.name)

        if self.name == '' or self.name is None:
            Log.critical("Gadget has no name!:\n%s" % self)
        file_name = ".%s" % self.name
        if self.cwd is not None:
            file_name = os.path.join(self.cwd, file_name)

        with utils.open(file_name, 'w') as f:
            print("#!/usr/bin/csh", file=f)
            for command in self.commands:
                lines = command.get_lines(self.runmod_modules)
                for line in lines:
                    print(line, file=f)
            print(file=f)

        file_name = utils.get_filename(file_name)
        self.cmd = "source %s" % (file_name)

        # Launch me!
        return self

    #--------------------------------------------
    def check_dependencies(self):
        """
        Returns True if this job must run based on dependencies, or False if it can be skipped.
        Most gadgets may have no dependencies, so this base class just returns true.
        """

        return True
