#!/usr/bin/env python2.7

"""
Given a list of sources and a list of targets, returns True if the
targets should be remade based on modification times of all files.

Will raise NonExistantFile if any sources are missing.

Includes the glob_files function which helps to aggregate files based
on known include directories and glob patterns.

This probably should just be replaced with something like scons or waf.

TODO: Generate dependencies for different languages?
"""

__version__ = '0.0.1'
__author__  = 'Brian Hunter'
__email__   = 'brian.hunter@cavium.com'

########################################################################################
# Globals

# A cache of modified filenames and their respective mtimes
Mtimes = {}

########################################################################################
# Exceptions

class NonExistantFile(Exception): pass
class EmptyFileList(Exception):   pass

########################################################################################
class Answer(object):
    def __init__(self, result, cause):
        self.result = result
        self.cause = cause

    def __str__(self):
        return "%s because %s" % (self.result, self.cause)

########################################################################################
def get_extreme_mtime(files, old, get_file=False):
    """
    Returns the oldest modification time of all the files given to it if old is True.
    Returns the newest modification time of all the files given to it if old is False.

    files   : (list of string, or string)
    old     : (bool)
    get_file: (bool) If true, also indication which file
    =>      : (int, string) A modification time and a filename (or None if not get_file)
    """


    if not files:
        raise EmptyFileList(files)

    func = {True:min, False:max}[old]

    if type(files) == str:
        files = [files,]

    # fill in the cached version of Mtimes and get it as a list
    mtimes = calc_mtimes(files)
    result = func(mtimes)

    cause = None
    if get_file:
        for key in Mtimes:
            if Mtimes[key] == result:
                cause = key
                break
    return (result, cause)

########################################################################################
def calc_mtimes(filenames):
    import os
    global Mtimes

    mtimes = []
    try:
        for fname in filenames:
            fname = os.path.abspath(fname)
            try:
                mtimes.append(Mtimes[fname])
            except KeyError:
                an_mtime = Mtimes[fname] = os.stat(fname).st_mtime
                mtimes.append(an_mtime)
    except:
        raise NonExistantFile(fname)

    return mtimes

########################################################################################
def pymake(targets, sources, get_cause=False):
    """
    Returns Answer class with result=True if any of the sources are
    newer than any of the targets, or if any of the targets do not exist.
    
    sources  : (list of string, or string) A list of (or one) filenames.
    targets  : (list of string, or string) A list of (or one) filenames.
    get_cause: (bool) If true, also return the cause.  If false, cause is None
    =>       : (bool, cause) If returning True and get_cause is False, then cause will be None
             : If returning True and get_cause is True, then cause is name of newest source
             : If returning False and get_cause is True, then cause will be name of oldest target
             : If returning False and get_cause is False, then cause will be None
    """

    try:
        (oldest_target_mtime, oldest_target) = get_extreme_mtime(targets, old=True, get_file=get_cause)
    except NonExistantFile as cause:
        return Answer(True, cause)

    try:
        (newest_source_mtime, newest_source) = get_extreme_mtime(sources, old=False, get_file=get_cause)
    except NonExistantFile as cause:
        raise NonExistantFile("Cannot find source file %s" % cause)
    except EmptyFileList:
        # if there are no sources, then we return True only if the target didn't exist, which happened above
        # so return false.
        return Answer(False, "no sources")

    if newest_source_mtime > oldest_target_mtime:
        return Answer(True, newest_source)
    else:
        return Answer(False, oldest_target)

########################################################################################
def glob_files(dirs, patterns, recursive=False):
    """
    Returns a list of all filenames that match the patterns given in all of the
    directories.

    If recursive is True, each directory will be searched top-down 
    (but will exclude '.' directories)
    """

    from glob import glob
    import os.path

    result = []
    for dir in dirs:
        if not recursive:
            for pattern in patterns:
                result.extend(glob(os.path.join(dir, pattern)))
        else:
            all_dirs = os.walk(dir)
            for adir in all_dirs:
                # prune .  directories to speed things up
                for idx, it in enumerate(adir[1]):
                    if it.startswith('.'):
                        del(adir[1][idx])

                    for pattern in patterns:
                        result.extend(glob(os.path.join(adir[0], pattern)))

    # ensure uniqueness and return absolute paths to each file
    result = list(set(result))
    result = [os.path.abspath(it) for it in result]
    return result

########################################################################################
if __name__ == '__main__':
    # treat argv[0] as target and rest as sources
    import sys
    print("Checking %s against %s" % (sys.argv[1], sys.argv[2:]))

    try:
        print(pymake(sys.argv[1], sys.argv[2:], get_cause=True))
    except NonExistantFile as file:
        print(file)
