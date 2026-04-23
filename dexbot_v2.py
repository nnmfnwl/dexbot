#!/usr/bin/env python3
import time
import random
import argparse
import sys
import logging
from utils import dxbottools
from utils import dxsettings

import features.glob as glob

from features.log import *
from features.log_cfg import *
from features.cli import *

from features.reset_afot import *
from features.slide_dyn import *
from features.sboundary import *
from features.rboundary import *
from features.flush_co import *
from features.pricing_storage import *
from features.pricing_proxy_client import *
from features.tmp_cfg import *
from features.fixed_fee import *

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
    LOG_ACTION('Starting maker bot')

# initialization of config independent items or items needed for config load
def init_preconfig():
    global c, s, d
    
    LOG_ACTION('Preconfig initialization')
    
    # TODO remove lines an replace global as glob.c,s,d
    c = glob.c
    s = glob.s
    d = glob.d

    global_vars_init_preconfig()
    
    log__init_preconfig__()
    
    cli__init_preconfig__()
    
    feature__tmp_cfg__init_preconfig__()
    
    pricing_storage__init_preconfig__()
    
    fixed_fee__init_preconfig__()
    
    reset_afot__init_preconfig__()
    
    feature__maker_price__init_preconfig()
    
    feature__flush_co__init_preconfig()
    
    feature__balance_save_asset__init_preconfig()
    
    sboundary__init_preconfig__()
    rboundary__init_preconfig__()
    
    events_wait_reopenfinished_init()
    
    feature__slide_dyn__init_preconfig__()
    
    feature__takerbot__init_preconfig()

# initialization of items dependent on config
def init_postconfig():
    global c, s, d
    LOG_ACTION('Postconfig initialization')
    
    global_vars_init_postconfig()
    
    # RPC configuration is part of strategy config,
    # it is not loaded by program arguments rather included.
    # Reason because args are system wide public and these config parameters are 
    # sensitive information
    dxbottools.init_postconfig(c.BOTrpc_user,
                               c.BOTrpc_password,
                               c.BOTrpc_hostname,
                               c.BOTrpc_port)
    
    # initialize pricing proxy client
    pricing_proxy_client__init_postconfig()
    
    # initialize pricing storage and set proxy client
    pricing_storage__init_postconfig(c.BOTconfigname + ".tmp.pricing", c.BOTdelay_check_price, 1, 8, pricing_proxy_client__pricing_storage__try_get_price_fn, c.BOTcfg.price_redirections)
    
    feature__slide_dyn__init_postconfig(c.BOTsellmarket, c.BOTbuymarket, pricing_storage__try_get_price)
    
    fixed_fee__init_postconfig(c.BOTbuymarket, pricing_storage__try_get_price)
    
    cli__init_postconfig()
    
    log__init_postconfig(cli__register_cmd)
    
#global variables initialization
def global_vars_init_preconfig():
    global c, s, d
    LOG_ACTION('Global variables initialization')
    
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
    
    # list of virtual order statuses which could be used to detect order as been finished when been switched from one of these statuses into finished status
    s.status_list__valid_switch_to_finish =  [s.status_list__hidden,
                                              s.status_list__creating,
                                              s.status_list__new,
                                              s.status_list__open,
                                              s.status_list__accepting,
                                              s.status_list__hold,
                                              s.status_list__initialized,
                                              s.status_list__created,
                                              s.status_list__commited]

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
        LOG_ERROR('<maker_price> value <{0}> is invalid. Allowed values are: -1, -2 and 0'.format(c.feature__maker_price__cfg_price))
        error_num += 1
    
    return error_num, crazy_num

