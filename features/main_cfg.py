#!/usr/bin/python3

# main configuration definition and base checking module

import os.path
import datetime
import shutil

import features.glob as glob
from features.log import *

# main configuration initialization
def feature__main_cfg__init_preconfig__():
   
   glob.d.main_cfg = glob.GlobVars()
   glob.d.main_cfg.cfg = {}
   glob.d.main_cfg.filename = "default.cfg.py"
   
   glob.c.main_cfg = glob.GlobVars()
   glob.c.main_cfg.cfg = glob.GlobVars()
   
# main configuration automatic initialization
feature__main_cfg__init_preconfig__()

# add one more item to configuration variable definition
def feature__main_cfg__add_variable(var_name, default_val = None, validation_fn = None, validation_arg = None, description_str = None, examples_list = None):
   
   if var_name is None or var_name == "":
      LOG_ERROR('variable name {} >> name is invalid'.format(var_name))
      return False
      
   if description_str is None or description_str == "":
      LOG_ERROR('variable name {} >> description {} >> is invalid'.format(var_name, description_str))
      return False
   
   if glob.d.main_cfg.cfg.get(var_name, None) is not None:
      LOG_ERROR('variable name {} >> add failed because already exist'.format(var_name))
      return False
   
   glob.d.main_cfg.cfg[var_name] = {}
   glob.d.main_cfg.cfg[var_name]['description'] = description_str
   glob.d.main_cfg.cfg[var_name]['defaultvalue'] = default_val
   glob.d.main_cfg.cfg[var_name]['value'] = default_val
   glob.d.main_cfg.cfg[var_name]['validationfn'] = validation_fn
   glob.d.main_cfg.cfg[var_name]['validationarg'] = validation_arg
   glob.d.main_cfg.cfg[var_name]['examples'] = examples_list
   
   return True

# validate configuration value
def feature__main_cfg__add_value(var_name, value):
   
   if var_name is None or var_name == "":
      LOG_ERROR('variable >> {} >> name is invalid'.format(var_name))
      return False
      
   cfg = glob.d.main_cfg.cfg.get(var_name, None)
   if cfg is None:
      LOG_ERROR('variable >> {} >> not defined'.format(var_name))
      return False
      
   descr = cfg.get('description', None)
   default = cfg.get('defaultvalue', None)
   fn = cfg.get('validationfn', None)
   arg = cfg.get('validationarg', None)
   examples = cfg.get('examples', None)
   
   if value is not None: # else there is already default value
      if fn is None:
         cfg['value'] = value
      else:
         ret, value2 = fn(var_name, value, arg)
         if ret is True:
            cfg['value'] = value2
         else:
            LOG_ERROR('variable >> {} >> value >> {} >> is invalid'.format(var_name, value))
            return False
            
   return True

# load all configuration values from .py file
def feature__main_cfg__load_cfg(filename):
   error_num = 0
   
   if filename is None:
      LOG_ERROR(" --config filename is None")
      error_num +=1
      return error_num
   
   glob.d.main_cfg.filename = filename + '.py'
   
   # TODO analyze file extension and load by format
   
   LOG_INFO("using --config file >> <{}>".format(filename))
   glob.d.main_cfg.filedata = __import__(filename)
   
   # try to load and validate all configuration from file by main_cfg feature
   for cfg_name in glob.d.main_cfg.filedata.cfg.keys():
      ret = feature__main_cfg__add_value(cfg_name, glob.d.main_cfg.filedata.cfg[cfg_name])
      if ret is not True:
         error_num +=1
   
   return error_num

# convert all cfg variables into object format
def feature__main_cfg__parse_cfg():
   
   for cfg_name in glob.d.main_cfg.cfg.keys():
        setattr(glob.c.main_cfg.cfg, cfg_name, glob.d.main_cfg.cfg[cfg_name]["value"])

# return parsed cfg obj
def feature__main_cfg__get_cfg_obj():
   return glob.c.main_cfg.cfg

# get configuration variable value
def feature__main_cfg__get_value(var_name):
   
   if var_name is None or var_name == "":
      LOG_ERROR('variable >> {} >> name is invalid'.format(var_name))
      return False, None
   
   cfg = glob.d.main_cfg.cfg.get(var_name, None)
   if cfg is None:
      LOG_ERROR('variable >> {} >> not defined'.format(var_name))
      return False, None
      
   return True, cfg['value']
   
