#!/usr/bin/python3

# relative pricing boundaries relative to center price set manually or by thirty party asset
# for example if trading $BLOCK with $DOGE:
#   $BLOCK = 1 USD
#   $DOGE = 2 USD
#   so 1 BLOCK == 0.5 DOGE
#   you can set min boundary as 0.25(1/4) and 3 so:
#       bot will stop offering to sell $BLOCK if price go up 3 times up = 1*3 = $3 USD converted into $DOGE as 1.5 $DOGE
#       and bot will stop buying $BLOCK if price go under 1*(0.25) == 1/4 = $0.25 USD converted into $DOGE as 0.125 $DOGE
#       but above depends if price tracking is on of off and if $DOGE price changes or not
#
#   Please see all configuration definition parameters function for details
#
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

# preconfiguration  initialization
def rboundary__init_preconfig__():
    
    # relative boundary asset
    c.rboundary__asset = ""
    # relative boundary maximum
    c.rboundary__max = 0
    # relative boundary minimum
    c.rboundary__min = 0
    # enable disable maximum boundary tracking if other asset is specified
    c.rboundary__max_track_asset = False
    # enable disable minimum boundary tracking if other asset is specified
    c.rboundary__min_track_asset = False
    # reverse 1/x price, usable only when manually set initial center price
    c.rboundary__price_reverse = False
    # enable disable to cancel orders when reaching maximum boundary
    c.rboundary__max_cancel = False
    # enable disable to exit bot when reaching maximum boundary
    c.rboundary__max_exit = False
    # enable disable to cancel orders when reaching minimum boundary
    c.rboundary__max_cancel = False
    # enable disable to exit bot when reaching minimum boundary
    c.rboundary__max_exit = False
    
    # initial price recorded at bot start and last recorded price, it could be:
    # not reversed 1 - price(asset/taker, taker) so number or 1
    # reversed 2 - price(asset/taker, maker) or number
    
    # maker to taker
    d.rboundary__price_initial = 0
    # maker to specific asset
    c.rboundary__price_asset_initial = 0
    d.rboundary__price_asset_initial = 0
    # initial specific asset to taker
    d.rboundary__price_current = 0
    
    d.rboundary__maker = None
    d.rboundary__taker = None
    d.rboundary__get_price_fn = None
    
    d.rboundary__id_price_initial = None
    d.rboundary__id_price_current = None

rboundary__init_preconfig__()

# define argument parameter
def rboundary__load_config_define(parser, argparse):
    
    parser.add_argument('--rboundary_asset', type=str, help=
    'set relative boundary values in specific asset'
    'ie.: Static boundary with maker/taker BLOCK/BTC and boundary_asset is USDT, so possible boundary min 1.5 and max 3 USD (default= --taker)'
    , default="")
    
    parser.add_argument('--rboundary_price_initial', type=float, help='manually set initial center price. If asset is not specified, the price is set as taker (default=0 automatic)', default=0)
    
    parser.add_argument('--rboundary_max', type=float, help='maximum acceptable price of maker(sold one) where bot will stop selling(default=0 disabled)', default=0)
    parser.add_argument('--rboundary_min', type=float, help='minimum acceptable price of maker(sold one) where bot will stop selling(default=0 disabled)', default=0)
    
    parser.add_argument('--rboundary_max_track_asset', type=glob.t.argparse_bool, nargs='?', const=True, help='Track boundary asset price updates. This means, ie if trading BLOCK/BTC on USD also track USD/BTC price and update boundaries by it (default=False disabled)', default=False)
    parser.add_argument('--rboundary_min_track_asset', type=glob.t.argparse_bool, nargs='?', const=True, help='Track boundary asset price updates. This means, ie if trading BLOCK/BTC on USD also track USD/BTC price and update boundaries by it (default=False disabled)', default=False)
    
    parser.add_argument('--rboundary_price_reverse', type=glob.t.argparse_bool, nargs='?', const=True, help='reversed set pricing as 1/X, ie BLOCK/BTC vs BTC/BLOCK pricing can set like 0.000145 on both bot trading sides, instead of 0.000145 vs 6896.55.'
    'this feature works with relative boundary asset as well'
    ' (default=False Disabled)', default=False)
    
    parser.add_argument('--rboundary_max_cancel', type=glob.t.argparse_bool, nargs='?', const=True, help='cancel orders at max boundary hit, (default=True enabled)', default=True)
    parser.add_argument('--rboundary_max_exit', type=glob.t.argparse_bool, nargs='?', const=True, help='exit bot at max boundary hit, (default=True enabled)', default=True)
    parser.add_argument('--rboundary_min_cancel', type=glob.t.argparse_bool, nargs='?', const=True, help='cancel orders at min boundary hit, (default=True enabled)', default=True)
    parser.add_argument('--rboundary_min_exit', type=glob.t.argparse_bool, nargs='?', const=True, help='exit bot at min boundary hit, (default=False disabled)', default=False)

