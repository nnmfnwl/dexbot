#!/usr/bin/python3

# pricing storage for proxy server cache also proxy client cache

import time
import pickle

import features.glob as glob
from features.log import *
from features.main_cfg import *


# initialize pricing storage component
def pricing_storage__init_preconfig__():
    
    glob.d.pricing_storage = glob.GlobVars()
    glob.d.pricing_storage.data_redirect = {}
    glob.d.pricing_storage.data = {}
    glob.d.pricing_storage.update_interval = 60
    glob.d.pricing_storage.price_provider = ""
    glob.d.pricing_storage.price_providers_autotry = "on"
    glob.d.pricing_storage.auto_save_threshold = 3
    glob.d.pricing_storage.auto_save_threshold_status = 3
    glob.d.pricing_storage.auto_save_file_name = ""
    glob.d.pricing_storage__try_num = 1
    glob.d.pricing_storage__try_sleep = 6
    glob.d.pricing_storage.price_acceptable_outage = 0
    glob.d.pricing_storage.price_outage_extra_slide = 1.0
    glob.d.pricing_storage.req = {}
    glob.d.pricing_storage.pricing_mod = {}
    glob.d.pricing_storage.assetmap = {}

pricing_storage__init_preconfig__()


# define argument parameter
def pricing_storage__load_config_define():
    
    feature__main_cfg__add_variable('price_provider', "proxy", feature__main_cfg__validate_str, None, """Price provider.
    Default: "cg"; available options: "cg" (CoinGecko), "ccxt" (CCXT), "cmc" (Coinmarketcap) """, [['use external source by proxy client module','proxy'], ['CoinGecko','cg'],['ccxt','ccxt'],['CoinMarketCap','cmc'],['CoinPaprika','cp']])
    feature__main_cfg__add_variable('price_providers_autotry', "off", feature__main_cfg__validate_str, None, """off/auto - try also other price providers""", [['automatic','on'],['try only one provider','off']])
    feature__main_cfg__add_variable('price_acceptable_outage', 0, feature__main_cfg__validate_int, None, """Acceptable external pricing outage in seconds, previous price is used for time of outage. (default=0)""", None)
    feature__main_cfg__add_variable('price_outage_extra_slide', 1.0, feature__main_cfg__validate_float, None, """Xtra slide added to price in percent if outage happens. 1.05 is +5%. Default 0%""", [['no added slide', 1],['slide outage is considered as market pressure so automatically rise price 20%', 1.2]])


# parse configuration value
def pricing_storage__load_config_postparse(args):
    
    glob.d.pricing_storage.price_provider = str(args.price_provider)
    glob.d.pricing_storage.price_providers_autotry = str(args.price_providers_autotry)
    glob.d.pricing_storage.price_acceptable_outage = int(args.price_acceptable_outage)
    glob.d.pricing_storage.price_outage_extra_slide = float(args.price_outage_extra_slide)


# verify argument value after load
def pricing_storage__load_config_verify():
    
    error_num = 0
    crazy_num = 0
    
    if glob.d.pricing_storage.price_provider == "":
        LOG_ERROR('<price_provider> value <{0}> is invalid'.format(glob.d.pricing_storage.price_provider))
        error_num += 1
        
    if glob.d.pricing_storage.price_providers_autotry != "on" and glob.d.pricing_storage.price_providers_autotry != "off":
        LOG_ERROR('<price_providers_autotry> value <{0}> is invalid'.format(glob.d.pricing_storage.price_providers_autotry))
        error_num += 1
        
    if glob.d.pricing_storage.price_acceptable_outage < 0:
        LOG_ERROR('<price_acceptable_outage> value <{0}> is invalid'.format(glob.d.pricing_storage.price_acceptable_outage))
        error_num += 1
    
    if glob.d.pricing_storage.price_outage_extra_slide <= 0:
        LOG_ERROR('<price_outage_extra_slide> value <{0}> is invalid'.format(glob.d.pricing_storage.price_outage_extra_slide))
        error_num += 1
        
    if glob.d.pricing_storage.price_outage_extra_slide < 1:
        LOG_ERROR('<price_outage_extra_slide> value <{0}> seems abnormal value'.format(glob.d.pricing_storage.price_outage_extra_slide))
        crazy_num += 1
    
    return error_num, crazy_num