def load_config_verify_or_exit(error_num, crazy_num):
    global c, s, d
    LOG_ACTION('Verifying configuration')
    
    # arguments: main maker/taker
    if hasattr(c, 'BOTmaker_address') == False:
        LOG_ERROR('<maker_address> is not specified')
        error_num += 1
        
    if hasattr(c, 'BOTtaker_address') == False:
        LOG_ERROR('<taker_address> is not specified')
        error_num += 1
    
    if c.BOTsell_type <= -1 or c.BOTsell_type >= 1:
        LOG_ERROR('<sell_type> value <{0}> is invalid. Valid range is -1 up to 1 only'.format(c.BOTsell_type))
        error_num += 1
    
    # arguments: basic values
    if c.BOTsell_start_max <= 0:
        LOG_ERROR('<sell_start_max> value <{0}> is invalid'.format(c.BOTsell_start_max))
        error_num += 1
    
    if c.BOTsell_end_max <= 0:
        LOG_ERROR('<sell_end_max> value <{0}> is invalid'.format(c.BOTsell_end_max))
        error_num += 1
    
    if c.BOTsell_start_min != 0:
        if c.BOTsell_start_min < 0:
            LOG_ERROR('<sell_start_min> value <{0}> is invalid. Must be more than 0'.format(c.BOTsell_start_min))
            error_num += 1
        
        if c.BOTsell_start_min > c.BOTsell_start_max:
            LOG_ERROR('<sell_start_min> value <{}> is invalid. Must be less than <sell_start_max> <{}>'.format(c.BOTsell_start_min, c.BOTsell_start_max))
            error_num += 1
            
    if c.BOTsell_end_min != 0:
        if c.BOTsell_end_min < 0:
            LOG_ERROR('<sell_end_min> value <{}> is invalid. Must be more than 0'.format(c.BOTsell_end_min))
            error_num += 1
        
        if c.BOTsell_end_min > c.BOTsell_end_max:
            LOG_ERROR('<sell_end_min> value <{}> is invalid. Must be less than <sell_end_max> <{}>'.format(c.BOTsell_end_min, c.BOTsell_end_max))
            error_num += 1
    
    # ~ if c.BOTmarking != 0:
        # ~ if c.BOTmarking < 0:
            # ~ LOG_ERROR('<marking> value <{}> is invalid. Must be more than 0'.format(c.BOTmarking))
            # ~ error_num += 1
        
        # ~ if c.BOTmarking >= 0.001:
            # ~ LOG_WARNING('<marking> value <{}> seems invalid. Values more than 0.001 can possibly have very impact on order value'.format(c.BOTmarking))
            # ~ LOG_HINT('If you are really sure about what you are doing, you can ignore this warning by using --im_really_sure_what_im_doing argument')
            # ~ crazy_num += 1
    
    error_num_tmp, crazy_num_tmp = log__load_config_verify()
    error_num += error_num_tmp
    crazy_num += crazy_num_tmp
    
    error_num_tmp, crazy_num_tmp = cli__load_config_verify()
    error_num += error_num_tmp
    crazy_num += crazy_num_tmp
    
    error_num_tmp, crazy_num_tmp = fixed_fee__load_config_verify()
    error_num += error_num_tmp
    crazy_num += crazy_num_tmp
    
    if c.BOTsell_start_slide <= 1:
        LOG_WARNING('<sell_start_slide> value <{0}> seems invalid. Values less than 1 means selling something under price.'.format(c.BOTsell_start_slide))
        LOG_HINT('If you are really sure about what you are doing, you can ignore this warning by using --im_really_sure_what_im_doing argument')
        crazy_num += 1
    
    if c.BOTsell_start_slide > 10:
        LOG_WARNING('<sell_start_slide> value <{0}> seems invalid. <1.01> means +1%, <1.10> means +10%, more than <2> means +100% of actual price'.format(c.BOTsell_start_slide))
        LOG_HINT('If you are really sure about what you are doing, you can ignore this warning by using --im_really_sure_what_im_doing argument')
        crazy_num += 1
    
    if c.BOTsell_end_slide <= 1:
        LOG_WARNING('<sell_end_slide> value <{0}> seems invalid. Values less than 1 means selling something under price.'.format(c.BOTsell_end_slide))
        LOG_HINT('If you are really sure about what you are doing, you can ignore this warning by using --im_really_sure_what_im_doing argument')
        crazy_num += 1
    
    if c.BOTsell_end_slide > 10:
        LOG_WARNING('<sell_end_slide> value <{0}> seems invalid. <1.01> means +1%, <1.10> means +10%, more than <2> means +100% of actual price'.format(c.BOTsell_end_slide))
        LOG_HINT('If you are really sure about what you are doing, you can ignore this warning by using --im_really_sure_what_im_doing argument')
        crazy_num += 1
    
    if c.BOTmax_open_orders < 1:
        LOG_ERROR('<max_open_orders> value <{0}> is invalid'.format(c.BOTmax_open_orders))
        error_num += 1
    
    if c.BOTreopen_finished_delay < 0:
        LOG_ERROR('<reopen_finished_delay> value <{0}> is invalid'.format(c.BOTreopen_finished_delay))
        error_num += 1
    
    if c.BOTreopen_finished_num < 0:
        LOG_ERROR('<reopen_finished_num> value <{0}> is invalid'.format(c.BOTreopen_finished_num))
        error_num += 1
    
    if c.BOTreopen_finished_num > c.BOTmax_open_orders:
        LOG_ERROR('<reopen_finished_num> can not be more than <max_open_ordersorders> value <{0}>/<{1}> is invalid'.format(c.BOTreopen_finished_num, c.BOTmax_open_orders))
        error_num += 1
    
    if c.BOTtakerbot < 0:
        LOG_ERROR('<takerbot> value <{0}> is invalid'.format(c.BOTtakerbot))
        error_num += 1
    
    if c.BOThidden_orders == True:
        if c.BOTtakerbot < 0:
            LOG_ERROR('when <hidden_orders> {0} are enabled <takerbot> <{1} mut be enabled also>'.format(c.BOThidden_orders, c.BOTtakerbot))
            error_num += 1
    
    error_num_tmp, crazy_num_tmp = feature__tmp_cfg__load_config_verify()
    error_num += error_num_tmp
    crazy_num += crazy_num_tmp
    
    error_num_tmp, crazy_num_tmp = sboundary__load_config_verify()
    error_num += error_num_tmp
    crazy_num += crazy_num_tmp
    
    error_num_tmp, crazy_num_tmp = rboundary__load_config_verify()
    error_num += error_num_tmp
    crazy_num += crazy_num_tmp
    
    if c.BOTbalance_save_number < 0:
        LOG_ERROR('<balance_save_number> value <{0}> is invalid'.format(c.BOTbalance_save_number))
        error_num += 1
    
    if c.BOTbalance_save_percent < 0 or c.BOTbalance_save_percent > 1:
        LOG_ERROR('<balance_save_percent> value <{0}> is invalid'.format(c.BOTbalance_save_percent))
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
    
    # arguments: dynamic values
    
    error_num_tmp, crazy_num_tmp = feature__slide_dyn__load_config_verify()
    error_num += error_num_tmp
    crazy_num += crazy_num_tmp
    
    # arguments: reset orders by events
    if c.BOTreset_on_price_change_positive < 0:
        LOG_ERROR('<reset_on_price_change_positive> value <{0}> is invalid'.format(c.BOTreset_on_price_change_positive))
        error_num += 1
    
    if c.BOTreset_on_price_change_negative < 0:
        LOG_ERROR('<reset_on_price_change_negative> value <{0}> is invalid'.format(c.BOTreset_on_price_change_negative))
        error_num += 1
    
    if c.BOTreset_after_delay < 0:
        LOG_ERROR('<reset_after_delay> value <{0}> is invalid'.format(c.BOTreset_after_delay))
        error_num += 1
    
    error_num_tmp, crazy_num_tmp = reset_afot__load_config_verify()
    error_num += error_num_tmp
    crazy_num += crazy_num_tmp
    
    # arguments: internal values changes
    if c.BOTdelay_internal_op < 1:
        LOG_ERROR('<delay_internal_op> value <{0}> is invalid'.format(c.BOTdelay_internal_op))
        error_num += 1
        
    if c.BOTdelay_internal_error < 1:
        LOG_ERROR('<delay_internal_error> value <{0}> is invalid'.format(c.BOTdelay_internal_error))
        error_num += 1
        
    # arguments: internal values changes
    if c.BOTdelay_internal_loop < 1:
        LOG_ERROR('<delay_internal_loop> value <{0}> is invalid'.format(c.BOTdelay_internal_loop))
        error_num += 1
    
    if c.BOTdelay_check_price < 1:
        LOG_ERROR('<delay_check_price> value <{0}> is invalid'.format(c.BOTdelay_check_price))
        error_num += 1
    
    # if there are unresolved configuration warnings or error, then exit bot with error
    if crazy_num != c.BOTim_really_sure_what_im_doing or error_num != 0:
        if error_num != 0:
            LOG_ERROR("errors in configuration detected > {}".format(error_num))
        if crazy_num != 0:
            LOG_WARNING("crazy config values detected, but not expected> {}/{}".format(crazy_num, c.BOTim_really_sure_what_im_doing))
        if crazy_num < c.BOTim_really_sure_what_im_doing:
            LOG_WARNING("crazy config values not detected, but expected > {}/{}".format(crazy_num, c.BOTim_really_sure_what_im_doing))
            
        LOG_ERROR('Verifying configuration failed.'
        'Please read help and use <im_really_sure_what_im_doing> argument correctly, it allows you to specify number of crazy/meaningless/special configuration values, which are expected, to confirm you are sure what you are doing.')
        sys.exit(1)
    else:
        if crazy_num != 0 and crazy_num == c.BOTim_really_sure_what_im_doing:
            LOG_DEBUG("crazy config values match expected > {}/{}".format(crazy_num, c.BOTim_really_sure_what_im_doing))
            
        LOG_INFO('Verifying configuration success')

def feature__maker_price__load_config_define():
    feature__main_cfg__add_variable('maker_price', 0, feature__main_cfg__validate_float, None, """Value for live price updates or static price configuration'
    '0 - live price updates are activated'
    '-1 - local one time price activated, center price is loaded from remote source and saved int cfg file every time bot starts, even not updated after crash'
    '-2 - local long term price activated, center price is loaded from remote source and saved into cfg file only once, even not updated after restart/crash'
    'Other than 0, -1, or -2 values are invalid'
    'Even if center price is configured like-static, spread and dynamic spread should take care about order position management, this like system dexbot is able to handle situations when no pricing source is available, but it is up to user how to configure price movement'
    'There is also another special pricing configuration feature called "price_redirections"(see bot_v2_template.py file for details)'
    '(default=0 live price update)""", None)

def feature__maker_price__load_config_postparse(args):
    global c, s, d
    
    c.feature__maker_price__cfg_price = float(args.maker_price)

def load_config_argument_parser_define(parser):
    global c, s, d
    
    # arguments: action arg
    parser.add_argument('--action', type=str, help='reset/restore action, default is "none"'
    'reset is used to force features which implements reset to force to not use values from tmp cfg, rather load new ones'
    'restore is used to force features which implementes restore to force to try to use values from tmp cfg'
    'reset spread zero value if is set to automatic by -2,)'
    'restore spread zero value if set to one time by -1'
    'restore static or dynamic initial price value'
    , default="none")
    
    # arguments: config file(will be used instead of arguments later)
    parser.add_argument('--config', type=str, help='python bot/strategy config file', default=None)
    
    # arguments: utility arguments
    parser.add_argument('--configaction', type=str, default=None, help='defaults/template configuration action'
    'instead of using configuration file, just generate new template file or defaults values None/template/defaults. (default = None)')
    parser.add_argument('--cancelall', help='cancel all orders and exit', action='store_true')
    parser.add_argument('--cancelmarket', help='cancel all orders in market specified by pair --maker and --taker', action='store_true')
    parser.add_argument('--canceladdress', help='cancel all orders in market specified by configuration variables maker= + taker= + maker_address= + taker_address= ', action='store_true')

def load_config_argument_parser_postparse(args):
    global c, s, d
    
    c.BOTaction_arg = str(args.action)
    
    # arguments: utility arguments
    c.BOTcancelall = args.cancelall
    c.BOTcancelmarket = args.cancelmarket
    c.BOTcanceladdress = args.canceladdress
    c.BOTconfigaction = args.configaction
    
    # check if configuration argument is set as --config and try to import configuration file
    c.BOTconfigname = args.config
    if c.BOTconfigname is None:
        LOG_ERROR("--config file is invalid")
        sys.exit(1)
    
    # temporary configuration
    feature__tmp_cfg__load_config_postparse(args)

