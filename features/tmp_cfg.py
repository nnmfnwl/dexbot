#!/usr/bin/python3

# flush canceled orders timer plugin

import time
import pickle

import features.glob as glob

def feature__tmp_cfg__load_cfg(tmp_cfg_file_name):
    
    glob.d.feature__tmp_cfg__file_name = tmp_cfg_file_name
    glob.d.feature__tmp_cfg__data = {}
    
    try:
        file = open(glob.d.feature__tmp_cfg__file_name, "rb")
        glob.d.feature__tmp_cfg__data = pickle.load(file)
        file.close()
    except FileNotFoundError:
        print('DEBUG: temporary configuration was not created yet')
    except EOFError:
        print('DEBUG: temporary configuration was empty')
    
    print('DEBUG: temporary configuration data: {}'.format(glob.d.feature__tmp_cfg__data))
    
# returns value of loaded temporary configuration
def feature__tmp_cfg__get_value(name, default = None):
    
    ret = glob.d.feature__tmp_cfg__data.get(name, default)
    return ret
    
# updates value of temporary configuration file
def feature__tmp_cfg__set_value(name, value, update_tmp_cfg_file = True):
    
    glob.d.feature__tmp_cfg__data[name] = value
    
    if update_tmp_cfg_file == True:
        file = open(glob.d.feature__tmp_cfg__file_name,'wb')
        pickle.dump(glob.d.feature__tmp_cfg__data, file)
        file.close()
