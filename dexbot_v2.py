#!/usr/bin/env python3
import time
import random
import argparse
import sys
import logging
from utils import dxbottools
from utils import dxsettings

import features.glob as glob

from features.flush_co import *
from features.pricing_storage import *
from features.pricing_proxy_client import *
from features.tmp_cfg import *

# ~ logging.basicConfig(filename='botdebug.log',
                    # ~ level=logging.INFO,
                    # ~ format='%(asctime)s %(levelname)s - %(message)s',
                    # ~ datefmt='[%Y-%m-%d:%H:%M:%S]')

########################################################################
# for better variables naming, understanding, finding and code management and autocomplete 
# variables has been divided into 3 groups global config as c, global static as s, global dynamic as d
########################################################################

# welcome message
def start_welcome_message():
    global c, s, d
    print('>>>> Starting maker bot')

# initialization of config independent items or items needed for config load
def init_preconfig():
    global c, s, d
    
    print('>>>> Preconfig initialization')
    
    # TODO remove lines an replace global as glob.c,s,d
    c = glob.c
    s = glob.s
    d = glob.d

    global_vars_init_preconfig()
    
    feature__maker_price__init_preconfig()
    
    feature__flush_co__init_preconfig()
    
    feature__balance_save_asset__init_preconfig()
    
    feature__boundary__init_preconfig()
    
    events_wait_reopenfinished_init()
    
    feature__slide_dyn__init_preconfig()
    
    feature__takerbot__init_preconfig()

# initialization of items dependent on config
def init_postconfig():
    global c, s, d
    print('>>>> Postconfig initialization')
    
    global_vars_init_postconfig()
    
    # RPC configuration is part of strategy config,
    # it is not loaded by program arguments rather included.
    # Reason because args are system wide public and these config parameters are 
    # sensitive information
    dxbottools.init_postconfig(c.BOTcf.rpcuser,
                               c.BOTcf.rpcpassword,
                               c.BOTcf.rpchostname,
                               c.BOTcf.rpcport)
    
    # initialize pricing proxy client
    pricing_proxy_client__init_postconfig()
    
    # initialize pricing storage and set proxy client
    pricing_storage__init_postconfig(c.BOTconfigfile + ".tmp.pricing", c.BOTdelaycheckprice, c.BOTuse, 2, 8, pricing_proxy_client__pricing_storage__try_get_price_fn, c.BOTcf.price_redirections)
    
#global variables initialization
def global_vars_init_preconfig():
    global c, s, d
    print('>>>> Global variables initialization')
    d.ordersfinished = 0
    d.ordersfinishedtime = 0
    
    # price of asset vs maker in which are orders sizes set
    d.feature__sell_size_asset__price = 0
    
    d.balance_maker_total = 0
    d.balance_maker_available = 0
    d.balance_maker_reserved = 0
    d.balance_taker_available = 0
    d.balance_taker_total = 0
    d.balance_taker_reserved = 0
    
    status_list__init_preconfig()

# for better understanding how are order statuses managed read:
# https://api.blocknet.co/#status-codes
#
# order with statuses which are considered as open are in flow:
#       ['open', 'accepting', 'hold', 'initialized', 'created', 'commited']
#
# order with status hidden are considered as open but funds are reserved virtually only
# and waiting to be used by takerbot
#       [ 'hidden']
#
# order with statuses which are considered as finished are:
#       ['finished']
#
# order with statuses which are considered by default to reopen are:
#       ['clear', 'expired', 'offline', 'canceled', 'invalid', 'rolled back', 'rollback failed']
#
# order with statuses which are considered by default + option <reopenfinished> enabled to reopen are:
#       ['clear', 'expired', 'offline', 'canceled', 'invalid', 'rolled back', 'rollback failed', 'finished']
def status_list__init_preconfig():
    global c, s, d
    
    # basic statuses
    s.status_list__clear = 'clear'                       # order data cleared
    s.status_list__hidden = 'hidden'                     # not broadcasted order, takerbot order only
    
    s.status_list__creating = 'creating' # first stage, virtually created, xbridge API called, waiting for confirmations that is new or open
    
    s.status_list__new = 'new'                            # New order, not yet broadcasted
    s.status_list__open = 'open'                          # Open order, waiting for taker
    s.status_list__accepting = 'accepting'                # Taker accepting order
    s.status_list__hold = 'hold'                          # Counterparties acknowledge each other
    s.status_list__initialized = 'initialized'            # Counterparties agree on order
    s.status_list__created = 'created'                    # Swap process starting
    s.status_list__commited = 'commited'                  # Swap finalized
    s.status_list__finished = 'finished'                  # Order complete
    s.status_list__expired = 'expired'                    # Order expired
    s.status_list__offline = 'offline'                    # Maker or taker went offline
    s.status_list__canceled = 'canceled'                  # Order was canceled
    s.status_list__invalid = 'invalid'                    # Problem detected with the order
    s.status_list__rolled_back = 'rolled back'            # Trade failed, funds being rolled back
    s.status_list__rollback_failed = 'rollback failed'    # Funds unsuccessfully redeemed in failed trade
    
    # list of virtual order statuses which have reserved balance
    s.status_list__with_reserved_balance = [ s.status_list__hidden, s.status_list__new, s.status_list__open, s.status_list__accepting, s.status_list__hold, s.status_list__initialized, s.status_list__created, s.status_list__commited]
    
    # list of virtual order statuses which to be opened or reopened
    s.status_list__ready_to_reopen_nfinished = [s.status_list__clear, s.status_list__expired, s.status_list__offline, s.status_list__canceled, s.status_list__invalid, s.status_list__rolled_back, s.status_list__rollback_failed]
    
    s.status_list__ready_to_reopen_wfinished = s.status_list__ready_to_reopen_nfinished + [s.status_list__finished]

    # list of virtual order statuses which are in accepted but still in progress
    s.status_list__l_in_progress = [s.status_list__accepting, s.status_list__hold, s.status_list__initialized, s.status_list__created, s.status_list__commited]

def feature__boundary__init_preconfig():
    global c, s, d
    # relative pricing to boundary asset - actual
    d.feature__boundary__price_relative_current = 0
    # relative pricing to boundary asset - at bot initialization
    d.feature__boundary__price_relative_initial = 0
    
    # initial price of maker for taker
    d.feature__boundary__price_maker_initial_center = 0
    # initial price of maker to taker relative to boundary price
    d.feature__boundary__price_maker_initial_center_relative = 0

def feature__maker_price__init_preconfig():
    global c, s, d
    
    # maker price set at bot startup or loaded from cmp.cfg depending on maker_price config
    d.feature__maker_price__value_startup = 0
    # price used by bot, could be same as remote price or price customized by price_redirections
    d.feature__maker_price__value_current_used = 0
    # remote price loaded from markets, even if price redirect is specified, this variable holds value loaded directly from specific market
    # ~ d.feature__maker_price__value_remote = 0
    # bot price configuration
    c.feature__maker_price__cfg_price = 0

def feature__slide_dyn__init_preconfig():
    global c, s, d
    
    d.feature__slide_dyn__value = 0
    
    d.feature__slide_dyn__zero_asset_price = 0
    
    c.feature__slide_dyn__zero_value = None
    
    c.feature__slide_dyn__maker_price_value_startup = None

def feature__takerbot__init_preconfig():
    global c, s, d
    
    s.feature__takerbot__list_of_usable_statuses = [ s.status_list__new, s.status_list__open, s.status_list__hidden]
    d.feature__takerbot__time_start = 0

# reopen after finished number and reopen after finished delay features initialization
def events_wait_reopenfinished_init():
    global c, s, d
    
    s.orders_pending_to_reopen_opened_statuses = [s.status_list__open, s.status_list__accepting, s.status_list__hold, s.status_list__initialized, s.status_list__created, s.status_list__commited]
    
    events_wait_reopenfinished_reinit()

# reopen after finished number and reopen after finished delay features re-initialization
def events_wait_reopenfinished_reinit():
    global c, s, d
    
    d.orders_pending_to_reopen_opened = 0
    d.orders_pending_to_reopen_finished = 0
    d.orders_pending_to_reopen_finished_time = 0

def feature__maker_price__load_config_verify():
    global c, s, d
    error_num = 0
    crazy_num = 0
    
    if c.feature__maker_price__cfg_price != -1 and c.feature__maker_price__cfg_price != -2 and c.feature__maker_price__cfg_price != 0:
        print('**** ERROR, <maker_price> value <{0}> is invalid. Allowed values are: -1, -2 and 0'.format(c.feature__maker_price__cfg_price))
        error_num += 1
    
    return error_num, crazy_num

def feature__slide_dyn__load_config_verify():
    global c, s, d
    error_num = 0
    crazy_num = 0
    
    if c.BOTslide_dyn_zero != -1 and c.BOTslide_dyn_zero != -2:
        # type=relative zero more than 1 or less than 0 does not make sense
        if c.BOTslide_dyn_zero_type == 'relative' and (c.BOTslide_dyn_zero > 1 or c.BOTslide_dyn_zero < 0):
            print('**** ERROR, <slide_dyn_zero> value <{0}> is invalid'.format(c.BOTslide_dyn_zero))
            error_num += 1
        # type=static value less than 0 does not make sense
        if c.BOTslide_dyn_zero_type == 'static' and (c.BOTslide_dyn_zero < 0):
            print('**** ERROR, <slide_dyn_zero> value <{0}> is invalid'.format(c.BOTslide_dyn_zero))
            error_num += 1
    
    # SLIDE DYNAMIC FOR MAKER SELL OPERATIONS
    if c.BOTslide_dyn_sell_ignore < 0:
        print('**** ERROR, <slide_dyn_sell_ignore> value <{0}> is invalid'.format(c.BOTslide_dyn_sell_ignore))
        error_num += 1
    
    if c.BOTslide_dyn_sell_threshold <= 0:
        print('**** ERROR, <BOTslide_dyn_sell_threshold> value <{0}> is invalid'.format(c.BOTslide_dyn_sell_threshold))
        error_num += 1
    
    if c.BOTslide_dyn_type == "relative":
        if c.BOTslide_dyn_sell_ignore > 1:
            print('**** ERROR, relative <slide_dyn_sell_ignore> value <{0}> is invalid'.format(c.BOTslide_dyn_sell_ignore))
            error_num += 1
    
        if c.BOTslide_dyn_sell_threshold > 1:
            print('**** ERROR, relative <BOTslide_dyn_sell_threshold> value <{0}> is invalid'.format(c.BOTslide_dyn_sell_threshold))
            error_num += 1
    
    if c.BOTslide_dyn_sell_step < 0:
        print('**** WARNING, <BOTslide_dyn_sell_step> value <{0}> seems invalid, but yes it can be negative'.format(c.BOTslide_dyn_sell_step))
        print('++++ HINT, If you are really sure about what you are doing, you can ignore this warning by using --imreallysurewhatimdoing argument')
        crazy_num += 1
    
    if c.BOTslide_dyn_sell_step_multiplier < 0:
        print('**** ERROR, <BOTslide_dyn_sell_step_multiplier> value <{0}> is invalid, must be positive'.format(c.BOTslide_dyn_sell_step_multiplier))
        error_num += 1
        
    if c.BOTslide_dyn_sell_step_multiplier < 1:
        print('**** WARNING, <BOTslide_dyn_sell_step_multiplier> value <{0}> seems invalid, but yes it can be less than 1'.format(c.BOTslide_dyn_sell_step_multiplier))
        print('++++ HINT, If you are really sure about what you are doing, you can ignore this warning by using --imreallysurewhatimdoing argument')
        crazy_num += 1
    
    if c.BOTslide_dyn_sell_step > 1 and c.BOTslide_dyn_sell_step < -1:
        print('**** WARNING, <BOTslide_dyn_sell_step> value <{0}> seems invalid, absolute value more than 1 means 100% slide change, it is possble but:'.format(c.BOTslide_dyn_sell_step))
        print('++++ HINT, If you are really sure about what you are doing, you can ignore this warning by using --imreallysurewhatimdoing argument')
        crazy_num += 1
    
    if (c.BOTslide_dyn_sell_max > 0 and c.BOTslide_dyn_sell_step < 0) or (c.BOTslide_dyn_sell_max < 0 and c.BOTslide_dyn_sell_step > 0):
        print('**** ERROR, <BOTslide_dyn_sell_max> value <{0}> is invalid, must be positive or negative number same as <BOTslide_dyn_sell_step>'.format(c.BOTslide_dyn_sell_max))
        error_num += 1
    
    # SLIDE DYNAMIC FOR MAKER BUY OPERATIONS
    if c.BOTslide_dyn_buy_ignore < 0:
        print('**** ERROR, <slide_dyn_buy_ignore> value <{0}> is invalid'.format(c.BOTslide_dyn_buy_ignore))
        error_num += 1
    
    if c.BOTslide_dyn_buy_threshold <= 0:
        print('**** ERROR, <BOTslide_dyn_buy_threshold> value <{0}> is invalid'.format(c.BOTslide_dyn_buy_threshold))
        error_num += 1
    
    if c.BOTslide_dyn_type == "relative":
        if c.BOTslide_dyn_buy_ignore > 1:
            print('**** ERROR, relative <slide_dyn_buy_ignore> value <{0}> is invalid'.format(c.BOTslide_dyn_buy_ignore))
            error_num += 1
    
        if c.BOTslide_dyn_buy_threshold > 1:
            print('**** ERROR, relative <BOTslide_dyn_buy_threshold> value <{0}> is invalid'.format(c.BOTslide_dyn_buy_threshold))
            error_num += 1
    
    if c.BOTslide_dyn_buy_step < 0:
        print('**** WARNING, <BOTslide_dyn_buy_step> value <{0}> seems invalid, but yes it can be negative'.format(c.BOTslide_dyn_buy_step))
        print('++++ HINT, If you are really sure about what you are doing, you can ignore this warning by using --imreallysurewhatimdoing argument')
        crazy_num += 1
    
    if c.BOTslide_dyn_buy_step_multiplier < 0:
        print('**** ERROR, <BOTslide_dyn_buy_step_multiplier> value <{0}> is invalid, must be positive'.format(c.BOTslide_dyn_buy_step_multiplier))
        error_num += 1
        
    if c.BOTslide_dyn_buy_step_multiplier < 1:
        print('**** WARNING, <BOTslide_dyn_buy_step_multiplier> value <{0}> seems invalid, but yes it can be less than 1'.format(c.BOTslide_dyn_buy_step_multiplier))
        print('++++ HINT, If you are really sure about what you are doing, you can ignore this warning by using --imreallysurewhatimdoing argument')
        crazy_num += 1
    
    if c.BOTslide_dyn_buy_step > 1 and c.BOTslide_dyn_buy_step < -1:
        print('**** WARNING, <BOTslide_dyn_buy_step> value <{0}> seems invalid, absolute value more than 1 means 100% slide change, it is possble but:'.format(c.BOTslide_dyn_buy_step))
        print('++++ HINT, If you are really sure about what you are doing, you can ignore this warning by using --imreallysurewhatimdoing argument')
        crazy_num += 1
    
    if (c.BOTslide_dyn_buy_max > 0 and c.BOTslide_dyn_buy_step < 0) or (c.BOTslide_dyn_buy_max < 0 and c.BOTslide_dyn_buy_step > 0):
        print('**** ERROR, <BOTslide_dyn_buy_max> value <{0}> is invalid, must be positive or negative number same as <BOTslide_dyn_buy_step>'.format(c.BOTslide_dyn_buy_max))
        error_num += 1
    
    return error_num, crazy_num