# parse configuration value
def rboundary__load_config_postparse(args):
    
    c.rboundary__asset = args.rboundary_asset
    
    c.rboundary__price_asset_initial = float(args.rboundary_price_initial)
    
    c.rboundary__max = float(args.rboundary_max)
    c.rboundary__min = float(args.rboundary_min)
    
    c.rboundary__max_track_asset = bool(args.rboundary_max_track_asset)
    c.rboundary__min_track_asset = bool(args.rboundary_min_track_asset)
    
    c.rboundary__price_reverse = bool(args.rboundary_price_reverse)
    
    c.rboundary__max_cancel = bool(args.rboundary_max_cancel)
    c.rboundary__max_exit = bool(args.rboundary_max_exit)
    c.rboundary__min_cancel = bool(args.rboundary_min_cancel)
    c.rboundary__min_exit = bool(args.rboundary_min_exit)
    
# verify argument value after load
def rboundary__load_config_verify():
    
    error_num = 0
    crazy_num = 0
    
    if d.rboundary__price_initial < 0:
        print('**** ERROR, <rboundary_price_initial> value <{0}> is invalid. Must be real exiting asset ticker'.format(d.rboundary__price_initial))
        error_num += 1
    
    if c.rboundary__max < 0:
        print('**** ERROR, <rboundary_max> value <{0}> is invalid. Maximum price boundary must be positive number'.format(c.rboundary__max))
        error_num += 1
    elif c.rboundary__max > 0 and c.rboundary__max < 1:
        print('**** WARNING, <rboundary_max> value <{0}> seems invalid. Maximum price boundary supposed to be number more than 1'.format(c.rboundary__max))
        crazy_num += 1
        
    if c.rboundary__min < 0:
        print('**** ERROR, <rboundary_min> value <{0}> is invalid. Minimum price boundary must be positive number'.format(c.rboundary__min))
        error_num += 1
    elif c.rboundary__min > 0 and c.rboundary__min > 1:
        print('**** WARNING, <rboundary__in> value <{0}> seems invalid. Minimum price boundary supposed to be number less or equal 1'.format(c.rboundary__max))
        crazy_num += 1
        
    if c.rboundary__max < c.rboundary__min:
        print('**** ERROR, <rboundary__max> value <{0}> can not be less than <rboundary__min> value <{1}>.'.format(c.rboundary__max, c.rboundary__min))
        error_num += 1
    
    return error_num, crazy_num

def rboundary__get_price_cb__(maker, taker):
    print('**** ERROR >>> dexbot.features.rboundary.rboundary__get_price_cb__() function is just empty default callback, please replace with pricing_storage__try_get_price')
    return 0

