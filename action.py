"""
Defines the base class Action.
Commands returned by create_cmds will be concatenated with semicolons and run as a single sge Job.
"""

import sge_tools as sge
import gvars

Log = gvars.Log

class Action(sge.Job):
    """The base class action."""

    #--------------------------------------------
    def __init__(self):
        super(Action, self).__init__()

        self.runmod_modules = []
        self.quiet = False
        self.echo = True

    #--------------------------------------------
    def create_cmds(self):
        """
        Returns the commands as a list of strings.
        """

        return [""]

    #--------------------------------------------
    def run(self):
        """
        Executes the commands.
        """

        # Get the commands to run
        self.commands = self.create_cmds()

        Log.info("Running %s" % self.name)

        # Add runmod to each command if necessary
        if self.runmod_modules:
            modules = ' -m '.join(self.runmod_modules)
            runmod_cmd = "runmod -m %s" % (modules)
            self.commands = ["%s %s" % (runmod_cmd, it) for it in self.commands]

        # Concatenate the commands
        # If it's too long, send it to a dot-file
        self.cmd = ' ;'.join(self.commands)
        if len(self.cmd) > 1024:
            file_name = ".%s" % self.name
            with open(file_name, 'w') as f:
                print >>f, "#!/usr/bin/csh"
                for command in self.commands:
                    print >>f, command
                print >>f
            self.cmd = "source ./%s" % (file_name)

        # Launch me!
        sge.launch(self)