def load_config_verify_or_exit():
    global c, s, d
    print('>>>> Verifying configuration')
    
    error_num = 0
    crazy_num = 0
    
    if c.BOTconfigfile is None:
        print("**** ERROR, --config file is invalid")
        sys.exit(1)
    
    print("**** INFO, --config file <{}>".format(c.BOTconfigfile))
    
    # try to import configuration file cf
    c.BOTcf = __import__(c.BOTconfigfile)
    
    # check configuration file
    if not c.BOTcf.rpchostname:
        print("**** ERROR, config.rpchostname is invalid")
        error_num += 1
    print("**** INFO, config.rpchostname <{}>".format(c.BOTcf.rpchostname))
    
    if not c.BOTcf.rpcport:
        print("**** ERROR, config.rpcport is invalid")
        error_num += 1
    print("**** INFO, config.rpcport <{}>".format(c.BOTcf.rpcport))
    
    if not c.BOTcf.rpcuser:
        print("**** ERROR, config.rpcuser is invalid")
        error_num += 1
    print("**** INFO, config.rpcuser <{}>".format(c.BOTcf.rpcuser))
    
    if not c.BOTcf.rpcpassword:
        print("**** ERROR, config.rpcpassword is invalid")
        error_num += 1
    print("**** INFO, config.rpcpassword <{}>".format("****"))
    
    # arguments: main maker/taker
    if hasattr(c, 'BOTmakeraddress') == False:
        print('**** ERROR, <makeraddress> is not specified')
        error_num += 1
        
    if hasattr(c, 'BOTtakeraddress') == False:
        print('**** ERROR, <takeraddress> is not specified')
        error_num += 1
    
    if c.BOTsell_type <= -1 or c.BOTsell_type >= 1:
        print('**** ERROR, <sell_type> value <{0}> is invalid. Valid range is -1 up to 1 only'.format(c.BOTsell_type))
        error_num += 1
    
    # arguments: basic values
    if c.BOTsellstart <= 0:
        print('**** ERROR, <sellstart> value <{0}> is invalid'.format(c.BOTsellstart))
        error_num += 1
    
    if c.BOTsellend <= 0:
        print('**** ERROR, <sellend> value <{0}> is invalid'.format(c.BOTsellend))
        error_num += 1
    
    if c.BOTsellstartmin != 0:
        if c.BOTsellstartmin < 0:
            print('**** ERROR, <sellstartmin> value <{0}> is invalid. Must be more than 0'.format(c.BOTsellstartmin))
            error_num += 1
        
        if c.BOTsellstartmin >= c.BOTsellstart:
            print('**** ERROR, <sellstartmin> value <{}> is invalid. Must be less than <sellstart> <{}>'.format(c.BOTsellstartmin, c.BOTsellstart))
            error_num += 1
            
    if c.BOTsellendmin != 0:
        if c.BOTsellendmin < 0:
            print('**** ERROR, <sellendmin> value <{}> is invalid. Must be more than 0'.format(c.BOTsellendmin))
            error_num += 1
        
        if c.BOTsellendmin >= c.BOTsellend:
            print('**** ERROR, <sellendmin> value <{}> is invalid. Must be less than <sellend> <{}>'.format(c.BOTsellendmin, c.BOTsellend))
            error_num += 1
    
    # ~ if c.BOTmarking != 0:
        # ~ if c.BOTmarking < 0:
            # ~ print('**** ERROR, <marking> value <{}> is invalid. Must be more than 0'.format(c.BOTmarking))
            # ~ error_num += 1
        
        # ~ if c.BOTmarking >= 0.001:
            # ~ print('**** WARNING, <marking> value <{}> seems invalid. Values more than 0.001 can possibly have very impact on order value'.format(c.BOTmarking))
            # ~ print('++++ HINT, If you are really sure about what you are doing, you can ignore this warning by using --imreallysurewhatimdoing argument')
            # ~ crazy_num += 1
                
    if c.BOTslidestart <= 1:
        print('**** WARNING, <slidestart> value <{0}> seems invalid. Values less than 1 means selling something under price.'.format(c.BOTslidestart))
        print('++++ HINT, If you are really sure about what you are doing, you can ignore this warning by using --imreallysurewhatimdoing argument')
        crazy_num += 1
    
    if c.BOTslidestart > 10:
        print('**** WARNING, <slidestart> value <{0}> seems invalid. <1.01> means +1%, <1.10> means +10%, more than <2> means +100% of actual price'.format(c.BOTslidestart))
        print('++++ HINT, If you are really sure about what you are doing, you can ignore this warning by using --imreallysurewhatimdoing argument')
        crazy_num += 1
    
    if c.BOTslideend <= 1:
        print('**** WARNING, <slideend> value <{0}> seems invalid. Values less than 1 means selling something under price.'.format(c.BOTslideend))
        print('++++ HINT, If you are really sure about what you are doing, you can ignore this warning by using --imreallysurewhatimdoing argument')
        crazy_num += 1
    
    if c.BOTslideend > 10:
        print('**** WARNING, <slideend> value <{0}> seems invalid. <1.01> means +1%, <1.10> means +10%, more than <2> means +100% of actual price'.format(c.BOTslideend))
        print('++++ HINT, If you are really sure about what you are doing, you can ignore this warning by using --imreallysurewhatimdoing argument')
        crazy_num += 1
    
    if c.BOTmaxopenorders < 1:
        print('**** ERROR, <maxopen> value <{0}> is invalid'.format(c.BOTmaxopenorders))
        error_num += 1
    
    if c.BOTreopenfinisheddelay < 0:
        print('**** ERROR, <reopenfinisheddelay> value <{0}> is invalid'.format(c.BOTreopenfinisheddelay))
        error_num += 1
    
    if c.BOTreopenfinishednum < 0:
        print('**** ERROR, <reopenfinishednum> value <{0}> is invalid'.format(c.BOTreopenfinishednum))
        error_num += 1
    
    if c.BOTreopenfinishednum > c.BOTmaxopenorders:
        print('**** ERROR, <reopenfinishednum> can not be more than <maxopenorders> value <{0}>/<{1}> is invalid'.format(c.BOTreopenfinishednum, c.BOTmaxopenorders))
        error_num += 1
    
    if c.BOTtakerbot < 0:
        print('**** ERROR, <takerbot> value <{0}> is invalid'.format(c.BOTtakerbot))
        error_num += 1
    
    if c.BOThidden_orders == True:
        if c.BOTtakerbot < 0:
            print('**** ERROR when <hidden_orders> {0} are enabled <takerbot> <{1} mut be enabled also>'.format(c.BOThidden_orders, c.BOTtakerbot))
            error_num += 1
            
    if c.BOTboundary_start_price != 0:
        if c.BOTboundary_start_price < 0:
            print('**** ERROR, <boundary_start_price> value <{0}> is invalid. Center price must be positive number'.format(c.BOTboundary_start_price))
            error_num += 1
    
    if c.BOTboundary_max_relative != 0:
        if c.BOTboundary_max_relative < 0:
            print('**** ERROR, <boundary_max_relative> value <{0}> is invalid. For example value <1.12> means bot will work up to price relative to +12% of price when bot started'.format(c.BOTboundary_max_relative))
            error_num += 1
        elif c.BOTboundary_max_relative < 1:
            print('**** WARNING, <boundary_max_relative> value <{0}> is invalid. For example value <1.12> means bot will work up to price relative to +12% of price when bot started'.format(c.BOTboundary_max_relative))
            print('++++ HINT, If you are really sure about what you are doing, you can ignore this warning by using --imreallysurewhatimdoing argument')
            crazy_num += 1
    
    if c.BOTboundary_min_relative != 0:
        if c.BOTboundary_min_relative < 0:
            print('**** ERROR, <boundary_min_relative> value <{0}> is invalid. For example value <0.8> means bot will work at least of 0.8 of price, which is -20% of price when bot started'.format(c.BOTboundary_min_relative))
            error_num += 1
            
        elif c.BOTboundary_min_relative > 1:
            print('**** WARNING, <boundary_min_relative> value <{0}> seems invalid. For example value <0.8> means bot will work at least of 0.8 of price, which is -20% of price when bot started'.format(c.BOTboundary_min_relative))
            print('++++ HINT, If you are really sure about what you are doing, you can ignore this warning by using --imreallysurewhatimdoing argument')
            crazy_num += 1
    
    if (c.BOTboundary_max_relative != 0 or c.BOTboundary_min_relative != 0) and (c.BOTboundary_max_static != 0 and c.BOTboundary_min_static != 0):
        print('**** ERROR, <boundary_***_relative> and <boundary_***_static> can not be configured at same time')
        error_num += 1
    
    if c.BOTboundary_max_relative != 0 and c.BOTboundary_max_relative < c.BOTboundary_min_relative:
        print('**** ERROR, <boundary_max_relative> value <{0}> can not be less than <boundary_min_relative> value <{1}>.'.format(c.BOTboundary_max_relative, c.BOTboundary_min_relative))
        error_num += 1
    
    if c.BOTboundary_max_static < 0:
        print('**** ERROR, <boundary_max_static> value <{0}> is invalid. For example value <100> means bot will sell maker for price maximum of 100 takers by one maker'.format(c.BOTboundary_max_static))
        error_num += 1
    
    if c.BOTboundary_min_static < 0:
        print('**** ERROR, <boundary_min_static> value <{0}> is invalid. For example value <10> means bot will sell maker for minimum price 10 takers by one maker'.format(c.BOTboundary_min_static))
        error_num += 1
    
    if c.BOTboundary_max_static < c.BOTboundary_min_static:
        print('**** ERROR, <boundary_max_static> value <{0}> can not be less than <boundary_min_static> value <{1}>.'.format(c.BOTboundary_max_static, c.BOTboundary_min_static))
        error_num += 1
    
    if c.BOTbalance_save_number < 0:
        print('**** ERROR, <balance_save_number> value <{0}> is invalid'.format(c.BOTbalance_save_number))
        error_num += 1
    
    if c.BOTbalance_save_percent < 0 or c.BOTbalance_save_percent > 1:
        print('**** ERROR, <balance_save_percent> value <{0}> is invalid'.format(c.BOTbalance_save_percent))
        error_num += 1
    
    error_num_tmp, crazy_num_tmp = feature__maker_price__load_config_verify()
    error_num += error_num_tmp
    crazy_num += crazy_num_tmp
    
    error_num_tmp, crazy_num_tmp = feature__flush_co__load_config_verify()
    error_num += error_num_tmp
    crazy_num += crazy_num_tmp
    
    error_num_tmp, crazy_num_tmp = pricing_proxy_client__load_config_verify()
    error_num += error_num_tmp
    crazy_num += crazy_num_tmp
    
    error_num_tmp, crazy_num_tmp = pricing_storage__load_config_verify()
    error_num += error_num_tmp
    crazy_num += crazy_num_tmp
    
    # arguments: dynamic values, special pump/dump order
    
    error_num_tmp, crazy_num_tmp = feature__slide_dyn__load_config_verify()
    error_num += error_num_tmp
    crazy_num += crazy_num_tmp
    
    if c.BOTslidepump < 0:
        print('**** ERROR, <slidepump> value <{0}> is invalid'.format(c.BOTslidepump))
        error_num += 1
    
    if c.BOTpumpamount < 0 and c.BOTslidepump > 0:
        print('**** ERROR, <pumpamount> value <{0}> is invalid'.format(c.BOTpumpamount))
        error_num += 1
        
    # arguments: reset orders by events
    if c.BOTresetonpricechangepositive < 0:
        print('**** ERROR, <resetonpricechangepositive> value <{0}> is invalid'.format(c.BOTresetonpricechangepositive))
        error_num += 1
    
    if c.BOTresetonpricechangenegative < 0:
        print('**** ERROR, <resetonpricechangenegative> value <{0}> is invalid'.format(c.BOTresetonpricechangenegative))
        error_num += 1
    
    if c.BOTresetafterdelay < 0:
        print('**** ERROR, <resetafterdelay> value <{0}> is invalid'.format(c.BOTresetafterdelay))
        error_num += 1
    
    if c.BOTresetafterorderfinishnumber < 0:
        print('**** ERROR, <resetafterorderfinishnumber> value <{0}> is invalid'.format(c.BOTresetafterorderfinishnumber))
        error_num += 1
    
    if c.BOTresetafterorderfinishdelay < 0:
        print('**** ERROR, <resetafterorderfinishdelay> value <{0}> is invalid'.format(c.BOTresetafterorderfinishdelay))
        error_num += 1
    
    # arguments: internal values changes
    if c.BOTdelayinternal < 1:
        print('**** ERROR, <delayinternal> value <{0}> is invalid'.format(c.BOTdelayinternal))
        error_num += 1
        
    if c.BOTdelayinternalerror < 1:
        print('**** ERROR, <delayinternalerror> value <{0}> is invalid'.format(c.BOTdelayinternalerror))
        error_num += 1
        
    # arguments: internal values changes
    if c.BOTdelayinternalcycle < 1:
        print('**** ERROR, <delayinternalcycle> value <{0}> is invalid'.format(c.BOTdelayinternalcycle))
        error_num += 1
    
    if c.BOTdelaycheckprice < 1:
        print('**** ERROR, <delaycheckprice> value <{0}> is invalid'.format(c.BOTdelaycheckprice))
        error_num += 1
        
    if crazy_num != c.BOTimreallysurewhatimdoing or error_num != 0:
        if error_num != 0:
            print("**** ERROR > errors in configuration detected > {}".format(error_num))
        if crazy_num != 0:
            print("**** WARNING > crazy config values detected, but not expected> {}/{}".format(crazy_num, c.BOTimreallysurewhatimdoing))
        if crazy_num < c.BOTimreallysurewhatimdoing:
            print("**** WARNING > crazy config values not detected, but expected > {}/{}".format(crazy_num, c.BOTimreallysurewhatimdoing))
            
        print('>>>> Verifying configuration failed.'
        'Please read help and use <imreallysurewhatimdoing> argument correctly, it allows you to specify number of crazy/meaningless/special configuration values, which are expected, to confirm you are sure what you are doing.')
        sys.exit(1)
    else:
        print('>>>> Verifying configuration success')

def argparse_bool(arg):
    if isinstance(arg, bool):
        return arg
    elif isinstance(arg, str):
        if arg.lower() in ['true', 'enabled', 'yes', '1']:
            return True
        else:
            return False
    else:
        return False

def feature__maker_price__load_config_define(parser, argparse):
    parser.add_argument('--maker_price', type=float, help='Value for live price updates or static price configuration'
    '0 - live price updates are activated'
    '-1 - local one time price activated, center price is loaded from remote source and saved int cfg file every time bot starts, even not updated after crash'
    '-2 - local long term price activated, center price is loaded from remote source and saved into cfg file only once, even not updated after restart/crash'
    'Other than 0, -1, or -2 values are invalid'
    'Even if center price is configured like-static, spread and dynamic spread should take care about order position management, this like system dexbot is able to handle situations when no pricing source is available, but it is up to user how to configure price movement'
    'There is also another special pricing configuration feature called "price_redirections"(see bot_v2_template.py file for details)'
    '(default=0 live price update)', default=0)

