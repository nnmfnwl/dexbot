#!/usr/bin/python3

# dynamic slide computed by balance changes

import time

import features.glob as glob
c = glob.c
s = glob.s
d = glob.d

from features.tmp_cfg import *

# preconfiguration  initialization
def feature__slide_dyn__init_preconfig__():
    
    d.feature__slide_dyn__value = 0
    
    d.feature__slide_dyn__zero_asset_price = 0
    
    c.feature__slide_dyn__zero_value = None
    
    c.feature__slide_dyn__maker_price_value_startup = None
    
    d.feature__slide_dyn__get_price_fn = None
    
feature__slide_dyn__init_preconfig__()

# define argument parameter
def feature__slide_dyn__load_config_define(parser, argparse):
    
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

# parse configuration value
def feature__slide_dyn__load_config_postparse(args):
    
    c.BOTslide_dyn_asset = args.slide_dyn_asset
    
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
    
# verify argument value after load
def feature__slide_dyn__load_config_verify():
    
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
        
# asset which dynamic slide zero size is set in pricing update
def feature__slide_dyn__asset_pricing_update():
    
    temp_price = pricing_storage__try_get_price(c.BOTslide_dyn_asset, c.BOTsellmarket)
    if temp_price != 0:
        d.feature__slide_dyn__asset_price = temp_price
    
    return temp_price

# convert asset which dynamic slide zero size is set to maker 
def feature__slide_dyn__asset_convert_to_maker(size_in_slide_dyn_asset):
    
    return d.feature__slide_dyn__asset_price * size_in_slide_dyn_asset
    
# convert maker to asset which dynamic slide zero size is set in
def feature__slide_dyn__maker_convert_to_asset(size_in_slide_dyn_maker):
    
    return size_in_slide_dyn_maker / d.feature__slide_dyn__asset_price

def feature__slide_dyn__get_price_cb__(maker, taker):
    print('**** ERROR >>> dexbot.features.slide_dyn.feature__slide_dyn__get_price_cb__() function is just empty default callback, please replace with pricing_storage__try_get_price')
    return 0

# initialize dynamic slide feature
def feature__slide_dyn__init_postpricing(maker, taker, get_price_fn = feature__slide_dyn__get_price_cb__):
    
    if c.BOTslide_dyn_asset is None:
        c.BOTslide_dyn_asset = taker
        
    d.feature__slide_dyn__maker = maker
    d.feature__slide_dyn__taker = taker
    d.feature__slide_dyn__get_price_fn = get_price_fn
    
    # try to restore maker price when slide zero is -2 or restore is true
    if (c.BOTaction_arg != "reset") and (c.BOTslide_dyn_zero == -2 or c.BOTaction_arg == 'restore'):
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
            if (c.BOTaction_arg != 'reset') and (c.BOTslide_dyn_zero == -2 or c.BOTaction_arg == 'restore'):
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
            if (c.BOTaction_arg != 'reset') and (c.BOTslide_dyn_zero == -2 or c.BOTaction_arg == 'restore'):
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
    
    # apply dynamic slide maximum, can be also negative, zero means unlimited
    if tmp_max_final > 0:
        slide_dyn_final = min(slide_dyn_final, tmp_max_final)
    elif tmp_max_final < 0:
        slide_dyn_final = max(slide_dyn_final, tmp_max_final)
    
    # ~ print('>>>> dynamic_slide >> <'+str(case_buy_sell)+'> zero type <')
    print('>>>> DYNAMIC_SLIDE >> <'+str(case_buy_sell)+'> dyn zero at <'+str(c.BOTslide_dyn_zero_type)+' '+str(c.BOTslide_dyn_zero)+'~'+str(c.feature__slide_dyn__zero_value)+' '+str(tmp_dyn_zero_asset)+'> ~~ <'+str(tmp_bot_slide_dyn_zero)+' '+str(c.BOTsellmarket)+'> maker actual balance <'+str(d.balance_maker_total)+'> maker balance diff <'+str(balance_diff_dirty)+'> maker ignore <'+str(tmp_ignore_dirty)+' '+str(tmp_dyn_asset)+' ~~ '+str(tmp_ignore_final)+' '+str(c.BOTsellmarket)+'> maker balance diff final <'+str(balance_diff_final)+'> slide type <'+str(c.BOTslide_dyn_type)+'> slide step threshold <'+str(tmp_threshold_dirty)+'>~<'+str(tmp_threshold_final)+'> slide dyn step num * size <'+str(slide_dyn_step_num)+'*'+str(tmp_step_final)+'> final dyn slide <'+str(slide_dyn_final)+'> at max <'+str(tmp_max_final)+'>')
    
    return slide_dyn_final 
