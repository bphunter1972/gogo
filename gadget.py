"""
Defines the base class Gadget.
Commands returned by create_cmds will be concatenated with semicolons and run as a single sge Job.
"""

import sge_tools as sge
import gvars

Log = gvars.Log

class GadgetFailed(Exception): pass


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
        Returns the commands as a list of strings.
        Descendants which do not override this will not run on SGE.
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
        if type(self.commands) is str:
            self.commands = [self.commands]

        Log.info("Running %s" % self.name)

        # Add runmod to each command if necessary
        if self.runmod_modules:
            self.prepend_runmod()

        # check for exit status between each (non-echo) command
        # If it's too long, send it to a dot-file
        if len(self.commands) > 1:
            self.add_check_exit_status()

        file_name = ".%s" % self.name
        if self.cwd is not None:
            file_name = os.path.join(self.cwd, file_name)

        with open(file_name, 'w') as f:
            print >>f, "#!/usr/bin/csh"
            for command in self.commands:
                print >>f, command
            print >>f
            self.turds.append(os.path.abspath(file_name))
        self.cmd = "source %s" % (file_name)

        # Launch me!
        return self

    #--------------------------------------------
    def prepend_runmod(self):
        """
        Adds a runmod command in front of every command that doesn't start with an echo
        """

        modules = ' -m '.join(self.runmod_modules)
        runmod_cmd = "runmod -m %s" % (modules)

        def prepend_it(cmd):
            if not cmd.startswith('echo'):
                return "%s %s" % (runmod_cmd, cmd)
            else:
                return cmd

        self.commands = [prepend_it(it) for it in self.commands]

    #--------------------------------------------
    def add_check_exit_status(self):
        """
        Between each of the commands in self.commands, adds an exit-status checker
        """

        new_commands = []
        for cmd in self.commands:
            new_commands.append(cmd)
            if cmd.startswith('echo'):
                continue
            new_commands.extend(["if($?) then", "exit(-1);", "endif"])
        self.commands = new_commands

    #--------------------------------------------
    def check_dependencies(self):
        """
        Returns True if this job must run based on dependencies, or False if it can be skipped.
        Most gadgets may have no dependencies, so this base class just returns true.
        """

        return True