def feature__maker_price__load_config_postparse(args):
    global c, s, d
    
    c.feature__maker_price__cfg_price = float(args.maker_price)

def feature__slide_dyn__load_config_define(parser, argparse):
    global c, s, d
    parser.add_argument('--slide_dyn_asset', type=str, help='dynamic slide static values are set in specific asset instead of maker (default=--maker)', default=None)
    parser.add_argument('--slide_dyn_asset_track', type=argparse_bool, nargs='?', const=True, help=
    'track dynamic slide asset price updates True/False'
    'This means, ie if trading BLOCK/BTC and asset is USD,'
    'so USD/BLOCK price will be tracked,'
    'so values will be updated with ASSET/MAKER price change.(default=False disabled)', default=False)
    parser.add_argument('--slide_dyn_zero_type', type=str, choices=['relative', 'static'], help='relative to maker+taker or static value when dynamic slide is 0.(default=relative)', default='relative')
    parser.add_argument('--slide_dyn_zero', type=float, help=
    'Relative(to maker+taker balance) or static specific value when dynamic slide intensity is 0%%.'
    ' Value -1 means, to autoconfig value to intensity be 0%% for bot startup MAKER/TAKER amounts.'
    ' Value -2 means, bot will first try to load value from previous run otherwise same like -1 value'
    ' Otherwise it means value=(maker+taker*dyn_zero) at which dynamic slide is at 0%% intensity.'
    ' ie, #1 at type=relative, zero=0.5, means 0%% dyn slide at 50:50 balance converted to zero_asset,'
    ' ie, #2 at type=relative, zero=1.0, means 0%% dyn slide at 100%% of balance in MAKER,'
    ' ie, #3 at type=relative, zero=0.0, means 0%% intensity at 100%% of balance in TAKER.'
    'Static value means static amount of maker where dynamic slide intensity is at 0%%.'
    ' ie, #4 at type=static, zero=120, slide_dyn_asset=USDT, slide_dyn_asset_track=True'
    '   is zero also updated by price of USDT/MAKER'
    '(default=-2 autoconfig)', default=-2)
    
    parser.add_argument('--slide_dyn_type', type=str, choices=['relative', 'static'], default='relative',
    help='relative to maker+taker or static values of, ignore, threshold, (default=relative)', )
    
    parser.add_argument('--slide_dyn_sell_ignore', type=float, default=0,
    help='dynamic slide sell ignore is amount of maker that could be sold and no dyn slide will be activated. (default=0 means no sell ignore zone)')
    parser.add_argument('--slide_dyn_sell_threshold', type=float, default=0.02,
    help='every reached sell threshold will do a one dynamic slide sell step'
    '(default=0.02 at slide_dyn_type=relative, it means, every time 2%% of maker is sold, slide will be increased by slide_dyn_sell_step)')
    
    parser.add_argument('--slide_dyn_sell_step', type=float, default=0,
    help='dynamic slide addition for every reached sell threshold.(default=0 means sell slide step is none)')
    parser.add_argument('--slide_dyn_sell_step_multiplier', type=float, default=1,
    help='recursive sell step multiplier.(default=1 means no multiply)')
    
    parser.add_argument('--slide_dyn_sell_max', type=float, default=0, 
    help='maximum dynamic slide for sell operations(default=0 means disabled)')
    
    parser.add_argument('--slide_dyn_buy_ignore', type=float, default=0, 
    help='dynamic slide buy ignore is amount of maker that could be bought and no dyn slide will be activated. (default=0 means no buy ignore zone)')
    parser.add_argument('--slide_dyn_buy_threshold', type=float, default=0.02,
    help='every reached buy threshold will do a one dynamic slide buy step'
    '(default=0.02 at slide_dyn_type=relative, it means, every time 2%% of maker is buyght, slide will be increased by slide_dyn_buy_step)')
    
    parser.add_argument('--slide_dyn_buy_step', type=float, default=0, 
    help='every reached buy threshold will do a one dynamic slide buy step(default=0 means buy slide step is none)')
    parser.add_argument('--slide_dyn_buy_step_multiplier', type=float, default=1,
    help='recursive buy step multiplier.(default=1 means no multiply)')
    
    parser.add_argument('--slide_dyn_buy_max', type=float, default=0,
    help='maximum dynamic slide for buy operations(default=0 means disabled)')

def feature__slide_dyn__load_config_postparse(args):
    global c, s, d
    if args.slide_dyn_asset is None:
        c.BOTslide_dyn_asset = c.BOTsellmarket
    else:
        c.BOTslide_dyn_asset = str(args.slide_dyn_asset)
    
    c.BOTslide_dyn_asset_track = bool(args.slide_dyn_asset_track)
    
    c.BOTslide_dyn_zero_type = str(args.slide_dyn_zero_type)
    c.BOTslide_dyn_zero = float(args.slide_dyn_zero)
    
    c.BOTslide_dyn_type = str(args.slide_dyn_type)
    
    c.BOTslide_dyn_sell_ignore = float(args.slide_dyn_sell_ignore)
    c.BOTslide_dyn_sell_threshold = float(args.slide_dyn_sell_threshold)
    c.BOTslide_dyn_sell_step = float(args.slide_dyn_sell_step)
    c.BOTslide_dyn_sell_step_multiplier = float(args.slide_dyn_sell_step_multiplier)
    c.BOTslide_dyn_sell_max = float(args.slide_dyn_sell_max)
    
    c.BOTslide_dyn_buy_ignore = float(args.slide_dyn_buy_ignore)
    c.BOTslide_dyn_buy_threshold = float(args.slide_dyn_buy_threshold)
    c.BOTslide_dyn_buy_step = float(args.slide_dyn_buy_step)
    c.BOTslide_dyn_buy_step_multiplier = float(args.slide_dyn_buy_step_multiplier)
    c.BOTslide_dyn_buy_max = float(args.slide_dyn_buy_max)
    
def load_config():
    global c, s, d
    print('>>>> Loading program configuration')
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--reset', type=argparse_bool, nargs='?', const=True, help='Force reset auto-configured values from tmp cfg. (default=False not reset)', default=False)
    parser.add_argument('--restore', type=argparse_bool, nargs='?', const=True, help='Variable used to let bot know to try restore auto-configured values from tmp cfg. Usable when secondary run script management by, also manual testing... (default=False not restoring)', default=False)
    
    # arguments: config file(will be used instead of arguments later)
    parser.add_argument('--config', type=str, help='python bot/strategy config file', default=None)
    
    # arguments: main maker/taker
    parser.add_argument('--maker', type=str, help='asset being sold (default=BLOCK)', default='BLOCK')
    parser.add_argument('--taker', type=str, help='asset being bought (default=LTC)', default='LTC')
    parser.add_argument('--makeraddress', type=str, help='trading address of asset being sold (default=None)', default=None)
    parser.add_argument('--takeraddress', type=str, help='trading address of asset being bought (default=None)', default=None)
    parser.add_argument('--address_funds_only', type=argparse_bool, nargs='?', const=True, help='limit bot to use and compute funds only from maker and taker address(default=False disabled)', default=False)
    
    # ~ parser.add_argument('--maker_address_funds_only', nargs='+', type=str, help='limit bot to use and compute funds from specific maker addresses(or multiple addresses separated by space) only, otherwise all addresses are used', action='store_true')
    # ~ parser.add_argument('--taker_address_funds_only', nargs='+', type=str, help='limit bot to use and compute funds from specific taker addresses(or multiple addresses separated by space) only, otherwise all addresses are used', action='store_true')
    
    feature__flush_co__load_config_define(parser, argparse)
    
    pricing_proxy_client__load_config_define(parser, argparse)
    
    pricing_storage__load_config_define(parser, argparse)
    
    # arguments: basic values
    parser.add_argument('--sell_type', type=float, choices=range(-1, 1), help='<float> number between -1 and 1. -1 means maximum exponential to 0 means linear to 1 means maximum logarithmic. '
    'Recommended middle range log and exp values are 0.8 and -0.45'
    ' (default=0 linear)', default=0)
    
    parser.add_argument('--sell_size_asset', type=str, help='size of orders are set in specific asset instead of maker (default=--maker)', default=None)
    
    parser.add_argument('--sellstart', type=float, help='size of first order or random from range sellstart and sellend (default=0.001)', default=0.001)
    parser.add_argument('--sellend', type=float, help='size of last order or random from range sellstart and sellend (default=0.001)', default=0.001)
    
    parser.add_argument('--sellstartmin', type=float, help='Minimum acceptable size of first order.'
    'If this is configured and there is not enough balance to create first order at <sellstart> size, order will be created at maximum possible size between <sellstart> and <sellstartmin>'
    'By default this feature is disabled.'
    '(default=0 disabled)', default=0)
    parser.add_argument('--sellendmin', type=float, help='Minimum acceptable size of last order.'
    'If this is configured and there is not enough balance to create last order at <sellend> size, order will be created at maximum possible size between <sellend> and <sellendmin>'
    'By default this feature is disabled.'
    '(default=0 disabled)', default=0)
    # ~ parser.add_argument('--marking', type=float, help='mark order amount by decimal number for example 0.000777 (default=0 disabled)', default=0)
    
    parser.add_argument('--sellrandom', help='orders size will be random number between sellstart and sellend, otherwise sequence of orders starting by sellstart amount and ending with sellend amount(default=disabled)', action='store_true')
    
    parser.add_argument('--slidestart', type=float, help='price of first order will be equal to (slidestart * actual_price) (default=1.01 means +1%%)', default=1.01)
    parser.add_argument('--slideend', type=float, help='price of last order will be equal to (slideend * actual price) (default=1.021 means +2.1%%)', default=1.021)
    
    parser.add_argument('--maxopen', type=int, help='Max amount of orders to have open at any given time. Placing orders sequence: first placed order is at slidestart(price slide),sellstart(amount) up to slideend(price slide),sellend(amount), last order placed is slidepump if configured, is not counted into this number (default=5)', default=5)
    
    parser.add_argument('--make_next_on_hit', type=argparse_bool, nargs='?', const=True, help='create next order on 0 amount hit, so if first order is not created, rather skipped, next is created(default=False disabled)', default=False)
    
    parser.add_argument('--reopenfinisheddelay', type=int, help='finished orders will be reopened after specific delay(seconds) of last filled order(default=0 disabled)', default=0)
    parser.add_argument('--reopenfinishednum', type=int, help='finished orders will be reopened after specific number of filled orders(default=0 disabled)', default=0)
    
    parser.add_argument('--partial_orders', type=argparse_bool, nargs='?', const=True, help='enable or disable partial orders. Partial orders minimum is set by <sellstartmin> <sellendmin> along with dynamic size of orders(default=False disabled)', default=False)
    parser.add_argument('--takerbot', type=int, help='Keep checking for possible partial orders which meets requirements(size, price) and accept that orders.'
    'If this feature is enabled, takerbot is automatically searching for orders at size between <sellstart-sellend>...<sellstartmin-sellendmin> and at price <slidestart-slideend>+<dynamic slide>*<price> and higher.'
    'This feature can be also understood as higher layer implementation of limit order feature on top of atomic swaps on BlockDX exchange. Takerbot can possible cancel multiple opened orders to autotake orders which meets requirements'
    '(I.e. value 30 means check every 30 seconds)'
    'By default this feature is disabled.'
    '(default=0 disabled)', default=0)

    # ~ TODO = not implemented yet
    parser.add_argument('--hidden_orders', type=argparse_bool, nargs='?', const=True, help='Orders will be created only virtually, hidden from dx and acting like takerbot only.  (default=False disabled)', default=False)
    
    # ~ parser.add_argument('--external_type', type=str, choices=[None, 'uniswap', 'bittrex'], help='choose external  (default=None)', default=None)
    # ~ parser.add_argument('--external_balance_type', type=str, choices=['auto','relative', 'static'], help='(default=auto)', default=None)
    # ~ parser.add_argument('--external_balance_min', type=float, help='minimum unbalance size when bot trigger balancing', default=0)
    # ~ parser.add_argument('--external_balance_threshold', type=float, help='', default=0.5)
    # liquidity vs arbitrage vs mirroring vs balancing relative
    
    # arguments: boundaries configuration
    parser.add_argument('--boundary_asset', type=str, help='boundary measurement asset, i.e.: if maker/taker pair is BLOCK/BTC and boundary_asset_is USDT, so possible boundary min 1.5 and max 3 USD (default= --taker)', default=None)
    parser.add_argument('--boundary_asset_track', type=argparse_bool, nargs='?', const=True, help='Track boundary asset price updates. This means, ie if trading BLOCK/BTC on USD also track USD/BTC price and update boundaries by it (default=False disabled)', default=False)
    
    parser.add_argument('--boundary_reversed_pricing', type=argparse_bool, nargs='?', const=True, help='reversed set pricing as 1/X, ie BLOCK/BTC vs BTC/BLOCK pricing can set like 0.000145 on both bot trading sides, instead of 0.000145 vs 6896.55.'
    'Is used in configuration <boundary_start_price>, <boundary_max_static> and <boundary_min_static>.'
    ' (default=False Disabled)', default=False)
    
    parser.add_argument('--boundary_start_price', type=float, help='manually set center price. Its usable only when using relative boundaries and boundary_asset_track is Disabled (default=0 automatic)', default=0)
    
    parser.add_argument('--boundary_max_relative', type=float, help='maximum acceptable price of maker(sold one) where bot will stop selling, price is relative to price when bot started,i.e.: Start price:100, config value:3, so bot will sell up to 100*3 = 300 price, (default=0 disabled)', default=0)
    parser.add_argument('--boundary_min_relative', type=float, help='minimum acceptable price of maker(sold one) where bot will stop selling, price is relative to price when bot started,i.e.: Start price:100, config value:0.8, so bot will sell at least for 100*0.8 = 80 price, (default=0 disabled)', default=0)
    
    parser.add_argument('--boundary_max_static', type=float, help='maximum acceptable price of maker(sold one) where bot will stop selling(default=0 disabled)', default=0)
    parser.add_argument('--boundary_min_static', type=float, help='minimum acceptable price of maker(sold one) where bot will stop selling(default=0 disabled)', default=0)
    
    parser.add_argument('--boundary_max_nocancel', help='do not cancel orders, default is to cancel orders', action='store_true')
    parser.add_argument('--boundary_max_noexit', help='wait instead of exit program, default is to exit program', action='store_true')
    parser.add_argument('--boundary_min_nocancel', help='do not cancel orders, default is to cancel orders', action='store_true')
    parser.add_argument('--boundary_min_noexit', help='wait instead of exit program, default is to exit program', action='store_true')
    
    parser.add_argument('--balance_save_asset', type=str, help='size of balance to save is set in specific asset instead of maker (default=--maker)', default=None)
    parser.add_argument('--balance_save_asset_track', type=argparse_bool, nargs='?', const=True, help='Track balance save asset price updates. This means, ie if trading BLOCK/BTC on USD also track USD/BLOCK price and update balance to save by it (default=False disabled)', default=False)
    parser.add_argument('--balance_save_number', help='min taker balance you want to save and do not use for making orders specified by number (default=0)', default=0)
    parser.add_argument('--balance_save_percent', help='min taker balance you want to save and do not use for making orders specified by percent of maker+taker balance (default=0.05 means 5%%)', default=0.05)
    
    feature__maker_price__load_config_define(parser, argparse)
    
    # arguments: dynamic values, special pump/dump order
    
    feature__slide_dyn__load_config_define(parser, argparse)
    
    parser.add_argument('--slidepump', type=float, help='if slide pump is non zero a special order out of slidemax is set, this order will be filled when pump happen(default=0 disabled, 0.5 means order will be placed +50%% out of maximum slide)', default=0)
    parser.add_argument('--pumpamount', type=float, help='pump order size, 0 means maximum, otherwise sellend is used(default=--sellend)', default=0)
    parser.add_argument('--pumpamountmin', type=float, help='minimum acceptable pump order size, otherwise sellendmin is used(default=--sellendmin)', default=0)

    # arguments: reset orders by events
    parser.add_argument('--resetonpricechangepositive', type=float, help='percentual price positive change(you can buy more) when reset all orders. I.e. 0.05 means reset at +5%% change. (default=0 disabled)', default=0)
    parser.add_argument('--resetonpricechangenegative', type=float, help='percentual price negative change(you can buy less) when reset all orders. I.e. 0.05 means reset at -5%% change. (default=0 disabled)', default=0)
    parser.add_argument('--resetafterdelay', type=int, help='keep resetting orders in specific number of seconds (default=0 disabled)', default=0)
    parser.add_argument('--resetafterorderfinishnumber', type=int, help='number of orders to be finished before resetting orders (default=0 disabled)', default=0)
    parser.add_argument('--resetafterorderfinishdelay', type=int, help='delay after finishing last order before resetting orders in seconds (default=0 disabled)', default=0)

    # arguments: internal values changes
    parser.add_argument('--delayinternal', type=float, help='sleep delay, in seconds, between place/cancel orders or other internal operations(can be used ie. case of bad internet connection...) (default=2.3)', default=2.3)
    parser.add_argument('--delayinternalerror', type=float, help='sleep delay, in seconds, when error happen to try again. (default=10)', default=10)
    parser.add_argument('--delayinternalcycle', type=float, help='sleep delay, in seconds, between main loops to process all things to handle. (default=8)', default=8)
    parser.add_argument('--delaycheckprice', type=float, help='sleep delay, in seconds to check again pricing (default=180)', default=180)
    
    # arguments: pricing source arguments
    parser.add_argument('--usecb', help='enable cryptobridge pricing', action='store_true')
    parser.add_argument('--usecg', help='enable coingecko pricing', action='store_true')
    parser.add_argument('--usecustom', help='enable custom pricing', action='store_true')

    # arguments: utility arguments
    parser.add_argument('--cancelall', help='cancel all orders and exit', action='store_true')
    parser.add_argument('--cancelmarket', help='cancel all orders in market specified by pair --maker and --taker', action='store_true')
    parser.add_argument('--canceladdress', help='cancel all orders in market specified by pair --maker + --taker + --makeraddress + --takeraddress ', action='store_true')
    
    # arguments: special arguments
    parser.add_argument('--imreallysurewhatimdoing', type=int, default=0, help='This argument allows user to specify number of non-standard configuration values for special cases like user want to activate bot trading later relatively higher price than actual is')
    
    args = parser.parse_args()
    
    # check if configuration argument is set
    c.BOTconfigfile = args.config
    
    # try to load auto-generated temporary configuration
    feature__tmp_cfg__load_cfg(c.BOTconfigfile + ".tmp.cfg")
    
    # arguments: main maker/taker
    c.BOTsellmarket = args.maker.upper()
    c.BOTbuymarket = args.taker.upper()
    
    # try to autoselect maker/taker address from config file
    if c.BOTsellmarket in dxsettings.tradingaddress:
        c.BOTmakeraddress = dxsettings.tradingaddress[c.BOTsellmarket]
    
    if c.BOTbuymarket in dxsettings.tradingaddress:
        c.BOTtakeraddress = dxsettings.tradingaddress[c.BOTbuymarket]
    
    # try to autoselect maker/taker address from program arguments
    if args.makeraddress is not None:
        c.BOTmakeraddress = args.makeraddress
        
    if args.takeraddress is not None:
        c.BOTtakeraddress = args.takeraddress
    
    c.BOTreset = bool(args.reset)
    c.BOTrestore = bool(args.restore)
    
    c.BOTaddress_funds_only = bool(args.address_funds_only)
    
    c.BOTpartial_orders = bool(args.partial_orders)
    
    c.BOThidden_orders = bool(args.hidden_orders)
    
    feature__maker_price__load_config_postparse(args)
    
    feature__flush_co__load_config_postparse(args)
    
    pricing_proxy_client__load_config_postparse(args)
    
    pricing_storage__load_config_postparse(args)
    
    if args.boundary_asset is None:
        c.BOTboundary_asset = c.BOTbuymarket
    else:
        c.BOTboundary_asset = str(args.boundary_asset)
    
    c.BOTboundary_asset_track = bool(args.boundary_asset_track)
    
    c.BOTboundary_reversed_pricing = bool(args.boundary_reversed_pricing)
    
    c.BOTboundary_start_price = float(args.boundary_start_price)
    
    c.BOTboundary_max_relative = args.boundary_max_relative
    c.BOTboundary_min_relative = args.boundary_min_relative
    
    c.BOTboundary_max_static = args.boundary_max_static
    c.BOTboundary_min_static = args.boundary_min_static
    
    c.BOTboundary_max_nocancel = args.boundary_max_nocancel
    c.BOTboundary_max_noexit = args.boundary_max_noexit
    c.BOTboundary_min_nocancel = args.boundary_min_nocancel
    c.BOTboundary_min_noexit = args.boundary_min_noexit
    
    # arguments: basic values
    c.BOTsellrandom = args.sellrandom
    
    if args.sell_size_asset is None:
        c.BOTsell_size_asset = c.BOTsellmarket
    else:
        c.BOTsell_size_asset = str(args.sell_size_asset)
    
    c.BOTsell_type = float(args.sell_type)
    
    c.BOTsellstart = float(args.sellstart)
    c.BOTsellend = float(args.sellend)
    c.BOTsellstartmin = float(args.sellstartmin)
    c.BOTsellendmin = float(args.sellendmin)
    c.BOTslidestart = float(args.slidestart)
    c.BOTslideend = float(args.slideend)
    c.BOTslidemin = min(c.BOTslidestart, c.BOTslideend)
    c.BOTslidemax = max(c.BOTslidestart, c.BOTslideend)
    c.BOTmaxopenorders = int(args.maxopen)
    c.BOTmake_next_on_hit = bool(args.make_next_on_hit)
    c.BOTreopenfinisheddelay = int(args.reopenfinisheddelay)
    c.BOTreopenfinishednum = int(args.reopenfinishednum)
    if c.BOTreopenfinishednum > 0 or c.BOTreopenfinisheddelay > 0:
        c.BOTreopenfinished = 1
    else:
        c.BOTreopenfinished = 0
    
    # ~ c.BOTmarking = float(args.marking)
    
    if args.balance_save_asset is None:
        c.BOTbalance_save_asset = c.BOTsellmarket
    else:
        c.BOTbalance_save_asset = str(args.balance_save_asset)
    c.BOTbalance_save_asset_track = bool(args.balance_save_asset_track)
    c.BOTbalance_save_number = float(args.balance_save_number)
    c.BOTbalance_save_percent = float(args.balance_save_percent)
    
    c.BOTtakerbot = int(args.takerbot)
    
    # arguments: dynamic values, special pump/dump order
    
    feature__slide_dyn__load_config_postparse(args)
        
    c.BOTslidepump = float(args.slidepump)
    c.BOTslidepumpenabled = (True if c.BOTslidepump > 0 else False)
    c.BOTpumpamount = (float(args.pumpamount) if float(args.pumpamount) >= 0 else c.BOTsellend)
    
    # arguments: reset orders by events
    c.BOTresetonpricechangepositive = float(args.resetonpricechangepositive)
    c.BOTresetonpricechangenegative = float(args.resetonpricechangenegative)
    c.BOTresetafterdelay = int(args.resetafterdelay)
    c.BOTresetafterorderfinishnumber = int(args.resetafterorderfinishnumber)
    c.BOTresetafterorderfinishdelay = int(args.resetafterorderfinishdelay)
    
    # arguments: internal values changes
    c.BOTdelayinternal = float(args.delayinternal)
    c.BOTdelayinternalerror = float(args.delayinternalerror)
    c.BOTdelayinternalcycle = float(args.delayinternalcycle)
    c.BOTdelaycheckprice = int(args.delaycheckprice)
    
    # arguments: pricing source arguments
    if args.usecustom:
        c.BOTuse = 'custom'
    elif args.usecg:
        c.BOTuse = 'cg'
    elif args.usecb:
        c.BOTuse = 'cb'
    else:
        c.BOTuse = 'bt'
    
    # arguments: utility arguments
    c.cancelall = args.cancelall
    c.cancelmarket = args.cancelmarket
    c.canceladdress = args.canceladdress
    
    # arguments: special arguments
    c.BOTimreallysurewhatimdoing = int(args.imreallysurewhatimdoing)
    
    load_config_verify_or_exit()
    
