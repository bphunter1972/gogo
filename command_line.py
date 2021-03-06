"Functions to parse the gogo command-line"

import gvars
import cn_logging, logging
import sge_tools as sge
import argparse
from sys import exit

Log = None

SHORTCUTS = {
             'c'        : 'clean',
             'cln'      : 'clean',
             'clean'    : 'clean',
             'b'        : 'build',
             'build'    : 'build',
             'bld'      : 'build',
             'g'        : 'genip',
             'genip'    : 'genip',
             'v'        : 'vlog',
             'vlog'     : 'vlog',
             's'        : 'simulate',
             'sim'      : 'simulate',
             'simu'     : 'simulate',
             'simulate' : 'simulate',
             'latest'   : 'latest',
             'tree'     : 'tree',
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
    p.add_argument('--dbg',          action='store_true',        default=False,   help="Used for debugging gogo.")
    p.add_argument('--noflush',      action='store_true',        default=False,   help="Permit turd files to stay.")

    gvars.Options = p.parse_args()

    # check for --dbg
    if gvars.Options.dbg:
        gvars.Log.setLevel(logging.DEBUG)

    # filter variables from gadgets on the command-line
    gvars.CommandLineVariables = [it for it in gvars.Options.varg if '=' in it]

    # get the gadgets to run
    gadgets = handle_gadgets(gvars.Options.varg)

    return gadgets

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

    # convert all to full-names
    gadgets = [SHORTCUTS[gdt] for gdt in gadgets]

    if 'genip' in gadgets:
        gvars.VLOG.COMPTYPE = 'genip'
    if 'vlog' in gadgets and gvars.VLOG.COMPTYPE == 'genip':
        gadgets.append('genip')

    return gadgets

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
