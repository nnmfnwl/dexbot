#!/usr/bin/env python3
import time
import random
import argparse
import sys
import logging
from utils import dxbottools
from utils import getpricing as pricebot
from utils import dxsettings

from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer

import features.glob as glob

from features.pricing_storage import *
from features.pricing_proxy_server import *

# welcome message
def start_welcome_message():
    print('>>>> Starting maker bot proxy cache')

# initialization of config independent items or items needed for config load
def init_preconfig():
    print('>>>> Preconfig initialization')
    
    proxy_server__init_preconfig()

# initialization of items dependent on config
def init_postconfig():
    print('>>>> Postconfig initialization')
    
    proxy_server__init_postconfig()
    
    # initialize pricing storage and set proxy client
    pricing_storage__init_postconfig("proxy.tmp.pricing", 60, "", 2, 6, pricing_proxy_server__pricing_storage__try_get_price_fn)

def load_config():
    global c, s, d
    print('>>>> Loading program configuration')
    
    # prepare arg parser and define arguments
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--restore', type=glob.t.argparse_bool, nargs='?', const=True, help='Variable used to let bot know to try restore auto-configured values from tmp cfg. Usable when secondary run script management by, also manual testing... (default=False not restoring)', default=False)
    
    parser.add_argument('--imreallysurewhatimdoing', type=int, default=0, help='This argument allows user to specify number of non-standard configuration values for special cases like user want to activate bot trading later relatively higher price than actual is')
    
    proxy_server__load_config_define(parser, argparse)
    
    pricing_storage__load_config_define(parser, argparse)
    
    # parse arguments and postparse arguments
    args = parser.parse_args()
    
    proxy_server__load_config_postparse(args)
    
    pricing_storage__load_config_postparse(args)
    
    glob.c.BOTrestore = bool(args.restore)

    glob.c.BOTimreallysurewhatimdoing = int(args.imreallysurewhatimdoing)
    
    # verify arguments
    load_config_verify_or_exit()

def load_config_verify_or_exit():
    global c, s, d
    print('>>>> Verifying configuration')
    
    error_num = 0
    crazy_num = 0
    
    error_num_tmp, crazy_num_tmp = proxy_server__load_config_verify()
    error_num += error_num_tmp
    crazy_num += crazy_num_tmp
    
    error_num_tmp, crazy_num_tmp = pricing_storage__load_config_verify()
    error_num += error_num_tmp
    crazy_num += crazy_num_tmp
    
    if crazy_num != glob.c.BOTimreallysurewhatimdoing or error_num != 0:
        if error_num != 0:
            print("**** ERROR > errors in configuration detected > {}".format(error_num))
        if crazy_num != 0:
            print("**** WARNING > crazy config values detected, but not expected> {}/{}".format(crazy_num, glob.c.BOTimreallysurewhatimdoing))
        if crazy_num < glob.c.BOTimreallysurewhatimdoing:
            print("**** WARNING > crazy config values not detected, but expected > {}/{}".format(crazy_num, glob.c.BOTimreallysurewhatimdoing))
            
        print('>>>> Verifying configuration failed.'
        'Please read help and use <imreallysurewhatimdoing> argument correctly, it allows you to specify number of crazy/meaningless/special configuration values, which are expected, to confirm you are sure what you are doing.')
        sys.exit(1)
    else:
        print('>>>> Verifying configuration success')

# check if pricing works or exit
def pricing_check_or_exit():
    print('>>>> Internal test >> Checking pricing information for <{0}> <{1}>'.format("USDT", "LTC"))
    
    # try to get main pricing
    price_maker = pricing_storage__try_get_price("USDT", "LTC", "cg", 2, 30)
    if price_maker == 0:
        print('#### Internal test >> failed >> pricing not available')
        sys.exit(1)
    
    print('>>>> Internal test >> Get pricing information for <{0}> <{1}> <{2}> >> success'.format("USDT", "LTC", price_maker))

def proxy_server__init_preconfig():
    glob.d.proxy_server__server = None
    glob.c.proxy_server__default_addr = "127.0.0.1"
    glob.c.proxy_server__default_port = 22333
    glob.c.proxy_server__addr = ""
    glob.c.proxy_server__port = 0
    
def proxy_server__load_config_define(parser, argparse):
    parser.add_argument('--proxy_server_addr', type=str, help='proxy server address to listen on (default="'+glob.c.proxy_server__default_addr+'")', default=glob.c.proxy_server__default_addr)
    
    parser.add_argument('--proxy_server_port', type=int, help='proxy server port to listen on (default="'+str(glob.c.proxy_server__default_port)+'")', default=glob.c.proxy_server__default_port)
    
def proxy_server__load_config_postparse(args):
    
    glob.c.proxy_server__addr = str(args.proxy_server_addr)
    glob.c.proxy_server__port = int(args.proxy_server_port)
    
def proxy_server__load_config_verify():
    
    error_num = 0
    crazy_num = 0
    
    if glob.c.proxy_server__addr == "":
        print('**** ERROR, <proxy_server_addr> value <{0}> is invalid'.format(glob.c.proxy_server__addr))
        error_num += 1
    
    if glob.c.proxy_server__port <= 0:
        print('**** ERROR, <proxy_server_port> value <{0}> is invalid'.format(glob.c.proxy_server__port))
        error_num += 1
    
    return error_num, crazy_num

def proxy_server__rpc_get_price(maker__item_to_sell, taker__payed_by, price_provider = ""):
    
    print('**** get external price >> {}/{}/{}'.format(maker__item_to_sell, taker__payed_by, price_provider))
    return pricing_storage__try_get_price(maker__item_to_sell, taker__payed_by, price_provider)

def proxy_server__init_postconfig():
    
    glob.d.proxy_server__server = SimpleJSONRPCServer((glob.c.proxy_server__addr, glob.c.proxy_server__port))
    glob.d.proxy_server__server.register_function(proxy_server__rpc_get_price)

def proxy_server__serve_forever():
    
    glob.d.proxy_server__server.serve_forever()

# main function
if __name__ == '__main__':
    
    start_welcome_message()
    
    init_preconfig()
    
    load_config()
    
    init_postconfig()
    
    pricing_check_or_exit()
    
    proxy_server__serve_forever()