# global variables which have dependency on configuration be done
def global_vars_init_postconfig():
    global c, s, d
    print('>>>> Global variables post-configuration initialization')
    
    if c.BOTreopenfinished == 0:
        s.reopenstatuses = s.status_list__ready_to_reopen_nfinished
    else:
        s.reopenstatuses = s.status_list__ready_to_reopen_wfinished
    
    s.ordersvirtualmax = c.BOTmaxopenorders + int(c.BOTslidepumpenabled) # pump and dump order is extra if exist
    d.ordersvirtual = [0]*s.ordersvirtualmax
    for i in range(s.ordersvirtualmax):
        d.ordersvirtual[i] = {}
        virtual_orders__update_status(d.ordersvirtual[i], s.status_list__canceled)
        d.ordersvirtual[i]['id'] = 0
    
# cancel all my orders
def do_utils_cancel_orders_all():
    global c, s, d
    print('>>>> Using utility to cancel all orders on all markets')
    retcode, retdata = dxbottools.cancelallorders()
    print('>>>> Cancel orders result: {0} >> {1}'.format(retcode, retdata))
    return retcode

# cancel orders specified by maker and taker
def do_utils_cancel_orders_market():
    global c, s, d
    print('>>>> Using utility to cancel specific market pair {0}-{1} orders'.format(c.BOTsellmarket, c.BOTbuymarket))
    retcode, retdata = dxbottools.cancelallordersbymarket(c.BOTsellmarket, c.BOTbuymarket)
    print('>>>> Cancel orders result: {0} >> {1}'.format(retcode, retdata))
    return retcode

# cancel all orders that belongs to running bot instance
def do_utils_cancel_orders_address():
    global c, s, d
    print('>>>> Using utility to cancel specifix market pair and address {0}-{1} {2}-{3}'.format(c.BOTsellmarket, c.BOTbuymarket, c.BOTmakeraddress, c.BOTtakeraddress))
    retcode, retdata = dxbottools.cancelallordersbyaddress(c.BOTsellmarket, c.BOTbuymarket, c.BOTmakeraddress, c.BOTtakeraddress)
    print('>>>> Cancel orders result: {0} >> {1}'.format(retcode, retdata))
    return retcode

# do utils and exit
def do_utils_and_exit():
    global c, s, d
    if c.cancelall:
        retcode = do_utils_cancel_orders_all()
        sys.exit(retcode)
    elif c.cancelmarket:
        retcode = do_utils_cancel_orders_market()
        sys.exit(retcode)
    elif c.canceladdress:
        retcode = do_utils_cancel_orders_address()
        sys.exit(retcode)

# try to update remote maker pricing value
def feature__maker_price__pricing_update():
    global c, s, d
    
    # load pricing from remote source
    price_maker_used = pricing_storage__try_get_price(c.BOTsellmarket, c.BOTbuymarket)
    # ~ price_maker_remote = pricing_storage__try_get_price(c.BOTsellmarket, c.BOTbuymarket, allow_redirect = False)
    
    # Check if price been loaded from remote pricing storage or remote
    if price_maker_used != 0:
        # actual remote value
        # ~ d.feature__maker_price__value_remote = price_maker_remote
        
        # remote pricing checking activated
        if c.feature__maker_price__cfg_price == 0:
            d.feature__maker_price__value_current_used = price_maker_used
            
        # local one time price activated
        elif c.feature__maker_price__cfg_price == -1:
            
            if d.feature__maker_price__value_current_used == 0:
                # try to restore maker price only after crash
                if c.BOTrestore == True:
                    d.feature__maker_price__value_current_used = feature__tmp_cfg__get_value("feature__maker_price__value_current_used", 0)
            
            # if bot is started normally local price is zero so it will be stored in tmp cfg
            if d.feature__maker_price__value_current_used == 0:
                d.feature__maker_price__value_current_used = price_maker_used
                feature__tmp_cfg__set_value("feature__maker_price__value_current_used", price_maker_used)
        
        # local long term price activated
        elif c.feature__maker_price__cfg_price == -2:
            
            # try to restore maker price always
            if c.feature__maker_price__value_current_used == 0:
                d.feature__maker_price__value_current_used = feature__tmp_cfg__get_value("feature__maker_price__value_current_used", 0)
            
            # even long term price must be set for the first time
            if c.feature__maker_price__value_current_used == 0:
                d.feature__maker_price__value_current_used = price_maker_used
                feature__tmp_cfg__set_value("feature__maker_price__value_current_used", price_maker_used)
                
        # invalid maker_price configuration
        else:
            return 0
            
        # startup maker price value load or restore
        if d.feature__maker_price__value_startup == 0:
            if c.feature__maker_price__cfg_price == -1 or c.feature__maker_price__cfg_price == -2:
                d.feature__maker_price__value_startup = d.feature__maker_price__value_current_used
            elif c.BOTrestore == True:
                d.feature__maker_price__value_startup = feature__tmp_cfg__get_value("feature__maker_price__value_startup", 0)
            
            if d.feature__maker_price__value_startup == 0:
                d.feature__maker_price__value_startup = price_maker_used
                feature__tmp_cfg__set_value("feature__maker_price__value_startup", price_maker_used)
            
    return price_maker_used

# check if pricing works or exit
def pricing_check_or_exit():
    global c, s, d
    print('>>>> Checking pricing information for <{0}> <{1}>'.format(c.BOTsellmarket, c.BOTbuymarket))
    
    # check if sell and buy market are not same
    if c.BOTsellmarket == c.BOTbuymarket:
        print('ERROR: Maker and taker asset cannot be the same')
        sys.exit(1)
    
    # try to get main pricing
    price_maker = feature__maker_price__pricing_update()
    if price_maker == 0:
        print('#### Main pricing not available')
        sys.exit(1)
    
    # try to get initial price of asset which balance save size is set in
    price__balance_save_asset = feature__balance_save_asset__pricing_update()
    if price__balance_save_asset == 0:
        print('#### balance save asset pricing not available')
        sys.exit(1)
    
    # try to get initial price of asset vs maker in which is dynamic slide zero set
    price_slide_dyn_asset = feature__slide_dyn__asset_pricing_update()
    if price_slide_dyn_asset == 0:
        print('#### dynamic slide asset pricing not available')
        sys.exit(1)
    
    # try to get initial price of asset vs maker in which are orders sizes set, ie USD
    price_sell_size_asset = feature__sell_size_asset__pricing_update()
    if price_sell_size_asset == 0:
        print('#### Sell size asset pricing not available')
        sys.exit(1)
    
    # try to get initial boundary pricing if custom
    price_boundary = feature__boundary__pricing_update_relative_init()
    if price_boundary == 0:
        print('#### Boundary pricing not available')
        sys.exit(1)

