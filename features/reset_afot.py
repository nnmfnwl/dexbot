#!/usr/bin/python3

# reset all orders after specific number of open orders been finished or not enough orders finished and timeout happen
# AFOT - reset after finish or timeout

import time

import features.glob as glob
from features.main_cfg import *

# preconfiguration  initialization
def reset_afot__init_preconfig__():
    
    glob.d.reset_afot__finished_num = 0
    glob.d.reset_afot__finished_at = 0
    
    glob.c.reset_afot__num = 0
    glob.c.reset_afot__delay = 0
    
reset_afot__init_preconfig__()

# define argument parameter
def reset_afot__load_config_define():
    
    feature__main_cfg__add_variable('reset_after_order_finish_number', 0,  feature__main_cfg__validate_int, None, """number of orders to be finished before resetting orders (default=0 disabled)""", None)
    feature__main_cfg__add_variable('reset_after_order_finish_delay', 0, feature__main_cfg__validate_int, None, """delay after finishing last order before resetting orders in seconds (default=0 disabled)""", None)

# verify argument value after load
def reset_afot__load_config_verify():
    
    error_num = 0
    crazy_num = 0
    
    if glob.c.reset_afot__num < 0:
        print('**** ERROR.reset_afot >> <reset_after_order_finish_number> value <{0}> is invalid'.format(glob.c.reset_afot__num))
        error_num += 1
    
    if glob.c.reset_afot__delay < 0:
        print('**** ERROR.reset_afot >> <reset_after_order_finish_delay> value <{0}> is invalid'.format(glob.c.reset_afot__delay))
        error_num += 1
    
    return error_num, crazy_num

# parse configuration value
def reset_afot__load_config_postparse(args):
    
    glob.c.reset_afot__num = int(args.reset_after_order_finish_number)
    glob.c.reset_afot__delay = int(args.reset_after_order_finish_delay)

# reset counters and timers
def reset_afot__reset():
    
    glob.d.reset_afot__finished_num = 0
    glob.d.reset_afot__finished_at = 0

# add one more finished order into counter
def reset_afot__add():
    
    glob.d.reset_afot__finished_num += 1
    glob.d.reset_afot__finished_at = time.time()

# check if enough orders been finished or timeout happened
def reset_afot__check():
    
    # check if reset afot is enabled
    if glob.c.reset_afot__num != 0:
        # if already reached break and reset orders
        if glob.d.reset_afot__finished_num >= glob.c.reset_afot__num:
            print('^^^^ ACTION.reset_afot >> Maximum orders finished {0} / {1} has been reached, going to all orders reset now...'.format(glob.d.reset_afot__finished_num, glob.c.reset_afot__num))
            return True
        
        # if reset after order finish delay is enabled
        if glob.c.reset_afot__delay != 0:
            # if already reached delay break and reset orders
            if glob.d.reset_afot__finished_at != 0 and (time.time() - glob.d.reset_afot__finished_at) > glob.c.reset_afot__delay:
                print('^^^^ ACTION.reset_afot >> Maximum orders finished delay {0} / {1} has been reached, going to all orders reset now...'.format((time.time() - glob.d.reset_afot__finished_at), glob.c.reset_afot__delay))
                return True
    
    return False
