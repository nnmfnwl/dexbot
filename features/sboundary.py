#!/usr/bin/python3

# static pricing boundaries set in taker or other specific asset
# for example if:
#   $BLOCK = 1 USD
#   $DOGE = 2 USD
#   so 1 BLOCK == 0.5 DOGE
#   so you can set max boundary as 1 DOGE or as 2 USD, so:
#       bot will stop offering to sell $BLOCK if price go over $2 USD converted into $DOGE as 1 $DOGE
#           but above depends if price tracking is on of off and if $DOGE price changes or not
#       
#       If price max track asset is enabled and BLOCK stays at price 1, but DOGE goes up to price 4, the bot with max set at 2 USD which was initially 1 DOGE,
#       will recompute max into 2 USD currently to 0.5 DOGE and stop selling BLOCK coins more soon.
#       But if DOGE goes down to price 1 USD, the bot with max set to 2 USD which was initially 1 DOGE,
#       will recompute max into 2 USD currently to 2 DOGE and stop selling BLOCK coins later.
#       
#       Same if price min track is enabled and BLOCK stays at price 1, but doge goes to to price 4, the bot with min set at 0.5 USD which was initially 0.25 DOGE,
#       will recompute max to 0.5 USD currently to 0.125 DOGE and stop selling BLOCK coins later.


#   Please see all configuration definition parameters function for details

# static and relative boundary libraries should not be merged in one library, because
#   there are many cases where user would like to configure both type of boundaries with different pricing settings.
#   Fo example:
#       User want to set relative boundary at +- 50% on top of static center price
#       and at same time user configures static boundary specified as relative USDT asset with price tracking.

import time

import features.glob as glob
c = glob.c
s = glob.s
d = glob.d

from features.tmp_cfg import *

# pre-configuration  initialization
def sboundary__init_preconfig__():
    
    # static boundary asset
    c.sboundary__asset = ""
    # static boundary maximum
    c.sboundary__max = 0
    # static boundary minimum
    c.sboundary__min = 0
    # enable disable maximum boundary tracking of asset
    c.sboundary__max_track_asset = False
    # enable disable minimum boundary tracking of asset
    c.sboundary__min_track_asset = False
    # reverse 1/x price, usable for more easy pricing setting ie
    # BLOCK to BTC, set price of BLOCK as $0.01 USDT so boundary recomputes just 0.01 USDT to BTC, and reverse trading pair BTC to BLOCK recomputes just 1/(0.01 USDT to BTC)
    c.sboundary__price_reverse = False
    # enable disable to cancel orders when reaching maximum boundary
    c.sboundary__max_cancel = False
    # enable disable to exit bot when reaching maximum boundary
    c.sboundary__max_exit = False
    # enable disable to cancel orders when reaching minimum boundary
    c.sboundary__max_cancel = False
    # enable disable to exit bot when reaching minimum boundary
    c.sboundary__max_exit = False
    
    # initial price recorded at bot start and last recorded price, it could be:
    # not reversed 1 - price(asset/taker, taker) so number or 1
    # reversed 2 - price(asset/taker, maker) or number
    d.sboundary__price_initial = 0
    d.sboundary__price_current = 0
    
    d.sboundary__maker = None
    d.sboundary__taker = None
    d.sboundary__get_price_fn = None
    
    d.sboundary__id_price_initial = None
    d.sboundary__id_price_current = None

sboundary__init_preconfig__()

