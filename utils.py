"""
Common utilities module.
"""

from __future__ import print_function

import gvars
import os
from __builtin__ import open as builtin_open

AllVerilogSources = None

CURR_TIME = 0

########################################################################################
def get_all_sources(source_type='verilog'):
    """
    Returns a list of all of the sources of the given type.
    source_type : (str) Currently only 'verilog' is supported
    =>          : (list of str) The list of all of the source files.
    """

    global AllVerilogSources
    import os.path
    from pymake import glob_files

    # only ever do this once
    if AllVerilogSources is None:
        AllVerilogSources = []
        for vkit in gvars.Vkits:
            AllVerilogSources.extend(vkit.get_all_sources())

        for flist in gvars.TB.FLISTS:
            fname = os.path.abspath(flist)
            dirname = os.path.dirname(fname)
            all_flist_sources = glob_files([dirname], ['*.v', '*.sv', '*.vh', '*.svh'])
            AllVerilogSources.extend(all_flist_sources)

    return AllVerilogSources

########################################################################################
def check_files_exist(files):
    """
    Returns 0 if any of the files do not exist.

    files : (list of str) The list of filenames
            (str) A single filename
    =>    : (bool) Returns True if all of the files exist
    """

    # in the case of being passed only 1 string, just put that string in a list
    if type(files) == str:
        files = [files,]

    from os.path import exists
    missing_files = [it for it in files if exists(it) == False]
    if missing_files:
        return False
    else:
        return True

########################################################################################
def get_time_int():
    """
    Returns the number of seconds since the epoch--performs this calculation only 
    once per run so that it is consistent with any other uses
    """
    import time
    global CURR_TIME
    
    if CURR_TIME == 0:
        CURR_TIME = int(time.time())
    return CURR_TIME

########################################################################################
def open(filename, mode='w'):
    """
    Returns a file handle to the translated filename using get_filename.
    """

    filename = get_filename(filename)
    afile = builtin_open(filename, mode)

    return afile

########################################################################################
def get_filename(filename):
    """
    Returns the name of a file in the .gogo directory that corresponds to a real path in
    the project directory.

    filename : (str) A file of the form /nfs/.../t88/verif/vkits/cn/vlog would be translated
                     to /nfs/.../t88/.gogo/verif_vkits_cn/vlog
    =>       : (str) The translated name
    """

    # when handed a previously translated file name...
    if filename.startswith(gvars.GogoDir):
        return filename

    if not os.path.exists(gvars.GogoDir):
        os.mkdir(gvars.GogoDir)

    # calculate the directory name underneath the gvars.GogoDir in which the file will be
    filename = os.path.abspath(filename)
    if not filename.startswith(gvars.RootDir):
        raise IOError("Cannot create a file in {}".format(filename))
    dirname, filename = os.path.split(filename)

    dirname = dirname.replace(gvars.RootDir, '')
    dirname = dirname.replace('/', '_')[1:]
    dirname = os.path.join(gvars.GogoDir, dirname)

    if not os.path.exists(dirname):
        os.mkdir(dirname)
    filename = os.path.join(dirname, filename)
    return filename

########################################################################################
def order_vkits(all_vkits):
    """
    Returns a dictionary of all vkit names as keys, with their dependency group level
    See also: depends.order_dependencies()
    """

    import depends
    depends.Log = gvars.Log

    vkit_dict = {it.name: it.dependencies for it in all_vkits}
    ordered = depends.order_dependencies(vkit_dict)
    return ordered

########################################################################################
def sort_vkits(all_vkits):
    """
    Returns the list of vkits sorted by dependency requirements. UVM will always be
    the first in the list.
    """

    sorted_vkits = []
    ordered = order_vkits(all_vkits)
    groups = range(max(ordered.values())+1)
    for group in groups:
        sorted_vkits.extend([name for name in ordered.keys() if ordered[name]==group])
    return [next(it for it in all_vkits if it.name == item) for item in sorted_vkits]
