#!/usr/bin/python3

# logger functionality

import sys
import select

import features.glob as glob
c = glob.c
s = glob.s
d = glob.d

from features.main_cfg import *


# pre-configuration  initialization
def cli__init_preconfig__():
   
   # enable disable config option
   c.cli__enabled = True
   
   # command line commands database
   d.cli__cmds = {}


cli__init_preconfig__()


# define argument parameter
def cli__load_config_define():
   
   feature__main_cfg__add_variable('cli_enabled', True, feature__main_cfg__validate_bool, None, """Enabled command line interface""", None)


# parse configuration value
def cli__load_config_postparse(args):
   
   d.cli__enabled = bool(args.cli_enabled)


# verify argument value after load
def cli__load_config_verify():
   
   error_num = 0
   crazy_num = 0
   
   return error_num, crazy_num


# initialize interactive keyboard configuration
def cli__init_postconfig():
   
   cli__register_cmd("help", cli__help_cmd_help, cli__help_cmd, "Command line help")
   
   return


# register command function
def cli__register_cmd(cmd_name, help_fn, exec_fn, cmd_short_descr):
   
   if cmd_name is None or cmd_name == "":
      LOG_ERROR('command name {} >> name is invalid'.format(cmd_name))
      return False
   
   d.cli__cmds[cmd_name] = glob.GlobVars()
   d.cli__cmds[cmd_name].cmd_name = cmd_name
   d.cli__cmds[cmd_name].cmd_short_descr = cmd_short_descr
   d.cli__cmds[cmd_name].help_fn = help_fn
   d.cli__cmds[cmd_name].exec_fn = exec_fn


# check and do interactive keyboard configuration
def cli__try_read_cmd():
   
   if select.select([sys.stdin], [], [], 0)[0]: # detect input to read
      clicmd = sys.stdin.readline().strip()  # Read a line without blocking
      if clicmd != None: # check return command line
         
         scmd = clicmd.split(None, 2) # split into arguments
         
         cmd1 = scmd[0] if len(scmd) > 0 else None
         arg2 = scmd[1] if len(scmd) > 1 else None
         arg3 = scmd[2] if len(scmd) > 2 else None
         
         cmd = d.cli__cmds.get(cmd1, None) # try to get possible command line command obj from dictionary
         
         if cmd == None:
            printf("Command <{}> not defined".format(cmd1))
         else:
            cmd.exec_fn(cmd1, arg2, arg3)

# self help functionality to describe other commands
def cli__help_cmd(cmd1, arg2, arg3):
   
   if arg2 is None or arg2 == "":
      print("""Welcome in Blocknet decentralized exchange automatic trading bot command line interface:
USAGE:

help                  - to show this help, and list all commands
help <command name>   - to show help for specific command

COMMANDS:""")

      for cmd_name in d.cli__cmds.keys():
         print("{} - {}".format(d.cli__cmds[cmd_name].cmd_name, d.cli__cmds[cmd_name].cmd_short_descr))
      
   else:
      cmd = d.cli__cmds.get(arg2, None)
      if cmd is None:
         print('command >> {} >> not defined'.format(arg2))
      else:
         print("{} - {}".format(cmd.cmd_name, cmd.cmd_short_descr))
         cmd.help_fn(arg2, arg3)

# help for help command
def cli__help_cmd_help(cmd1, arg2):
   print("""Rise and Shine Mr. Freeman, welcome in Blocknet Mesa Help transit systems ))""")