# asset which dynamic slide zero size is set in pricing update
def feature__slide_dyn__asset_pricing_update():
    global c, s, d
    
    temp_price = pricing_storage__try_get_price(c.BOTslide_dyn_asset, c.BOTsellmarket)
    if temp_price != 0:
        d.feature__slide_dyn__asset_price = temp_price
    
    return temp_price

# convert asset which dynamic slide zero size is set to maker 
def feature__slide_dyn__asset_convert_to_maker(size_in_slide_dyn_asset):
    global c, s, d
    
    return d.feature__slide_dyn__asset_price * size_in_slide_dyn_asset
    
# convert maker to asset which dynamic slide zero size is set in
def feature__slide_dyn__maker_convert_to_asset(size_in_slide_dyn_maker):
    global c, s, d
    
    return size_in_slide_dyn_maker / d.feature__slide_dyn__asset_price
    
# price of asset which balance save size is set in initialization
def feature__balance_save_asset__init_preconfig():
    global c, s, d
    
    d.feature__balance_save_asset__price = 0

# price of asset which balance save size is set in pricing update
def feature__balance_save_asset__pricing_update():
    global c, s, d
    
    temp_price = pricing_storage__try_get_price(c.BOTbalance_save_asset, c.BOTsellmarket)
    if temp_price != 0:
        d.feature__balance_save_asset__price = temp_price
    
    return temp_price

# convert asset which balance save size is set to maker 
def feature__balance_save_asset__convert_to_maker(size_in_balance_save_asset):
    global c, s, d
    
    return d.feature__balance_save_asset__price * size_in_balance_save_asset

# get price of asset vs maker in which are orders sizes set, ie USD
def feature__sell_size_asset__pricing_update():
    global c, s, d
    
    temp_price = pricing_storage__try_get_price(c.BOTsell_size_asset, c.BOTsellmarket)
    if temp_price != 0:
        d.feature__sell_size_asset__price = temp_price
    
    return temp_price

# relative boundaries can be specified as relative to maker taker market so price must be checked separately
def feature__boundary__pricing_update():
    global c, s, d
    
    tmp_feature__boundary__price_relative_current = 0
    
    # not reversed pricing system: BOUNDARY >> TAKER
    if c.BOTboundary_reversed_pricing is False:
        price_boundary_for_taker = pricing_storage__try_get_price(c.BOTboundary_asset, c.BOTbuymarket)
        tmp_feature__boundary__price_relative_current = price_boundary_for_taker
        print(">>>> Boundary pricing update: not reversed: <{}/{}>: <{}>".format(c.BOTboundary_asset, c.BOTbuymarket, tmp_feature__boundary__price_relative_current))
    
    # reversed pricing system: BOUNDARY >> 1/MAKER
    else:
        price_boundary_for_maker = pricing_storage__try_get_price(c.BOTboundary_asset, c.BOTsellmarket)
        if price_boundary_for_maker == 0:
            tmp_feature__boundary__price_relative_current = 0
        else:
            tmp_feature__boundary__price_relative_current = 1/price_boundary_for_maker
        print(">>>> Boundary pricing update: reversed: <{}/{}>: <{}>".format(c.BOTboundary_asset, c.BOTbuymarket, tmp_feature__boundary__price_relative_current))
        
    if tmp_feature__boundary__price_relative_current != 0:
        d.feature__boundary__price_relative_current = tmp_feature__boundary__price_relative_current
    
    return tmp_feature__boundary__price_relative_current

# initial get pricing for relative boundaries
def feature__boundary__pricing_update_relative_init():
    global c, s, d
    
    tmp_feature__boundary__price_relative_current = feature__boundary__pricing_update()
    
    d.feature__boundary__price_relative_initial = tmp_feature__boundary__price_relative_current
    
    if c.BOTboundary_start_price > 0:
        d.feature__boundary__price_maker_initial_center = c.BOTboundary_start_price * tmp_feature__boundary__price_relative_current
        d.feature__boundary__price_maker_initial_center_relative = c.BOTboundary_start_price
        print(">>>> Boundary pricing initial update: manual: {} = {} * {}".format(d.feature__boundary__price_maker_initial_center, c.BOTboundary_start_price, tmp_feature__boundary__price_relative_current))
    else:
        d.feature__boundary__price_maker_initial_center = d.feature__maker_price__value_current_used
        d.feature__boundary__price_maker_initial_center_relative = d.feature__maker_price__value_current_used / tmp_feature__boundary__price_relative_current
        print(">>>> Boundary pricing initial update: auto: {}".format(d.feature__boundary__price_maker_initial_center))
        
    return tmp_feature__boundary__price_relative_current
        
# update balances for specific assset
def balance_get(token, address_funds_only = None):
    global c, s, d
    
    ret = {"total": 0, "available": 0, "reserved": 0}
    
    # get all utxos
    utxos = dxbottools.get_utxos(token, True)
    
    # check if get utxos error been occurred
    if isinstance(utxos, list):
        
        for utxo in utxos:
            if address_funds_only == None or utxo.get("address", "") == address_funds_only:
                tmp = utxo.get("amount", 0)
                if utxo.get("orderid", "") == "":
                    ret["available"] += float(tmp)
                else:
                    ret["reserved"] += float(tmp)
                ret["total"] += float(tmp)
    else:
        print('ERROR: get_utxos call invalid response: {}'.format(utxos))
    
    return ret
    
# update actual balanced of maker and taker
def update_balances():
    global c, s, d
    
    print('>>>> Updating balances')
    
    tmp_maker = {}
    tmp_taker = {}
    
    tmp_maker_address = None
    tmp_taker_address = None
    
    # if bot using funds from specific address only
    if c.BOTaddress_funds_only is True:
        tmp_maker_address = c.BOTmakeraddress
        tmp_taker_address = c.BOTtakeraddress
    
    tmp_maker = balance_get(c.BOTsellmarket, tmp_maker_address)
    tmp_taker = balance_get(c.BOTbuymarket, tmp_taker_address)
    
    d.balance_maker_total = tmp_maker["total"]
    d.balance_maker_available = tmp_maker["available"]
    d.balance_maker_reserved = tmp_maker["reserved"]
    
    d.balance_taker_total = tmp_taker["total"]
    d.balance_taker_available = tmp_taker["available"]
    d.balance_taker_reserved = tmp_taker["reserved"]
    
    print('>>>> Actual balance maker token <{}> <{}> total <{}> available <{}> reserved <{}>'.format(tmp_maker_address, c.BOTsellmarket, d.balance_maker_total, d.balance_maker_available, d.balance_maker_reserved))
    print('>>>> Actual balance taker token <{}> <{}> total <{}> available <{}> reserved <{}>'.format(tmp_taker_address, c.BOTbuymarket, d.balance_taker_total, d.balance_taker_available, d.balance_taker_reserved))

# initialize dynamic slide feature
def feature__slide_dyn__init_postpricing():
    global c, s, d
    
    # try to restore maker price when slide zero is -2 or restore is true
    if (c.BOTreset == False) and (c.BOTslide_dyn_zero == -2 or c.BOTrestore == True):
        c.feature__slide_dyn__maker_price_value_startup = feature__tmp_cfg__get_value("feature__slide_dyn__maker_price_value_startup", None)
    
    # if maker price value is None or was not restored, than save actual as default for later usage
    if c.feature__slide_dyn__maker_price_value_startup == None:
        c.feature__slide_dyn__maker_price_value_startup = d.feature__maker_price__value_current_used
        feature__tmp_cfg__set_value("feature__slide_dyn__maker_price_value_startup", c.feature__slide_dyn__maker_price_value_startup)
    
    # get total balance maker + taker represented as maker
    balance_taker_in_maker = (d.balance_taker_total / c.feature__slide_dyn__maker_price_value_startup)
    balance_total = d.balance_maker_total + balance_taker_in_maker
    
    if c.BOTslide_dyn_zero_type == 'relative':
        
        # slide dyn zero auto set
        if c.BOTslide_dyn_zero == -1 or c.BOTslide_dyn_zero == -2:
            
            # if slide dyn zero is -2 or restore is true, try to load tmp cfg
            if (c.BOTreset == False) and (c.BOTslide_dyn_zero == -2 or c.BOTrestore == True):
                if feature__tmp_cfg__get_value("BOTslide_dyn_zero_type") == 'relative':
                    c.feature__slide_dyn__zero_value = feature__tmp_cfg__get_value("feature__slide_dyn__zero_value", None)
                    
            # if load tmp cfg failed, auto configure value and safe actual value
            if c.feature__slide_dyn__zero_value == None:
                
                if balance_total == 0:
                    c.feature__slide_dyn__zero_value = 0.5
                elif balance_taker_in_maker == 0:
                    c.feature__slide_dyn__zero_value = 1
                elif d.balance_maker_total == 0:
                    c.feature__slide_dyn__zero_value = 0
                else:
                    c.feature__slide_dyn__zero_value = d.balance_maker_total / balance_total
                
                feature__tmp_cfg__set_value("BOTslide_dyn_zero_type", "relative")
                feature__tmp_cfg__set_value("feature__slide_dyn__zero_value", c.feature__slide_dyn__zero_value)
                
            print('>>>> dynamic slide init auto-set <relative> zero intensity at value <{} ~ {}>'.format(c.BOTslide_dyn_zero, c.feature__slide_dyn__zero_value))
            
        else:
            c.feature__slide_dyn__zero_value = c.BOTslide_dyn_zero
            print('>>>> dynamic slide init manu-set <relative> zero intensity at value <{} ~ {}>'.format(c.BOTslide_dyn_zero, c.feature__slide_dyn__zero_value))
            
    elif c.BOTslide_dyn_zero_type == 'static':
        
        if c.BOTslide_dyn_zero == -1 or c.BOTslide_dyn_zero == -2:
            
            # if slide dyn zero is -2 or restore is true, try to load tmp cfg
            if (c.BOTreset == False) and (c.BOTslide_dyn_zero == -2 or c.BOTrestore == True):
                if feature__tmp_cfg__get_value("BOTslide_dyn_zero_type") == 'static':
                    if feature__tmp_cfg__get_value("BOTslide_dyn_asset") == c.BOTslide_dyn_asset:
                        c.feature__slide_dyn__zero_value = feature__tmp_cfg__get_value("feature__slide_dyn__zero_value")
                        
            # if load tmp cfg failed, auto configure value and safe actual value
            if c.feature__slide_dyn__zero_value == None:
                c.feature__slide_dyn__zero_value = feature__slide_dyn__maker_convert_to_asset(d.balance_maker_total)
                
                feature__tmp_cfg__set_value("BOTslide_dyn_zero_type", "static")
                feature__tmp_cfg__set_value("BOTslide_dyn_asset", c.BOTslide_dyn_asset)
                feature__tmp_cfg__set_value("feature__slide_dyn__zero_value", c.feature__slide_dyn__zero_value)
                
            print('>>>> dynamic slide auto auto-set <static> zero intensity at value <{} ~ {}>'.format(c.BOTslide_dyn_zero, c.feature__slide_dyn__zero_value))
        else:
            c.feature__slide_dyn__zero_value = c.BOTslide_dyn_zero
            print('>>>> dynamic slide init manu-set <static> zero intensity at value <{} ~ {}>'.format(c.BOTslide_dyn_zero, c.feature__slide_dyn__zero_value))
    else:
        print('!!!! internal BUG Detected <BOTslide_dyn_zero_type> is <{}>'.format(c.BOTslide_dyn_zero_type))
        sys.exit(1)
        
