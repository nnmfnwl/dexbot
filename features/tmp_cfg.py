#!/usr/bin/python3

# flush canceled orders timer plugin

import time
import pickle
import sys

import features.glob as glob

# preconfiguration  initialization
def feature__tmp_cfg__init_preconfig__():
    
    glob.c.feature__tmp_cfg__file_name = None
    glob.d.feature__tmp_cfg__data = {}
    glob.d.feature__tmp_cfg__ready = False

feature__tmp_cfg__init_preconfig__()

# define argument parameter
def feature__tmp_cfg__load_config_define(parser, argparse):
    return

# parse configuration value
def feature__tmp_cfg__load_config_postparse(args):
    
    glob.c.feature__tmp_cfg__file_name = str(args.config)

# verify argument value after load
def feature__tmp_cfg__load_config_verify():
    
    error_num = 0
    crazy_num = 0
    
    if glob.c.feature__tmp_cfg__file_name != None and glob.c.feature__tmp_cfg__file_name != "":
        glob.c.feature__tmp_cfg__file_name = glob.c.feature__tmp_cfg__file_name + ".tmp.cfg"
        glob.d.feature__tmp_cfg__ready = True
    else:
        print('** ERROR >> setting >> --config filename+.tmp.cfg >> value <{}> is invalid'.format(glob.c.feature__tmp_cfg__file_name))
        error_num += 1
        
    return error_num, crazy_num

# load temporary configuration from saved file
def feature__tmp_cfg__load_saved_cfg():
    
    if glob.d.feature__tmp_cfg__ready == False:
        print('** FATAL >> feature__tmp_cfg >> must be initialized first!')
        sys.exit(1)
    
    try:
        file = open(glob.c.feature__tmp_cfg__file_name, "rb")
        glob.d.feature__tmp_cfg__data = pickle.load(file)
        file.close()
    except FileNotFoundError:
        print('DEBUG: temporary configuration was not created yet')
    except EOFError:
        print('DEBUG: temporary configuration was empty')
    
    print('DEBUG: temporary configuration data: {}'.format(glob.d.feature__tmp_cfg__data))
    
# returns value of loaded temporary configuration
def feature__tmp_cfg__get_value(name, default = None):
    
    if glob.d.feature__tmp_cfg__ready == False:
        print('** FATAL >> feature__tmp_cfg >> must be initialized first!')
        sys.exit(1)
    
    ret = glob.d.feature__tmp_cfg__data.get(name, default)
    return ret
    
# updates value of temporary configuration file
def feature__tmp_cfg__set_value(name, value, update_tmp_cfg_file = True):
    
    if glob.d.feature__tmp_cfg__ready == False:
        print('** FATAL >> feature__tmp_cfg >> must be initialized first!')
        sys.exit(1)
    
    glob.d.feature__tmp_cfg__data[name] = value
    
    if update_tmp_cfg_file == True:
        file = open(glob.c.feature__tmp_cfg__file_name,'wb')
        pickle.dump(glob.d.feature__tmp_cfg__data, file)
        file.close()