# set update interval in seconds
def pricing_storage__init_postconfig(auto_save_file_name, update_interval, try_num = 1, try_sleep = 6, data_redirect = {}, price_acceptable_outage = 0):
    
    glob.d.pricing_storage.auto_save_file_name = auto_save_file_name
    glob.d.pricing_storage.update_interval = update_interval
    glob.d.pricing_storage__try_num = try_num
    glob.d.pricing_storage__try_sleep = try_sleep
    
    # try to load auto auto saved pricing data
    pricing_storage__file_load()
    
    pricing_storage__assetmap_update({'ticker': "BLOCK", 'name': "blocknet", 'ucid': "707"})
    pricing_storage__assetmap_update({'ticker': "BTC", 'name': "bitcoin", 'ucid': "1"})
    pricing_storage__assetmap_update({'ticker': "ETH", 'name': "ethereum", 'ucid': "1027"})
    pricing_storage__assetmap_update({'ticker': "USDT", 'name': "tether", 'ucid': "825"})
    pricing_storage__assetmap_update({'ticker': "USDC", 'name': "usd-coin", 'ucid': "3408"})
    pricing_storage__assetmap_update({'ticker': "DOGE", 'name': "dogecoin", 'ucid': "74"})
    pricing_storage__assetmap_update({'ticker': "BCH", 'name': "bitcoin-cash", 'ucid': "1831"})
    pricing_storage__assetmap_update({'ticker': "LTC", 'name': "litecoin", 'ucid': "2"})
    pricing_storage__assetmap_update({'ticker': "DASH", 'name': "dash", 'ucid': "131"})
    pricing_storage__assetmap_update({'ticker': "PIVX", 'name': "pivx", 'ucid': "1169"})
    pricing_storage__assetmap_update({'ticker': "PART", 'name': "particl", 'ucid': "1826"})
    pricing_storage__assetmap_update({'ticker': "PKOIN", 'name': "pocketnet", 'ucid': "5925"})
    pricing_storage__assetmap_update({'ticker': "BTX", 'name': "bitcore", 'ucid': "1654"})
    pricing_storage__assetmap_update({'ticker': "SCC", 'name': "stakecubecoin", 'ucid': "3986"})
    pricing_storage__assetmap_update({'ticker': "XVG", 'name': "verge", 'ucid': "693"})
    
    pricing_storage__update_data_redirect(data_redirect)

# get pair identificator for storing price information
def pricing_storage__get_pair_id(maker, taker, price_provider = ""):
    if (price_provider != ""):
        price_provider = "__" + price_provider
    
    return str(maker + "__" + taker + price_provider)


# set price manually
def pricing_storage__set_price(pair, price):
    glob.d.pricing_storage.data[pair] = {}
    glob.d.pricing_storage.data[pair]['price'] = price
    glob.d.pricing_storage.data[pair]['time'] = time.time()
    
    LOG_DEBUG(f"Updating pair <{pair}> <{glob.d.pricing_storage.data[pair]}>")


# update asset map by ticker to name, ticker, ucid, etc...
def pricing_storage__assetmap_update(asset_dict = {}):
    
    ret = {}
    
    # get asset ticker
    ticker = asset_dict.get("ticker", None)
    # check is asset ticker is valid
    if ticker != None:
        # if asset not exists create it first
        if glob.d.pricing_storage.assetmap.get(ticker, None) == None:
            glob.d.pricing_storage.assetmap[ticker] = {}
        # update asset data by merging current and new data
        glob.d.pricing_storage.assetmap[ticker].update(asset_dict)
        # return updated asset dictionary
        ret = glob.d.pricing_storage.assetmap[ticker]
    else:
        LOG_ERROR(f"param asset_dict is invalid: {asset_dict}")

    return ret


# get asset dict
def pricing_storage__assetmap_find(asset_ticker):
    
    ret = {}
    
    if asset_ticker != None:
        ret = glob.d.pricing_storage.assetmap.get(asset_ticker, {})
    else:
        LOG_ERROR(f"param asset_ticker is invalid: {asset_ticker}")
    
    return ret