# compute and get dynamic slide value
def feature__slide_dyn__get_dyn_slide():
    global c, s, d
    
    # additional dynamic price slide == dynamic spread == slide_dyn

    # Theory about:
    #
    # if someone is running a MAKER/TAKER dxbot,
    #
    # >> and if situation: price of MAKER(TO BE SOLD) is going up, so probably users around are buying MAKER more and more, so this BOT have less and less MAKER(TO SELL) with also placing orders on position of actual (price + slide) of MAKER
    # >> unfortunately nobody can predict which will be upcoming top price of MAKER, also we must secure liquidity, not doing an empty spread in depth chart.
    # >> but what we can do is, by every specific sold amount of MAKER, bot could increase slide little bit and this way testing next expected price. And if this pass more and more times, dxbot will predict higher and higher MAKER price by increasing dynamic slide
    # >> but what is also happening very often is price manipulation, for example pumping price before dumping more. for this like situations, bot could loss because pushing orders on (price + slide + dynamic slide) position. For this case, there is as sell dynamic slide configuration along with buy dynamic slide, which could also increase price of TAKER on oposite dxbot side little bit to prevent pump and dump loss.
    # 
    # >> buy and sell dynamic slide is very native market behavior expectation algorithm. as prices will go up and down, up and down bot will profit..., but remember, there are also txfees...
    
    print('>>>> dynamic_slide >> recomputing')
    
    if c.BOTslide_dyn_asset_track is True:
        while True:
            if feature__slide_dyn__asset_pricing_update() != 0:
                break
            print('#### Pricing of dynamic slide asset not available... waiting to restore...')
            time.sleep(c.BOTdelayinternalerror)
    
    # zero type = relative >> so we get relative value to both balance total
    if c.BOTslide_dyn_zero_type == 'relative':
        tmp_dyn_zero_asset=""
        if c.BOTslide_dyn_asset_track is True:
            balance_taker_in_maker = (d.balance_taker_total / d.feature__maker_price__value_current_used) #convert taker balance to by price
        else:
            balance_taker_in_maker = (d.balance_taker_total / c.feature__slide_dyn__maker_price_value_startup) #convert taker balance to by price
        balance_total = d.balance_maker_total + balance_taker_in_maker
        tmp_bot_slide_dyn_zero = c.feature__slide_dyn__zero_value * balance_total
        
    # zero type = static >> so we get static value which could also be relative to zero asset
    elif c.BOTslide_dyn_zero_type == 'static':
        tmp_dyn_zero_asset=c.BOTslide_dyn_asset
        tmp_bot_slide_dyn_zero = feature__slide_dyn__asset_convert_to_maker(c.feature__slide_dyn__zero_value)
        
    # check difference between zero point and actual maker balances
    # negative value means MAKER was sold,
    # positive value means MAKER was bought by opposite dxbot
    balance_diff_dirty = (d.balance_maker_total - tmp_bot_slide_dyn_zero)
    
    # processing no MAKER OP
    if balance_diff_dirty == 0:
        case_buy_sell='no-buy-no-ssel'
        tmp_step_final = 0
        tmp_step_multiplier = 0
        tmp_max_final = 0
        tmp_ignore_dirty = 0
        tmp_threshold_dirty = 0
    # MAKER BUY HAPPEN - total is more than zeropoint
    elif balance_diff_dirty > 0:
        case_buy_sell = 'buy'
        tmp_step_final = c.BOTslide_dyn_buy_step
        tmp_step_multiplier = c.BOTslide_dyn_buy_step_multiplier
        tmp_max_final = c.BOTslide_dyn_buy_max
        tmp_ignore_dirty = c.BOTslide_dyn_buy_ignore
        tmp_threshold_dirty = c.BOTslide_dyn_buy_threshold
    # MAKER SELL HAPPEN - total is less than zeropoint
    elif balance_diff_dirty < 0:
        case_buy_sell = 'sell'
        tmp_step_final = c.BOTslide_dyn_sell_step
        tmp_step_multiplier = c.BOTslide_dyn_sell_step_multiplier
        tmp_max_final = c.BOTslide_dyn_sell_max
        tmp_ignore_dirty = c.BOTslide_dyn_sell_ignore
        tmp_threshold_dirty = c.BOTslide_dyn_sell_threshold
            
    # processing relative
    if c.BOTslide_dyn_type == 'relative':
        tmp_dyn_asset=""
        tmp_ignore_final = tmp_ignore_dirty * d.balance_total
        tmp_threshold_final = tmp_threshold_dirty * d.balance_total
            
    # processing static 
    elif c.BOTslide_dyn_type == 'static':
        tmp_dyn_asset=c.BOTslide_dyn_asset
        tmp_ignore_final = feature__slide_dyn__asset_convert_to_maker(tmp_ignore_dirty)
        tmp_threshold_final = feature__slide_dyn__asset_convert_to_maker(tmp_threshold_dirty)
        
    # apply ignore zone
    balance_diff_final = abs(balance_diff_dirty)
    balance_diff_final = balance_diff_final - tmp_ignore_final
    balance_diff_final = max(0, balance_diff_final)
    
    # how many buy thresholds happen
    if tmp_threshold_final == 0:
        slide_dyn_step_num = 0
    else:
        slide_dyn_step_num = balance_diff_final / tmp_threshold_final
    
    # compute dynamic slide
    slide_dyn_final = float(0)
    slide_dyn_stages="none; "
    for i in range(int(slide_dyn_step_num)):
        slide_dyn_stages = slide_dyn_stages + str(i)+"# "+str(slide_dyn_final)+"+"+str(tmp_step_final)+" > "
        slide_dyn_final = slide_dyn_final + tmp_step_final
        tmp_step_final = tmp_step_final * tmp_step_multiplier
    print('>>>> dyn slide stacking: ' + slide_dyn_stages)
    
    # ~ slide_dyn_final = slide_dyn_step_num * tmp_step_final
    
    # apply dynamic slide maximum boundary, can be also negative, zero means unlimited
    if tmp_max_final > 0:
        slide_dyn_final = min(slide_dyn_final, tmp_max_final)
    elif tmp_max_final < 0:
        slide_dyn_final = max(slide_dyn_final, tmp_max_final)
    
    # ~ print('>>>> dynamic_slide >> <'+str(case_buy_sell)+'> zero type <')
    print('>>>> DYNAMIC_SLIDE >> <'+str(case_buy_sell)+'> dyn zero at <'+str(c.BOTslide_dyn_zero_type)+' '+str(c.BOTslide_dyn_zero)+'~'+str(c.feature__slide_dyn__zero_value)+' '+str(tmp_dyn_zero_asset)+'> ~~ <'+str(tmp_bot_slide_dyn_zero)+' '+str(c.BOTsellmarket)+'> maker actual balance <'+str(d.balance_maker_total)+'> maker balance diff <'+str(balance_diff_dirty)+'> maker ignore <'+str(tmp_ignore_dirty)+' '+str(tmp_dyn_asset)+' ~~ '+str(tmp_ignore_final)+' '+str(c.BOTsellmarket)+'> maker balance diff final <'+str(balance_diff_final)+'> slide type <'+str(c.BOTslide_dyn_type)+'> slide step threshold <'+str(tmp_threshold_dirty)+'>~<'+str(tmp_threshold_final)+'> slide dyn step num * size <'+str(slide_dyn_step_num)+'*'+str(tmp_step_final)+'> final dyn slide <'+str(slide_dyn_final)+'> at max <'+str(tmp_max_final)+'>')
    
    return slide_dyn_final 

def virtual_orders__get_status(order):
    return order.get("status",None)

def order__check_status(order, ifyes = None, ifnot = None):
    if (order is not None):
        if (ifyes is None) or (order.get("status", None) in ifyes):
            if (ifnot is None) or order.get("status", None) not in ifnot:
                return True
    return False

def virtual_orders__update_status(order, status, ifyes = None, ifnot = None):
    if (ifyes is None) or (order.get("status", None) in ifyes):
        if ifnot is None or order.get("status", None) not in ifnot:
            order["status"] = status
            return True
    return False
    
# virtual-orders cancel, clear and wait for process done
def virtual_orders__clear_all():
    global c, s, d
    print('>>>> Clearing all session virtual orders and waiting for be done...')
    
    # mark all virtual orders as cleared
    for i in range(s.ordersvirtualmax):
        virtual_orders__update_status(d.ordersvirtual[i], s.status_list__clear, ifnot = [s.status_list__clear])
    
    virtual_orders__cancel_all()

# virtual-orders cancel and wait for process done
def virtual_orders__cancel_all():
    global c, s, d
    print('>>>> Canceling all session virtual orders and waiting for be done...')
    
    # loop while some orders are opened otherwise break while, do not cancel orders which are in progress
    while 1:
        clearing = int(0)
        ordersopen = dxbottools.getallmyordersbymarket(c.BOTsellmarket,c.BOTbuymarket)
        # loop all previously opened virtual orders and try clearing opened
        for i in range(s.ordersvirtualmax):
            # try to find match between session and existing orders and clear it
            for z in ordersopen:
                # clear orders which are new or opened and match by id with virtual order
                if (z['status'] == s.status_list__open or z['status'] == s.status_list__new) and z['id'] == d.ordersvirtual[i]['id']:
                    print('>>>> Clearing virtual order index <{0}> id <{1}> and waiting for be done...'.format(i, z['id']))
                    dxbottools.rpc_connection.dxCancelOrder(z['id'])
                    clearing += 1
                    break
        if clearing > 0:
            print('>>>> Sleeping waiting for old orders to be cleared')
            time.sleep(c.BOTdelayinternal)
        else:
            break
        
    # wait for orders which are in progress state (TODO)
    
# search for item that contains named item that contains specific data
def lookup_universal(lookup_data, lookup_name, lookup_id):
    # find my orders, returns order if orderid passed is inside myorders
    for zz in lookup_data:
        if zz[lookup_name] == lookup_id:
            return zz

def lookup_order_id_2(orderid, myorders):
    return lookup_universal(myorders, 'id', orderid)

# check all virtual-orders if there is some finished  
def virtual_orders__check_status_update_status():
    global c, s, d
    print('>>>> Checking all session virtual orders how many orders finished and last time when order was finished...')
    
    ordersopen = dxbottools.getallmyordersbymarket(c.BOTsellmarket,c.BOTbuymarket)
    for i in range(s.ordersvirtualmax):
        
        # checking all virtual orders that has ID assigned, so is/was active
        if d.ordersvirtual[i]['id'] != 0:
            
            # try to match virtual-order with order by ID
            order = lookup_order_id_2(d.ordersvirtual[i]['id'], ordersopen)
            
            #debug log
            print('>>>> Order <{}> sell maker <{}> amount <{}> to buy taker <{}> amount <{}> status original <{}> to actual <{}> id <{}> market price <{}> order price <{}> description <{}>'
            .format(d.ordersvirtual[i]['vid'], d.ordersvirtual[i]['maker'], d.ordersvirtual[i]['maker_size'], d.ordersvirtual[i]['taker'], d.ordersvirtual[i]['taker_size'], 
            d.ordersvirtual[i]['status'], (order['status'] if (order is not None) else 'no status'), d.ordersvirtual[i]['id'], d.ordersvirtual[i]['market_price'], d.ordersvirtual[i]['order_price'], d.ordersvirtual[i]['name'] ))
            
            # if virtual order is clear BUT order is still in progress, skip this order, because is not finished yet
            if order__check_status(d.ordersvirtual[i], ifyes = [s.status_list__clear]):
                if order__check_status(order, ifyes = [s.status_list__l_in_progress]) == True:
                    print('virtual order <{}> is in progress... skipping...'.format(i))
                    continue
            
            # if virtual order previous status was not finished or clear and now finished is or was taken by takerbot, count this order in finished number
            if d.ordersvirtual[i]['status'] != s.status_list__finished:
                if (order is not None) and order['status'] == s.status_list__finished:
                    d.ordersfinished += 1
                    d.ordersfinishedtime = time.time()
                elif feature__takerbot__virtual_order_was_taken_get(d.ordersvirtual[i]) == True:
                    d.ordersfinished += 1
                    d.ordersfinishedtime = time.time()
            
            # update "reopen finished feature" data
            events_wait_reopenfinished_update(d.ordersvirtual[i], order, feature__takerbot__virtual_order_was_taken_get(d.ordersvirtual[i]))
            
            # finally update virtual order status from previous to actual
            
            # if order was taken by takerbot clear virtual order
            if feature__takerbot__virtual_order_was_taken_get(d.ordersvirtual[i]) == True:
                virtual_orders__update_status(d.ordersvirtual[i], s.status_list__clear, ifnot = [s.status_list__clear])
                feature__takerbot__virtual_order_was_taken_set(d.ordersvirtual[i], False)
            # if order does not exist clear virtual order
            elif order is None:
                virtual_orders__update_status(d.ordersvirtual[i], s.status_list__clear, ifnot = [s.status_list__clear])
            # else update status of virtual order to existing order status
            else:
                virtual_orders__update_status(d.ordersvirtual[i], order['status'], ifnot = [s.status_list__clear])

# update information needed by reopen after finish feature to know how many orders are opened and how many finished
def events_wait_reopenfinished_update(virtual_order, actual_order, finished_by_takerbot):
    global c, s, d
    
    # if previous status was not open and now open is, count this order in opened number
    if virtual_order['status'] not in s.orders_pending_to_reopen_opened_statuses and (actual_order is not None) and actual_order['status'] in s.orders_pending_to_reopen_opened_statuses:
        d.orders_pending_to_reopen_opened += 1
        if d.orders_pending_to_reopen_opened > c.BOTmaxopenorders:
            print('!!!! internal BUG Detected. DEBUG orders opened {0} orders finished {1} last time order finished {2}'.format(d.orders_pending_to_reopen_opened, d.orders_pending_to_reopen_finished, d.orders_pending_to_reopen_finished_time))
            sys.exit(1)
        
    # if previous status was open and now is not open, do not count this order in opened number
    if virtual_order['status'] in s.orders_pending_to_reopen_opened_statuses and ((actual_order is None) or actual_order['status'] not in s.orders_pending_to_reopen_opened_statuses):
        d.orders_pending_to_reopen_opened -= 1
        if d.orders_pending_to_reopen_opened < 0:
            print('!!!! internal BUG Detected. DEBUG orders opened {0} orders finished {1} last time order finished {2}'.format(d.orders_pending_to_reopen_opened, d.orders_pending_to_reopen_finished, d.orders_pending_to_reopen_finished_time))
            sys.exit(1)
        
    # if previous status was not finished and now finished is, count this order in finished number
    if virtual_order['status'] != s.status_list__finished and (((actual_order is not None) and actual_order['status'] == s.status_list__finished) or finished_by_takerbot == True):
        d.orders_pending_to_reopen_finished += 1
        d.orders_pending_to_reopen_finished_time = time.time()
    
    # ~ print('%%%% DEBUG orders opened {0} orders finished {1} last time order finished {2}'.format(d.orders_pending_to_reopen_opened, d.orders_pending_to_reopen_finished, d.orders_pending_to_reopen_finished_time))

# create order and update also corresponding virtual-order
def virtual_orders__create_one(order_id, order_name, price, slide, stageredslide, slide_dyn, sell_amount, sell_amount_min):
    global c, s, d
    makermarketpriceslide = float(price) * (slide + stageredslide + slide_dyn)
    
    # limit precision to 6 digits
    sell_amount = '%.6f' % sell_amount
    
    buyamount = (float(sell_amount) * float(makermarketpriceslide)) 
    
    # limit precision to 6 digits
    buyamount = '%.6f' % buyamount
    
    print('>>>> Placing partial<{}> Order id <{}> name <{}> {}->{} at price {} slide {} staggered-slide {} dynamic-slide {} final slide {} final-price {} to sell {} n buy {}'
          .format(c.BOTpartial_orders, order_id, order_name, c.BOTsellmarket, c.BOTbuymarket, price, slide, stageredslide, slide_dyn, (slide + stageredslide + slide_dyn), makermarketpriceslide, sell_amount, buyamount))
    
    if c.BOTpartial_orders is False:
        try:
            results = {}
            results = dxbottools.makeorder(c.BOTsellmarket, str(sell_amount), c.BOTmakeraddress, c.BOTbuymarket, str(buyamount), c.BOTtakeraddress, use_all_funds = not c.BOTaddress_funds_only)
            print('>>>> Exact Order placed - id: <{}>, maker_size: <{}>, taker_size: <{}>'.format(results['id'], results['maker_size'], results['taker_size']))
            # ~ logging.info('Order placed - id: {0}, maker_size: {1}, taker_size: {2}'.format(results['id'], results['maker_size'], results['taker_size']))
        except Exception as err:
            print('exact ERROR: %s' % err)
    else:
        try:
            results = {}
            results = dxbottools.make_partial_order(c.BOTsellmarket, str(sell_amount), c.BOTmakeraddress, c.BOTbuymarket, str(buyamount), c.BOTtakeraddress, sell_amount_min, repost = False, use_all_funds = not c.BOTaddress_funds_only, auto_split = False)
            print('>>>> Partial Order placed - id: <{}>, maker_size: <{}>, taker_size: <{}>'.format(results['id'], results['maker_size'], results['taker_size']))
            # ~ logging.info('Order placed - id: {0}, maker_size: {1}, taker_size: {2}'.format(results['id'], results['maker_size'], results['taker_size']))
        except Exception as err:
            print('partial ERROR: %s' % err)
    
    if results:
        d.ordersvirtual[order_id] = results
        d.ordersvirtual[order_id]['vid'] = order_id
        virtual_orders__update_status(d.ordersvirtual[order_id], s.status_list__creating)
        d.ordersvirtual[order_id]['name'] = order_name
        d.ordersvirtual[order_id]['market_price'] = price
        d.ordersvirtual[order_id]['order_price'] = makermarketpriceslide
        d.ordersvirtual[order_id]['maker_size_min'] = sell_amount_min

# recompute order tx fee (TODO)
def sell_amount_txfee_recompute(sell_amount):
    global c, s, d
    txfee = sell_amount * 0.007
    return txfee