# define argument parameter
def sboundary__load_config_define(parser, argparse):
    
    parser.add_argument('--sboundary_asset', type=str, help=
    'set static boundary values in specific asset'
    'ie.: Static boundary with maker/taker BLOCK/BTC and boundary_asset is USDT, so possible boundary min 1.5 and max 3 USD (default= --taker)'
    , default="")
    
    parser.add_argument('--sboundary_max', type=float, help='maximum acceptable price of maker(sold one) where bot will stop selling(default=0 disabled)', default=0)
    parser.add_argument('--sboundary_min', type=float, help='minimum acceptable price of maker(sold one) where bot will stop selling(default=0 disabled)', default=0)
    
    parser.add_argument('--sboundary_max_track_asset', type=glob.t.argparse_bool, nargs='?', const=True, help='Track boundary asset price updates. This means, ie if trading BLOCK/BTC on USD also track USD/BTC price and update boundaries by it (default=False disabled)', default=False)
    parser.add_argument('--sboundary_min_track_asset', type=glob.t.argparse_bool, nargs='?', const=True, help='Track boundary asset price updates. This means, ie if trading BLOCK/BTC on USD also track USD/BTC price and update boundaries by it (default=False disabled)', default=False)
    
    parser.add_argument('--sboundary_price_reverse', type=glob.t.argparse_bool, nargs='?', const=True, help='reversed set pricing as 1/X, ie BLOCK/BTC vs BTC/BLOCK pricing can set like 0.000145 on both bot trading sides, instead of 0.000145 vs 6896.55.'
    'this feature works with sboundary asset as well'
    ' (default=False Disabled)', default=False)
    
    parser.add_argument('--sboundary_max_cancel', type=glob.t.argparse_bool, nargs='?', const=True, help='cancel orders at max boundary hit, (default=True enabled)', default=True)
    parser.add_argument('--sboundary_max_exit', type=glob.t.argparse_bool, nargs='?', const=True, help='exit bot at max boundary hit, (default=True enabled)', default=True)
    parser.add_argument('--sboundary_min_cancel', type=glob.t.argparse_bool, nargs='?', const=True, help='cancel orders at min boundary hit, (default=True enabled)', default=True)
    parser.add_argument('--sboundary_min_exit', type=glob.t.argparse_bool, nargs='?', const=True, help='exit bot at min boundary hit, (default=False disabled)', default=False)

# parse configuration value
def sboundary__load_config_postparse(args):
    
    c.sboundary__asset = args.sboundary_asset
    
    c.sboundary__max = float(args.sboundary_max)
    c.sboundary__min = float(args.sboundary_min)
    
    c.sboundary__max_track_asset = bool(args.sboundary_max_track_asset)
    c.sboundary__min_track_asset = bool(args.sboundary_min_track_asset)
    
    c.sboundary__price_reverse = bool(args.sboundary_price_reverse)
    
    c.sboundary__max_cancel = bool(args.sboundary_max_cancel)
    c.sboundary__max_exit = bool(args.sboundary_max_exit)
    c.sboundary__min_cancel = bool(args.sboundary_min_cancel)
    c.sboundary__min_exit = bool(args.sboundary_min_exit)
    
# verify argument value after load
def sboundary__load_config_verify():
    
    error_num = 0
    crazy_num = 0
    
    if c.sboundary__max != 0:
        if c.sboundary__max < 0:
            print('**** ERROR, <sboundary__max> value <{0}> is invalid. Maximum price boundary must be positive number'.format(c.sboundary__max))
            error_num += 1
        
    if c.sboundary__min != 0:
        if c.sboundary__min < 0:
            print('**** ERROR, <sboundary__min> value <{0}> is invalid. Minimum price boundary must be positive number'.format(c.sboundary__min))
            error_num += 1
        
    if c.sboundary__max < c.sboundary__min:
        print('**** ERROR, <sboundary__max> value <{0}> can not be less than <sboundary__min> value <{1}>.'.format(c.sboundary__max, c.sboundary__min))
        error_num += 1
    
    return error_num, crazy_num

def sboundary__get_price_cb__(maker, taker):
    print('**** ERROR >>> dexbot.features.sboundary.sboundary__get_price_cb__() function is just empty default callback, please replace with pricing_storage__try_get_price')
    return 0

