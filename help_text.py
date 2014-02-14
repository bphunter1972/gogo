"Generates help text"

import gvars
from textwrap import wrap

########################################################################################
def print_help_vars():
    print("""
Assign variables with the following names in either project.py or tb.py.

project.py : There should be one of these per-project.
tb.py      : There should be one (or more) of these per-testbench.

If more than one tb.py is available, select which to use with the --tb command-
line option.

You may also make variable assignments from the command-line, with '=' 
to override or '+=' to append.

Example:
   % gogo SIM.TEST=exer SIM.DBG=200 SIM.WDOG+=2000 vlog sim

For assignments to SIM variables, you may skip specifying SIM:
   % gogo TEST=exer DBG=200 WDOG+=2000 vlog sim

Plusargs must be separated by commas:
   % gogo TEST=exer PLUSARGS+=my_plusarg=150,your_plusarg

""")

    for vtype in sorted(gvars.VTYPES.keys()):
        print("%s : " % vtype)
        for var in gvars.VTYPES[vtype]:
            txt = wrap(gvars.get_vtype(vtype).help(var), 80)
            print("   %-18s%s" % (var, txt[0]))
            for line in txt[1:]:
                print("   %-18s%s" % (' ', line))
        print("")

########################################################################################
def print_help_gadgets():
    from command_line import SHORTCUTS
    import importlib

    print('')
    txt_lines = wrap("""The following gadgets are available from the command-line, together with their shortcuts.
You may cancel a gadget from running by preceding it with 'no'. """, 80)

    for line in txt_lines:
        print(line)
    print('')

    # neatly print the documentation of each gadget
    gdts = sorted(list(set(SHORTCUTS.values())))
    for gadget in gdts:
        try:
            gdt = importlib.import_module('gadgets.' + gadget)
            doc = gdt.__doc__.lstrip()
            docs = wrap(doc, 60)
        except ImportError:
            docs = ['']

        print("%-8s\t%s" % (gadget, docs[0]))
        for line in docs[1:]:
            print("%-8s\t%s" % ('', line))

        print('')

    print("""
Examples:

% gogo clean build vlog sim
        Compile and run from a clean tree.

% gogo sim
        Just run, don't compile anything.

% gogo
        By default, calling gogo will run vlog and simulate.

% gogo c v s
        Clean up, compile verilog, and simulate (all with easy shortcuts!)

% sim/exer/rerun novlog DBG=200 WAVE=vpd
        The rerun script that gogo generates will normally run both vlog, 
        and sim, but appending 'novlog' will turn off the verilog compile
        step.
""")
