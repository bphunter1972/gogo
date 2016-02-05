#!/usr/bin/env python2.7

"""
Determines package dependencies from vkits
Orders a generic dictionary of dependencies into levels.
"""

from __future__ import print_function
__author__  = 'Brian Hunter'
__version__ = '0.0'
__email__   = 'brian.hunter@cavium.com'

########################################################################################
# Imports
from generators import *
import cn_logging
import argparse

########################################################################################
# Globals
ACTIONS = (
    'test',   # run the test dictionary
    'tree',   # prints out the dependency tree
    'graph',  # graphs the dependency tree
    'deps',   # print the dependencies of a particular vkit
    'query',  # writes out the file graph.gml
    )
FONT_SIZE = 18          # letter size in graphs
CHAR_SPACING = 5*FONT_SIZE   # helps determines space between nodes in subgraphs

########################################################################################
# Exceptions
class DependencyException(Exception):
    pass

class Swapped(Exception):
    pass

########################################################################################
def order_dependencies(deps):
    """
    The function order_dependencies is given a dictionary. Each key in the dictionary is an entry,
    and it is assigned a list of other entries that it depends upon.

    It returns a dictionary of nodes with their level number.
    """

    if type(deps) != dict:
        raise DependencyException("Argument must be a dictionary.")

    result = {it : 0 for it in deps.keys()}
    Log.debug("Starting with \n{}".format(deps))

    curr_level = 0
    swapped = True
    while swapped:
        swapped = False
        entries = [it for it in result.keys() if result[it] == curr_level]
        Log.debug("In level {} there are {}".format(curr_level, entries))
        if(len(entries) == 0):
            Log.debug("Something is wrong at empty level {}\n{}".format(curr_level, result))
            return None
        for key_entry in entries:
            Log.debug("Looking at {} at level {}".format(key_entry, result[key_entry]))
            try:
                for check_entry in entries:
                    if key_entry == check_entry:
                        continue
                    if check_entry in deps[key_entry]:
                        result[key_entry] = curr_level+1
                        Log.debug("Elevating {} to level {} because it depends on {}".format(key_entry, result[key_entry], check_entry))
                        Log.debug("deps[{}] are {}".format(key_entry, deps[key_entry]))
                        # check for circular import
                        if key_entry in deps[check_entry]:
                            exc = "Found circular import between {} and {}".format(key_entry, check_entry)
                            raise DependencyException(exc)
                        raise Swapped
            except Swapped:
                swapped = True
        curr_level += 1

    return result

########################################################################################
def find_dependencies(working_dir):
    """
    Looks at all of the sub-directories of working_dir, considering each one a node.
    Searches through each file looking for references to pkgs with a different name.
    Returns a dictionary of nodes and lists of dependencies. Only dependencies that
    are also nodes are considered. The rest are considered extraneous.

    working_dir : (str) The name of a directory (usually vkits/)
    =>          : (dict) Keys are subdirectories of working_dir. Each value is a list
                         of strings representing packages that dir depends upon.
    """
    import os
    import re
    pat = re.compile("([\w_]+)_pkg")

    Log.debug("Finding dependencies in {}".format(working_dir))

    vkits = [it for it in os.listdir(working_dir) if os.path.isdir(it)]
    results = {it : [] for it in vkits}

    for vkit in vkits:
        requirements = []
        lines = lines_from_dir("*.sv", vkit)
        matching_lines = grep("_pkg", lines)
        for line in matching_lines:
            # remove anything trailing a //
            line = line.split('//')[0]
            # remove anything between double-quotes
            while line.count('"') >= 2:
                sep_line = line.split('"')
                line = sep_line[0] + sep_line[2]
                Log.debug("Pulled {} and now line is {}".format(sep_line[1], line))
            matches = pat.findall(line)
            requirements.extend([it for it in matches if it != vkit and it in vkits])
        # make unique
        requirements = list(set(requirements))
        results[vkit] = requirements
        Log.debug("vkit {} requires {}".format(vkit, requirements))
    return results