def load_config_main_cfg_define():
    
    # configuration file variables rules definition
    feature__main_cfg__add_variable("rpc_user", None, feature__main_cfg__validate_str, None, """RPC authentication username used to connect to Blocknet node wallet""", [["use JohnSmith", "JohnSmith"]])
    feature__main_cfg__add_variable("rpc_password", None, feature__main_cfg__validate_password, None, """RPC authentication password used to connect to Blocknet node wallet""", None)
    feature__main_cfg__add_variable("rpc_hostname", None, feature__main_cfg__validate_str, None, """Blocknet node wallet hostname or ip address""", [["use localhost 127.0.0.1", "127.0.0.1"]])
    feature__main_cfg__add_variable("rpc_port", None, feature__main_cfg__validate_int, None, """RPC authentication port used to connect to Blocknet node wallet""", [["use port 41414", "41414"]])
    
    # arguments: main maker/taker
    feature__main_cfg__add_variable('maker_ticker', 'BLOCK', feature__main_cfg__validate_str, None, """asset being sold (default=BLOCK). For example BLOCK LTC BTC PIVX XVG DASH DOGE""")
    feature__main_cfg__add_variable('taker_ticker', 'LTC', feature__main_cfg__validate_str, None, """asset being bought (default=LTC). For example BLOCK LTC BTC PIVX XVG DASH DOGE""")
    feature__main_cfg__add_variable('maker_address', None, feature__main_cfg__validate_str, None, """trading address of asset being sold (default=None)""")
    feature__main_cfg__add_variable('taker_address', None, feature__main_cfg__validate_str, None, """trading address of asset being bought (default=None)""")
    feature__main_cfg__add_variable('address_funds_only', None, feature__main_cfg__validate_bool, None, """limit bot to use and compute funds only from maker and taker address(default=False disabled)""")
    
    feature__main_cfg__add_variable('price_redirections', dict({}), feature__main_cfg__validate_dict, None, """Price redirections is feature used to optionally set custom ASSET 1 price in thirty ASSET 2.
For example trading BLOCK with LTC, you would rather set BLOCK price manually in USDT and BOT automatically converts value into LTC.""",
[["example to redirect Blocknet price by $59 USDT per $BLOCK, and $1299 LTC ", """ "BLOCK": { "asset": "USDT", "price": 59} , "LTC": { "asset": "USDT", "price": 1299}"""]])
    
    log__load_config_define()
    
    cli__load_config_define()
    
    feature__flush_co__load_config_define()
    
    pricing_proxy_client__load_config_define()
    
    pricing_storage__load_config_define()
    
    # arguments: basic values
    feature__main_cfg__add_variable('sell_type', 0, feature__main_cfg__validate_int, None, """<float> number between -1 and 1. -1 means maximum exponential to 0 means linear to 1 means maximum logarithmic.
Recommended middle range log and exp values are 0.8 and -0.45
(default=0 linear)
# EXAMPLE INFOGRAPHIC:
#      ^
#      |                                                
# O    |                                              8  > order number #1 up to order number #8 with LINEAR --sell_type 0 order amount distribution
# R    |                                           7  | 
# D    |                                        6  |--| 
# E    |                                     5  |--|--| 
# R S  |                                  4  |--|--|--| 
#   I  |                               3  |--|--|--|--| 
#   Z  |                            2  |--|--|--|--|--| 
#   E  |                         1  |--|--|--|--|--|--| 
#      |                         |--|--|--|--|--|--|--| 
#      ------------------------------------------------------>
#                                ^                        price
#                          center price
#

#      ^
#      |                                                
# O    |                                           7  8  > order number #1 up to order number #8 with EXPONENTIAL --sell_type -0.45 order amount distribution
# R    |                                           |--| 
# D    |                                        6  |--| 
# E    |                                        |--|--| 
# R S  |                                     5  |--|--| 
#   I  |                                     |--|--|--| 
#   Z  |                                  4  |--|--|--| 
#   E  |                         1  2  3  |--|--|--|--| 
#      |                         |--|--|--|--|--|--|--| 
#      ------------------------------------------------------>
#                                ^                        price
#                          center price
#""", None)
    
    feature__main_cfg__add_variable('sell_size_asset', None, feature__main_cfg__validate_str, None, """size of orders are set in specific asset instead of maker (default=--maker)""",None)
    
    feature__main_cfg__add_variable('sell_start_max', 0.001, feature__main_cfg__validate_float, None, """First order maximum possible size or random from range sell_start_max and sell_end_max (default=0.001).
In theory we need bot to try to create orders in dynamic size if there is not enough balance available to create order at maximum. But only between <value, min value>, because of transaction fees.""",None)
    feature__main_cfg__add_variable('sell_end_max', 0.001, feature__main_cfg__validate_float, None, """size of last order or random from range sell_start_max and sell_end_max (default=0.001)""", None)
    
    feature__main_cfg__add_variable('sell_start_min', 0, feature__main_cfg__validate_float, None, """Minimum acceptable size of first order.'
    'If this is configured and there is not enough balance to create first order at <sell_start_max> size, order will be created at maximum possible size between <sell_start_max> and <sell_start_min>'
    'By default this feature is disabled.'
    '(default=0 disabled)', default=0)""", None)
    feature__main_cfg__add_variable('sell_end_min', 0, feature__main_cfg__validate_float, None, """Minimum acceptable size of last order.
    'If this is configured and there is not enough balance to create last order at <sell_end_max> size, order will be created at maximum possible size between <sell_end_max> and <sell_end_min>'
    'By default this feature is disabled.'
    '(default=0 disabled)""", None)
    
    
    feature__main_cfg__add_variable('sell_random', False, feature__main_cfg__validate_bool, None, """orders size will be random number between sell_start_max and sell_end_max, otherwise sequence of orders starting by sell_start_max amount and ending with sell_end_max amount(default=disabled)""", None)
    
    fixed_fee__load_config_define()
    
    feature__main_cfg__add_variable('sell_start_slide', 1.01, feature__main_cfg__validate_float, None, """price of first order will be equal to (sell_start_slide * actual_price) (default=1.01 means +1%%)""", None)
    feature__main_cfg__add_variable('sell_end_slide', 1.021, feature__main_cfg__validate_float, None, """price of last order will be equal to (sell_end_slide * actual price) (default=1.021 means +2.1%%)""", None)
    
    feature__main_cfg__add_variable('max_open_orders', 5, feature__main_cfg__validate_int, None, """Max amount of orders to have open at any given time. Placing orders sequence: first placed order is at sell_start_slide(price slide),sell_start_max(amount) up to sell_end_slide(price slide),sell_end_max(amount) (default=5)""", None)
    
    feature__main_cfg__add_variable('make_next_on_hit', False, feature__main_cfg__validate_bool, None, """create next order on 0 amount hit, so if first order is not created, rather skipped, next is created(default=False disabled)""", None)
    
    feature__main_cfg__add_variable('reopen_finished_delay', 0, feature__main_cfg__validate_int, None, """finished orders will be reopened after specific delay(seconds) of last filled order(default=0 disabled)""", None)
    feature__main_cfg__add_variable('reopen_finished_num', 0, feature__main_cfg__validate_int, None, """finished orders will be reopened after specific number of filled orders(default=0 disabled)
    Example reopen_finished_num=2 means recreate orders when 2 orders are accepted.""", None)
    
    feature__main_cfg__add_variable('partial_orders', False, feature__main_cfg__validate_bool, None, """enable or disable partial orders. Partial orders minimum is set by <sell_start_min> <sell_end_min> along with dynamic size of orders(default=False disabled)""", None)
    
    feature__main_cfg__add_variable('takerbot', 0, feature__main_cfg__validate_int, None, """Keep checking for possible partial orders which meets requirements(size, price) and accept that orders.'
    'If this feature is enabled, takerbot is automatically searching for orders at size between <sell_start_max-sell_end_max>...<sell_start_min-sell_end_min> and at price <sell_start_slide-sell_end_slide>+<dynamic slide>*<price> and higher.'
    'This feature can be also understood as higher layer implementation of limit order feature on top of atomic swaps on BlockDX exchange. Takerbot can possible cancel multiple opened orders to autotake orders which meets requirements'
    '(I.e. value 30 means check every 30 seconds)'
    'By default this feature is disabled.'
    '(default=0 disabled)""", None)

    # ~ TODO = not implemented yet
    feature__main_cfg__add_variable('hidden_orders', False, feature__main_cfg__validate_bool, None, """Orders will be created only virtually, hidden from dx and acting like takerbot only.  (default=False disabled)""", None)
    
    sboundary__load_config_define()
    rboundary__load_config_define()
    
    feature__main_cfg__add_variable('balance_save_asset', None, feature__main_cfg__validate_str, None, """size of balance to save is set in specific asset instead of maker (default=--maker)""", None)
    feature__main_cfg__add_variable('balance_save_asset_track', False, feature__main_cfg__validate_bool, None, """Track balance save asset price updates. This means, ie if trading BLOCK/BTC on USD also track USD/BLOCK price and update balance to save by it (default=False disabled)""")
    feature__main_cfg__add_variable('balance_save_number', 0, feature__main_cfg__validate_str, None, """min taker balance you want to save and do not use for making orders specified by number (default=0)""", None)
    feature__main_cfg__add_variable('balance_save_percent', 0.05, feature__main_cfg__validate_float, None, """min taker balance you want to save and do not use for making orders specified by percent of maker+taker balance (default=0.05 means 5%%)""", None)
    
    feature__maker_price__load_config_define()
    
    # arguments: dynamic values
    
    feature__slide_dyn__load_config_define()

    # arguments: reset orders by events
    feature__main_cfg__add_variable('reset_on_price_change_positive', 0, feature__main_cfg__validate_float, None, """price positive change which inits reset of all orders. I.e. 0.05 means reset at +5%% change. (default=0 disabled)""", None)
    feature__main_cfg__add_variable('reset_on_price_change_negative', 0, feature__main_cfg__validate_float, None, """price negative change which inits reset of all orders. I.e. 0.01 means reset at -1%% change. (default=0 disabled)""", None)
    feature__main_cfg__add_variable('reset_after_delay', 0, feature__main_cfg__validate_int, None, """keep resetting orders in specific number of seconds (default=0 disabled)""")
    
    reset_afot__load_config_define()

    # arguments: internal values changes
    feature__main_cfg__add_variable('delay_internal_op', 2.3, feature__main_cfg__validate_float, None, """sleep delay, in seconds, between place/cancel orders or other internal operations(can be used ie. case of bad internet connection...) (default=2.3)""", None)
    feature__main_cfg__add_variable('delay_internal_error', 10, feature__main_cfg__validate_float, None, """sleep delay, in seconds, when error happen to try again. (default=10)""")
    feature__main_cfg__add_variable('delay_internal_loop', 8, feature__main_cfg__validate_float, None, """sleep delay, in seconds, between main loops to process all things to handle. (default=8)""", None)
    feature__main_cfg__add_variable('delay_check_price', 180, feature__main_cfg__validate_float, None, """sleep delay, in seconds to check again pricing (default=180)""", None)
    
    # arguments: special arguments
    feature__main_cfg__add_variable('im_really_sure_what_im_doing', 0, feature__main_cfg__validate_int, None, """This argument allows user to specify number of non-standard configuration values for special cases like user want to activate bot trading later relatively higher price than actual is""")
    
    feature__tmp_cfg__load_config_define()