# recompute amount available minus reserved for save and fees, also apply max and min
def balance_available_to_sell_recompute(sell_amount_max=0, sell_amount_min=0):
    global c, s, d
    
    # get available balance without fee
    sell_amount = d.balance_maker_available
    sell_amount_tmp = sell_amount
    sell_amount_txfee = sell_amount_txfee_recompute(sell_amount)
    sell_amount = sell_amount - sell_amount_txfee
    sell_amount = max(sell_amount, 0)
    print('>>>> balance txfee {} apply, sell amount original {} new {}'.format(sell_amount_txfee, sell_amount_tmp, sell_amount))
    
    #apply BOTbalance_save_number if enabled
    if c.BOTbalance_save_number != 0:
        balance_save_size = feature__balance_save_asset__convert_to_maker(c.BOTbalance_save_number)
        sell_amount_tmp = sell_amount
        sell_amount = min(sell_amount, d.balance_maker_available - sell_amount_txfee - balance_save_size)
        sell_amount = max(sell_amount, 0)
        print('>>>> balance_save_number {} apply, sell amount original {} new {}'.format(balance_save_size, sell_amount_tmp, sell_amount))
        
    #apply BOTbalance_save_percent if enabled
    if c.BOTbalance_save_percent != 0:
        sell_amount_tmp = sell_amount
        sell_amount = min(sell_amount, d.balance_maker_available - sell_amount_txfee - (c.BOTbalance_save_percent * d.balance_maker_total))
        sell_amount = max(sell_amount, 0)
        print('>>>> balance_save_percent {} apply, sell amount original {} new {}'.format(c.BOTbalance_save_percent, sell_amount_tmp, sell_amount))
    
    # apply maximum amount if enabled
    if sell_amount_max != 0:
        sell_amount_tmp = sell_amount
        sell_amount = min(sell_amount_max, sell_amount)
        print('>>>> sell amount max {} apply, sell amount original {} new {}'.format(sell_amount_max, sell_amount_tmp, sell_amount))
    
    # apply minimum amount if enabled otherwise try to apply maximum as exact amount if enabled
    if sell_amount_min != 0:
        sell_amount_tmp = sell_amount
        if sell_amount < sell_amount_min:
            sell_amount = 0
        print('>>>> sell amount min {} apply, sell amount original {} new {}'.format(sell_amount_min, sell_amount_tmp, sell_amount))
    elif sell_amount_max != 0:
        sell_amount_tmp = sell_amount
        if sell_amount_max != sell_amount:
            sell_amount = 0
        print('>>>> strict sell amount max {} apply, sell amount original {} new {}'.format(sell_amount_max, sell_amount_tmp, sell_amount))
    
    # ~ if c.BOTmarking != 0:
        # ~ if sell_amount != 0:
            # ~ sell_amount_tmp = sell_amount
            # ~ before, after = str(sell_amount_tmp).split('.')
            # ~ sell_amount_tmp = before + "." + str(int(after))
            # ~ if sell_amount > c.BOTmarking:
    
    return sell_amount

# one time needed prepare process before switching into second internal loop 
def virtual_orders__prepare_once():
    global c, s, d
    update_balances()
    
    while feature__maker_price__pricing_update() == 0:
        print('#### Pricing not available... waiting to restore...')
        time.sleep(c.BOTdelayinternalerror)
    
    d.reset_on_price_change_start = d.feature__maker_price__value_current_used
    
    # how many orders finished reset
    d.ordersfinished = 0
    
    d.time_start_reset_orders = time.time()
    d.ordersfinishedtime = 0
    
    d.time_start_update_pricing = time.time()
    
    events_wait_reopenfinished_reinit()

# every time main event loop pass, some dynamics should be recomputed
def virtual_orders__prepare_recheck():
    global c, s, d
    
    feature__flush_co__check(dxbottools)
    
    # every loop of creating or checking orders maker balance can be changed...
    update_balances()
    
    # every loop of creating or checking orders maker price can be changed...
    while True:
        if feature__maker_price__pricing_update() != 0:
            break
        print('#### Pricing main not available... waiting to restore...')
        time.sleep(c.BOTdelayinternalerror)
    
    d.feature__slide_dyn__value = feature__slide_dyn__get_dyn_slide()
    
    if c.BOTbalance_save_asset_track is True:
        while True:
            if feature__balance_save_asset__pricing_update() != 0:
                break
            print('#### Pricing of balance save asset not available... waiting to restore...')
            time.sleep(c.BOTdelayinternalerror)
    
    while True:
        if feature__sell_size_asset__pricing_update() != 0:
            break
        print('#### Pricing of sell size asset not available... waiting to restore...')
        time.sleep(c.BOTdelayinternalerror)
    
    while True:
        if feature__boundary__pricing_update() != 0:
            break
        print('#### Pricing boundaries not available... waiting to restore...')
        time.sleep(c.BOTdelayinternalerror)
    
    events_wait_reopenfinished_reset_detect()
    
    # get open orders, match them with virtual orders, and check how many finished
    virtual_orders__check_status_update_status()

#
def feature__boundary__get_max_relative():
    global c, s, d
    
    maximum = 0
    
    if c.BOTboundary_max_relative != 0:
        if c.BOTboundary_asset_track is False:
            maximum = d.feature__boundary__price_maker_initial_center * c.BOTboundary_max_relative
        else:
            maximum = (d.feature__boundary__price_maker_initial_center_relative * d.feature__boundary__price_relative_current) * c.BOTboundary_max_relative
        
    return maximum

#
def feature__boundary__get_max_static():
    global c, s, d
    
    maximum = float(0)
    
    if c.BOTboundary_max_static != 0:
        if c.BOTboundary_asset_track is False:
            maximum = c.BOTboundary_max_static * d.feature__boundary__price_relative_initial
        else:
            maximum = c.BOTboundary_max_static * d.feature__boundary__price_relative_current
        
    return maximum

#
def feature__boundary__get_max():
    global c, s, d
    
    maximum = feature__boundary__get_max_relative()
    
    if maximum == 0:
        maximum = feature__boundary__get_max_static()
    
    return maximum

#
def feature__boundary__get_min_relative():
    global c, s, d
    
    minimum = 0
    
    if c.BOTboundary_min_relative != 0:
        if c.BOTboundary_asset_track is False:
            minimum = d.feature__boundary__price_maker_initial_center * c.BOTboundary_min_relative
        else:
            minimum = (d.feature__boundary__price_maker_initial_center_relative * d.feature__boundary__price_relative_current) * c.BOTboundary_min_relative
        
    return minimum

#
def feature__boundary__get_min_static():
    global c, s, d
    
    minimum = 0
    
    if c.BOTboundary_min_static != 0:
        if c.BOTboundary_asset_track is False:
            minimum = c.BOTboundary_min_static * d.feature__boundary__price_relative_initial
        else:
            minimum = c.BOTboundary_min_static * d.feature__boundary__price_relative_current
            
    return minimum

#
def feature__boundary__get_min():
    global c, s, d
    
    minimum = feature__boundary__get_min_relative()
    
    if minimum == 0:
        minimum = feature__boundary__get_min_static()
    
    return minimum

# recompute and get price with boundary limits
def feature__boundary__recompute_price():
    global c, s, d
    
    price = d.feature__maker_price__value_current_used
    
    maximum = feature__boundary__get_max()
    minimum = feature__boundary__get_min()
    
    if maximum != 0:
        price = min(price, maximum)
    
    if minimum != 0:
        price = max(price, minimum)
    
    return price

# function to check if price is not out of maximum boundary 
def feature__boundary__hit_max():
    global c, s, d
    
    # check if relative max boundary is configured
    if c.BOTboundary_max_relative != 0:
        # wait if out of price relative boundary happen
        maximum = feature__boundary__get_max_relative()
        if maximum < d.feature__maker_price__value_current_used:
            print('>>>> Maximum relative boundary <{}> hit <{}> / <{}>'.format(c.BOTboundary_max_relative, maximum, d.feature__maker_price__value_current_used))
            return True
            
    # check if static max boundary is configured
    if c.BOTboundary_max_static != 0:
        # wait if out of price static boundary happen
        maximum = feature__boundary__get_max_static()
        if maximum < d.feature__maker_price__value_current_used:
            print('>>>> Maximum static boundary <{}> hit <{}> / <{}>'.format(c.BOTboundary_max_static, maximum, d.feature__maker_price__value_current_used))
            return True
    
    return False

# function to check if price is not out of minimum boundary 
def feature__boundary__hit_min():
    global c, s, d
    
    # check if relative min boundary is configured
    if c.BOTboundary_min_relative != 0:
        # wait if out of price relative boundary happen
        minimum = feature__boundary__get_min_relative()
        if minimum > d.feature__maker_price__value_current_used:
            print('>>>> Minimum relative boundary <{}> hit <{}> / <{}>'.format(c.BOTboundary_min_relative, minimum, d.feature__maker_price__value_current_used))
            return True
    
    # check if static min boundary is configured
    if c.BOTboundary_min_static != 0:
        # wait if out of price static boundary happen
        minimum = feature__boundary__get_min_static()
        if minimum > d.feature__maker_price__value_current_used:
            print('>>>> Minimum static boundary <{}> hit <{}> / <{}>'.format(c.BOTboundary_min_static, minimum, d.feature__maker_price__value_current_used))
            return True
    
    return False

# function to check if price is not out of maximum boundary 
def feature__boundary__hit_max_exit():
    global c, s, d
    
    if not c.BOTboundary_max_noexit:
        if feature__boundary__hit_max() == True:
            if not c.BOTboundary_max_nocancel:
                virtual_orders__cancel_all()
            return True
            
    return False

# function to check if price is not out of minimum boundary 
def feature__boundary__hit_min_exit():
    global c, s, d
    
    if not c.BOTboundary_min_noexit:
        if feature__boundary__hit_min() == True:
            if not c.BOTboundary_min_nocancel:
                virtual_orders__cancel_all()
            return True
    
    return False

# function to check if price is not out of maximum boundary 
def feature__boundary__hit_max_noexit_cancel():
    global c, s, d
    
    if c.BOTboundary_max_noexit:
        if not c.BOTboundary_max_nocancel:
            if feature__boundary__hit_max() == True:
                virtual_orders__cancel_all()
                return True
            
    return False

# function to check if price is not out of minimum boundary 
def feature__boundary__hit_min_noexit_cancel():
    global c, s, d
    
    if c.BOTboundary_min_noexit:
        if not c.BOTboundary_min_nocancel:
            if feature__boundary__hit_min() == True:
                virtual_orders__cancel_all()
                return True
    
    return False

# function to scan all events that makes bot to exit
def events_exit_bot():
    global c, s, d
    ret = False
    
    print('checking for exit bot events')
    
    # detect and handle max boundary exit event
    if feature__boundary__hit_max_exit() == True:
        ret = True
    
    # detect and handle min boundary exit event
    if feature__boundary__hit_min_exit() == True:
        ret = True
    
    return ret
    
# function to scan all events that makes bot to reset orders
def events_reset_orders():
    global c, s, d
    
    print('checking for reset order events')
    
    # if reset on price change positive is set and price has been changed, break and reset orders
    if c.BOTresetonpricechangepositive != 0 and d.feature__maker_price__value_current_used >= (d.reset_on_price_change_start * (1 + c.BOTresetonpricechangepositive)):
        print('>>>> Reset on positive price change {0}% has been reached: price stored / actual {1} / {2}, going to order reset now...'.format(c.BOTresetonpricechangepositive, d.reset_on_price_change_start, d.feature__maker_price__value_current_used))
        return True
        
    # if reset on price change negative is set and price has been changed, break and reset orders
    if c.BOTresetonpricechangenegative != 0 and d.feature__maker_price__value_current_used <= (d.reset_on_price_change_start * (1 - c.BOTresetonpricechangenegative)):
        print('>>>> Reset on negative price change {0}% has been reached: price stored / actual {1} / {2}, going to order reset now...'.format(c.BOTresetonpricechangenegative, d.reset_on_price_change_start, d.feature__maker_price__value_current_used))
        return True
    
    # if reset after delay is set and reached break and reset orders
    if c.BOTresetafterdelay != 0 and (time.time() - d.time_start_reset_orders) > c.BOTresetafterdelay:
        print('>>>> Maximum orders lifetime {0} / {1} has been reached, going to order reset now...'.format((time.time() - d.time_start_reset_orders), c.BOTresetafterdelay))
        return True
        
    # if reset after order finish number is set and already reached break and reset orders
    if c.BOTresetafterorderfinishnumber != 0 and d.ordersfinished >= c.BOTresetafterorderfinishnumber:
        print('>>>> Maximum orders finished {0} / {1} has been reached, going to order reset...'.format(d.ordersfinished, c.BOTresetafterorderfinishnumber))
        return True
        
    # if reset after order finish delay is set and already reached break and reset orders
    if c.BOTresetafterorderfinishdelay != 0 and d.ordersfinished != 0 and d.ordersfinishedtime != 0 and (time.time() - d.ordersfinishedtime) > c.BOTresetafterorderfinishdelay:
        print('>>>> Maximum orders lifetime {0} / {1} after order finished has been reached, going to order reset now...'.format((time.time() - d.ordersfinishedtime), c.BOTresetafterorderfinishdelay))
        return True
        
    return False

# automatically detect passed wait events so reset data
def events_wait_reopenfinished_reset_detect():
    global c, s, d
    
    if events_wait_reopenfinished_check_num_silent() == "reached" or events_wait_reopenfinished_check_delay_silent() == "reached":
        print(">>>> reopen after finished reseting data...")
        d.orders_pending_to_reopen_finished = 0
        d.orders_pending_to_reopen_finished_time = 0;

# function to check bot have to wait, finished orders will be reopened after specific number of filled orders
def events_wait_reopenfinished_check_num_silent():
    global c, s, d
    
    # check if finished num is configured
    if c.BOTreopenfinishednum == 0:
        return "disabled"
    
    # this feature is activated only if at least one order has finished
    if d.orders_pending_to_reopen_finished > 0:
        # this feature is activated only if there is enough finished+open orders
        if (d.orders_pending_to_reopen_finished + d.orders_pending_to_reopen_opened) >= c.BOTreopenfinishednum:
            # wait if finished number has not been reached
            if d.orders_pending_to_reopen_finished < c.BOTreopenfinishednum:
                return "wait"
            else:
                return "reached"
                
    return "not ready"

# function to check bot have to wait, finished orders will be reopened after specific number of filled orders
def events_wait_reopenfinished_check_num():
    global c, s, d
    ret = events_wait_reopenfinished_check_num_silent()
    if ret == "wait":
        print('%%%% DEBUG Reopen finished order num {0} / {1} not reached, waiting...'.format(d.orders_pending_to_reopen_finished, c.BOTreopenfinishednum))
    
    return ret
    
# function to check bot have to wait, finished orders will be reopened after specific delay
def events_wait_reopenfinished_check_delay_silent():
    global c, s, d
    
    # check if finished delay is configured
    if c.BOTreopenfinisheddelay == 0:
        return "disabled"
    
    # this feature is activated only if at least one order has finished
    if d.orders_pending_to_reopen_finished_time != 0:
        # wait if we already have some finished order time and delay not reached
        if (time.time() - d.orders_pending_to_reopen_finished_time) < c.BOTreopenfinisheddelay:
            return "wait"
        else:
            return "reached"
    
    return "not ready"

# function to check bot have to wait, finished orders will be reopened after specific delay
def events_wait_reopenfinished_check_delay():
    global c, s, d
    ret = events_wait_reopenfinished_check_delay_silent()
    if ret == "wait":
        print('%%%% DEBUG Reopen finished orders delay {0} / {1} not reached, waiting...'.format((time.time() - d.orders_pending_to_reopen_finished_time), c.BOTreopenfinisheddelay))
        
    return ret