# initial get pricing for relative boundaries
def sboundary__pricing_init(maker, taker, action, get_price_fn = sboundary__get_price_cb__):
    
    if c.sboundary__asset == "":
        c.sboundary__asset = taker
    
    d.sboundary__maker = maker
    d.sboundary__taker = taker
    d.sboundary__get_price_fn = get_price_fn
    
    d.sboundary__id_price_initial = 'feature__sboundary__price_initial' + c.sboundary__asset
    d.sboundary__id_price_current = 'feature__sboundary__price_current' + c.sboundary__asset
    
    print('>> INFO >> sboundary >> pricing init >> started')
    
    # try to restore pricing from tmp cfg if requested
    if action == 'restore':
        print('>> INFO >> sboundary >> pricing init >> trying to restore configuration from tmp cfg')
        price_initial = feature__tmp_cfg__get_value(d.sboundary__id_price_initial)
        price_current = feature__tmp_cfg__get_value(d.sboundary__id_price_current)
        # if pricing been restored, then set values but run pricing update because if track is activated
        if price_initial != None and price_current != None:
            d.sboundary__price_initial = price_initial
            d.sboundary__price_current = price_current
            sboundary__pricing_update()
            print('>> INFO >> sboundary >> pricing init >> restore from tmp cfg >> price initial/current {}/{} >> success'.format(d.sboundary__price_initial, d.sboundary__price_current))
        # if pricing restore failed, then run normal pricing init
        else:
            print('>> WARN >> sboundary >> pricing init >> restore from tmp cfg >> price initial/current {}/{} >> failed'.format(price_initial, price_current))
            
    # if pricing restore not been called or failed, do normal initialization
    if d.sboundary__price_initial == 0:
        if c.sboundary__price_reverse is False:
            d.sboundary__price_initial = sboundary__pricing_update()
            if d.sboundary__price_initial != 0:
                feature__tmp_cfg__set_value(d.sboundary__id_price_initial, d.sboundary__price_initial, True)
                print('>> INFO >> sboundary >> pricing init >> not restore >> not reversed >> maker/asset/taker {}/{}/{} price initial/current {}/{} >> success'.format(maker, c.sboundary__asset, taker, d.sboundary__price_initial, d.sboundary__price_current))
            else:
                print('>> ERROR >> sboundary >> pricing init >> not restore >> not reversed >> maker/asset/taker {}/{}/{} price initial/current {}/{} >> failed'.format(maker, c.sboundary__asset, taker, d.sboundary__price_initial, d.sboundary__price_current))
        else:
            # code of reverse pricing magic ))
            tmp_price = d.sboundary__get_price_fn(d.sboundary__maker, d.sboundary__taker)
            if tmp_price != 0:
                tmp_min = tmp_price * c.sboundary__min
                tmp_max = tmp_price * c.sboundary__max
                d.sboundary__price_initial = sboundary__pricing_update()
                if d.sboundary__price_initial != 0:
                    if d.sboundary__taker == c.sboundary__asset:
                        tmp_min = tmp_min * tmp_price
                        tmp_max = tmp_max * tmp_price
                    c.sboundary__min = tmp_min
                    c.sboundary__max = tmp_max
                    feature__tmp_cfg__set_value(d.sboundary__id_price_initial, d.sboundary__price_initial, True)
                    print('>> INFO >> sboundary >> pricing init >> not restore >> reversed >> maker/asset/taker {}/{}/{} price initial/current {}/{} >> success'.format(maker, c.sboundary__asset, taker, d.sboundary__price_initial, d.sboundary__price_current))
                else:
                    print('>> ERROR >> sboundary >> pricing init >> not restore >> reversed >> maker/asset/taker {}/{}/{} price initial/current {}/{} >> failed'.format(maker, c.sboundary__asset, taker, d.sboundary__price_initial, d.sboundary__price_current))
            else:
                print('>> ERROR >> sboundary >> pricing init >> not restore >> reversed >> maker/asset/taker {}/{}/{} price initial/current {}/{} >> failed to reverse pricing'.format(maker, c.sboundary__asset, taker, d.sboundary__price_initial, d.sboundary__price_current))
                
    return d.sboundary__price_initial
    
# relative boundaries can be specified as relative to maker taker market so price must be checked separately
def sboundary__pricing_update():
    
    tmp_sboundary__price_current = 0
    
    # current price is loaded if is not already set or live tracking of asset price is activated
    if c.sboundary__max_track_asset is True or c.sboundary__min_track_asset is True or d.sboundary__price_current == 0:
        tmp_sboundary__price_current = d.sboundary__get_price_fn(c.sboundary__asset, d.sboundary__taker)
        if tmp_sboundary__price_current != 0:
            d.sboundary__price_current = tmp_sboundary__price_current
            feature__tmp_cfg__set_value(d.sboundary__id_price_current, d.sboundary__price_current, False)
            print(">>>> INFO >> sboundary >> pricing update >> <{}/{}>: <{}> >> success".format(c.sboundary__asset, d.sboundary__taker, tmp_sboundary__price_current))
        else:
            print("**** ERROR >> sboundary >> pricing update >> <{}/{}>: <{}> >> failed".format(c.sboundary__asset, d.sboundary__taker, tmp_sboundary__price_current))
    else:
        tmp_sboundary__price_current = d.sboundary__price_current
        
    return tmp_sboundary__price_current