def load_config_main_cfg_postparse():
    global c, s, d
    
    c.BOTrpc_user = c.BOTcfg.rpc_user
    c.BOTrpc_password = c.BOTcfg.rpc_password
    c.BOTrpc_hostname = c.BOTcfg.rpc_hostname
    c.BOTrpc_port = c.BOTcfg.rpc_port
    
    # arguments: main maker/taker
    c.BOTsellmarket = c.BOTcfg.maker_ticker.upper()
    c.BOTbuymarket = c.BOTcfg.taker_ticker.upper()
    
    # try to autoselect maker/taker address from config file
    if c.BOTsellmarket in dxsettings.tradingaddress:
        c.BOTmaker_address = dxsettings.tradingaddress[c.BOTsellmarket]
    
    if c.BOTbuymarket in dxsettings.tradingaddress:
        c.BOTtaker_address = dxsettings.tradingaddress[c.BOTbuymarket]
    
    # try to autoselect maker/taker address from program arguments
    if c.BOTcfg.maker_address is not None:
        c.BOTmaker_address = c.BOTcfg.maker_address
        
    if c.BOTcfg.taker_address is not None:
        c.BOTtaker_address = c.BOTcfg.taker_address
    
    c.BOTaddress_funds_only = bool(c.BOTcfg.address_funds_only)
    
    c.BOTpartial_orders = bool(c.BOTcfg.partial_orders)
    
    c.BOThidden_orders = bool(c.BOTcfg.hidden_orders)
    
    log__load_config_postparse(c.BOTcfg)
    
    cli__load_config_postparse(c.BOTcfg)
    
    feature__maker_price__load_config_postparse(c.BOTcfg)
    
    feature__flush_co__load_config_postparse(c.BOTcfg)
    
    pricing_proxy_client__load_config_postparse(c.BOTcfg)
    
    pricing_storage__load_config_postparse(c.BOTcfg)
    
    sboundary__load_config_postparse(c.BOTcfg)
    rboundary__load_config_postparse(c.BOTcfg)
    
    # arguments: basic values
    c.BOTsell_random = c.BOTcfg.sell_random
    
    c.BOTsell_size_asset = getattr(c.BOTcfg, 'sell_size_asset', None)
    if c.BOTcfg.sell_size_asset is None:
        c.BOTsell_size_asset = c.BOTsellmarket
    
    c.BOTsell_type = float(c.BOTcfg.sell_type)
    
    c.BOTsell_start_max = float(c.BOTcfg.sell_start_max)
    c.BOTsell_end_max = float(c.BOTcfg.sell_end_max)
    c.BOTsell_start_min = float(c.BOTcfg.sell_start_min)
    c.BOTsell_end_min = float(c.BOTcfg.sell_end_min)
    
    fixed_fee__load_config_postparse(c.BOTcfg)
    
    c.BOTsell_start_slide = float(c.BOTcfg.sell_start_slide)
    c.BOTsell_end_slide = float(c.BOTcfg.sell_end_slide)
    c.BOTslidemin = min(c.BOTsell_start_slide, c.BOTsell_end_slide)
    c.BOTslidemax = max(c.BOTsell_start_slide, c.BOTsell_end_slide)
    c.BOTmax_open_orders = int(c.BOTcfg.max_open_orders)
    c.BOTmake_next_on_hit = bool(c.BOTcfg.make_next_on_hit)
    c.BOTreopen_finished_delay = int(c.BOTcfg.reopen_finished_delay)
    c.BOTreopen_finished_num = int(c.BOTcfg.reopen_finished_num)
    if c.BOTreopen_finished_num > 0 or c.BOTreopen_finished_delay > 0:
        c.BOTreopenfinished = 1
    else:
        c.BOTreopenfinished = 0
    
    # ~ c.BOTmarking = float(c.BOTcfg.marking)
    
    if c.BOTcfg.balance_save_asset is None:
        c.BOTbalance_save_asset = c.BOTsellmarket
    else:
        c.BOTbalance_save_asset = str(c.BOTcfg.balance_save_asset)
    c.BOTbalance_save_asset_track = bool(c.BOTcfg.balance_save_asset_track)
    c.BOTbalance_save_number = float(c.BOTcfg.balance_save_number)
    c.BOTbalance_save_percent = float(c.BOTcfg.balance_save_percent)
    
    c.BOTtakerbot = int(c.BOTcfg.takerbot)
    
    # arguments: dynamic values,
    
    feature__slide_dyn__load_config_postparse(c.BOTcfg)
        
    # arguments: reset orders by events
    c.BOTreset_on_price_change_positive = float(c.BOTcfg.reset_on_price_change_positive)
    c.BOTreset_on_price_change_negative = float(c.BOTcfg.reset_on_price_change_negative)
    c.BOTreset_after_delay = int(c.BOTcfg.reset_after_delay)
    
    reset_afot__load_config_postparse(c.BOTcfg)
    
    # arguments: internal values changes
    c.BOTdelay_internal_op = float(c.BOTcfg.delay_internal_op)
    c.BOTdelay_internal_error = float(c.BOTcfg.delay_internal_error)
    c.BOTdelay_internal_loop = float(c.BOTcfg.delay_internal_loop)
    c.BOTdelay_check_price = int(c.BOTcfg.delay_check_price)
    
    # arguments: special arguments
    c.BOTim_really_sure_what_im_doing = int(c.BOTcfg.im_really_sure_what_im_doing)
    

