#!/usr/bin/env python3

# ~ MIT License

# ~ Copyright (c) 2020-2025 NNMFNWL

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

# copy rpc settings from blocknet.conf
rpcuser = "{cc_rpc_user}"
rpcpassword = "{cc_rpc_password}"
rpchostname = "{cc_rpc_hostname}"
rpcport = {cc_rpc_port}

# Price redirections is feature used to optionally set custom ASSET 1 price in thirty ASSET 2.
# For example trading BLOCK with LTC, you would rather set BLOCK price manually in USDT and BOT automatically converts value into LTC.
# 
# format of price redirections:
#
#   "BLOCK": { "asset": "USDT", "price": 59},
#   "LTC": { "asset": "USDT", "price": 1299}
#
# full example of price redirections:
#
#   price_redirections = {
#       "BLOCK": { "asset": "USDT", "price": 59},
#       "LTC": { "asset": "USDT", "price": 1299}
#   }
#
price_redirections = {
{cc_price_redirections}
}

botconfig = str(
# configure bot to sell(maker) for buy(taker), for example BLOCK LTC BTC PIVX XVG DASH DOGE
# --maker         | asset being sold (default=BLOCK)
# --taker         | asset being bought (default=LTC)
    "--maker {cc_ticker_maker}"
    "--taker {cc_ticker_taker}"

# addresses of sitting funds
# --makeraddress  | trading address of asset being sold (default=None)
# --takeraddress  | trading address of asset being bought (default=None)
    "--makeraddress {cc_address_maker}"
    "--takeraddress {cc_address_taker}"

# limit bot to use and compute funds only from maker and taker address.True/False(default=False disabled)
    "--address_funds_only {cc_address_funds_only}"

# --balance_save_asset | size of balance to save is set in specific asset instead of maker(default=--maker)
# --balance_save_number | min taker balance you want to save and do not use for making orders specified by number (default=0)
# --balance_save_percent | min taker balance you want to save and do not use for making orders specified by percent of maker+taker balance (default=0.05 means 5%)
# do not save any maker balance
    # set size of balance to save in alternative asset
        # ~ "--balance_save_asset BLOCK"
    # --balance_save_asset_track | track balance save asset price updates. This means, ie if trading BLOCK/BTC on USD also track USD/BLOCK price and update balance to save by it (default=False disabled)
    # enable to track balance save asset price updates. This means, ie if trading BLOCK/BTC on USD also track USD/BLOCK price and update balance to save by it.
        # ~ "--balance_save_asset_track True"
    # set in absolute value or percentage how much maker to save(reserve)
        "--balance_save_number {cc_balance_save_number} --balance_save_percent {cc_balance_save_percent}"

# cleaning up canceled orders from internal xbridge list in specified interval
    "--flush_canceled_orders {cc_flush_canceled_orders}"

# bot will try to create orders with dynamic size if there is not balance available to create order at maximum. but only between <value, min value>
 #also takerbot is accepting at least order with size in range between <value, min value>
    # --sell_size_asset | size of orders are set in specific asset instead of maker (default=--maker)
        # lets say size of orders are set in USDT
            # ~ "--sell_size_asset USDT"
        # lets say size of orders are set in BLOCK
            "--sell_size_asset {cc_sell_size_asset}"
    # --sellstart | size of first order or random from range sellstart and sellend (default=0.001)
    # --sellstartmin | minimum acceptable size of first order. If this is configured and there is not enough balance to create first order at <sellstart> size, order will be created at maximum possible size between <sellstart> and <sellstartmin>. (default=0 disabled)
        # first placed order at maker size min 15 up to max 100 by available balance
            # ~ "--sellstart 100 --sellstartmin 15"
            "--sellstart {cc_sell_start} --sellstartmin {cc_sell_start_min}"
    # last placed order at maker size min 15 up to max 50 by available balance
    # --sellend | size of last order or random from range sellstart and sellend  (default=0.001)
    # --sellendmin | minimum acceptable size of last order. If this is configured and there is not enough balance to create last order at <sellend> size, order will be created at maximum possible size between <sellend> and <sellendmin>. (default=0 disabled)
        # ~ "--sellend 50 --sellendmin 15"
        "--sellend {cc_sell_end} --sellendmin {cc_sell_end_min}"
    
    # --sellrandom | orders size will be random number between sellstart and sellend, otherwise orders size sequence starting by sellstart amount and ending with sellend amount
        # Uncomment below line to activate"
        # ~ "--sellrandom"
        
# --sell_type is <float> number between -1 and 1. -1 means maximum exponential to 0 means linear to 1 means maximum logarithmic. Recommended middle range log and exp values are 0.8 and -0.45 (default=0 linear)
    # ~ "--sell_type 0.45"

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

# --maxopen | Max amount of orders to have open at any given time. Placing orders sequence: first placed order is at slidestart(price slide),sellstart(amount) up to slideend(price slide),sellend(amount), last order placed is slidepump if configured, is not counted into this number (default=5)
# configure bot to have 3 orders opened. all other orders between first and last order are automatically recomputed by number of orders and linearly distributed between <sellstart, sellstartmin> and <sellend, sellendmin>
# so if bot have order size from <1> up to <6> and max number of orders is 3 middle will be 3.5, so orders will be <1> <3.5> <6>
    "--maxopen {cc_max_open_orders}"

# --make_next_on_hit | create next order on 0 amount hit, so if some order failed to be created, it is rather skipped, and next is created(default=False disabled)
    # ~ "--make_next_on_hit True"
    "--make_next_on_hit {cc_make_next_on_hit}"

# --partial_orders | enable or disable partial orders. Partial orders minimum is set by <sellstartmin> <sellendmin> along with dynamic size of orders(default=False disabled)
# enable or disable partial orders. Partial orders minimum is set by <sellstartmin> <sellendmin> along with dynamic size of orders(default=False disabled)
    # ~ "--partial_orders True"
    "--partial_orders {cc_partial_orders}"

# --slidestart | price of first order will be equal to slidestart * price source quote(default=1.01 means +1%)
# --slideend   | price of last order will be equal to slideend * price source quote(default=1.021 means +2.1%)
# first order at price slide to 110%(if price is 1 USD final is 1.10 USD), second order with price slide 106.5% and last order with price slide to 103%
    # ~ "--slidestart 1.10 --slideend 1.03"
    "--slidestart {cc_sell_start_spread} --slideend {cc_sell_end_spread}"

# no pump order. pump and dump orders are very useful, in case of pump you can buy back more and cheap.
    "--slidepump 0 --pumpamount 0 --pumpamountmin 0"

# Enabled dynamic slide based on maker amount and selling or buying maker.
# static type is based on difference between configured static maker amount and actual maker amount
# relative type is based on difference between relative to maker+taker amount and actual maker amount

    "--slide_dyn_asset {cc_slide_dyn_asset}"
        # dynamic slide static values are set in specific asset instead of maker (default=--maker)
    "--slide_dyn_asset_track {cc_slide_dyn_asset_track}"
        # enable to track dynamic dyn asset price updates. This means, ie if trading BLOCK/BTC on USD also track USD/BLOCK price and update dynamic slide zero asset price by it.
    
    "--slide_dyn_zero_type {cc_slide_dyn_zero_type}"
    "--slide_dyn_zero {cc_slide_dyn_zero}"
        # relative to maker+taker or static value when dynamic slide is 0.(default=relative)
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
        
    "--slide_dyn_type {cc_slide_dyn_type}"
        # relative to maker+taker or static values of, ignore, threshold
    
    "--slide_dyn_sell_ignore {cc_slide_dyn_sell_ignore}"
        # dynamic slide sell ignore is amount of maker that could be sold and no dyn slide will be activated.
    "--slide_dyn_sell_threshold {cc_slide_dyn_sell_threshold}"
        # every reached sell threshold will do a one dynamic slide sell step
        # (default=0.02 at slide_dyn_type=relative, it means, every time 2%% of maker is sold, slide will be increased by slide_dyn_sell_step)
    "--slide_dyn_sell_step {cc_slide_dyn_sell_step}"
        # dynamic slide addition for every reached sell threshold
    "--slide_dyn_sell_step_multiplier {cc_slide_dyn_sell_step_multiplier}"
        # dynamic slide addition stacking multiplier
    "--slide_dyn_sell_max {cc_slide_dyn_sell_max}"
        # maximum dynamic slide for sell operations, 0 means disabled
        
    "--slide_dyn_buy_ignore {cc_slide_dyn_buy_ignore}"
        # dynamic slide buy ignore is amount of maker that could be bought and no dyn slide will be activated.
    "--slide_dyn_buy_threshold {cc_slide_dyn_buy_threshold}"
        # every reached buy threshold will do a one dynamic slide sell step
        # (default=0.02 at slide_dyn_type=relative, it means, every time 2%% of maker is bought, slide will be increased by slide_dyn_buy_step)
    "--slide_dyn_buy_step {cc_slide_dyn_buy_step}"
        # dynamic slide addition for every reached buy threshold
    "--slide_dyn_buy_step_multiplier {cc_slide_dyn_buy_step_multiplier}"
        # dynamic slide addition stacking multiplier
    "--slide_dyn_buy_max {cc_slide_dyn_buy_max}"
        # maximum dynamic slide for buy operations, 0 means disabled)

# --reopenfinishednum | reopen finished orders after specific number of filled orders(default=0 means disabled)
# recreate order when 2 orders are accepted
    # ~ "--reopenfinishednum 2"
    "--reopenfinishednum {cc_reopen_finished_num}"
# --reopenfinisheddelay | reopen finished orders after specific delay of last filled order(default=0 means disabled)
# recreate orders by 600seconds timeout of last taken/accepted order
    # ~ "--reopenfinisheddelay 600"
    "--reopenfinisheddelay {cc_reopen_finished_delay}"

# reset all orders on positive +0.1% price change, but on negative price change, reset only when will reach -0.5% price change
    # ~ "--resetonpricechangepositive 0.01"
    # ~ "--resetonpricechangenegative 0.05"
    "--resetonpricechangepositive {cc_reset_on_price_change_positive}"
    "--resetonpricechangenegative {cc_reset_on_price_change_negative}"

# do not reset all orders at timer, reset all orders when 3 orders are taken/accepted, do not reset orders on timer when some order is accepted
    # ~ "--resetafterdelay 0"
    # ~ "--resetafterorderfinishnumber 3"
    # ~ "--resetafterorderfinishdelay 0"
    "--resetafterdelay {cc_reset_after_delay}"
    "--resetafterorderfinishnumber {cc_reset_after_order_finish_number}"
    "--resetafterorderfinishdelay {cc_reset_after_order_finish_delay}"


# static boundaries configuration:
    # set boundaries in specific asset rather than taker
        "--sboundary_asset {cc_sboundary_asset}"
    # boundary set in static specific price
        "--sboundary_max {cc_sboundary_max}"
        "--sboundary_min {cc_sboundary_min}"
    
    # enabled disable boundary asset price updates. This means, ie if trading BLOCK/BTC but boundary is set in USD, it also do USD/BTC price updates and dynamically update boundary according to.
        "--sboundary_max_track_asset {cc_sboundary_max_track_asset}"
        "--sboundary_min_track_asset {cc_sboundary_min_track_asset}"
    
    # Enable reversed pricing as 1/X, ie BLOCK/BTC vs BTC/BLOCK pricing can set like 0.000145 on both bot trading sides, instead of 0.000145 vs 6896.55.
        "--sboundary_price_reverse {cc_sboundary_price_reverse}"
    
    # maximum boundary hit behavior True/False
    # cancel orders on max boundary. The reason can be user is not willing to continue selling his maker-asset once price is too high bc expected bullmarket and user rather start staking
        "--sboundary_max_cancel {cc_sboundary_max_cancel}"
        "--sboundary_max_exit {cc_sboundary_max_exit}"
    # minimum boundary hit behavior True/False
    # do not cancel orders on min boundary, but rather keep open orders on minimum boundary. The reason can be user is not willing to sell his maker-asset by very low price, rather wait for price recover
        "--sboundary_min_cancel {cc_sboundary_min_cancel}"
        "--sboundary_min_exit {cc_sboundary_min_exit}"


# set relative maximum and minimum maker price boundaries
    # set relative boundary values in specific asset
    # ie.: Static boundary with maker/taker BLOCK/BTC and boundary_asset is USDT, so possible boundary min 1.5 and max 3 USD (default= --taker)'
        "--rboundary_asset {cc_rboundary_asset}"
    # manually set initial center price. Its usable only when some boundary_max/min_asset_track is Disabled
        "--rboundary_price_initial {cc_rboundary_price_initial}"
    
    # maximum and minimum acceptable price set as relative value to center price
    # set max at 150% and min 95% of price when bot was started as 1.5 0.95
        "--rboundary_max {cc_rboundary_max}"
        "--rboundary_min {cc_rboundary_min}"
    
    # Track boundary asset price updates. This means, ie if trading BLOCK/BTC on USD also track USD/BTC price and update boundaries by it
    # True/False
        "--rboundary_max_track_asset {cc_rboundary_max_track_asset}"
        "--rboundary_min_track_asset {cc_rboundary_min_track_asset}"
    
    # reversed set pricing as 1/X, ie BLOCK/BTC vs BTC/BLOCK pricing can set like 0.000145 on both bot trading sides, instead of 0.000145 vs 6896.55.'
    # this feature works with relative boundary asset as well
        "--rboundary_price_reverse {cc_rboundary_price_reverse}"
    
    # maximum boundary hit behavior True/False
    # cancel orders on max boundary. The reason can be user is not willing to continue selling his maker-asset once price is too high bc expected bullmarket and user rather start staking
        "--rboundary_max_cancel {cc_rboundary_max_cancel}"
        "--rboundary_max_exit {cc_rboundary_max_exit}"
    # minimum boundary hit behavior True/False
    # do not cancel orders on min boundary, but rather keep open orders on minimum boundary. The reason can be user is not willing to sell his maker-asset by very low price, rather wait for price recover
        "--rboundary_min_cancel {cc_rboundary_min_cancel}"
        "--rboundary_min_exit {cc_rboundary_min_exit}"
    

# takerbot act like limit orders on your actually created orders, its also taking whole range of dynamic size and multiple orders
    # enabled takerbot feature to check orders to take on 10 second interval
        "--takerbot {cc_takerbot}"
   
# delay between internal operations 2.3s
    "--delayinternal {cc_delay_internal}"
# check price every 60 seconds
    "--delaycheckprice {cc_delay_check_price}"
# sleep delay, in seconds, when error happen to try again. (default=10)
    "--delayinternalerror {cc_delay_internal_error}"
# sleep delay, in seconds, between main loops to process all things to handle
    "--delayinternalcycle {cc_delay_internal_cycle}"

# Value for live price updates or static price configuration'
#       0 - live price updates are activated
#       -1 - local one time price activated, center price is loaded from remote source and saved int cfg file every time bot starts, even not updated after crash
#       -2 - local long term price activated, center price is loaded from remote source and saved into cfg file only once, even not updated after restart/crash
#   Other than 0, -1, or -2 values are invalid
#   Even if center price is configured like-static, spread and dynamic spread should take care about order position management, this like system dexbot is able to handle situations when no pricing source is available, but it is up to user how to configure price movement
#   There is also another special pricing configuration feature called "price_redirections", seach in this file for details
     "--maker_price {cc_maker_price}"

# Pricing is based off BTC-XXX market pairs. For example, if running on the LTC-DASH market, the bot pulls the price
# for BTC-LTC and BTC-DASH then automatically calculates LTC-DASH price. This is how it works for all supported pricing sources:
#   * Bittrex: default (no flag)
#   * CryptoBridge: `--usecb`
#   * CoinGecko: `--usecg`
#   * Custom pricing: `--usecustom`
# use alternative coingecko insted of bittrex
    # ~ "--usecg"
    "{cc_price_source_argval}"
# enable exceptions in configuration values
    # ~ "--imreallysurewhatimdoing"
    "{cc_im_really_sure_what_im_doing_argval}"
)