# merge asset dict into request with custom prefix, for example as maker_/taker_...
def pricing_storage__assetmap_merge_into_req(asset_ticker, prefix, req_to_update = {}):
    req = pricing_storage__assetmap_find(asset_ticker)
    
    for key in req.keys():
        req_to_update[str(prefix) + str(key)] = req[key]
    
    return req_to_update


# merge two assets into request
def pricing_storage__assetmap_create_req(maker_ticker, taker_ticker, base_req = {}, update_provider_options = True):
    
    base_req = pricing_storage__assetmap_merge_into_req(maker_ticker, "maker_", base_req)
    base_req = pricing_storage__assetmap_merge_into_req(taker_ticker, "taker_", base_req)
    
    if update_provider_options == True:
        base_req["price_provider"] = d.pricing_storage.price_provider
        base_req["price_providers_autotry"] = d.pricing_storage.price_providers_autotry
    
    return base_req

# upt request parameter that is send to proxy pricing server
def pricing_storage__pricing_mod_upt_req_params(params = {}):
    
    for key in params.keys():
        value = params[key]
        if value != None and value != "":
            glob.d.pricing_storage.req[key] = value
        else:
            glob.d.pricing_storage.req.pop(key)


# register more pricing modules
def pricing_storage__pricing_mod_upt_one(module_name, module_req_price_fn):
    
    glob.d.pricing_storage.pricing_mod[module_name] = module_req_price_fn


# get pricing information from predefined source modules
def pricing_storage__try_get_price_from_mods(req):
    
    price = 0
    provider = ""
    
    LOG_TRACE(f"Request {req}")
    
    # get remote remote price provider
    price_provider = req.get("price_provider", "")
    # get auto try option
    price_providers_autotry = req.get("price_providers_autotry", "")
    if price_providers_autotry != "on" and price_providers_autotry != "off":
        price_providers_autotry = glob.d.pricing_storage.price_providers_autotry
    
    # first priority is custom remote price provider from request
    if price_provider != "":
        for module_name in glob.d.pricing_storage.pricing_mod.keys():
            LOG_TRACE(f"searching for remote selected price provider <{price_provider}> <{module_name}> ")
            if module_name == price_provider:
                price = glob.d.pricing_storage.pricing_mod[module_name](req)
                provider = module_name
                if price == 0:
                    LOG_WARNING(f"Remote selected price provider <{price_provider}>/<{module_name}> get price failed...")
                break
    
    # second priority is custom local price provider but only if price providers are auto on or remote price provider is not set
    if price == 0 and glob.d.pricing_storage.price_provider != "" and (price_providers_autotry == "on" or price_provider == ""):
        for module_name in glob.d.pricing_storage.pricing_mod.keys():
            LOG_TRACE(f"searching for local selected price provider <{price_provider}> <{module_name}> ")
            if module_name == glob.d.pricing_storage.price_provider:
                price = glob.d.pricing_storage.pricing_mod[module_name](req)
                if price == 0:
                    LOG_WARNING(f"Local selected price provider <{glob.d.pricing_storage.price_provider}>/<{module_name}> get price failed...")
                provider = module_name
                break
    
    # if custom price provider failed
    if price == 0 and price_providers_autotry == "on":
        for module_name in glob.d.pricing_storage.pricing_mod.keys():
            LOG_TRACE(f"trying all other price providers <{price_provider}> <{module_name}> ")
            if module_name != price_provider and module_name != glob.d.pricing_storage.price_provider:
                price = glob.d.pricing_storage.pricing_mod[module_name](req)
                if price == 0:
                    LOG_WARNING(f"Other auto price providers <{module_name}> get price failed...")
                if price != 0:
                    provider = module_name
                    break
    
    if price == 0:
        provider = ""
    
    LOG_DEBUG(f"get external pricing >> maker/taker <{req['maker_ticker']}>/<{req['taker_ticker']}> at provider local/request <{glob.d.pricing_storage.price_provider}/{price_provider}> current <{provider}> >> price <{price}>")
    
    return price, provider


