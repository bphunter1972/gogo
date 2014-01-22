"Functions to parse the gogo command-line"

import gvars
import cn_logging, logging
import sge_tools as sge
import argparse
import os.path
from sys import exit

Log = None

SHORTCUTS = {
             'c'        : 'clean',
             'cln'      : 'clean',
             'clean'    : 'clean',
             'b'        : 'build',
             'build'    : 'build',
             'bld'      : 'build',
             'v'        : 'vlog',
             'vlog'     : 'vlog',
             's'        : 'simulate',
             'sim'      : 'simulate',
             'simu'     : 'simulate',
             'simulate' : 'simulate',
             'latest'   : 'latest',
             }

########################################################################################
def parse_args(version, doc):
    """
    Parse Command-Line and return the gadgets to be run as a list of strings.
    """

    global Log

    gvars.Log = cn_logging.getLogger('gogo.log')
    gvars.Log.setLevel(logging.INFO)

    # create the handler
    console = logging.StreamHandler()
    console.setFormatter(cn_logging.formatter)
    gvars.Log.addHandler(console)

    Log = gvars.Log
    sge.Log = gvars.Log

    p = argparse.ArgumentParser(
        prog='gogo',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        usage="%(prog)s [options] [variables] [gadgets]",
        version=("%(prog)s v"+version),
        description=doc)

    p.add_argument('varg',           action='store', nargs='*',  help="Variable assignments or gadgets to run.")

    p.add_argument('--tb',           action='store',             default='tb',    help="Specify a different tb.py configuration file.")
    p.add_argument('--part', '-p',   action='store',             default='auto',  help="When 'auto', gogo generates the partition configuration from settings; when 'off', compile without partitions; else specify your own configuration file.")

    p.add_argument('--dbg',          action='store_true',        default=False,   help="Used for debugging gogo.")
    p.add_argument('--noflush',      action='store_true',        default=False,   help="Permit turd files to stay.")

    gvars.Options = p.parse_args()

    # check for --dbg
    if gvars.Options.dbg:
        gvars.Log.setLevel(logging.DEBUG)

    # filter variables from gadgets on the command-line
    handle_variables(gvars.Options.varg)

    # get the gadgets to run
    gadgets = handle_gadgets(gvars.Options.varg)

    if gvars.Options.part not in ('auto', 'off') and not os.path.exists(gvars.Options.part):
        Log.critical("Partition configuration file '%s' does not exist." % gvars.Options.part)

    return gadgets

########################################################################################
def handle_variables(vargs):
    variables = [it for it in vargs if '=' in it]
    try:
        gvars.command_line_assignment(variables)
    except Exception as ex:
        if gvars.Options.dbg:
            raise
        Log.critical("Unable to parse command-line: %s" % ex)

########################################################################################
def handle_gadgets(vargs):
    """
    Returns the gadget names to run from the command-line
    """

    gadgets_to_run = [it for it in vargs if not '=' in it]

    # do this above setup_globals so that it can be run anywhere, even when there is no tb.py
    send_help(gadgets_to_run)

    # Shortcut: just running 'gogo' will run vlog and simulate
    if gadgets_to_run == []:
        gadgets_to_run = ['build', 'vlog', 'sim']

    # filter any gadgets to run that start with a no...do this in order until done
    gadgets = []
    for gdt in gadgets_to_run:
        if gdt.startswith('no'):
            gadgets = [it for it in gadgets if it != gdt[2:]]
        else:
            gadgets.append(gdt)

    # ensure that all gadgets are legal as far as SHORTCUTS go
    for gdt in gadgets:
        if gdt not in SHORTCUTS.keys():
            Log.critical("Unknown gadget: %s" % gdt)

    return [SHORTCUTS[gdt] for gdt in gadgets]

########################################################################################
def send_help(gadgets):
    if 'help_vars' in gadgets:
        import help_text
        help_text.print_help_vars()
        exit(0)

    if 'help_gadgets' in gadgets:
        import help_text
        help_text.print_help_gadgets()
        exit(0)

########################################################################################
def print_latest():
    """
    Print the latest source file found in the given testbench.
    """

    import pymake, utils
    srcs = utils.get_all_sources() 
    # print(srcs)
    answer = pymake.get_extreme_mtime(srcs, old=False, get_file=True)
    print("Latest source is %s" % answer[1])
    exit(0)