def load_config():
    global c, s, d
    
    LOG_ACTION('Loading program configuration')
    error_num = 0
    crazy_num = 0
    
    
    # initialize argument parser
    parser = argparse.ArgumentParser()
    # argument parser argument definition
    load_config_argument_parser_define(parser)
    # parse arguments
    args = parser.parse_args()
    # post argument parse process
    load_config_argument_parser_postparse(args)
    
    
    # define main file configuration variables/rules
    load_config_main_cfg_define()
    
    # do requested configuration action
    if c.BOTconfigaction is not None:
        retcode = feature__main_cfg__generate_cfg(c.BOTconfigname + '.py', c.BOTconfigaction)
        sys.exit(retcode)
        
    # load configuration from configuration file
    error_num += feature__main_cfg__load_cfg(c.BOTconfigname)
    # parse loaded configuration and build obj file
    feature__main_cfg__parse_cfg()
    # return whole cfg as obj
    c.BOTcfg = feature__main_cfg__get_cfg_obj()
    # post main cfg parse process
    load_config_main_cfg_postparse()
    
    load_config_verify_or_exit(error_num, crazy_num)
    
# global variables which have dependency on configuration be done
def global_vars_init_postconfig():
    global c, s, d
    LOG_ACTION('Global variables post-configuration initialization')
    
    if c.BOTreopenfinished == 0:
        s.reopenstatuses = s.status_list__ready_to_reopen_nfinished
    else:
        s.reopenstatuses = s.status_list__ready_to_reopen_wfinished
    
    s.ordersvirtualmax = c.BOTmax_open_orders
    d.ordersvirtual = [0]*s.ordersvirtualmax
    for i in range(s.ordersvirtualmax):
        d.ordersvirtual[i] = {}
        virtual_orders__update_status(d.ordersvirtual[i], s.status_list__canceled)
        d.ordersvirtual[i]['id'] = 0
    
# cancel all my orders
def do_utils_cancel_orders_all():
    global c, s, d
    LOG_ACTION('Using utility to cancel all orders on all markets')
    retcode, retdata = dxbottools.cancelallorders()
    LOG_INFO('Cancel orders result: {0} >> {1}'.format(retcode, retdata))
    return retcode

# cancel orders specified by maker and taker
def do_utils_cancel_orders_market():
    global c, s, d
    LOG_ACTION('Using utility to cancel specific market pair {0}-{1} orders'.format(c.BOTsellmarket, c.BOTbuymarket))
    retcode, retdata = dxbottools.cancelallordersbymarket(c.BOTsellmarket, c.BOTbuymarket)
    LOG_INFO('Cancel orders result: {0} >> {1}'.format(retcode, retdata))
    return retcode

# cancel all orders that belongs to running bot instance
def do_utils_cancel_orders_address():
    global c, s, d
    LOG_ACTION('Using utility to cancel specifix market pair and address {0}-{1} {2}-{3}'.format(c.BOTsellmarket, c.BOTbuymarket, c.BOTmaker_address, c.BOTtaker_address))
    retcode, retdata = dxbottools.cancelallordersbyaddress(c.BOTsellmarket, c.BOTbuymarket, c.BOTmaker_address, c.BOTtaker_address)
    LOG_INFO('Cancel orders result: {0} >> {1}'.format(retcode, retdata))
    return retcode

# do utils and exit
def do_utils_and_exit():
    global c, s, d
    if c.BOTcancelall is True:
        retcode = do_utils_cancel_orders_all()
        sys.exit(retcode)
    elif c.BOTcancelmarket is True:
        retcode = do_utils_cancel_orders_market()
        sys.exit(retcode)
    elif c.BOTcanceladdress is True:
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
                if c.BOTaction_arg == 'restore':
                    d.feature__maker_price__value_current_used = feature__tmp_cfg__get_value("feature__maker_price__value_current_used", 0)
            
            # if bot is started normally local price is zero so it will be stored in tmp cfg
            if d.feature__maker_price__value_current_used == 0:
                d.feature__maker_price__value_current_used = price_maker_used
                feature__tmp_cfg__set_value("feature__maker_price__value_current_used", price_maker_used)
        
        # local long term price activated
        elif c.feature__maker_price__cfg_price == -2:
            
            # try to restore maker price always
            if d.feature__maker_price__value_current_used == 0:
                d.feature__maker_price__value_current_used = feature__tmp_cfg__get_value("feature__maker_price__value_current_used", 0)
            
            # even long term price must be set for the first time
            if d.feature__maker_price__value_current_used == 0:
                d.feature__maker_price__value_current_used = price_maker_used
                feature__tmp_cfg__set_value("feature__maker_price__value_current_used", price_maker_used)
                
        # invalid maker_price configuration
        else:
            return 0
            
        # startup maker price value load or restore
        if d.feature__maker_price__value_startup == 0:
            if c.feature__maker_price__cfg_price == -1 or c.feature__maker_price__cfg_price == -2:
                d.feature__maker_price__value_startup = d.feature__maker_price__value_current_used
            elif c.BOTaction_arg == 'restore':
                d.feature__maker_price__value_startup = feature__tmp_cfg__get_value("feature__maker_price__value_startup", 0)
            
            if d.feature__maker_price__value_startup == 0:
                d.feature__maker_price__value_startup = price_maker_used
                feature__tmp_cfg__set_value("feature__maker_price__value_startup", price_maker_used)
            
    return price_maker_used

# check if pricing works or exit
def pricing_check_or_error():
    global c, s, d
    LOG_ACTION('Checking pricing information for <{0}> <{1}>'.format(c.BOTsellmarket, c.BOTbuymarket))
    
    # check if sell and buy market are not same
    if c.BOTsellmarket == c.BOTbuymarket:
        LOG_ERROR('Maker and taker asset cannot be the same')
        return 1
    
    # try to get main pricing
    price_maker = feature__maker_price__pricing_update()
    if price_maker == 0:
        LOG_ERROR('Main pricing not available')
        return 1
    
    # try to get initial price of asset which balance save size is set in
    price__balance_save_asset = feature__balance_save_asset__pricing_update()
    if price__balance_save_asset == 0:
        LOG_ERROR('balance save asset pricing not available')
        return 1
    
    # try to get initial price of asset vs maker in which is dynamic slide zero set
    price_slide_dyn_asset = feature__slide_dyn__asset_pricing_update()
    if price_slide_dyn_asset == 0:
        LOG_ERROR('dynamic slide asset pricing not available')
        return 1
    
    # try to get initial price of asset vs maker in which are orders sizes set, ie USD
    price_sell_size_asset = feature__sell_size_asset__pricing_update()
    if price_sell_size_asset == 0:
        LOG_ERROR('Sell size asset pricing not available')
        return 1
    
    # initial static boundary pricing
    price_boundary = sboundary__pricing_init(c.BOTsellmarket, c.BOTbuymarket, c.BOTaction_arg, pricing_storage__try_get_price)
    if price_boundary == 0:
        LOG_ERROR('Static boundary pricing not available')
        return 1
        
    # initial relative boundary pricing
    price_boundary = rboundary__pricing_init(c.BOTsellmarket, c.BOTbuymarket, c.BOTaction_arg, pricing_storage__try_get_price)
    if price_boundary == 0:
        LOG_ERROR('Relative boundary pricing not available')
        return 1
    
    return 0
    
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
        LOG_ERROR('get_utxos call invalid response: {}'.format(utxos))
    
    return ret
    
# update actual balanced of maker and taker
def update_balances():
    global c, s, d
    
    LOG_DEBUG('Updating balances')
    
    tmp_maker = {}
    tmp_taker = {}
    
    tmp_maker_address = None
    tmp_taker_address = None
    
    # if bot using funds from specific address only
    if c.BOTaddress_funds_only is True:
        tmp_maker_address = c.BOTmaker_address
        tmp_taker_address = c.BOTtaker_address
    
    tmp_maker = balance_get(c.BOTsellmarket, tmp_maker_address)
    tmp_taker = balance_get(c.BOTbuymarket, tmp_taker_address)
    
    d.balance_maker_total = tmp_maker["total"]
    d.balance_maker_available = tmp_maker["available"]
    d.balance_maker_reserved = tmp_maker["reserved"]
    
    d.balance_taker_total = tmp_taker["total"]
    d.balance_taker_available = tmp_taker["available"]
    d.balance_taker_reserved = tmp_taker["reserved"]
    
    LOG_INFO('Actual balance maker token <{}> <{}> total <{}> available <{}> reserved <{}>'.format(tmp_maker_address, c.BOTsellmarket, d.balance_maker_total, d.balance_maker_available, d.balance_maker_reserved))
    LOG_INFO('Actual balance taker token <{}> <{}> total <{}> available <{}> reserved <{}>'.format(tmp_taker_address, c.BOTbuymarket, d.balance_taker_total, d.balance_taker_available, d.balance_taker_reserved))

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
    LOG_ACTION('Clearing all session virtual orders and waiting for be done...')
    
    # mark all virtual orders as cleared
    for i in range(s.ordersvirtualmax):
        virtual_orders__update_status(d.ordersvirtual[i], s.status_list__clear, ifnot = [s.status_list__clear])
    
    virtual_orders__cancel_all()

