"""
Imported by vkit configuration files to set compile options.
"""

import var_type

# How to compile and run with VCS
VLOG = {
    # Name             (default, possible types)   Help
    'OPTIONS'        : ["", (str,),       "Build options for both VCS and VLOGAN"],
    'VCS_OPTIONS'    : ["", (str,),       "Build options for VCS only"],
    'VLOGAN_OPTIONS' : ["", (str,),       "Build options for VLOGAN only"],
    'TAB_FILES'      : [[], (list,),      "PLI files that should also be added to the build command-line (-P <name>)"],
    'SO_FILES'       : [[], (list,),      "Shared Objects that will be added to the build command-line (-LDFLAGS '<all>')"],
    'ARC_LIBS'       : [[], (list,),      ".a/.o archive libraries that will be added to the build command-line"],
    'DEFINES'        : [[], (list,),      "All +defines as needed"],
    'IGNORE_WARNINGS': [[], (list,),      "Warnings that should be ignored by VCS during vlog."],
}

class Vlog(var_type.VarType):
    def __init__(self):
        super(Vlog, self).__init__(VLOG, 'VLOG')
