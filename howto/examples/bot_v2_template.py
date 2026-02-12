#!/usr/bin/env python3

# ~ MIT License

# ~ Copyright (c) 2020-2026 NNMFNWL

# ~ Permission is hereby granted, free of charge, to any person obtaining a copy
# ~ of this software and associated documentation files (the "Software"), to deal
# ~ in the Software without restriction, including without limitation the rights
# ~ to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# ~ copies of the Software, and to permit persons to whom the Software is
# ~ furnished to do so, subject to the following conditions:

# ~ The above copyright notice and this permission notice shall be included in all
# ~ copies or substantial portions of the Software.

# ~ THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# ~ IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# ~ FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# ~ AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# ~ LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# ~ OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# ~ SOFTWARE.

########################################################################

cfg = {}

cfg['rpc_user'] = "{cc_rpc_user}"
cfg['rpc_password'] = "{cc_rpc_password}"
cfg['rpc_hostname'] = "{cc_rpc_hostname}"
cfg['rpc_port'] = "{cc_rpc_port}"

cfg['price_redirections'] = { {cc_price_redirections} }

cfg['maker_ticker'] = "{cc_maker_ticker}"
cfg['taker_ticker'] = "{cc_taker_ticker}"

# --maker_address  | trading address of asset being sold (default=None)
cfg['maker_address'] = "{cc_address_maker}"
# --taker_address  | trading address of asset being bought (default=None)
cfg['taker_address'] = "{cc_address_taker}"

# limit bot to use and compute funds only from maker and taker address.True/False(default=False disabled)
cfg['address_funds_only'] = "{cc_address_funds_only}"

# size of balance to save is set in specific asset instead of maker(default=--maker)
cfg['balance_save_asset'] = "{cc_balance_save_asset}" 
# min taker balance you want to save and do not use for making orders specified by number (default=0)
cfg['balance_save_number'] = "{cc_balance_save_number}"
# min taker balance you want to save and do not use for making orders specified by percent of maker+taker balance (default=0.05 means 5%)
cfg['balance_save_percent'] = "{cc_balance_save_percent}"
# track balance save asset price updates. This means, ie if trading BLOCK/BTC on USD also track USD/BLOCK price and update balance to save by it (default=False disabled)
cfg['balance_save_asset_track'] = "{cc_balance_save_asset_track}"
# enable to track balance save asset price updates. This means, ie if trading BLOCK/BTC on USD also track USD/BLOCK price and update balance to save by it.

# cleaning up canceled orders from internal xbridge list in specified interval
cfg['flush_canceled_orders'] = "{cc_flush_canceled_orders}"

# size of orders are set in specific asset instead of maker (default=--maker)
cfg['sell_size_asset'] = "{cc_sell_size_asset}"


    
        # first placed order at maker size min 15 up to max 100 by available balance
            # ~ "--sell_start_max 100 --sell_start_min 15"
            
"""First order maximum possible size or random from range sell_start_max and sell_end_max (default=0.001).
In theory we need bot to try to create orders in dynamic size if there is not enough balance available to create order at maximum. But only between <value, min value>, because of transaction fees."""
cfg['sell_start_max'] = "{cc_sell_start_max}"
"""First order minimum possible acceptable size or random from range sell_start_min and sell_end_min (default=0 disabled).
In theory If this is configured and there is not enough balance to create first order at <sell_start_max> size, order will be created at maximum possible size between <sell_start_max> and <sell_start_min>. 
"""
cfg['sell_start_min'] = "{cc_sell_start_min}"

    # last placed order at maker size min 15 up to max 50 by available balance
    # --sell_end_max | size of last order or random from range sell_start_max and sell_end_max  (default=0.001)
    # --sell_end_min | minimum acceptable size of last order. If this is configured and there is not enough balance to create last order at <sell_end_max> size, order will be created at maximum possible size between <sell_end_max> and <sell_end_min>. (default=0 disabled)
        # ~ "--sell_end_max 50 --sell_end_min 15"
cfg['sell_end_max'] = "{cc_sell_end_max}"
cfg['sell_end_min'] = "{cc_sell_end_min}"

# """orders size will be random number between sell_start_max and sell_end_max, otherwise sequence of orders starting by sell_start_max amount and ending with sell_end_max amount(default=disabled)""", None)
cfg['sell_random'] = "{cc_sell_random}"

# sell_type is <float> number between -1 and 1. -1 means maximum exponential to 0 means linear to 1 means maximum logarithmic. Recommended middle range log and exp values are 0.8 and -0.45 (default=0 linear)
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
#
cfg['sell_type'] = "{cc_sell_type}"