########################################################################################
def print_ordered_deps(ordered):
    "Input is a dictionary of ordered nodes with their level number. Print by level number."

    level = 0
    while True:
        nodes = [it for it in ordered if ordered[it] == level]
        if not nodes:
            break
        Log.info("{:3d} : {}".format(level, nodes))
        level += 1

########################################################################################
def reduce_deps(deps, max_level, order=None):
    """
    Take in an ordered list, as well as a dictionary of dependencies.
    Eliminate from the deps those nodes that are > max_level
    """

    good_nodes = [it for it in order.keys() if order[it] <= max_level]
    result = {}
    for node in deps.keys():
        if node not in good_nodes:
            continue
        result[node] = [it for it in deps[node] if it in good_nodes]
    return result

########################################################################################
def graph_it(deps, pos=None, arrows=True):
    """
    Takes in the dependencies and creates a plot using networkx, matplotlib.pyplot.
    If vkits are specified, only graphs those vkits and their neighbors
    """

    try:
        import matplotlib.pyplot as plt
    except ImportError:
        Log.info("Unable to display graph. Install matplotlib.pyplot to continue.")
    else:
        my_pos = pos if pos else nx.spring_layout(graph, k=250.0)
        nx.draw(graph, with_labels=True, font_size=FONT_SIZE, node_shape='o', node_size=1, node_color='w',
                font_color='b', pos=my_pos, arrows=arrows, width=.25)
        plt.show()

########################################################################################
def create_DiGraph(deps):
    "Returns a Directed Graph based on the dependencies"

    graph = nx.DiGraph()
    graph.add_nodes_from(deps.keys())
    for node in deps:
        for dep in deps[node]:
            graph.add_edge(node, dep)
    return graph

########################################################################################
def set_pos(pos, lst, level=-1):
    "Add lst nodes to pos dictionary."
    if len(lst) == 0:
        return

    y_pos = 100
    num_rows = 1 if len(lst) < 10 else 2
    Log.debug("lst:{}".format(lst))
    Log.debug("lens: {}".format([len(it) for it in lst]))
    # spacing is the width of each node
    spacing = max(CHAR_SPACING * max([len(it) for it in lst]), 850)
    # full_width is width of the whole row in the x direction
    full_width = len(lst) * spacing

    # initial position is half the full width and negative
    x_pos = -(full_width / 2)
    Log.debug("spacing = {}, len(lst)={}, full_width={} starting x_pos={}".format(spacing, len(lst), full_width, x_pos))
    for a_node in lst:
        Log.debug("Adding {} -> ({}, {})".format(a_node, x_pos, level*y_pos))
        pos[a_node] = (x_pos, level*y_pos)
        x_pos += spacing
        if num_rows == 2:
            y_pos = (100 if y_pos == 120 else 120)

########################################################################################
def create_subgraph(graph, node):
    """
    Create a subgraph centered around node, showing only its successors and predecessors
    => : (subgraph, pos) pos is a dict with positional information for graphing
    """

    Log.info("Creating subgraph for {}".format(node))
    subgraph = nx.DiGraph()
    subgraph.add_node(node)
    succ = []
    succ.append(graph.successors(node))
    pred = graph.predecessors(node)
    subgraph.add_nodes_from(succ[0])
    subgraph.add_nodes_from(pred)
    subgraph.add_edges_from([(node, it) for it in succ[0]])
    subgraph.add_edges_from([(it, node) for it in pred])

    level = 0
    while True:
        nxt_lvl = []
        Log.debug("In Level: {}".format(level))
        for s in succ[level]:
            Log.debug("Looking for successors to {}".format(s))
            next_succ = graph.successors(s)
            Log.debug("Found: {}".format(next_succ))
            # filter out those that are already dependencies
            next_succ = [it for it in next_succ if it not in subgraph.nodes()]
            Log.debug("Filtered to: {}".format(next_succ))
            if next_succ:
                subgraph.add_nodes_from(next_succ)
                subgraph.add_edges_from([(s, it) for it in next_succ])
                nxt_lvl.extend(next_succ)
        level += 1
        if nxt_lvl:
            Log.debug("Adding nxt_lvl:{}".format(nxt_lvl))
            succ.append(nxt_lvl)
            Log.debug("succ is now:{}".format(succ))
        else:
            break

    # create pos with node at center
    pos = {node: (0, 0)}
    set_pos(pos, pred, level=-1)
    for lvl, s in enumerate(succ):
        Log.debug("Adding from succ[{}] = {}".format(lvl, s))
        set_pos(pos, s, level=lvl+1)

    Log.info("Graphing subgraph:")
    for lvl in range(len(succ)-1, -1, -1):
        Log.info("Dependencies[{}]: {}".format(lvl, succ[lvl]))
    Log.info("Vkit:             {}".format(node))
    Log.info("Required by:      {}".format(pred))

    return subgraph, pos