def pricing_storage__try_get_price_from_storage_solve(maker_ticker, taker_ticker, price_provider):
    pair = pricing_storage__get_pair_id(maker_ticker, taker_ticker, price_provider)
    price = glob.d.pricing_storage.data.get(pair, {}).get('price', 0)
    price_time = glob.d.pricing_storage.data.get(pair, {}).get('time', 0)
    if price != 0:
        if (time.time() - price_time) > glob.d.pricing_storage.update_interval:
            LOG_DEBUG(f"maker/taker {maker_ticker}/{taker_ticker} >> at {price_provider} >> found cached outdated price >> {price} >> time {time.time() - price_time}/{glob.d.pricing_storage.update_interval}")
            price = 0
        else:
            LOG_DEBUG(f"maker/taker {maker_ticker}/{taker_ticker} >> at {price_provider} >> found cached price >> {price} >> time {time.time() - price_time}/{glob.d.pricing_storage.update_interval}")
            
    return price

# get pricing information from local storage
def pricing_storage__try_get_price_from_storage(req):
    
    maker_ticker = req['maker_ticker']
    taker_ticker = req['taker_ticker']
    
    price = 0
    provider = ""
    
    # get remote remote price provider
    price_provider = req.get("price_provider", "")
    price_providers_autotry = req.get("price_providers_autotry", "")
    
    # first priority is custom remote price provider from request
    if price_provider != "":
        for module_name in glob.d.pricing_storage.pricing_mod.keys():
            if module_name == price_provider:
                price = pricing_storage__try_get_price_from_storage_solve(maker_ticker, taker_ticker, module_name)
                if price != 0:
                    provider = module_name
                break
    
    # second priority is custom local price provider
    if price == 0 and glob.d.pricing_storage.price_provider != "":
        for module_name in glob.d.pricing_storage.pricing_mod.keys():
            if module_name == glob.d.pricing_storage.price_provider:
                price = pricing_storage__try_get_price_from_storage_solve(maker_ticker, taker_ticker, module_name)
                if price != 0:
                    provider = module_name
                break
    
    # if custom price providers failed to provide price and are disabled or auto enabled
    if price == 0 and (price_providers_autotry == "on" or (price_provider == ""  and glob.d.pricing_storage.price_providers_autotry == "on")):
        for module_name in glob.d.pricing_storage.pricing_mod.keys():
            if module_name != price_provider and module_name != glob.d.pricing_storage.price_provider:
                price = pricing_storage__try_get_price_from_storage_solve(maker_ticker, taker_ticker, module_name)
                if price != 0:
                    provider = module_name
                    break
    
    if price == 0:
        provider = ""
    
    LOG_DEBUG(f"get local storage >> maker/taker <{req['maker_ticker']}>/<{req['taker_ticker']}> at <{price_provider}/{glob.d.pricing_storage.price_provider}> current <{provider}> >> previous <{price}> current <{price}>")
    
    return price, provider


# try to update specific pair price from external source by rest
def pricing_storage__try_get_price_from_remote(req, try_num, try_sleep):
    
    maker = req['maker_ticker']
    taker = req['taker_ticker']
    price_provider = req['price_provider']
    
    try_num_actual = 0
    
    while 1:
        # try to get price
        price, provider = pricing_storage__try_get_price_from_mods(req)
        # on success break cycle
        if price > 0:
            break;
        # on failed try again
        try_num_actual += 1
        if try_num_actual >= try_num:
            break
        else:
            LOG_WARNING("pricing storage update failed, price trying again... {}/{}".format(try_num_actual, try_num))
        # on failed wait a while
        time.sleep(try_sleep)
    
    return price, provider


# feature used to specify price of any asset by redirection to another asset
#   for example if price of BLOCK is not reliable from external sources
#   but we want to keep BLOCK price at level 0.035 USDT
#   so we set asset parameter to BLOCK and redirect asset to USDT and price to 0.035
#   then if pricing storage will be searching for BLOCK LTC price it will at first convert BLOCK to USDT and search how much it is in LTC
def pricing_storage__update_asset_redirect(asset, redirect_asset, price):
    
    glob.d.pricing_storage.data_redirect[asset] = {}
    # search for asset in existing predefined map and try to merge in the asset details
    redirect_asset = pricing_storage__assetmap_merge_into_req(redirect_asset.get('ticker', None), "", redirect_asset)
    # redirect for example BLOCK into USDT
    glob.d.pricing_storage.data_redirect[asset]['asset'] = redirect_asset
    # redirected BLOCK into USDT, so 1 BLOCK is 0.035 USDT
    glob.d.pricing_storage.data_redirect[asset]['price'] = price
    
    return