# virtual-orders cancel and wait for process done
def virtual_orders__cancel_all():
    global c, s, d
    LOG_ACTION('Canceling all session virtual orders and waiting for be done...')
    
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
                    LOG_INFO('Clearing virtual order index <{0}> id <{1}> and waiting for be done...'.format(i, z['id']))
                    dxbottools.rpc_connection.dxCancelOrder(z['id'])
                    clearing += 1
                    break
        if clearing > 0:
            LOG_DEBUG('Sleeping waiting for old orders to be cleared')
            time.sleep(c.BOTdelay_internal_op)
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
    LOG_DEBUG('Checking all session virtual orders how many orders finished and last time when order was finished...')
    
    ordersopen = dxbottools.getallmyordersbymarket(c.BOTsellmarket,c.BOTbuymarket)
    for i in range(s.ordersvirtualmax):
        
        # checking all virtual orders that has ID assigned, so is/was active
        if d.ordersvirtual[i]['id'] != 0:
            
            # try to match virtual-order with order by ID
            order = lookup_order_id_2(d.ordersvirtual[i]['id'], ordersopen)
            
            #debug log
            LOG_DEBUG('Order <{}> sell maker <{}> amount <{}> to buy taker <{}> amount <{}> status original <{}> to actual <{}> id <{}> market price <{}> order price <{}> description <{}>'
            .format(d.ordersvirtual[i]['vid'], d.ordersvirtual[i]['maker'], d.ordersvirtual[i]['maker_size'], d.ordersvirtual[i]['taker'], d.ordersvirtual[i]['taker_size'], 
            d.ordersvirtual[i]['status'], (order['status'] if (order is not None) else 'no status'), d.ordersvirtual[i]['id'], d.ordersvirtual[i]['market_price'], d.ordersvirtual[i]['order_price'], d.ordersvirtual[i]['name'] ))
            
            # if virtual order is clear BUT order is still in progress, skip this order, because is not finished yet
            if order__check_status(d.ordersvirtual[i], ifyes = [s.status_list__clear]):
                if order__check_status(order, ifyes = [s.status_list__l_in_progress]) == True:
                    LOG_DEBUG('virtual order <{}> is in progress... skipping...'.format(i))
                    continue
            
            # if virtual order previous status was not finished or clear and now finished is or was taken by takerbot, count this order in finished number
            if d.ordersvirtual[i]['status'] in s.status_list__valid_switch_to_finish:
                if (order is not None) and order['status'] == s.status_list__finished:
                    reset_afot__add()
                elif feature__takerbot__virtual_order_was_taken_get(d.ordersvirtual[i]) == True:
                    reset_afot__add()
            
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
        if d.orders_pending_to_reopen_opened > c.BOTmax_open_orders:
            LOG_FATAL('!!!! internal BUG Detected. DEBUG orders opened {0} orders finished {1} last time order finished {2}'.format(d.orders_pending_to_reopen_opened, d.orders_pending_to_reopen_finished, d.orders_pending_to_reopen_finished_time))
            sys.exit(1)
        
    # if previous status was open and now is not open, do not count this order in opened number
    if virtual_order['status'] in s.orders_pending_to_reopen_opened_statuses and ((actual_order is None) or actual_order['status'] not in s.orders_pending_to_reopen_opened_statuses):
        d.orders_pending_to_reopen_opened -= 1
        if d.orders_pending_to_reopen_opened < 0:
            LOG_FATAL('!!!! internal BUG Detected. DEBUG orders opened {0} orders finished {1} last time order finished {2}'.format(d.orders_pending_to_reopen_opened, d.orders_pending_to_reopen_finished, d.orders_pending_to_reopen_finished_time))
            sys.exit(1)
        
    # if previous status was not finished and now finished is, count this order in finished number
    if virtual_order['status'] != s.status_list__finished and (((actual_order is not None) and actual_order['status'] == s.status_list__finished) or finished_by_takerbot == True):
        d.orders_pending_to_reopen_finished += 1
        d.orders_pending_to_reopen_finished_time = time.time()
    
    # ~ LOG_DEBUG('orders opened {0} orders finished {1} last time order finished {2}'.format(d.orders_pending_to_reopen_opened, d.orders_pending_to_reopen_finished, d.orders_pending_to_reopen_finished_time))

# create order and update also corresponding virtual-order
def virtual_orders__create_one(order_id, order_name, price, slide_dyn, price_slide_dyn_boundary, slide, stageredslide, sell_amount, sell_amount_min):
    global c, s, d
    makermarketpriceslide = float(price_slide_dyn_boundary) * (slide + stageredslide)
    
    # limit precision to 6 digits
    sell_amount = '%.6f' % sell_amount
    
    buyamount = (float(sell_amount) * float(makermarketpriceslide))
    
    buyamount = float(fixed_fee__add_fee_int_amount(buyamount))
    
    # limit precision to 6 digits
    buyamount = '%.6f' % buyamount
    
    LOG_ACTION('Placing partial<{}> Order id <{}> name <{}> {}/{} >> at price {} * dynamic-slide {}/ boundary ->-> boundary-price {} * (slide {} + staggered-slide {}) ->-> final slide {} final-price {} to sell amount {} for buy amount {}'
          .format(c.BOTpartial_orders, order_id, order_name, c.BOTsellmarket, c.BOTbuymarket, price, slide_dyn, price_slide_dyn_boundary, slide, stageredslide, (slide + stageredslide), makermarketpriceslide, sell_amount, buyamount))
    
    if c.BOTpartial_orders is False:
        try:
            results = {}
            results = dxbottools.makeorder(c.BOTsellmarket, str(sell_amount), c.BOTmaker_address, c.BOTbuymarket, str(buyamount), c.BOTtaker_address, use_all_funds = not c.BOTaddress_funds_only)
            LOG_DEBUG('Exact Order placed - id: <{}>, maker_size: <{}>, taker_size: <{}>'.format(results['id'], results['maker_size'], results['taker_size']))
            # ~ logging.info('Order placed - id: {0}, maker_size: {1}, taker_size: {2}'.format(results['id'], results['maker_size'], results['taker_size']))
        except Exception as err:
            LOG_ERROR('exact ERROR: %s' % err)
    else:
        try:
            results = {}
            results = dxbottools.make_partial_order(c.BOTsellmarket, str(sell_amount), c.BOTmaker_address, c.BOTbuymarket, str(buyamount), c.BOTtaker_address, sell_amount_min, repost = False, use_all_funds = not c.BOTaddress_funds_only, auto_split = False)
            LOG_DEBUG('Partial Order placed - id: <{}>, maker_size: <{}>, taker_size: <{}>'.format(results['id'], results['maker_size'], results['taker_size']))
            # ~ logging.info('Order placed - id: {0}, maker_size: {1}, taker_size: {2}'.format(results['id'], results['maker_size'], results['taker_size']))
        except Exception as err:
            LOG_ERROR('partial ERROR: %s' % err)
    
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
    LOG_INFO('available balance >> txfee {} apply, sell amount original {} new {}'.format(sell_amount_txfee, sell_amount_tmp, sell_amount))
    
    #apply BOTbalance_save_number if enabled
    if c.BOTbalance_save_number != 0:
        balance_save_size = feature__balance_save_asset__convert_to_maker(c.BOTbalance_save_number)
        sell_amount_tmp = sell_amount
        sell_amount = min(sell_amount, sell_amount - balance_save_size)
        sell_amount = max(sell_amount, 0)
        LOG_INFO('available balance >> balance_save_number {} apply, sell amount original {} new {}'.format(balance_save_size, sell_amount_tmp, sell_amount))
        
    #apply BOTbalance_save_percent if enabled
    if c.BOTbalance_save_percent != 0:
        sell_amount_tmp = sell_amount
        sell_amount = min(sell_amount, sell_amount - (c.BOTbalance_save_percent * d.balance_maker_total))
        sell_amount = max(sell_amount, 0)
        LOG_INFO('available balance >> balance_save_percent {} apply, sell amount original {} new {}'.format(c.BOTbalance_save_percent, sell_amount_tmp, sell_amount))
    
    # apply maximum amount if enabled
    if sell_amount_max != 0:
        sell_amount_tmp = sell_amount
        sell_amount = min(sell_amount_max, sell_amount)
        LOG_INFO('available balance >> sell amount max {} apply, sell amount original {} new {}'.format(sell_amount_max, sell_amount_tmp, sell_amount))
    
    # apply minimum amount if enabled otherwise try to apply maximum as exact amount if enabled
    if sell_amount_min != 0:
        sell_amount_tmp = sell_amount
        if sell_amount < sell_amount_min:
            sell_amount = 0
        LOG_INFO('available balance >> sell amount min {} apply, sell amount original {} new {}'.format(sell_amount_min, sell_amount_tmp, sell_amount))
    elif sell_amount_max != 0:
        sell_amount_tmp = sell_amount
        if sell_amount_max != sell_amount:
            sell_amount = 0
        LOG_INFO('available balance >> strict sell amount max {} apply, sell amount original {} new {}'.format(sell_amount_max, sell_amount_tmp, sell_amount))
    
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
        LOG_WARNING('Pricing not available... waiting to restore...')
        time.sleep(c.BOTdelay_internal_error)
    
    d.reset_on_price_change_start = d.feature__maker_price__value_current_used
    
    # how many orders finished reset
    reset_afot__reset()
    
    d.time_start_reset_orders = time.time()
    
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
        LOG_WARNING('Pricing main not available... waiting to restore...')
        time.sleep(c.BOTdelay_internal_error)
    
    while True:
        if feature__slide_dyn__update_dyn_slide() == True:
            break
        LOG_WARNING('Pricing dynamic slide not available... waiting to restore...')
        time.sleep(c.BOTdelay_internal_error)
    
    if c.BOTbalance_save_asset_track is True:
        while True:
            if feature__balance_save_asset__pricing_update() != 0:
                break
            LOG_WARNING('Pricing of balance save asset not available... waiting to restore...')
            time.sleep(c.BOTdelay_internal_error)
    
    while True:
        if feature__sell_size_asset__pricing_update() != 0:
            break
        LOG_WARNING('Pricing of sell size asset not available... waiting to restore...')
        time.sleep(c.BOTdelay_internal_error)
        
    while True:
        if fixed_fee__asset_pricing_update() != 0:
            break
        LOG_WARNING('Pricing of fixed fee asset not available... waiting to restore...')
        time.sleep(c.BOTdelay_internal_error)
    
    while True:
        if sboundary__pricing_update() != 0:
            break
        LOG_WARNING('Pricing boundaries not available... waiting to restore...')
        time.sleep(c.BOTdelay_internal_error)
    
    while True:
        if rboundary__pricing_update() != 0:
            break
        LOG_WARNING('Pricing boundaries not available... waiting to restore...')
        time.sleep(c.BOTdelay_internal_error)
    
    events_wait_reopenfinished_reset_detect()
    
    # get open orders, match them with virtual orders, and check how many finished
    virtual_orders__check_status_update_status()

