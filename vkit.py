"""
A class that represents a Vkit, with common faculties
"""

import os.path
import gvars

class Vkit(object):
    """
    Represents a vkit

    entry:  1) A path pointing directly to the flist file, where the flist base name and package name are the same
            2) A 3 entry tuple, with a [0]=vkit dir name, [1]=flist name, [2]=pkg name
            3) A 2-entry tuple, with [0]=vkit dir name, [1]=flist & pkg name
    """
    def __init__(self, entry):
        if '/' in entry:
            self.dir_name, self.flist_name = os.path.split(entry)
            self.flist_name = self.flist_name.replace('.flist', '')
            self.pkg_name = self.flist_name
        elif type(entry) == tuple:
            try:
                self.dir_name, self.flist_name, self.pkg_name = entry
            except:
                self.dir_name, self.flist_name = entry
                self.pkg_name = self.flist_name
        else:
            self.dir_name = self.flist_name = self.pkg_name = entry

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