########################################################################################
def parse_args():
    "Parse command-line"

    global Log

    p = argparse.ArgumentParser()
    p.add_argument('actions', action='store', nargs='*', default='test', choices=ACTIONS)

    p.add_argument('--max',    '-m', type=int, default=None, help="Maximum number of levels to graph.")
    p.add_argument('--vkit',   '-v', type=str, default=None, help="When query is set, print the vkits that this vkit depends on.")
    p.add_argument('--dbg',    '-d', action='store_true', default=False, help="Enable debug")

    options = p.parse_args()

    Log = cn_logging.createLogger('log', debug_level=options.dbg)

    return options

########################################################################################
if __name__ == '__main__':
    options = parse_args()

    # determine dependencies to use
    if 'test' in options.actions:
        deps = {
            'uvm'       : [],
            'cn'        : ['uvm'],
            'csr_cn'    : ['cn'],
            'csr_pem'   : ['cn'],
            'csr_pcierc': ['cn'],
            'global'    : ['cn'],
            'pciesvt'   : ['uvm'],
            'dtx'       : ['global'],
            'reg'       : ['global', 'cn', 'uvm'],
            'rsl'       : ['cn', 'global'],
            'credits'   : ['cn', 'global'],
            'gmem'      : ['cn', 'global'],
            'swi'       : ['cn', 'global', 'credits', 'gmem'],
            'pcie'      : ['pciesvt', 'cn', 'uvm'],
            'pem'       : ['uvm', 'cn', 'csr_cn', 'csr_pem', 'csr_pcierc', 'global', 'pciesvt',
                           'dtx', 'reg', 'rsl', 'credits', 'gmem', 'swi', 'pcie'],
        }
    else:
        import os
        working_dir = os.getcwd()
        deps = find_dependencies(working_dir)

    if 'tree' in options.actions:
        Log.info("Ordering dependencies of {} vkits".format(len(deps.keys())))
        order = order_dependencies(deps)
        print_ordered_deps(order)

    if 'query' in options.actions or 'graph' in options.actions:
        try:
            import networkx as nx
        except ImportError:
            Log.info("Unable to query or display graph. Install networkx to continue.")
        pos = None
        arrows = options.vkit is None

        # graph only to level specified by --max
        if options.max:
            lvl_deps = reduce_deps(deps, order=order, max_level=options.max)
        else:
            lvl_deps = deps

        graph = create_DiGraph(lvl_deps)
        if options.vkit is not None and options.vkit in graph:
            subgraph, pos = create_subgraph(graph, options.vkit)
            graph = subgraph

        if 'query' in options.actions:
            Log.info("Writing graph to graph.gml")
            nx.write_gml(graph, 'graph.gml')
            Log.info("Run the following to start querying:")
            Log.info("% python")
            Log.info(">>> import networkx as nx")
            Log.info(">>> nx.read_gml('graph.gml')")

        if 'graph' in options.actions:
            graph_it(graph, pos, arrows)

    if 'deps' in options.actions:
        vkit = options.vkit if options.vkit else 'cn'
        Log.info("vkit {} depends on:".format(options.vkit))
        for vdep in deps[vkit]:
            Log.info(vdep)