# --max_open_orders | Max amount of orders to have open at any given time. Placing orders sequence: first placed order is at sell_start_slide(price slide),sell_start_max(amount) up to sell_end_slide(price slide),sell_end_max(amount), last order placed is pump_slide if configured, is not counted into this number (default=5)
# configure bot to have 3 orders opened. all other orders between first and last order are automatically recomputed by number of orders and linearly distributed between <sell_start_max, sell_start_min> and <sell_end_max, sell_end_min>
# so if bot have order size from <1> up to <6> and max number of orders is 3 middle will be 3.5, so orders will be <1> <3.5> <6>
cfg['max_open_orders'] = "{cc_max_open_orders}"

# --make_next_on_hit | create next order on 0 amount hit, so if some order failed to be created, it is rather skipped, and next is created(default=False disabled)
cfg['make_next_on_hit'] = "{cc_make_next_on_hit}"

# --partial_orders | enable or disable partial orders. Partial orders minimum is set by <sell_start_min> <sell_end_min> along with dynamic size of orders(default=False disabled)
# enable or disable partial orders. Partial orders minimum is set by <sell_start_min> <sell_end_min> along with dynamic size of orders(default=False disabled)
cfg['partial_orders'] = "{cc_partial_orders}"

# --sell_start_slide | price of first order will be equal to sell_start_slide * price source quote(default=1.01 means +1%)
# --sell_end_slide   | price of last order will be equal to sell_end_slide * price source quote(default=1.021 means +2.1%)
# first order at price slide to 110%(if price is 1 USD final is 1.10 USD), second order with price slide 106.5% and last order with price slide to 103%
    # ~ "--sell_start_slide 1.10 --sell_end_slide 1.03"
cfg['sell_start_slide'] = "{cc_sell_start_slide}"
cfg['sell_end_slide'] = "{cc_sell_end_slide}"

# no pump order. pump and dump orders are very useful, in case of pump you can buy back more and cheap.
cfg['pump_slide'] = "{cc_pump_slide}"
cfg['pump_amount_max'] = "{cc_pump_amount_max}"
cfg['pump_amount_min'] = "{cc_pump_amount_min]"


# Enabled dynamic slide based on maker amount and selling or buying maker.
# static type is based on difference between configured static maker amount and actual maker amount
# relative type is based on difference between relative to maker+taker amount and actual maker amount
# dynamic slide static values are set in specific asset instead of maker (default=--maker)
cfg['slide_dyn_asset'] = "{cc_slide_dyn_asset}"
# enable to track dynamic dyn asset price updates. This means, ie if trading BLOCK/BTC on USD also track USD/BLOCK price and update dynamic slide zero asset price by it.
cfg['slide_dyn_asset_track'] = "{cc_slide_dyn_asset_track}"

# relative to maker+taker or static maker value when dynamic slide is 0.(default=relative)
cfg['slide_dyn_zero_type'] = "{cc_slide_dyn_zero_type}"
# Relative(to maker+taker balance) or static specific value when dynamic slide intensity is 0%%.
#  Value -1 means, to autoconfig value to intensity be 0%% for bot startup MAKER/TAKER amounts.
#  Value -2 means, bot will first try to load value from previous run otherwise same like -1 value
#  Otherwise it means value=(maker+taker*dyn_zero) at which dynamic slide is at 0%% intensity.
#  ie, #1 at type=relative, zero=0.5, means 0%% dyn slide at 50:50 balance converted to zero_asset,
#  ie, #2 at type=relative, zero=1.0, means 0%% dyn slide at 100%% of balance in MAKER,
#  ie, #3 at type=relative, zero=0.0, means 0%% intensity at 100%% of balance in TAKER.
# Static value means static amount of maker where dynamic slide intensity is at 0%%.
#  ie, #4 at type=static, zero=120, slide_dyn_asset=USDT, slide_dyn_asset_track=True
#   is zero also updated by price of USDT/MAKER'
# (default=-2 autoconfig)', default=-2)
cfg['slide_dyn_zero_value'] = "{cc_slide_dyn_zero_value}"

# relative to maker+taker or static values of, ignore, threshold
cfg['slide_dyn_type'] = "{cc_slide_dyn_type}"

    # dynamic slide sell ignore is amount of maker that could be sold and no dyn slide will be activated.
cfg['slide_dyn_sell_ignore'] = "{cc_slide_dyn_sell_ignore}"
    # every reached sell threshold will do a one dynamic slide sell step
    # (default=0.02 at slide_dyn_type=relative, it means, every time 2%% of maker is sold, slide will be increased by slide_dyn_sell_step)
cfg['slide_dyn_sell_threshold'] = "{cc_slide_dyn_sell_threshold}"
    # dynamic slide addition for every reached sell threshold