# initial get pricing for relative boundaries
def rboundary__pricing_init(maker, taker, action, get_price_fn = rboundary__get_price_cb__):
    
    if c.rboundary__asset == "":
        # asset must be by default always taker because there exist no asset tracking between just two assets, so price updates will be internally always 1
        c.rboundary__asset = taker
    
    d.rboundary__maker = maker
    d.rboundary__taker = taker
    d.rboundary__get_price_fn = get_price_fn
    
    d.rboundary__id_price_initial = 'feature__rboundary__price_initial' + c.rboundary__asset
    d.rboundary__id_price_asset_initial = 'feature__rboundary__price_asset_initial' + c.rboundary__asset
    d.rboundary__id_price_current = 'feature__rboundary__price_current' + c.rboundary__asset
    
    # try to restore pricing from tmp cfg if requested
    if action == 'restore':
        print('>> INFO >> rboundary >> pricing initialization >> trying to restore configuration from tmp cfg')
        price_initial = feature__tmp_cfg__get_value(d.rboundary__id_price_initial)
        price_asset_initial = feature__tmp_cfg__get_value(d.rboundary__id_price_asset_initial)
        price_current = feature__tmp_cfg__get_value(d.rboundary__id_price_current)
        # if pricing been restored, then set values but run pricing update because if track is activated
        if price_initial != None and price_asset_initial != None and price_current != None:
            d.rboundary__price_initial = price_initial
            d.rboundary__price_asset_initial = price_asset_initial
            d.rboundary__price_current = price_current
            rboundary__pricing_update()
            print('>> INFO >> rboundary >> pricing initialization >> restore from tmp cfg >> success')
        # if pricing restore failed, then run normal pricing init
        else:
            print('>> INFO >> rboundary >> pricing initialization >> restore from tmp cfg >> failed')
    
    # if pricing restore not been called or failed, do normal initialization
    if d.rboundary__price_initial == 0:
        print('>> INFO >> rboundary >> pricing initialization >> normal init')
        
        # static initial price is not set
        if c.rboundary__price_asset_initial == 0:
            d.rboundary__price_asset_initial = d.rboundary__get_price_fn(d.rboundary__maker, c.rboundary__asset)
            if d.rboundary__price_asset_initial != 0:
                # if asset initial price load success then finally update pricing and set initial price
                d.rboundary__price_initial = rboundary__pricing_update()
                if d.rboundary__price_initial != 0:
                    feature__tmp_cfg__set_value(d.rboundary__id_price_asset_initial, d.rboundary__price_asset_initial, False)
                    feature__tmp_cfg__set_value(d.rboundary__id_price_initial, d.rboundary__price_initial, True)
                    print("*** INFO >> rboundary >> pricing init >> remote, not reversed: <{}/{}/{}>: asset-initial/initial/current {}/{}/{} >> success".format(d.rboundary__maker, c.rboundary__asset, d.rboundary__taker, d.rboundary__price_asset_initial, d.rboundary__price_initial, d.rboundary__price_current))
                else:
                    print("*** ERR >> rboundary >> pricing init >> remote, not reversed: <{}/{}/{}>: asset-initial/initial/current {}/{}/{} >> failed".format(d.rboundary__maker, c.rboundary__asset, d.rboundary__taker, d.rboundary__price_asset_initial, d.rboundary__price_initial, d.rboundary__price_current))
            else:
                print("*** ERR >> rboundary >> pricing init >> remote, not reversed: <{}/{}/{}>: asset-initial/initial/current {}/{}/{} >> failed".format(d.rboundary__maker, c.rboundary__asset, d.rboundary__taker, d.rboundary__price_asset_initial, d.rboundary__price_initial, d.rboundary__price_current))
                
        # static initial price is set as not reversed
        elif c.rboundary__price_reverse is False:
            # if asset initial price load success then finally update pricing and set initial price
            d.rboundary__price_asset_initial = c.rboundary__price_asset_initial
            d.rboundary__price_initial = rboundary__pricing_update()
            if d.rboundary__price_initial != 0:
                feature__tmp_cfg__set_value(d.rboundary__id_price_asset_initial, d.rboundary__price_asset_initial, False)
                feature__tmp_cfg__set_value(d.rboundary__id_price_initial, d.rboundary__price_initial, True)
                print("*** INFO >> rboundary >> pricing init >> manual, not reversed: <{}/{}/{}>: asset-initial/initial/current {}/{}/{} >> success".format(d.rboundary__maker, c.rboundary__asset, d.rboundary__taker, d.rboundary__price_asset_initial, d.rboundary__price_initial, d.rboundary__price_current))
            else:
                print("*** ERR >> rboundary >> pricing init >> manual, not reversed: <{}/{}/{}>: asset-initial/initial/current {}/{}/{} >> failed".format(d.rboundary__maker, c.rboundary__asset, d.rboundary__taker, d.rboundary__price_asset_initial, d.rboundary__price_initial, d.rboundary__price_current))
        
        # static initial price is set as reversed
        else:
            # we get default final price first
            d.rboundary__price_asset_initial = d.rboundary__get_price_fn(d.rboundary__maker, d.rboundary__taker)
            # and we convert back taker to asset by its manual initial price
            d.rboundary__price_asset_initial = d.rboundary__price_asset_initial * c.rboundary__price_asset_initial
            # if remote price load success
            if d.rboundary__price_asset_initial != 0:
                # if asset initial price load success then finally update pricing and set initial price
                d.rboundary__price_initial = rboundary__pricing_update()
                if d.rboundary__price_initial != 0:
                    feature__tmp_cfg__set_value(d.rboundary__id_price_asset_initial, d.rboundary__price_asset_initial, False)
                    feature__tmp_cfg__set_value(d.rboundary__id_price_initial, d.rboundary__price_initial, True)
                    print("*** INFO >> rboundary >> pricing init >> manual, reversed: <{}/{}/{}>: asset-initial/initial/current {}/{}/{} >> success".format(d.rboundary__maker, c.rboundary__asset, d.rboundary__taker, d.rboundary__price_asset_initial, d.rboundary__price_initial, d.rboundary__price_current))
                else:
                    print("*** ERR >> rboundary >> pricing init >> manual, reversed: <{}/{}/{}>: asset-initial/initial/current {}/{}/{} >> failed".format(d.rboundary__maker, c.rboundary__asset, d.rboundary__taker, d.rboundary__price_asset_initial, d.rboundary__price_initial, d.rboundary__price_current))
            else:
                print("*** ERR >> rboundary >> pricing init >> manual, reversed: <{}/{}/{}>: asset-initial/initial/current {}/{}/{} >> failed".format(d.rboundary__maker, c.rboundary__asset, d.rboundary__taker, d.rboundary__price_asset_initial, d.rboundary__price_initial, d.rboundary__price_current))
                
    return d.rboundary__price_initial
    
    
