#!/usr/bin/python3

# fixed fee for proxy server cache also proxy client cache

import time
import pickle

import features.glob as glob
c = glob.c
s = glob.s
d = glob.d
from features.main_cfg import *

# initialize fixed fee component
def fixed_fee__init_preconfig__():
    c.fixed_fee__asset = None
    c.fixed_fee__value = 0
    d.fixed_fee__price = 0
    d.fixed_fee__get_price_fn = None

fixed_fee__init_preconfig__()

# define argument parameter
def fixed_fee__load_config_define():
    
    feature__main_cfg__add_variable('fixed_fee_asset', None, feature__main_cfg__validate_str, None, """Fixed fee set in specific asset (default=--maker)""",None)
    feature__main_cfg__add_variable('fixed_fee_value', 0, feature__main_cfg__validate_float, None, """Fixed fee value, it is added price slide, for example when buying BTC the added +5 USDT is crucial because of expensive tx fees. (Default 0)""", None)
    
# parse configuration value
def fixed_fee__load_config_postparse(args):
    
    c.fixed_fee__value = float(args.fixed_fee_value)
    c.fixed_fee__asset = str(args.fixed_fee_asset)
    
# verify argument value after load
def fixed_fee__load_config_verify():
    
    error_num = 0
    crazy_num = 0
    
    if c.fixed_fee__value < 0:
        print('**** ERROR.fixed fee >> <fixed_fee_value> value <{0}> is invalid'.format(c.fixed_fee__value))
        error_num += 1
        
    # ~ if c.fixed_fee__asset == "":
        # ~ print('**** ERROR, <fixed_fee_asset> value <{0}> is invalid'.format(c.fixed_fee__asset))
        # ~ error_num += 1
        
    return error_num, crazy_num

def fixed_fee__get_price_cb__(maker, taker):
    print('**** ERROR.fixed fee >> dexbot.features.fixed_fee.fixed_fee__get_price_cb__() function is just empty default callback, please replace with pricing_storage__try_get_price')
    return 0

# set update interval in seconds
def fixed_fee__init_postconfig(taker, get_price_fn = fixed_fee__get_price_cb__):
    
    if c.fixed_fee__asset is None or c.fixed_fee__asset == "":
        c.fixed_fee__asset = taker
        
    d.fixed_fee__taker = taker
    d.fixed_fee__get_price_fn = get_price_fn

# get price of fixed fee asset vs taker
def fixed_fee__asset_pricing_update():
    
    temp_price = d.fixed_fee__get_price_fn(c.fixed_fee__asset, d.fixed_fee__taker)
    if temp_price != 0:
        d.fixed_fee__price = temp_price
    
    return temp_price
    
# add fixed fee amount into sell amount
def fixed_fee__add_fee_int_amount(buy_amount):
    add_amount = c.fixed_fee__value * d.fixed_fee__price
    final_amount = buy_amount + add_amount
    print('>>>> INFO.fixed_fee >> adding <{} {} = {} {}> into <{} {}> buy amount, resulted as <{} {}>'.format(c.fixed_fee__value, c.fixed_fee__asset, add_amount, d.fixed_fee__taker, buy_amount, d.fixed_fee__taker, final_amount, d.fixed_fee__taker))
    
    return final_amount 