# function to scan all events that makes bot to exit
def events_exit_bot():
    global c, s, d
    ret = False
    
    LOG_DEBUG('checking for exit bot events')
    
    # detect and handle max static boundary exit event
    ret_hit, ret_exit, ret_cancel, ret_price = sboundary__check_max(d.feature__maker_price__value_current_used + (d.feature__maker_price__value_current_used * d.feature__slide_dyn__value))
    if ret_hit is True and ret_exit is True:
        if ret_cancel is True:
            virtual_orders__cancel_all()
        ret = True
    
    # detect and handle min static boundary exit event
    ret_hit, ret_exit, ret_cancel, ret_price = sboundary__check_min(d.feature__maker_price__value_current_used + (d.feature__maker_price__value_current_used * d.feature__slide_dyn__value))
    if ret_hit is True and ret_exit is True:
        if ret_cancel is True:
            virtual_orders__cancel_all()
        ret = True
        
    # detect and handle max relative boundary exit event
    ret_hit, ret_exit, ret_cancel, ret_price = rboundary__check_max(d.feature__maker_price__value_current_used + (d.feature__maker_price__value_current_used * d.feature__slide_dyn__value))
    if ret_hit is True and ret_exit is True:
        if ret_cancel is True:
            virtual_orders__cancel_all()
        ret = True
    
    # detect and handle min relative boundary exit event
    ret_hit, ret_exit, ret_cancel, ret_price = rboundary__check_min(d.feature__maker_price__value_current_used + (d.feature__maker_price__value_current_used * d.feature__slide_dyn__value))
    if ret_hit is True and ret_exit is True:
        if ret_cancel is True:
            virtual_orders__cancel_all()
        ret = True
    
    return ret
    
# function to scan all events that makes bot to reset orders
def events_reset_orders():
    global c, s, d
    
    LOG_DEBUG('checking for reset order events')
    
    # if reset on price change positive is set and price has been changed, break and reset orders
    if c.BOTreset_on_price_change_positive != 0 and d.feature__maker_price__value_current_used >= (d.reset_on_price_change_start * (1 + c.BOTreset_on_price_change_positive)):
        LOG_ACTION('Reset on positive price change {0}% has been reached: price stored / actual {1} / {2}, going to order reset now...'.format(c.BOTreset_on_price_change_positive, d.reset_on_price_change_start, d.feature__maker_price__value_current_used))
        return True
        
    # if reset on price change negative is set and price has been changed, break and reset orders
    if c.BOTreset_on_price_change_negative != 0 and d.feature__maker_price__value_current_used <= (d.reset_on_price_change_start * (1 - c.BOTreset_on_price_change_negative)):
        LOG_ACTION('Reset on negative price change {0}% has been reached: price stored / actual {1} / {2}, going to order reset now...'.format(c.BOTreset_on_price_change_negative, d.reset_on_price_change_start, d.feature__maker_price__value_current_used))
        return True
    
    # if reset after delay is set and reached break and reset orders
    if c.BOTreset_after_delay != 0 and (time.time() - d.time_start_reset_orders) > c.BOTreset_after_delay:
        LOG_ACTION('Maximum orders lifetime {0} / {1} has been reached, going to order reset now...'.format((time.time() - d.time_start_reset_orders), c.BOTreset_after_delay))
        return True
    
    if reset_afot__check() == True:
        return True
        
    return False

# automatically detect passed wait events so reset data
def events_wait_reopenfinished_reset_detect():
    global c, s, d
    
    if events_wait_reopenfinished_check_num_silent() == "reached" or events_wait_reopenfinished_check_delay_silent() == "reached":
        LOG_ACTION("reopen after finished reseting data...")
        d.orders_pending_to_reopen_finished = 0
        d.orders_pending_to_reopen_finished_time = 0;

# function to check bot have to wait, finished orders will be reopened after specific number of filled orders
def events_wait_reopenfinished_check_num_silent():
    global c, s, d
    
    # check if finished num is configured
    if c.BOTreopen_finished_num == 0:
        return "disabled"
    
    # this feature is activated only if at least one order has finished
    if d.orders_pending_to_reopen_finished > 0:
        # this feature is activated only if there is enough finished+open orders
        if (d.orders_pending_to_reopen_finished + d.orders_pending_to_reopen_opened) >= c.BOTreopen_finished_num:
            # wait if finished number has not been reached
            if d.orders_pending_to_reopen_finished < c.BOTreopen_finished_num:
                return "wait"
            else:
                return "reached"
                
    return "not ready"

# function to check bot have to wait, finished orders will be reopened after specific number of filled orders
def events_wait_reopenfinished_check_num():
    global c, s, d
    ret = events_wait_reopenfinished_check_num_silent()
    if ret == "wait":
        LOG_ACTION('Reopen finished order num {0} / {1} not reached, waiting...'.format(d.orders_pending_to_reopen_finished, c.BOTreopen_finished_num))
    
    return ret
    
# function to check bot have to wait, finished orders will be reopened after specific delay
def events_wait_reopenfinished_check_delay_silent():
    global c, s, d
    
    # check if finished delay is configured
    if c.BOTreopen_finished_delay == 0:
        return "disabled"
    
    # this feature is activated only if at least one order has finished
    if d.orders_pending_to_reopen_finished_time != 0:
        # wait if we already have some finished order time and delay not reached
        if (time.time() - d.orders_pending_to_reopen_finished_time) < c.BOTreopen_finished_delay:
            return "wait"
        else:
            return "reached"
    
    return "not ready"

