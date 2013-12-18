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
        self.quiet = False
        self.echo = True

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
    def run(self):
        """
        Executes the commands.
        Get the commands to run
        In the event that create_cmds is undefined, then do nothing. Presumably the __init__ function
        did all the work for us.
        """

        self.commands = self.create_cmds()
        if self.commands is None or self.commands == []:
            return

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
            import os.path
            file_name = os.path.join(self.cwd, file_name)

        with open(file_name, 'w') as f:
            print >>f, "#!/usr/bin/csh"
            for command in self.commands:
                print >>f, command
            print >>f
        self.cmd = "source %s" % (file_name)

        # Launch me!
        sge.waitForJob(self)

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