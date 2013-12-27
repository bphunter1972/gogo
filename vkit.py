"""
A class that represents a Vkit, with common faculties
"""

import os.path
import gvars

Log = gvars.Log

class Vkit(object):
    """
    Represents a vkit

    entry:  1) A path pointing directly to the flist file, where the flist base name and package name are the same
            2) A dictionary with dir_name, flist_name, and pkg_name. If any are missing, the flist_name defaults to the dir_name
                and the pkg_name defaults to the flist_name
    """
    def __init__(self, entry):
        if type(entry) == dict:
            self.dir_name = entry['dir_name']
            self.flist_name = entry['flist_name'] if 'flist_name' in entry else self.dir_name
            self.pkg_name = entry['pkg_name'] if 'pkg_name' in entry else self.flist_name
        elif '/' in entry:
            self.dir_name, self.flist_name = os.path.split(entry)
            self.flist_name = self.flist_name.replace('.flist', '')
            self.pkg_name = self.flist_name
        else:
            self.dir_name = self.flist_name = self.pkg_name = entry

        Log.debug("Set dir_name=%s flist_name=%s pkg_name=%s" % (self.dir_name, self.flist_name, self.pkg_name))

    #--------------------------------------------
    def get_pkg_name(self):
        return "DEFAULT.%s_pkg" % self.pkg_name

    #--------------------------------------------
    def flist_file(self):
        return os.path.join(gvars.Vars['VKITS_DIR'], self.dir_name, "%s.flist" % self.flist_name)

    #--------------------------------------------
    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)

    #--------------------------------------------
    def __ne__(self, other):
        return not self.__eq__(other)

    #--------------------------------------------
    def get_all_sources(self, patterns=['.sv', '.v']):
        """
        Returns a list of ALL files in the vkit directory.
        """

        from pymake import glob_files
        dir = os.path.join(gvars.Vars['VKITS_DIR'], self.dir_name)
        patterns = ['*%s' % it for it in patterns]
        srcs = glob_files([dir], patterns, recursive=True)
        return srcs