# relative boundaries can be specified as relative to maker taker market so price must be checked separately
def rboundary__pricing_update():
    
    tmp_rboundary__price_current = 0
    
    # current price is loaded if is not already set or live tracking of asset price is activated
    if c.rboundary__max_track_asset is True or c.rboundary__min_track_asset is True or d.rboundary__price_current == 0:
        if d.rboundary__price_asset_initial != 0:
            tmp_rboundary__price_current = d.rboundary__get_price_fn(c.rboundary__asset, d.rboundary__taker)
            if tmp_rboundary__price_current != 0:
                tmp_rboundary__price_current = tmp_rboundary__price_current * d.rboundary__price_asset_initial
                d.rboundary__price_current = tmp_rboundary__price_current
                feature__tmp_cfg__set_value(d.rboundary__id_price_current, d.rboundary__price_current, False)
                print(">>>> INFO >> rboundary >> pricing update >> <{}/{}/{}>: <{}/{}> >> success".format(d.rboundary__maker, c.rboundary__asset, d.rboundary__taker, d.rboundary__price_asset_initial, tmp_rboundary__price_current))
            else:
                print("**** ERROR >> rboundary >> pricing update >> <{}/{}/{}>: <{}/{}> >> failed".format(d.rboundary__maker, c.rboundary__asset, d.rboundary__taker, d.rboundary__price_asset_initial, tmp_rboundary__price_current))
        else:
            print("*** ERR >> rboundary >> pricing update >> <{}/{}/{}>: asset initial <{}> >> not loaded >> failed".format(d.rboundary__maker, c.rboundary__asset, d.rboundary__taker, d.rboundary__price_asset_initial))
    else:
        tmp_rboundary__price_current = d.rboundary__price_current
    
    return tmp_rboundary__price_current

