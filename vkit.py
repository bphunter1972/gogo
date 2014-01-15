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

    entry: The name of the vkits directory in which to find a vcfg.py file
    """
    def __init__(self, entry):
        self.vkits_dir = gvars.PROJ.VKITS_DIR

        if type(entry) == dict:
            config = entry
        else:
            config = self.load_vcfg(entry)

        try:
            self.name = config['NAME']
            Log.debug("Loaded config for %s" % self.name)
        except KeyError:
            Log.critical("config for %s has no attribute NAME." % entry)

        try:
            self.dir_name = config['DIR']
            if not self.dir_name.startswith(os.path.join(self.vkits_dir)):
                self.dir_name = os.path.join(self.vkits_dir, self.dir_name)
        except KeyError:
            self.dir_name = os.path.join(self.vkits_dir, self.name)
        self.dir_name = os.path.abspath(self.dir_name)

        try:
            self.flist_name = config['FLIST']
        except KeyError:
            self.flist_name = os.path.join(self.dir_name, "%s.flist" % self.name)
        # Log.info("1. flist=%s" % self.flist_name)
        if not self.flist_name.startswith(self.dir_name):
            self.flist_name = os.path.join(self.dir_name, self.flist_name)
            # Log.info("2. flist=%s" % self.flist_name)
        if not self.flist_name.endswith(".flist"):
            self.flist_name += '.flist'
            # Log.info("3. flist=%s" % self.flist_name)

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
        From the path vkits/'entry', import the file 'vcfg.py' and use its 
        dictionary to get values for this vkit
        """

        vcfg_path = os.path.join(self.vkits_dir, entry)
        old_sys_path, sys.path = sys.path, [vcfg_path]

        # import, then reload, to ensure that we got the correct one.
        # if we've already imported one vcfg file, then importing it again won't do anything
        # if we just try to reload, then it will fail the first time
        try:
            import vcfg
            reload(vcfg)
        except ImportError:
            Log.critical("Unable to import vcfg.py from %s" % sys.path)

        # remove vcfg_path from system import path
        sys.path = old_sys_path

        result = vcfg.__dict__.copy()
        del sys.modules['vcfg']
        return result

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