# function to check bot have to wait, finished orders will be reopened after specific delay
def events_wait_reopenfinished_check_delay():
    global c, s, d
    ret = events_wait_reopenfinished_check_delay_silent()
    if ret == "wait":
        LOG_ACTION('Reopen finished orders delay {0} / {1} not reached, waiting...'.format((time.time() - d.orders_pending_to_reopen_finished_time), c.BOTreopen_finished_delay))
        
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
    
    LOG_DEBUG('checking for wait events')
    
    # wait if there is not enough balance to place order and pay fee
    if balance_available_to_sell_recompute() == 0:
        ret = True
    
    # check reopen after finished number or delay detection
    if events_wait_reopenfinished_check() == True:
        ret = True
    
    # detect and handle max static boundary event
    ret_hit, ret_exit, ret_cancel, ret_price = sboundary__check_max(d.feature__maker_price__value_current_used + (d.feature__maker_price__value_current_used * d.feature__slide_dyn__value))
    if ret_hit is True and ret_exit is False:
        if ret_cancel is True:
            virtual_orders__cancel_all()
        ret = True
    
    # detect and handle min static boundary event
    ret_hit, ret_exit, ret_cancel, ret_price = sboundary__check_min(d.feature__maker_price__value_current_used + (d.feature__maker_price__value_current_used * d.feature__slide_dyn__value))
    if ret_hit is True and ret_exit is False:
        if ret_cancel is True:
            virtual_orders__cancel_all()
        ret = True
        
    # detect and handle max relative boundary event
    ret_hit, ret_exit, ret_cancel, ret_price = rboundary__check_max(d.feature__maker_price__value_current_used + (d.feature__maker_price__value_current_used * d.feature__slide_dyn__value))
    if ret_hit is True and ret_exit is False:
        if ret_cancel is True:
            virtual_orders__cancel_all()
        ret = True
    
    # detect and handle min relative boundary event
    ret_hit, ret_exit, ret_cancel, ret_price = rboundary__check_min(d.feature__maker_price__value_current_used + (d.feature__maker_price__value_current_used * d.feature__slide_dyn__value))
    if ret_hit is True and ret_exit is False:
        if ret_cancel is True:
            virtual_orders__cancel_all()
        ret = True
    
    return ret

# function to compute and return amount of maker to be sold
def sell_amount_recompute(sell_start, sell_end, order_num_all, order_num_actual, sell_type):
    global c, s, d
    
    sell_amount = float(0)
    
    # sell amount old style random
    if c.BOTsell_random is True:
        sell_min = min(sell_start, sell_end)
        sell_max = max(sell_start, sell_end)
        sell_amount = random.uniform(sell_min, sell_max)
    
    # sell amount staggered
    else:
        # first order is always at exact position
        if order_num_actual == 0:
            sell_type_res = 0
            
        # linear staggered orders size distribution
        elif sell_type == 0:
            sell_type_res = order_num_actual / (order_num_all - 1)
        
        # exponential staggered order size distribution
        elif sell_type > 0:
            sell_type_res = (order_num_actual / order_num_all - 1)**(1-(sell_type))
        
        # logarithmic staggered order size distribution
        elif sell_type < 0:
            # ~ sell_type_res = (order_num_actual / order_num_all)**(1-(10*sell_type))
            sell_type_res = (order_num_actual / order_num_all - 1)**((float(100)**(sell_type*-1))+(sell_type*4.4))
        
        # sell amount = amount starting point + (variable amount * intensity) 
        sell_amount = sell_start + ((sell_end - sell_start) * sell_type_res)
        # ~ sell_amount = sell_start + (( (sell_end - sell_start) / max((order_num_all-1),1) )*order_num_actual)

    # sell amount limit to 6 decimal numbers
    sell_amount = float('%.6f' % sell_amount)
    
    return sell_amount

# function to loop all virtual orders and recreate em if needed
def virtual_orders__handle():
    global c, s, d
    
    LOG_DEBUG('checking for virtual orders to handle')
    
    # loop all virtual orders and try to create em
    
    # staggered orders handling
    for i in range(s.ordersvirtualmax):
        if d.ordersvirtual[i]['status'] in s.reopenstatuses:
            
            # update total available and reserve balances
            update_balances()
            
            # sse - sell size asset
            # compute dynamic order size range, apply <sell_type> linear/log/exp on maximum amount by order number distribution
            sell_amount_max_sse = sell_amount_recompute(c.BOTsell_start_max, c.BOTsell_end_max, s.ordersvirtualmax, i, c.BOTsell_type)
            sell_amount_min_sse = sell_amount_recompute(c.BOTsell_start_min, c.BOTsell_end_min, s.ordersvirtualmax, i, c.BOTsell_type)
            
            # convert sell size in sell size asset to maker asset
            sell_amount_max = sell_amount_max_sse * d.feature__sell_size_asset__price
            sell_amount_min = sell_amount_min_sse * d.feature__sell_size_asset__price
            
            # recompute sell amount by available balance, other limit conditions
            sell_amount = balance_available_to_sell_recompute(sell_amount_max, sell_amount_min)
            
            # convert final amount to sell to sell size asset amount
            sell_amount_sse = sell_amount / d.feature__sell_size_asset__price
            
            # recompute (price * dynamic slide) with configured boundaries
            sret_hit, sret_exit, sret_cancel, price_maker_with_boundaries = sboundary__check(d.feature__maker_price__value_current_used + (d.feature__maker_price__value_current_used * d.feature__slide_dyn__value))
            rret_hit, rret_exit, rret_cancel, price_maker_with_boundaries = rboundary__check(price_maker_with_boundaries)
            
            LOG_ACTION('Order maker size <{}/{} {}~{} min {}~{} final {}~{}>'.format(c.BOTsellmarket, c.BOTsell_size_asset, sell_amount_max, sell_amount_max_sse, sell_amount_min, sell_amount_min_sse, sell_amount, sell_amount_sse))
            
            if sell_amount == 0:
                # do not create next order on first 0 amount hit, so if first order is not created, also next not created
                if c.BOTmake_next_on_hit is True:
                    continue
                else:
                    break
                
            # first order is min slide
            if i == 0:
                if c.BOTsell_start_slide >= c.BOTsell_end_slide:
                    order_name = 'first staggered order with max-slide'
                else:
                    order_name = 'first staggered order with min-slide'
            # last order is max slide
            elif i == s.ordersvirtualmax -1:
                if c.BOTsell_start_slide >= c.BOTsell_end_slide:
                    order_name = 'last staggered order with max-slide'
                else:
                    order_name = 'last staggered order with min-slide'
            # any other orders between min and max slide
            else:
                order_name = 'middle staggered order'
            
            # compute staggered orders slides
            staggeredslide = ((c.BOTsell_end_slide - c.BOTsell_start_slide) / max((s.ordersvirtualmax -1),1 ))*i
            
            virtual_orders__create_one(i, order_name, d.feature__maker_price__value_current_used, d.feature__slide_dyn__value, price_maker_with_boundaries, c.BOTsell_start_slide, staggeredslide, sell_amount, sell_amount_min)
            time.sleep(c.BOTdelay_internal_op)
            
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
    
    LOG_DEBUG('checking for takerbot actions')
    
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
            # ~ LOG_DEBUG('\n\norders_market_sorted: <{}>'.format(orders_market_sorted))
            # ~ LOG_DEBUG('\n\norders_virtual_sorted: <{}>'.format(orders_virtual_sorted))
            
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
                                    
                                    LOG_ACTION('takerbot activated >>...')
                                    
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
                                    ret_takeorder = dxbottools.takeorder(orders_market_sorted[i]['order_id'], c.BOTtaker_address, c.BOTmaker_address)
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
    
    feature__tmp_cfg__load_saved_cfg()
    
    init_postconfig() # initialization of items dependent on config
    
    
    do_utils_and_exit() # if some utility are planned do them and exit program
    
    do_utils_cancel_orders_address()
    
    if pricing_check_or_error() != 0: # check if pricing works
        sys.exit(1)
    
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
            
            # keyboard interactions
            sleep_start = float(0)
            while sleep_start < c.BOTdelay_internal_loop:
                sleep_start += float(0.2)
                time.sleep(0.2)
                cli__try_read_cmd()
                
            # ~ log__update_keyboard_cfg()
            # ~ time.sleep(c.BOTdelay_internal_loop)
            
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