#
def rboundary__get_max__():
    
    maximum = float(0)
    
    # if max boundary is activated
    if c.rboundary__max != 0:
        # if asset track is disabled
        if c.rboundary__max_track_asset is False:
            maximum = d.rboundary__price_initial * c.rboundary__max
            print(">>>> INFO >> rboundary >> get maximum >> track no, initial * max = final {} * {} = {}".format(d.rboundary__price_initial, c.rboundary__max, maximum))
        else:
            maximum = d.rboundary__price_current * c.rboundary__max
            print(">>>> INFO >> rboundary >> get maximum >> track yes, current * max = final {} * {} = {}".format(d.rboundary__price_current, c.rboundary__max, maximum))
        
    return maximum

#
def rboundary__get_min__():
    
    minimum = float(0)
    
    if c.rboundary__min != 0:
        # if asset track is disabled
        if c.rboundary__min_track_asset is False:
            minimum = d.rboundary__price_initial * c.rboundary__min
            print(">>>> INFO >> rboundary >> get minimim >> track no, initial * min = final {} * {} = {}".format(d.rboundary__price_initial, c.rboundary__min, minimum))
        else:
            minimum = d.rboundary__price_current * c.rboundary__min
            print(">>>> INFO >> rboundary >> get minimim >> track yes, current * min = final {} * {} = {}".format(d.rboundary__price_current, c.rboundary__min, minimum))
            
    return minimum

# function to check if price is not out of maximum relative boundary 
def rboundary__check_max(price):
    
    # check if relative max rboundary is configured
    if c.rboundary__max != 0:
        # wait if out of price relative rboundary happen
        maximum = rboundary__get_max__()
        if maximum < price:
            print('>>>> INFO >> rboundary >> Maximum cfg <{}:{}> for <{}/{}> price {} hit maximum at {}'.format(c.rboundary__asset, c.rboundary__max, d.rboundary__maker, d.rboundary__taker, price, maximum))
            return True, c.rboundary__max_exit, c.rboundary__max_cancel, maximum
    
    #      hit    exit   cancel price 
    return False, False, False, price

# function to check if price is not out of minimum relative boundary 
def rboundary__check_min(price):
    
    # check if relative min rboundary is configured
    if c.rboundary__min != 0:
        # wait if out of price relative rboundary happen
        minimum = rboundary__get_min__()
        if minimum > price:
            print('>>>> INFO >> rboundary >> Minimum cfg <{}:{}> for <{}/{}> price {} hit minimum at {}'.format(c.rboundary__asset, c.rboundary__min, d.rboundary__maker, d.rboundary__taker, price, minimum))
            return True, c.rboundary__min_exit, c.rboundary__min_cancel, minimum
    
    #      hit    exit   cancel price 
    return False, False, False, price

# check if max or min boundary happened
def rboundary__check(price):
    
    # check if hit max boundary happened
    ret_hit, ret_exit, ret_cancel, ret_price = rboundary__check_max(price)
    
    # if max boundary not happened, try also check min boundary
    if ret_hit is False:
        ret_hit, ret_exit, ret_cancel, ret_price = rboundary__check_min(price)
    
    print(">>>> INFO >> rboundary >> check boundary hit >> price > final price {} > {} ".format(price, ret_price))
    
    return ret_hit, ret_exit, ret_cancel, ret_price