# get configuration variable object
def feature__main_cfg__get_cfg(var_name):
   
   if var_name is None or var_name == "":
      LOG_ERROR('variable >> {} >> name is invalid'.format(var_name))
      return False, None
   
   cfg = glob.d.main_cfg.cfg.get(var_name, None)
   if cfg is None:
      LOG_ERROR('variable >> {} >> not defined'.format(var_name))
      return False, None
      
   return True, cfg

# generate new configuration template file
def feature__main_cfg__generate_cfg(filename, action):
   
   # check action validity
   if action == "defaults":
      LOG_ACTION('generate_cfg >> generating configuration file >> {} >> style >> {}'.format(filename, action))
   elif action == "template":
      LOG_ACTION('generate_cfg >> generating configuration file >> {} >> style >> {}'.format(filename, action))
   elif action == "update":
      LOG_ACTION('generate_cfg >> generating configuration file >> {} >> style >> {}'.format(filename, action))
   else:
      LOG_ACTION('generate_cfg >> generating configuration file >> {} >> invalid style >> {}'.format(filename, action))
      return False
   
   # check if file not exist
   if os.path.exists(filename) is True and os.path.getsize(filename) > 0 :
      if action == "update":
         shutil.copy("./" + filename, "./cfg_backup/" + filename + str(datetime.datetime.now()))
      else:
         LOG_ERROR('generate_cfg >> generating configuration file >> {} >> file already exist >> {} >> please remove configuration file first'.format(filename, action))
         return False
   
   # open file
   file = open(filename,'w', encoding="utf-8")
   
   # write down copyright
   file.write("""#!/usr/bin/env python3

# ~ MIT License

# ~ Copyright (c) 2020-2026 NNMFNWL

# ~ Permission is hereby granted, free of charge, to any person obtaining a copy
# ~ of this software and associated documentation files (the "Software"), to deal
# ~ in the Software without restriction, including without limitation the rights
# ~ to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# ~ copies of the Software, and to permit persons to whom the Software is
# ~ furnished to do so, subject to the following conditions:

# ~ The above copyright notice and this permission notice shall be included in all
# ~ copies or substantial portions of the Software.

# ~ THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# ~ IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# ~ FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# ~ AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# ~ LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# ~ OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# ~ SOFTWARE.\n""")
   
   # write down main cfg dict variable
   file.write('cfg = {}\n')

   # iterate all configuration and write em all into file
   for cfg_name in glob.d.main_cfg.cfg.keys():
      
      cfg = glob.d.main_cfg.cfg[cfg_name]
      
      # write down description
      file.write('\n"""{}"""\n'.format(cfg["description"]))
      
      # write down default values
      if action == "defaults":
         if cfg.get("validationfn", None) == feature__main_cfg__validate_dict:
            file.write('cfg[\'{}\'] = {}\n'.format(cfg_name, cfg.get("defaultvalue", "{}")))
         elif cfg.get("validationfn", None) == feature__main_cfg__validate_list:
            file.write('cfg[\'{}\'] = {}\n'.format(cfg_name, cfg.get("defaultvalue", "[]")))
         elif cfg.get("validationfn", None) == feature__main_cfg__validate_bool:
            file.write('cfg[\'{}\'] = {}\n'.format(cfg_name, cfg.get("defaultvalue", False)))
         elif cfg.get("validationfn", None) == feature__main_cfg__validate_int:
            file.write('cfg[\'{}\'] = {}\n'.format(cfg_name, cfg.get("defaultvalue", 0)))
         elif cfg.get("validationfn", None) == feature__main_cfg__validate_float:
            file.write('cfg[\'{}\'] = {}\n'.format(cfg_name, cfg.get("defaultvalue", 0.0)))
         else:
            file.write('cfg[\'{}\'] = "{}"\n'.format(cfg_name, cfg.get("value", "")))
      # write down as template
      elif action == "template":
         file.write('cfg[\'{}\'] = "{}cc_{}{}"\n'.format(cfg_name, '{', cfg_name, '}'))
      # else write down actual update configuration
      else:
         if cfg.get("validationfn", None) == feature__main_cfg__validate_dict:
            file.write('cfg[\'{}\'] = {}\n'.format(cfg_name, cfg.get("value", "{}")))
         elif cfg.get("validationfn", None) == feature__main_cfg__validate_list:
            file.write('cfg[\'{}\'] = {}\n'.format(cfg_name, cfg.get("value", "[]")))
         elif cfg.get("validationfn", None) == feature__main_cfg__validate_bool:
            file.write('cfg[\'{}\'] = {}\n'.format(cfg_name, cfg.get("value", False)))
         elif cfg.get("validationfn", None) == feature__main_cfg__validate_int:
            file.write('cfg[\'{}\'] = {}\n'.format(cfg_name, cfg.get("value", 0)))
         elif cfg.get("validationfn", None) == feature__main_cfg__validate_float:
            file.write('cfg[\'{}\'] = {}\n'.format(cfg_name, cfg.get("value", 0.0)))
         else:
            file.write('cfg[\'{}\'] = "{}"\n'.format(cfg_name, cfg.get("value", "")))
      
   # close file
   file.close()
   
   return True