# main reopen fisnihed delay/num detection function
def events_wait_reopenfinished_check():
    global c, s, d
    
    # check reopen after finished number or delay detection
    ret_delay = events_wait_reopenfinished_check_delay()
    ret_num = events_wait_reopenfinished_check_num()
    if ret_delay == "wait" and ret_num == "wait": # timeout did not happen but number of finished orders has been reached
        return True
    elif ret_delay == "disabled" and ret_num == "wait":
        return True
    elif ret_delay == "wait" and ret_num == "disabled":
        return True

# function to scan all events that makes bot wait
def events_wait():
    global c, s, d
    ret = False
    
    print('checking for wait events')
    
    # wait if there is not enough balance to place order and pay fee
    if balance_available_to_sell_recompute() == 0:
        ret = True
    
    # check reopen after finished number or delay detection
    if events_wait_reopenfinished_check() == True:
        ret = True
    
    # detect and handle max boundary event
    if feature__boundary__hit_max_noexit_cancel() == True:
        ret = True
    
    # detect and handle min boundary event
    if feature__boundary__hit_min_noexit_cancel() == True:
        ret = True
    
    return ret

# function to compute and return amount of maker to be sold
def sell_amount_recompute(sell_start, sell_end, order_num_all, order_num_actual, sell_type):
    global c, s, d
    
    sell_amount = float(0)
    
    # sell amount old style random
    if c.BOTsellrandom:
        sell_min = min(sell_start, sell_end)
        sell_max = max(sell_start, sell_end)
        sell_amount = random.uniform(sell_min, sell_max)
    
    # sell amount staggered
    else:
        # linear staggered orders size distribution
        if sell_type == 0:
            sell_type_res = order_num_actual / order_num_all
        
        # exponential staggered order size distribution
        elif sell_type > 0:
            sell_type_res = (order_num_actual / order_num_all)**(1-(sell_type))
        
        # logarithmic staggered order size distribution
        elif sell_type < 0:
            # ~ sell_type_res = (order_num_actual / order_num_all)**(1-(10*sell_type))
            sell_type_res = (order_num_actual / order_num_all)**((float(100)**(sell_type*-1))+(sell_type*4.4))
        
        # sell amount = amount starting point + (variable amount * intensity) 
        sell_amount = sell_start + ((sell_end - sell_start) * sell_type_res)
        # ~ sell_amount = sell_start + (( (sell_end - sell_start) / max((order_num_all-1),1) )*order_num_actual)

    # sell amount limit to 6 decimal numbers
    sell_amount = float('%.6f' % sell_amount)
    
    return sell_amount

# function to loop all virtual orders and recreate em if needed
def virtual_orders__handle():
    global c, s, d
    
    print('checking for virtual orders to handle')
    
    pumpdump_order_cleared = False
    
    # loop all virtual orders and try to create em
    
    # staggered orders handling
    for i in range(s.ordersvirtualmax - int(c.BOTslidepumpenabled)):
        if d.ordersvirtual[i]['status'] in s.reopenstatuses:
            
            # as we found not virtual order to reopen, first it is cancel pump dump order needed
            if c.BOTslidepumpenabled is True and pumpdump_order_cleared is False and d.ordersvirtual[s.ordersvirtualmax-1]['status'] in s.status_list__with_reserved_balance:
                pumpdump_order_cleared = True
                
            
            update_balances()
            
            # sse sell size asset
            # compute dynamic order size range, apply <sell_type> linear/log/exp on maximum amount by order number distribution
            sell_amount_max_sse = sell_amount_recompute(c.BOTsellstart, c.BOTsellend, s.ordersvirtualmax - int(c.BOTslidepumpenabled), i, c.BOTsell_type)
            sell_amount_min_sse = sell_amount_recompute(c.BOTsellstartmin, c.BOTsellendmin, s.ordersvirtualmax - int(c.BOTslidepumpenabled), i, c.BOTsell_type)
            
            # convert sell size in sell size asset to maker asset
            sell_amount_max = sell_amount_max_sse * d.feature__sell_size_asset__price
            sell_amount_min = sell_amount_min_sse * d.feature__sell_size_asset__price
            
            # recompute sell amount by available balance, other limit conditions
            sell_amount = balance_available_to_sell_recompute(sell_amount_max, sell_amount_min)
            
            # convert final amount to sell to sell size asset amount
            sell_amount_sse = sell_amount / d.feature__sell_size_asset__price
            
            # recompute price by configured boundaries
            price_maker_with_boundaries = feature__boundary__recompute_price()
            
            print('>>>> Order maker size <{}/{} {}~{} min {}~{} final {}~{}>'.format(c.BOTsellmarket, c.BOTsell_size_asset, sell_amount_max, sell_amount_max_sse, sell_amount_min, sell_amount_min_sse, sell_amount, sell_amount_sse))
            
            if sell_amount == 0:
                # do not create next order on first 0 amount hit, so if first order is not created, also next not created
                if c.BOTmake_next_on_hit is True:
                    continue
                else:
                    break
                
            # first order is min slide
            if i == 0:
                order_name = 'first staggered order with min-slide'
            # last order is max slide
            elif i == (s.ordersvirtualmax - int(c.BOTslidepumpenabled) -1):
                order_name = 'last staggered order with max-slide'
            # any other orders between min and max slide
            else:
                order_name = 'middle staggered order with computed-slide'
            
            # compute staggered orders slides
            staggeredslide = ((c.BOTslideend - c.BOTslidestart) / max((s.ordersvirtualmax -1 -int(c.BOTslidepumpenabled)),1 ))*i
            
            virtual_orders__create_one(i, order_name, price_maker_with_boundaries, c.BOTslidestart, staggeredslide, d.feature__slide_dyn__value, sell_amount, sell_amount_min)
            time.sleep(c.BOTdelayinternal)
    
    # special pump/dump order handling
    if c.BOTslidepumpenabled is True and d.ordersvirtual[s.ordersvirtualmax-1]['status'] in s.reopenstatuses:
        update_balances()
        
        # convert sell size in sell size asset to maker asset
        sell_amount_pumpdump = c.BOTpumpamount * d.feature__sell_size_asset__price
        
        # recompute sell amount by available balance, other limit conditions
        sell_amount = balance_available_to_sell_recompute(sell_amount_pumpdump, sell_amount_min)
        
        if sell_amount > 0:
            virtual_orders__create_one(s.ordersvirtualmax-1, 'pump/dump', price_maker_with_boundaries, c.BOTslidemax, c.BOTslidepump, d.feature__slide_dyn__value, sell_amount, sell_amount_min)
            
# check if virtual order was taken by takerbot
def feature__takerbot__virtual_order_was_taken_get(virtual_order):
    return virtual_order.get('takerbot', False)

# set flag that order was taker by takerbot
def feature__takerbot__virtual_order_was_taken_set(virtual_order, true_false):
    virtual_order['takerbot'] = true_false
    
#by adding takerbot feature:
#   counting reset after finish functionality is affected
#   counting reset after timeout functionality is affected
#   counting reopen finished orders after number of timeout functionality is affected
#Solution #1(prob TODO) is to reset all orders after takerbot success action, but if price action happen before it can cause bot loss.
#Solution #2(added) is to update above 4 features to know takerbot did action
#
# function to loop all already created orders, find match with thirty party created orders and accept em.
def feature__takerbot__run():
    global c, s, d
    
    print('checking for takerbot actions')
    
    ret = False
    
    # run takerbot process if feature is enabled
    if c.BOTtakerbot != 0:
        
        # turn on takerbot timer first
        if d.feature__takerbot__time_start == 0:
            d.feature__takerbot__time_start = time.time()
        
        # run takerbot on timer
        elif (time.time() - d.feature__takerbot__time_start) > c.BOTtakerbot:
            
            # get market order book type 3 format results
            fullbook = dxbottools.rpc_connection.dxGetOrderBook(3, c.BOTsellmarket, c.BOTbuymarket)
            bidlist = list(fullbook.get('bids', list([])))
            
            # convert market order book from list to dictionary format
            keys = [ 'order_price', 'size' , 'order_id' ]
            orders_market = [dict(zip(keys, bidlist_item)) for bidlist_item in bidlist ]
            
            # simulation of market order >> testing >> debug
            # ~ orders_market.append({'order_price': '0.029277', 'size': '1.98', 'order_id': '123456789'})
            
            # convert strings to floats
            for i in range(len(orders_market)):
                orders_market[i]['order_price'] = float(orders_market[i]['order_price'])
                orders_market[i]['size'] = float(orders_market[i]['size'])
            
            # filter only opened virtual orders
            orders_virtual_sorted = list()
            for i in range(len(d.ordersvirtual)):
                if d.ordersvirtual[i].get('order_price', None) is not None:
                    orders_virtual_sorted.append(d.ordersvirtual[i])
            
            # convert strings to floats
            for i in range(len(orders_virtual_sorted)):
                orders_virtual_sorted[i]['maker_size_min'] = float(orders_virtual_sorted[i]['maker_size_min'])
                orders_virtual_sorted[i]['maker_size'] = float(orders_virtual_sorted[i]['maker_size'])
            
            # sort market order book and my order book by price
            
            # market orders sorting from higher price to catch best orders.
            orders_market_sorted = sorted(orders_market, key=lambda order: order['order_price'], reverse=True)
            # my order sorting from lowest price to catch best difference.
            orders_virtual_sorted = sorted(orders_virtual_sorted, key=lambda order: order['order_price'], reverse=False)
            
            # simulation >> testing >> debug
            # ~ print('\n\norders_market_sorted: <{}>'.format(orders_market_sorted))
            # ~ print('\n\norders_virtual_sorted: <{}>'.format(orders_virtual_sorted))
            
            # takerbot process. Something like limit orders layer on top of blockdx atomic swap order book.
            
            # go all market open orders sorted by best price
            err = None
            for i in range(len(orders_market_sorted)):
                print('\n *** checking order_market_sorted no <{}> <{}>\n'.format(i, orders_market_sorted[i]))
                
                maker_sum = float(0)
                order_candidates = list()
                
                # per every market order, go all bot open orders, sum up bot orders to match market order size
                for j in range(len(orders_virtual_sorted)):
                    print('\n *** *** checking order_virtual_sorted no <{}> <{}>\n'.format(j, orders_virtual_sorted[j]))
                    
                    # if maker order price is higher or equal by bot opened order
                    if orders_market_sorted[i]['order_price'] >= orders_virtual_sorted[j]['order_price']:
                        
                        # if orders which status is usable to for takerbot like new/open
                        if orders_virtual_sorted[j]['status'] in s.feature__takerbot__list_of_usable_statuses:
                            
                            # count those orders in acceptable list, if market order size is at least virtual order minimum acceptable size
                            # or if virtual order min size is not set, at least virtual order size
                            if (orders_virtual_sorted[j]['maker_size_min'] != 0 and orders_market_sorted[i]['size'] >= orders_virtual_sorted[j]['maker_size_min']) or (orders_market_sorted[i]['size'] >= orders_virtual_sorted[j]['maker_size']):
                                print('\n *** *** *** order_virtual_sorted no <{}> passed requirements <{}>\n'.format(j, orders_virtual_sorted[j]))
                                
                                # add virtual order to list of candidates for takerbot to be canceled and market order accepted
                                order_candidates.append(orders_virtual_sorted[j])
                                
                                # increase available maker amount to sell
                                maker_sum = maker_sum + float(orders_virtual_sorted[j]['maker_size'])
                                
                                # if there is enough balance and order meet requirements, try to handle situation and take order
                                if maker_sum >= float(orders_market_sorted[i]['size']):
                                    print('\n *** *** *** *** summary of makers sizes <{}> is enough for <{}>\n'.format(maker_sum, orders_market_sorted[i]['size']))
                                    # try to cancel bot orders which are dependant on takerbot action
                                    for k in range(len(order_candidates)):
                                        ret_cancelorder = dxbottools.rpc_connection.dxCancelOrder(order_candidates[k]['id'])
                                        err = ret_cancelorder.get('error', None)
                                        # in case of cancel order process error we must exit whole takerbot process and let bot recreate orders
                                        if err is not None:
                                            print('\n *** *** *** *** *** cancel virtual order candidate <{}> failed <{}> \n'.format(k, err))
                                            return ret
                                    
                                    #try to accept order
                                    ret_takeorder = dxbottools.takeorder(orders_market_sorted[i]['order_id'], c.BOTtakeraddress, c.BOTmakeraddress)
                                    err = ret_takeorder.get('error', None)
                                    # in case of take order process error we must exit whole takerbot process and let bot recreate orders
                                    if err is not None:
                                        print('\n *** *** *** *** *** take market order <{}> failed <{}> \n'.format(i, err))
                                        return ret
                                    
                                    # if process success, update order candidates as accepted by takerbot
                                    print('\n *** *** *** *** *** take market order <{}> success\n'.format(i))
                                    for k in range(len(order_candidates)):
                                        feature__takerbot__virtual_order_was_taken_set(order_candidates[k], True)
                                    ret = True
                                    
                                else:
                                    print('\n *** *** *** *** summary of makers sizes <{}> is not enough for <{}>\n'.format(maker_sum, orders_market_sorted[i]['size']))
                    else:
                        break
                    
                # if takerbot checks all the open orders on the market, reset timer to check later again
                if i == len(orders_market_sorted)-1:
                    d.feature__takerbot__time_start = time.time()
    
    return ret

# main function
if __name__ == '__main__':
    
    ####################################################################
    # following logic is about:
    # one time needed initialization 
    # one time needed checks
    ####################################################################
    
    start_welcome_message() # some welcome message
    
    
    init_preconfig() # initialization of config independent items or items needed for config load
    
    load_config() # load configuration from config file if specified than load program arguments with higher priority by replacing config file options
    
    init_postconfig() # initialization of items dependent on config
    
    
    do_utils_and_exit() # if some utility are planned do them and exit program
    
    
    pricing_check_or_exit() # check if pricing works
    
    
    update_balances() # update balances information
    
    feature__slide_dyn__init_postpricing()
    
    while 1:  # primary loop, starting point, after reset-orders-events
        
        ################################################################
        # following logic is about to wait for all session orders to be 
        # canceled and cleared
        ################################################################
        
        virtual_orders__clear_all()
        
        ################################################################
        # following logic is about to prepare for order placement by:
        # updating balances
        # update pricing
        # update custom dynamic parameters
        # reset counters
        # reset timers
        ################################################################
        
        virtual_orders__prepare_once()
        
        while 1: # secondary loop, starting point for handling events and orders
            
            ############################################################
            # following loop is about to:
            # staggered orders are created 
            # pump/dump order is created
            # finished orders are recreated if needed
            # orders reset on delay/afterfinish/afterfinishdelay...
            ############################################################
        
            virtual_orders__prepare_recheck() # every time main event loop pass, specific dynamic vars should be recomputed
            
            # highest priority is to check for events that forces bot to exit
            if events_exit_bot() == True:
                sys.exit(0)
                
            # second highest priority is to check for events that forces bot to reset orders.
            elif events_reset_orders() == True:
                break
                
            # takerbot priority is before wait events which can potentially break takerbot functionality. Check for partial orders to be accepted. If some orders been takerbot accepted, bot must call prepare recheck() function again so pass is called
            elif feature__takerbot__run() == True:
                pass
                
            # check for events that forces bot to wait instead of placing orders
            elif events_wait() == True:
                pass
                
            # lowest priority after all main events is to loop all virtual orders and try to re/create them
            else:
                virtual_orders__handle()
            
            time.sleep(c.BOTdelayinternalcycle)
            
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
