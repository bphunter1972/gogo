#!/usr/bin/env python

"""
Given a list of sources and a list of targets, returns True if the
targets should be remade based on modification times of all files.

Will raise NonExistantFile if any sources are missing.

Includes the glob_files function which helps to aggregate files based
on known include directories and glob patterns.

This probably should just be replaced with something like scons or waf.

TODO: Generate dependencies for different languages?
"""

__version__ = '0.0.0'
__author__  = 'Brian Hunter'
__email__   = 'brian.hunter@cavium.com'

########################################################################################
# Constants

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

    import os

    if not files:
        raise EmptyFileList(files)

    func = {True:min, False:max}[old]

    # if only one file is present
    if type(files) == str:
        try:
            return os.stat(files).st_mtime, files
        except:
            raise NonExistantFile(files)
    elif get_file:
        # if we have to also return the cause
        try:
            mtimes = [(os.stat(file).st_mtime, file) for file in files]
        except OSError:
            raise NonExistantFile(file)
        else:
            extreme_mtime = func([it[0] for it in mtimes])
            return [it for it in mtimes if it[0] == extreme_mtime][0]
    else:
        # else, this one is faster
        try:
            mtimes = [os.stat(file).st_mtime for file in files]
        except:
            raise NonExistantFile(file)
        else:
            return (func(mtimes), None)

########################################################################################
def pymake(targets, sources, get_cause=False):
    """
    Returns true (target should be made) if any of the sources are
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
    print("Checking", sys.argv[1], "against", sys.argv[2:])

    try:
        print(pymake(sys.argv[1], sys.argv[2:], get_cause=True))
    except NonExistantFile as file:
        print(file)
