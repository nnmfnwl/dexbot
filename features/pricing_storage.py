#!/usr/bin/python3

# pricing storage for proxy server cache also proxy client cache

import time
import pickle

import features.glob as glob

def pricing_storage__try_get_price_empty_fn(maker, taker, price_provider):
    print('**** WARNING >> Using predefined empty pricing storage get price function')
    print('**** WARNING >> Pricing will not work correctly')
    print('**** WARNING >> please initialize with pricing_storage__init_postconfig()')
    return 0

# initialize pricing storage component
def pricing_storage__init_preconfig__():
    
    glob.d.pricing_storage = glob.GlobVars()
    glob.d.pricing_storage.data = {}
    glob.d.pricing_storage.update_interval = 60
    glob.d.pricing_storage.price_provider = ""
    glob.d.pricing_storage.try_get_price_fn = pricing_storage__try_get_price_empty_fn
    glob.d.pricing_storage.auto_save_threshold = 3
    glob.d.pricing_storage.auto_save_threshold_status = 3
    glob.d.pricing_storage.auto_save_file_name = ""
    glob.d.pricing_storage__try_num = 2
    glob.d.pricing_storage__try_sleep = 6

pricing_storage__init_preconfig__()

# define argument parameter
def pricing_storage__load_config_define(parser, argparse):
    
    parser.add_argument('--price_provider', type=str, help='price provider (default="")', default="")

# parse configuration value
def pricing_storage__load_config_postparse(args):
    
    glob.d.pricing_storage.price_provider = str(args.price_provider)

# verify argument value after load
def pricing_storage__load_config_verify():
    
    error_num = 0
    crazy_num = 0
    
    if glob.d.pricing_storage.price_provider == None:
        print('**** ERROR, <price_provider> value <{0}> is invalid'.format(glob.d.pricing_storage.price_provider))
        error_num += 1
    
    return error_num, crazy_num

# set update interval in seconds
def pricing_storage__init_postconfig(auto_save_file_name, update_interval, price_provider, try_num = 2, try_sleep = 6, try_get_price_fn = pricing_storage__try_get_price_empty_fn):
    
    glob.d.pricing_storage.auto_save_file_name = auto_save_file_name
    glob.d.pricing_storage.update_interval = update_interval
    glob.d.pricing_storage.price_provider = price_provider
    glob.d.pricing_storage.try_get_price_fn = try_get_price_fn
    glob.d.pricing_storage__try_num = try_num
    glob.d.pricing_storage__try_sleep = try_sleep
    
    # try to load auto auto saved pricing data
    pricing_storage__file_load()


# get pair identificator for storing price information
def pricing_storage__get_pair_id(maker, taker, price_provider = ""):
    if (price_provider != ""):
        price_provider = "__" + price_provider
    
    return str(maker + "__" + taker + price_provider)

# get pricing information from predefined source
def pricing_storage__try_get_price_fn(maker__item_to_sell, taker__payed_by, previous_price, price_provider, try_get_price_fn):
    
    maker_price_in_takers = try_get_price_fn(maker__item_to_sell, taker__payed_by, price_provider)
    print('>>>> Pricing storage >> get external pricing >> maker <{0}> taker <{1}> /{2} previous <{3}> actual <{4}>'.format(maker__item_to_sell, taker__payed_by, price_provider, previous_price, maker_price_in_takers))
    
    return maker_price_in_takers
    
