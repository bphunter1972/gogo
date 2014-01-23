"""
A class that represents a Vkit, with common faculties
"""

import os.path
import gvars
import sys

Log = gvars.Log

class Vkit(object):
    """
    Represents a vkit

    entry: (string) The name of the vkits directory in which to find a vcfg.py file
           (dict)   A dictionary containing the vkit parameters found in a vcfg.py file
    """
    def __init__(self, entry):
        self.vkits_dir = gvars.PROJ.VKITS_DIR

        # The vkit is either a dictionary, or a vcfg.py file located in the specified path from vkits_dir, 
        # or it's simply a name that can be applied to a default dictionary
        config = {}
        if type(entry) == dict:
            config = entry
        elif type(entry) == str:
            if entry.endswith('.py') and os.path.exists(entry):
                config = self.load_vcfg(entry)
            else:
                # create a simple default vkit
                config = {'NAME':entry, 'DIR':entry, 'FLIST':entry}

        try:
            self.name = config['NAME']
            Log.debug("Loaded config for %s" % self.name)
        except KeyError:
            Log.critical("config for %s has no attribute NAME." % entry)

        try:
            self.dir_name = config['DIR']
            if not isinstance(self.dir_name, str):
                Log.critical("Directory specified for %s is not a string." % entry)
            if not self.dir_name.startswith(os.path.join(self.vkits_dir)):
                self.dir_name = os.path.join(self.vkits_dir, self.dir_name)
        except KeyError:
            self.dir_name = os.path.join(self.vkits_dir, self.name)
        self.dir_name = os.path.abspath(self.dir_name)

        try:
            self.flist_name = config['FLIST']
        except KeyError:
            self.flist_name = os.path.join(self.dir_name, "%s.flist" % self.name)
        if not self.flist_name.startswith(self.dir_name):
            self.flist_name = os.path.join(self.dir_name, self.flist_name)
        if not self.flist_name.endswith(".flist"):
            self.flist_name += '.flist'

        try:
            self.pkg_name = config['PKG_NAME']
        except KeyError:
            self.pkg_name = "%s_pkg" % self.name
        if not self.pkg_name.endswith("_pkg"):
            self.pkg_name += "_pkg"

        try:
            self.dependencies = config['DEPENDENCIES']
        except KeyError:
            self.dependencies = []

    #--------------------------------------------
    def load_vcfg(self, entry):
        """
        The entry represents a vcfg.py file. Import it and use its dictionary to get 
        values for this vkit.
        """

        import imp
        mod_name,ext = os.path.splitext(os.path.basename(entry))
        try:
            mod = imp.load_source(mod_name , entry)
        except ImportError:
            if gvars.Options.dbg:
                raise
            else:
                Log.critical("Unable to import %s from %s" % (mod_name))

        result = mod.__dict__.copy()
        del sys.modules[mod_name]
        return result

    #--------------------------------------------
    def __repr__(self):
        return self.get_pkg_name()

    #--------------------------------------------
    def get_pkg_name(self):
        return "DEFAULT.%s" % self.pkg_name

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
        patterns = ['*%s' % it for it in patterns]
        srcs = glob_files([self.dir_name], patterns, recursive=True)
        return srcs
