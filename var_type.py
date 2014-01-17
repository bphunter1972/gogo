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
    def set_value(self, name, value):
        # value will be a string
        # cast for correct type if necessary
        my_value = self.cast_for_types(name, value)
        self.__setattr__(name, my_value)

    #--------------------------------------------
    def incr_value(self, name, value):
        my_value = self.cast_for_types(name, value)
        curr_val = self.__getattr__(name)
        self.__setattr__(name, (curr_val + my_value))

    #--------------------------------------------
    def help(self, name):
        return self.myvars[name][__HELP__]

    def cast_for_types(self, name, value):
        my_value = value if isinstance(value, self.myvars[name][__TYPES__]) else None
        if not my_value:
            # try casting to each of the possible types until one is found
            for my_type in self.myvars[name][__TYPES__]:
                try:
                    t = my_type(value)
                except TypeError:
                    continue
                else:
                    my_value = t

            if my_value is None:
                Log.critical("%s cannot go into %s.%s" % (value, self.v_type, name))

        return my_value