# update pricing redirection definitions
#   for example BLOCK to LTC pricing becomes delisted on cmc cg cp ... then you could set to BLOCK redirect to USDT static price 2.777$...
#   this way:
#       price_redirections='"BLOCK": { "asset": { name: "Tether USDt", ticker: "USDT", ucid: "825" }, "price": 2.777}'
#       pricing_storage__update_data_redirect(price_redirections)
def pricing_storage__update_data_redirect(data_redirect = {}):
    
    for asset_name in data_redirect.keys():
        pricing_storage__update_asset_redirect(asset_name, data_redirect[asset_name]['asset'], data_redirect[asset_name]['price'])
    
    return


# try to get price from pricing storage
def pricing_storage__try_get_price(req, try_num = None, try_sleep = None, allow_redirect = True):
    
    maker = req['maker_ticker']
    taker = req['taker_ticker']
    price_provider = req.get('price_provider', None)
    price_providers_autotry = req.get('price_providers_autotry', None)
            
    # merge in predefined parameters from other sub-pricing libraries like cmc, cg, cp, ccxt...
    req.update(glob.d.pricing_storage.req)
    
    final_price = 0
    virtual_price = 0
    
    LOG_DEBUG('START >> maker/taker {0}/{1}'.format(maker, taker))
    
    if maker == taker:
        virtual_maker = maker
        virtual_maker_price = 1
        
        virtual_taker = taker
        virtual_taker_price = 1
        
        virtual_price = 1
        
        LOG_DEBUG('maker/taker {0}/{1} >> redirected {2}/{3} >> at {4} >> found auto price >> {5}'.format(maker, taker, virtual_maker, virtual_taker, price_provider, virtual_price))
        
    else:
        # default price provider
        if price_provider is None:
            price_provider = glob.d.pricing_storage.price_provider
            req['price_provider'] = price_provider
        
        # default try num
        if try_num is None:
            try_num = glob.d.pricing_storage__try_num
        
        # default try sleep
        if try_sleep is None:
            try_sleep= glob.d.pricing_storage__try_sleep
        
        if (allow_redirect == True):
            # try to load maker and taker token pricing redirection data and update request according to them
            virtual_maker_price = glob.d.pricing_storage.data_redirect.get(maker, {}).get('price', 1)
            virtual_maker_data = glob.d.pricing_storage.data_redirect.get(maker, {}).get('asset', None)
            if virtual_maker_data != None:
                req['maker_name'] = virtual_maker_data['name']
                req['maker_ticker'] = virtual_maker_data['ticker']
                req['maker_ucid'] = virtual_maker_data['ucid']
                virtual_maker = virtual_maker_data['ticker']
            else:
                virtual_maker = maker
            
            virtual_taker_price = glob.d.pricing_storage.data_redirect.get(taker, {}).get('price', 1)
            virtual_taker_data = glob.d.pricing_storage.data_redirect.get(taker, {}).get('asset', None)
            if virtual_taker_data != None:
                req['taker_name'] = virtual_taker_data['name']
                req['taker_ticker'] = virtual_taker_data['ticker']
                req['taker_ucid'] = virtual_taker_data['ucid']
                virtual_taker = virtual_taker_data['ticker']
            else:
                virtual_taker = taker
            
        else:
            virtual_maker = maker
            virtual_taker = taker
            virtual_maker_price = 1
            virtual_taker_price = 1
        
        LOG_DEBUG(f'redirection status <{allow_redirect}> >> maker->virtual/taker->virtual {maker}->{virtual_maker}/{taker}->{virtual_taker} >> virtual_maker_price <{virtual_maker_price}> virtual_taker_price <{virtual_taker_price}>')
        
        if virtual_maker == virtual_taker:
            virtual_price = 1
            LOG_DEBUG('maker/taker {0}/{1} >> redirected {2}/{3} >> at {4} >> found auto price >> {5}'.format(maker, taker, virtual_maker, virtual_taker, price_provider, virtual_price))
        else:
            
            # try to get price from local storage
            virtual_price, virtual_provider = pricing_storage__try_get_price_from_storage(req)
            
            # try to get price from opposite pair local storage
            if virtual_price == 0:
                
                # make taker/maker opposite request copy
                req_opposite = req.copy()
                req_opposite = pricing_storage__assetmap_create_req(virtual_taker, virtual_maker, req_opposite, False)
                virtual_price, virtual_provider = pricing_storage__try_get_price_from_storage(req_opposite)
                if virtual_price != 0:
                    virtual_price = 1/virtual_price
                
            # if price is not found or out of date in local storage, try to update price remotely from other modules
            if virtual_price == 0:
                virtual_price, virtual_provider = pricing_storage__try_get_price_from_remote(req, try_num, try_sleep)
                LOG_DEBUG(f'maker/taker {maker}/{taker} >> redirected {virtual_maker}/{virtual_taker} >> at {price_provider} redir {virtual_provider} >> found remote price >> {virtual_price}')
            
                if virtual_price > 0:
                    
                    # update provider price
                    virtual_pair = pricing_storage__get_pair_id(virtual_maker, virtual_taker, virtual_provider)
                    pricing_storage__set_price(virtual_pair, virtual_price)
                    # update general no provider price used as previous price
                    virtual_pair = pricing_storage__get_pair_id(virtual_maker, virtual_taker)
                    pricing_storage__set_price(virtual_pair, virtual_price)
                    
                    # auto safe when price remote updates reach threshold
                    if glob.d.pricing_storage.auto_save_threshold != 0:
                        glob.d.pricing_storage.auto_save_threshold_status += 1
                        if glob.d.pricing_storage.auto_save_threshold_status >= glob.d.pricing_storage.auto_save_threshold:
                            glob.d.pricing_storage.auto_save_threshold_status = 0
                            pricing_storage__file_save()
            
            # if storage and remote price get failed, the temporary price outage could be ignored for a while
            if virtual_price == 0:
                
                # get previous price and time from general no provider storage
                virtual_pair = pricing_storage__get_pair_id(virtual_maker, virtual_taker)
                price_time = glob.d.pricing_storage.data.get(virtual_pair, {}).get('time', 0)
                virtual_price_previous = glob.d.pricing_storage.data.get(virtual_pair, {}).get('price', 0)
                
                outage = time.time() - (price_time + glob.d.pricing_storage.update_interval)
                if outage < glob.d.pricing_storage.price_acceptable_outage:
                    virtual_price = virtual_price_previous * glob.d.pricing_storage.price_outage_extra_slide
                    LOG_INFO(f'maker/taker {virtual_maker}/{virtual_maker} >> outage accepted {outage}/{glob.d.pricing_storage.price_acceptable_outage} >> using previous price * price_outage_extra_slide >> {virtual_price_previous}*{glob.d.pricing_storage.price_outage_extra_slide}={price}')
                    
                else:
                    LOG_INFO(f'maker/taker {virtual_maker}/{virtual_maker} >> outage not accepted {outage}/{glob.d.pricing_storage.price_acceptable_outage} >> not using previous price')
            
    
    # compute final price from virtual price redirects
    final_price = virtual_maker_price * virtual_price / virtual_taker_price
    # EXAMPLE: 1 BLOCK = 0.5 USD       1 USD = 0.9 EUR           1 LTC = 100 EUR
    #                0.5            *       0.9             /         100   
    LOG_INFO(f'FINISH >> {maker}/{taker} >> redirected maker->virtual/taker->virtual {maker}->{virtual_maker}/{taker}->{virtual_taker} >> virtual_maker_price * virtual_price / virtual_taker_price >> {final_price} = {virtual_maker_price} * {virtual_price} / {virtual_taker_price} at provider <{price_provider}> auto <{price_providers_autotry}>')
    
    return final_price


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
        LOG_DEBUG('temporary pricing database was not created yet')
    except EOFError:
        LOG_DEBUG('temporary pricing database was empty')
    
    LOG_DEBUG('temporary pricing database data: {}'.format(glob.d.pricing_storage.data))

