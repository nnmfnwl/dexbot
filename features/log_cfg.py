#!/usr/bin/python3

# logger functionality

import sys, select, time

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
   c.log__debug = bool(args.log_debug)
   c.log__hint = bool(args.log_hint)

   c.log__fatal = bool(args.log_fatal)
   c.log__error = bool(args.log_error)
   c.log__warning = bool(args.log_warning)
   
# verify argument value after load
def log__load_config_verify():
   
   error_num = 0
   crazy_num = 0

   return error_num, crazy_num
   
# register commands
def log__init_postconfig(reg_fn):
   
   reg_fn('a', log__cli_help, log__cli_cmd, "enable/disable ACTION log messages")
   reg_fn('i', log__cli_help, log__cli_cmd, "enable/disable INFO log messages")
   reg_fn('d', log__cli_help, log__cli_cmd, "enable/disable DEBUG log messages")
   reg_fn('h', log__cli_help, log__cli_cmd, "enable/disable HINT log messages")
   reg_fn('f', log__cli_help, log__cli_cmd, "enable/disable FATAL log messages")
   reg_fn('e', log__cli_help, log__cli_cmd, "enable/disable ERROR log messages")
   reg_fn('w', log__cli_help, log__cli_cmd, "enable/disable WARNING log messages")
   
# help for log cli
def log__cli_help(cmd1, arg2):
   
   if cmd1 == 'a':
      print("\nLOG >> enable/disable ACTION log messages\n")
   
   if cmd1 == 'i':
      print("\nLOG >> enable/disable INFO log messages\n")
   
   if cmd1 == 'd':
      print("\nLOG >> enable/disable DEBUG log messages\n")
         
   if cmd1 == 'h':
      print("\nLOG >> enable/disable HINT log messages\n")
         
   if cmd1 == 'f':
      print("\nLOG >> enable/disable FATAL log messages\n")
      
   if cmd1 == 'e':
      print("\nLOG >> enable/disable ERROR log messages\n")
   
   if cmd1 == 'w':
      print("\nLOG >> enable/disable WARNING log messages\n")
   
# check and do command line interface configuration
def log__cli_cmd(cmd1, arg2, arg3):
   
   if cmd1 == 'a':
      if c.log__action == True:
         c.log__action = False
         print("\nLOG >> ACTION disabled\n")
      else:
         c.log__action = True
         print("\nLOG >> ACTION enabled\n")
   
   if cmd1 == 'i':
      if c.log__info == True:
         c.log__info = False
         print("\nLOG >> INFO disabled\n")
      else:
         c.log__info = True
         print("\nLOG >> INFO enabled\n")
   
   if cmd1 == 'd':
      if c.log__debug == True:
         c.log__debug = False
         print("\nLOG >> DEBUG disabled\n")
      else:
         c.log__debug = True
         print("\nLOG >> DEBUG enabled\n")
         
   if cmd1 == 'h':
      if c.log__hint == True:
         c.log__hint = False
         print("\nLOG >> HINT disabled\n")
      else:
         c.log__hint = True
         print("\nLOG >> HINT enabled\n")
         
   if cmd1 == 'f':
      if c.log__fatal == True:
         c.log__fatal = False
         print("\nLOG >> FATAL disabled\n")
      else:
         c.log__fatal = True
         print("\nLOG >> FATAL enabled\n")
   
   if cmd1 == 'e':
      if c.log__error == True:
         c.log__error = False
         print("\nLOG >> ERROR disabled\n")
      else:
         c.log__error = True
         print("\nLOG >> ERROR enabled\n")
   
   if cmd1 == 'w':
      if c.log__warning == True:
         c.log__warning = False
         print("\nLOG >> WARNING disabled\n")
      else:
         c.log__warning = True
         print("\nLOG >> WARNING enabled\n")
   
