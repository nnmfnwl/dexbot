#!/usr/bin/python3

# flush canceled orders timer plugin

import time

import features.glob as glob

# preconfiguration  initialization
def feature__flush_co__init_preconfig():
    
    glob.c.feature__flush_co__delay = 0
    glob.d.feature__flush_co__time_start = time.time()

# define argument parameter
def feature__flush_co__load_config_define(parser, argparse):
    
    parser.add_argument('--flush_canceled_orders', type=int, help='timer in seconds to remove all canceled orders from xbridge orders history(default=0 disabled)', default=0)

# verify argument value after load
def feature__flush_co__load_config_verify():
    
    error_num = 0
    crazy_num = 0
    
    if glob.c.feature__flush_co__delay < 0:
        print('**** ERROR, <feature__flush_co__delay> value <{0}> is invalid'.format(glob.c.feature__flush_co__delay))
        error_num += 1
    
    return error_num, crazy_num

# parse configuration value
def feature__flush_co__load_config_postparse(args):
    
    glob.c.feature__flush_co__delay = int(args.flush_canceled_orders)

# check if and in care of timeout flush all canceled orders
def feature__flush_co__check(dxbottools):
    
    if glob.c.feature__flush_co__delay > 0:
        if (time.time() - glob.d.feature__flush_co__time_start) > glob.c.feature__flush_co__delay:
            print('>>>> As timer {} we are flushing canceled orders'.format(glob.c.feature__flush_co__delay))
            glob.d.feature__flush_co__time_start = time.time()
            dxbottools.rpc_connection.dxFlushCancelledOrders()
            return True
        
    return False