# try to update specific pair price from external source by rest
def pricing_storage__try_update_price(maker, taker, price_provider, try_num, try_sleep, try_get_price_fn):
    
    pair = pricing_storage__get_pair_id(maker, taker, price_provider)
    previous_price = glob.d.pricing_storage.data.get(pair, {}).get('price', 0)
    try_num_actual = 0
    
    while 1:
        # try to get price
        price = pricing_storage__try_get_price_fn(maker, taker, previous_price, price_provider, try_get_price_fn)
        # on success break cycle
        if price > 0:
            break;
        # on failed try again
        try_num_actual += 1
        if try_num_actual >= try_num:
            break
        print("#### DEBUG pricing storage update price try again...")
        # on failed wait a while
        time.sleep(try_sleep)
    
    if price > 0:
        glob.d.pricing_storage.data[pair] = {}
        glob.d.pricing_storage.data[pair]['price'] = price
        glob.d.pricing_storage.data[pair]['time'] = time.time()
        
        # auto safe when price remote updates reach threshold
        if glob.d.pricing_storage.auto_save_threshold != 0:
            glob.d.pricing_storage.auto_save_threshold_status += 1
            if glob.d.pricing_storage.auto_save_threshold_status >= glob.d.pricing_storage.auto_save_threshold:
                glob.d.pricing_storage.auto_save_threshold_status = 0
                pricing_storage__file_save()

    return price

# try to get price from pricing storage
def pricing_storage__try_get_price(maker, taker, price_provider = None, try_num = None, try_sleep = None, try_get_price_fn = None):
    
    price = 1
    
    if maker != taker:
        
        # default price provider
        if price_provider is None:
            price_provider = glob.d.pricing_storage.price_provider
        
        # default get price function
        if try_get_price_fn is None:
            try_get_price_fn = glob.d.pricing_storage.try_get_price_fn
        
        # default try num
        if try_num is None:
            try_num = glob.d.pricing_storage__try_num
        
        # default try sleep
        if try_sleep is None:
            try_sleep= glob.d.pricing_storage__try_sleep
        
        # get pair id string
        pair = pricing_storage__get_pair_id(maker, taker, price_provider)
        
        # get actual price stored in
        price = glob.d.pricing_storage.data.get(pair, {}).get('price', 0)
        price_time = glob.d.pricing_storage.data.get(pair, {}).get('time', 0)
        
        # also try reversed pair and do 1/price
        if price == 0 or (time.time() - price_time) > glob.d.pricing_storage.update_interval:
            pair_r = pricing_storage__get_pair_id(taker, maker, price_provider)
            price = glob.d.pricing_storage.data.get(pair_r, {}).get('price', 0)
            price_time = glob.d.pricing_storage.data.get(pair_r, {}).get('time', 0)
            if price != 0:
                price = 1/price
        
        # if price is not found, try to update price
        if price == 0:
            price = pricing_storage__try_update_price(maker, taker, price_provider, try_num, try_sleep, try_get_price_fn)
            print('>>>> Pricing storage >> new external pricing >> maker <{0}> taker <{1}> /{2}'.format(maker, taker, price_provider))
            
        # if price is found but out of date, try to update price
        elif (time.time() - price_time) > glob.d.pricing_storage.update_interval:
            price = pricing_storage__try_update_price(maker, taker, price_provider, try_num, try_sleep, try_get_price_fn)
            print('>>>> Pricing storage >> updating external pricing >> maker <{0}> taker <{1}> /{2}'.format(maker, taker, price_provider))
        
        # price cache
        else:
            print('>>>> Pricing storage >> cached external pricing >> maker <{0}> taker <{1}> /{2}'.format(maker, taker, price_provider))
        
    return price

# dump data to file(done automatically at every threshold) 
def pricing_storage__file_save(file_name = None):
    
    if file_name is None:
        file_name = glob.d.pricing_storage.auto_save_file_name
        
    file = open(file_name,'wb')
    pickle.dump(glob.d.pricing_storage.data, file)
    file.close()

# restore db from json file(done automatically at every postconfig init)
def pricing_storage__file_load(file_name = None):
    
    if file_name is None:
        file_name = glob.d.pricing_storage.auto_save_file_name
    
    try:
        file = open(file_name+"", "rb")
        glob.d.pricing_storage.data = pickle.load(file)
        file.close()
    except FileNotFoundError:
        print('DEBUG: temporary pricing database was not created yet')
    except EOFError:
        print('DEBUG: temporary pricing database was empty')
    
    print('DEBUG: temporary pricing database data: {}'.format(glob.d.pricing_storage.data))