# compute and return actual maximum static boundary.
# the boundary itself could be configured as static but also little dynamic depending on configuration values
def sboundary__get_max__():
    
    maximum = float(0)
    
    # if max boundary is activated
    if c.sboundary__max != 0:
        # if asset track is disabled
        if c.sboundary__max_track_asset is False:
            maximum = d.sboundary__price_initial * c.sboundary__max
            print(">>>> INFO >> sboundary >> get maximum >> track no >> maker/asset/taker {}/{}/{} >> price initial(price of asset) * max(set in asset) = final >> {} * {} = {}".format(d.sboundary__maker, c.sboundary__asset, d.sboundary__taker, d.sboundary__price_initial, c.sboundary__max, maximum))
        else:
            maximum = d.sboundary__price_current * c.sboundary__max
            print(">>>> INFO >> sboundary >> get maximum >> track yes >> maker/asset/taker {}/{}/{} >> price initial(price of asset) * max(set in asset) = final >> {} * {} = {}".format(d.sboundary__maker, c.sboundary__asset, d.sboundary__taker, d.sboundary__price_current, c.sboundary__max, maximum))
    
    return maximum

# compute and return actual minimum static boundary
# the boundary itself could be configured as static but also little dynamic depending on configuration parameters
def sboundary__get_min__():
    
    minimum = float(0)
    
    if c.sboundary__min != 0:
        # if asset track is disabled
        if c.sboundary__min_track_asset is False:
            minimum = d.sboundary__price_initial * c.sboundary__min
            print(">>>> INFO >> sboundary >> get minimum >> track no >> maker/asset/taker {}/{}/{} >> price initial(price of asset) * min(set in asset) = final >> {} * {} = {}".format(d.sboundary__maker, c.sboundary__asset, d.sboundary__taker, d.sboundary__price_initial, c.sboundary__min, minimum))
        else:
            minimum = d.sboundary__price_current * c.sboundary__min
            print(">>>> INFO >> sboundary >> get minimum >> track yes >> maker/asset/taker {}/{}/{} >> price initial(price of asset) * min(set in asset) = final >> {} * {} = {}".format(d.sboundary__maker, c.sboundary__asset, d.sboundary__taker, d.sboundary__price_current, c.sboundary__min, minimum))
            
    return minimum

# function to check if price is not out of maximum static boundary 
def sboundary__check_max(price):
    
    final_price = price
    
    # check if static max sboundary is configured
    if c.sboundary__max != 0:
        # wait if out of price static sboundary happen
        maximum = sboundary__get_max__()
        if maximum < price:
            print('>>>> INFO >> sboundary >> Maximum cfg <{}:{}> for <{}/{}> price {} hit maximum {}'.format(c.sboundary__asset, c.sboundary__max, d.sboundary__maker, d.sboundary__taker, price, maximum))
            return True, c.sboundary__max_exit, c.sboundary__max_cancel, maximum
    
    return False, False, False, final_price

# function to check if price is not out of minimum static boundary
def sboundary__check_min(price):
    
    final_price = price
    
    # check if relative min sboundary is configured
    if c.sboundary__min != 0:
        # wait if out of price relative sboundary happen
        minimum = sboundary__get_min__()
        if minimum > price:
            print('>>>> INFO >> sboundary >> Minimum cfg <{}:{}> for <{}/{}> price {} hit minimum {}'.format(c.sboundary__asset, c.sboundary__min, d.sboundary__maker, d.sboundary__taker, price, minimum))
            return True, c.sboundary__min_exit, c.sboundary__min_cancel, minimum
    
    return False, False, False, final_price

# check if max or min boundary happened
def sboundary__check(price):
    
    # check if hit max boundary happened
    ret_hit, ret_exit, ret_cancel, ret_price = sboundary__check_max(price)
    
    # if max boundary not happened, try also check min boundary
    if ret_hit is False:
        ret_hit, ret_exit, ret_cancel, ret_price = sboundary__check_min(price)
    
    print(">>>> INFO >> sboundary >> check boundary hit >> price > final price {} > {} ".format(price, ret_price))
    
    return ret_hit, ret_exit, ret_cancel, ret_price
