"""
A class that holds a global variable type
"""

__VALUE__, __TYPES__, __HELP__ = range(3)

Log = None

class VarType(object):
    def __init__(self, v_dict, v_type):
        self.myvars = v_dict.copy()
        self.v_type = v_type

    #--------------------------------------------
    def __setattr__(self, name, value):
        if name in ('myvars', 'v_type'):
            object.__setattr__(self, name, value)
            return
        try:
            if type(value) not in self.myvars[name][__TYPES__]:
                raise AttributeError("%s is not permitted for %s" % (type(value), name))
            self.myvars[name][__VALUE__] = value
        except KeyError:
            Log.critical("The variable %s.%s does not exist. Perhaps one of these instead?\n\t%s" % (self.v_type, name, self.myvars.keys()))

    #--------------------------------------------
    def __getattr__(self, name):
        return self.myvars[name][__VALUE__]

    #--------------------------------------------
    def __repr__(self):
         d = dict([(key,self.myvars[key][__VALUE__]) for key in self.myvars.keys()])
         return d.__repr__()

    #--------------------------------------------
    def help(self, name):
        return self.myvars[name][__HELP__]