cfg['slide_dyn_sell_step'] = "{cc_slide_dyn_sell_step}"
    # dynamic slide addition stacking multiplier
cfg['slide_dyn_sell_step_multiplier'] = "{cc_slide_dyn_sell_step_multiplier}"
    # maximum dynamic slide for sell operations, 0 means disabled
cfg['slide_dyn_sell_max'] = "{cc_slide_dyn_sell_max}"
    # dynamic slide buy ignore is amount of maker that could be bought and no dyn slide will be activated.
cfg['slide_dyn_buy_ignore'] = "{cc_slide_dyn_buy_ignore}"
    # every reached buy threshold will do a one dynamic slide sell step
    # (default=0.02 at slide_dyn_type=relative, it means, every time 2%% of maker is bought, slide will be increased by slide_dyn_buy_step)
cfg['slide_dyn_buy_threshold'] = "{cc_slide_dyn_buy_threshold}"
    # dynamic slide addition for every reached buy threshold
cfg['slide_dyn_buy_step'] = "{cc_slide_dyn_buy_step}"
    # dynamic slide addition stacking multiplier
cfg['slide_dyn_buy_step_multiplier'] = "{cc_slide_dyn_buy_step_multiplier}"
    # maximum dynamic slide for buy operations, 0 means disabled)
cfg['slide_dyn_buy_max'] = "{cc_slide_dyn_buy_max}"


    # --reopen_finished_num | reopen finished orders after specific number of filled orders(default=0 means disabled)
    # recreate order when 2 orders are accepted
    # ~ "--reopen_finished_num 2"
cfg['reopen_finished_num'] = "{cc_reopen_finished_num}"
    # --reopen_finished_delay | reopen finished orders after specific delay of last filled order(default=0 means disabled)
    # recreate orders by 600seconds timeout of last taken/accepted order
    # ~ "--reopen_finished_delay 600"
cfg['reopen_finished_delay'] = "{cc_reopen_finished_delay}"

    # reset all orders on positive +0.1% price change, but on negative price change, reset only when will reach -0.5% price change
    # ~ "--reset_on_price_change_positive 0.01"
    # ~ "--reset_on_price_change_negative 0.05"
cfg['reset_on_price_change_positive'] = "{cc_reset_on_price_change_positive}"
cfg['reset_on_price_change_negative'] = "{cc_reset_on_price_change_negative}"

"""keep resetting orders in specific number of seconds (default=0 disabled)"""
cfg['reset_after_delay'] = "{cc_reset_after_delay}"
"""number of orders to be finished before resetting orders (default=0 disabled)"""
cfg['reset_after_order_finish_number'] = "{cc_reset_after_order_finish_number}"
"""delay after finishing last order before resetting orders in seconds (default=0 disabled)"""
cfg['reset_after_order_finish_delay'] = "{cc_reset_after_order_finish_delay}"

# static boundaries configuration:

    # set boundaries in specific asset rather than taker
cfg['sboundary_asset'] = "{cc_sboundary_asset}"
"""maximum acceptable price of maker(sold one) where bot will stop selling(default=0 disabled)"""
cfg['sboundary_max'] = "{cc_sboundary_max}"
"""minimum acceptable price of maker(sold one) where bot will stop selling(default=0 disabled)"""
cfg['sboundary_min'] = "{cc_sboundary_min}"
    
    # enabled disable boundary asset price updates. This means, ie if trading BLOCK/BTC but boundary is set in USD, it also do USD/BTC price updates and dynamically update boundary according to.
"""Track boundary asset price updates. This means, ie if trading BLOCK/BTC on USD also track USD/BTC price and update boundaries by it (default=False disabled)"""
cfg['sboundary_max_track_asset'] = "{cc_sboundary_max_track_asset}"
"""Track boundary asset price updates. This means, ie if trading BLOCK/BTC on USD also track USD/BTC price and update boundaries by it (default=False disabled)"""
cfg['sboundary_min_track_asset'] = "{cc_sboundary_min_track_asset}"
    
    # Enable reversed pricing as 1/X, ie BLOCK/BTC vs BTC/BLOCK pricing can set like 0.000145 on both bot trading sides, instead of 0.000145 vs 6896.55.
cfg['sboundary_price_reverse'] = "{cc_sboundary_price_reverse}"
    
    # maximum boundary hit behavior True/False
    # cancel orders on max boundary. The reason can be user is not willing to continue selling his maker-asset once price is too high bc expected bullmarket and user rather start staking
cfg['sboundary_max_cancel'] = "{cc_sboundary_max_cancel}"
cfg['sboundary_max_exit'] = "{cc_sboundary_max_exit}"
    # minimum boundary hit behavior True/False
    # do not cancel orders on min boundary, but rather keep open orders on minimum boundary. The reason can be user is not willing to sell his maker-asset by very low price, rather wait for price recover