# validate boolean
def feature__main_cfg__validate_bool(var_name, val, arg):
   
   if arg is not None:
      LOG_ERROR('variable >> {} = {} >> unexpect argument found {}'.format(var_name, val, arg))
      return False, False
   
   if isinstance(val, bool):
      return True, val
   elif isinstance(val, str):
      if val.lower() in ['true', 'enabled', 'yes', '1']:
         return True, True
      else:
         return True, False
   elif isinstance(val, int):
      if val > 0:
         return True, True
      else:
         return False, False
      
   return False, False
      
# validate int
def feature__main_cfg__validate_int(var_name, val, arg):
   
   if arg is not None:
      LOG_ERROR('variable >> {} = {} >> unexpect argument found {}'.format(var_name, val, arg))
      return False, int(0)
   
   if isinstance(val, int):
      return True, val
   elif isinstance(val, str):
      return True, int(val)
   
   return False, int(0)

# validate float
def feature__main_cfg__validate_float(var_name, val, arg):
   
   if arg is not None:
      LOG_ERROR('variable >> {} = {} >> unexpect argument found {}'.format(var_name, val, arg))
      return False, float(0)
   
   if isinstance(val, float):
      return True, val
   elif isinstance(val, str):
      return True, float(val)
   
   return False, float(0)

# validate str
def feature__main_cfg__validate_str(var_name, val, arg):
   
   if arg is not None:
      LOG_ERROR('variable >> {} = {} >> unexpect argument found {}'.format(var_name, val, arg))
      return False, str("")
   
   if isinstance(val, str):
      return True, val
   
   return True, str(val)

def feature__main_cfg__validate_password(var_name, val, arg):
   
   if arg is not None:
      LOG_ERROR('variable >> {} = {} >> unexpect argument found {}'.format(var_name, val, arg))
      return False, str("")
   
   if isinstance(val, str):
      return True, val
   
   return False, None

# validate select
def feature__main_cfg__validate_select(var_name, val, arg):
   
   if arg is None:
      LOG_ERROR('variable >> {} = {} >> expected argument not found {}'.format(var_name, val, arg))
      return False, str("")
   
   return True, val
   
# validate dict
def feature__main_cfg__validate_dict(var_name, val, arg):
   
   if arg is not None:
      LOG_ERROR('variable >> {} = {} >> unexpect argument found {}'.format(var_name, val, arg))
      return False, dict({})
   
   if isinstance(val, dict):
      return True, val
   
   return True, dict(val)
   
# validate list
def feature__main_cfg__validate_list(var_name, val, arg):
   
   if arg is not None:
      LOG_ERROR('variable >> {} = {} >> unexpect argument found {}'.format(var_name, val, arg))
      return False, list([])
   
   if isinstance(val, list):
      return True, val
   
   return True, list(val)


# register commands
def main_cfg__init_postconfig(reg_fn):
   
   reg_fn('cfg', main_cfg__cli_cfg_help, main_cfg__cli_cfg, "update configuration")
   
# help for log cli
def main_cfg__cli_cfg_help(cmd1, arg2):
   print("\nCFG >> just one argument <update> needed to make configuration update\n")
   
# check and do command line interface configuration
def main_cfg__cli_cfg(cmd1, arg2, arg3):
   
      if arg2 == "update":
         LOG_ACTION("configuration update in progress")
         feature__main_cfg__generate_cfg(glob.d.main_cfg.filename, "update")
      else:
         LOG_ERROR("command <cfg> takes only argument <update>")
   
