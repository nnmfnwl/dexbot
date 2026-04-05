#!/usr/bin/python3

# logger functionality

import features.glob as glob
c = glob.c
s = glob.s
d = glob.d

from features.main_cfg import *

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
