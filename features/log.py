#!/usr/bin/python3

# logger functionality

import time

from inspect import getframeinfo, stack
import os

import features.glob as glob
c = glob.c
s = glob.s
d = glob.d

from features.tmp_cfg import *
from features.main_cfg import *

# pre-configuration  initialization
def log__init_preconfig__():
    
    # static boundary asset
    c.log__action = True
    c.log__info = True
    c.log__debug = True
    c.log__hint = True
    
    c.log__fatal = True
    c.log__error = True
    c.log__warning = True

log__init_preconfig__()

# define argument parameter
def log__load_config_define():
    
    feature__main_cfg__add_variable('log_action', True, feature__main_cfg__validate_bool, None, """show action log messages, (default=True enabled)""", None)
    feature__main_cfg__add_variable('log_info', True, feature__main_cfg__validate_bool, None, """show info log messages, (default=True enabled)""", None)
    feature__main_cfg__add_variable('log_debug', True, feature__main_cfg__validate_bool, None, """show debug log messages, (default=True enabled)""", None)
    feature__main_cfg__add_variable('log_hint', True, feature__main_cfg__validate_bool, None, """show hint log messages, (default=True enabled)""", None)
    
    feature__main_cfg__add_variable('log_fatal', True, feature__main_cfg__validate_bool, None, """show fatal log messages, (default=True enabled)""", None)
    feature__main_cfg__add_variable('log_error', True, feature__main_cfg__validate_bool, None, """show error log messages, (default=True enabled)""", None)
    feature__main_cfg__add_variable('log_warning', True, feature__main_cfg__validate_bool, None, """show warning log messages, (default=True enabled)""", None)
    

# parse configuration value
def log__load_config_postparse(args):
    
    c.log__action = bool(args.log_action)
    c.log__info = bool(args.log_info)
    c.log__debug = bool(args.log_dbg)
    
    c.log__fatal = bool(args.log_fatal)
    c.log__error = bool(args.log_error)
    c.log__warning = bool(args.log_warning)
    
# verify argument value after load
def log__load_config_verify():
    
    error_num = 0
    crazy_num = 0
    
    return error_num, crazy_num

# log action message
def LOG_ACTION(message, prefix = ""):
    
    if c.log__action:
        caller = getframeinfo(stack()[1][0]) # <-- stack()[1][0] for next caller line
        print("{}^^^^ ACTION {}:{} >> {}".format(prefix, os.path.basename(caller.filename), caller.lineno, message))
        
# log info message
def LOG_INFO(message, prefix = ""):
    
    if c.log__info:
        caller = getframeinfo(stack()[1][0]) # <-- stack()[1][0] for next caller line
        print("{}>>>> INFO {}:{} >> {}".format(prefix, os.path.basename(caller.filename), caller.lineno, message))
        
# log info message
def LOG_DEBUG(message, prefix = ""):
    
    if c.log__debug:
        caller = getframeinfo(stack()[1][0]) # <-- stack()[1][0] for next caller line
        print("{}---- DEBUG {}:{} >> {}".format(prefix, os.path.basename(caller.filename), caller.lineno, message))
        
# log info message
def LOG_HINT(message, prefix = ""):
    
    if c.log__hint:
        caller = getframeinfo(stack()[1][0]) # <-- stack()[1][0] for next caller line
        print("{}++++ HINT {}:{} >> {}".format(prefix, os.path.basename(caller.filename), caller.lineno, message))


# log fatal message
def LOG_FATAL(message, prefix = ""):
    
    if c.log__fatal:
        caller = getframeinfo(stack()[1][0]) # <-- stack()[1][0] for next caller line
        print("{}**** FATAL {}:{} >> {}".format(prefix, os.path.basename(caller.filename), caller.lineno, message))
        
# log error message
def LOG_ERROR(message, prefix = ""):
    
    if c.log__error:
        caller = getframeinfo(stack()[1][0]) # <-- stack()[1][0] for next caller line
        print("{}**** ERROR {}:{} >> {}".format(prefix, os.path.basename(caller.filename), caller.lineno, message))
        

# log warning message
def LOG_WARNING(message, prefix = ""):
    
    if c.log__warning:
        caller = getframeinfo(stack()[1][0]) # <-- stack()[1][0] for next caller line
        print("{}#### WARNING {}:{} >> {}".format(prefix, os.path.basename(caller.filename), caller.lineno, message))