cfg['sboundary_min_cancel'] = "{cc_sboundary_min_cancel}"
cfg['sboundary_min_exit'] = "{cc_sboundary_min_exit}"


# set relative maximum and minimum maker price boundaries

    # set relative boundary initial price values in specific asset
cfg['rboundary_asset'] = "{cc_rboundary_asset}"
    # manually set initial center price. Its usable only when some boundary_max/min_asset_track is Disabled
cfg['rboundary_price_initial'] = "{cc_rboundary_price_initial}"
    
    # maximum acceptable price set as relative value to center price
    # To set maximum to 150% value is 1.5
cfg['rboundary_max'] = "{cc_rboundary_max}"
    # minimum acceptable price set as relative value to center price
    # To set minimum to 95% value is 0.95.
cfg['rboundary_min'] = "{cc_rboundary_min}"
    
    # Track boundary asset price updates. This means, ie if trading BLOCK/BTC on USD also track USD/BTC price and update boundaries by it
    # True/False
cfg['rboundary_max_track_asset'] = "{cc_rboundary_max_track_asset}"
cfg['rboundary_min_track_asset'] = "{cc_rboundary_min_track_asset}"
    
    # initial center pricing been set as reversed as 1/X, ie BLOCK/BTC vs BTC/BLOCK pricing can set like 0.000145 on both bot trading sides, instead of 0.000145 vs 6896.55.'
    # (default=False Disabled)
cfg['rboundary_price_reverse'] = "{cc_rboundary_price_reverse}"


"""cancel orders at max boundary hit, (default=True enabled)"""
cfg['rboundary_max_cancel'] = "{cc_rboundary_max_cancel}"
"""exit bot at max boundary hit, (default=True enabled)
The reason can be user is not willing to continue selling his maker-asset once price is too high bc expected bullmarket and user rather start staking"""
cfg['rboundary_max_exit'] = "{cc_rboundary_max_exit}"

"""cancel orders at min boundary hit, (default=True enabled)"""
cfg['rboundary_min_cancel'] = "{cc_rboundary_min_cancel}"
"""exit bot at min boundary hit, (default=False disabled)
Do not cancel orders on min boundary, but rather keep open orders on minimum boundary. The reason can be user is not willing to sell his maker-asset by very low price, rather wait for price recover"""
cfg['rboundary_min_exit'] = "{cc_rboundary_min_exit}"

    # takerbot act like limit orders on your actually created orders, its also taking whole range of dynamic size and multiple orders
    # enabled takerbot feature to check orders to take on 10 second interval
    #also takerbot is accepting at least order with size in range between <value, min value>
cfg['takerbot'] = "{cc_takerbot}"
   
    # delay between internal operations 2.3s
cfg['delay_internal_op'] = "{cc_delay_internal_op}"
    # check price every 60 seconds
cfg['delay_check_price'] = "{cc_delay_check_price}"
    # sleep delay, in seconds, when error happen to try again. (default=10)
cfg['delay_internal_error'] = "{cc_delay_internal_error}"
    # sleep delay, in seconds, between main loops to process all things to handle
cfg['delay_internal_loop'] = "{cc_delay_internal_cycle}"

# Value for live price updates or static price configuration'
#       0 - live price updates are activated
#       -1 - local one time price activated, center price is loaded from remote source and saved int cfg file every time bot starts, even not updated after crash
#       -2 - local long term price activated, center price is loaded from remote source and saved into cfg file only once, even not updated after restart/crash
#   Other than 0, -1, or -2 values are invalid
#   Even if center price is configured like-static, spread and dynamic spread should take care about order position management, this like system dexbot is able to handle situations when no pricing source is available, but it is up to user how to configure price movement
#   There is also another special pricing configuration feature called "price_redirections", seach in this file for details
cfg['maker_price'] = "{cc_maker_price}"

# Pricing is based off BTC-XXX market pairs. For example, if running on the LTC-DASH market, the bot pulls the price
# for BTC-LTC and BTC-DASH then automatically calculates LTC-DASH price. This is how it works for all supported pricing sources:

    # Price providers: "cg" - coingecko
cfg['price_provider'] = "{cc_price_provider}"
    # Acceptable external pricing outage in seconds, previous price is used for time of outage.
cfg['price_acceptable_outage'] = "{cc_price_acceptable_outage}"
    # Extra slide added to price in percent if outage happens. 1.05 means price+5%
cfg['price_outage_extra_slide'] = "{cc_price_outage_extra_slide}"
    
    # enable exceptions in configuration values
cfg['im_really_sure_what_im_doing'] = "{cc_im_really_sure_what_im_doing}"
