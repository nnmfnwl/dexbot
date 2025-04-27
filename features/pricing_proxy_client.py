#!/usr/bin/python3

# pricing proxy client for pricing storage

import features.glob as glob

import jsonrpclib

def pricing_proxy_client__init_preconfig__():
    glob.d.pricing_proxy_client__conn = None
    glob.c.pricing_proxy_client__default_url = "http://localhost:22333"
    glob.c.pricing_proxy_client__url = ""

pricing_proxy_client__init_preconfig__()

def pricing_proxy_client__load_config_define(parser, argparse):
    
    parser.add_argument('--pricing_proxy_url', type=str, help='pricing proxy url address (default="'+glob.c.pricing_proxy_client__default_url+'")', default=glob.c.pricing_proxy_client__default_url)

def pricing_proxy_client__load_config_postparse(args):
    
    glob.c.pricing_proxy_client__url = str(args.pricing_proxy_url)

def pricing_proxy_client__load_config_verify():
    
    error_num = 0
    crazy_num = 0
    
    if glob.c.pricing_proxy_client__url == "":
        print('**** ERROR, <pricing_proxy_url> value <{0}> is invalid'.format(glob.c.pricing_proxy_client__url))
        error_num += 1
    
    return error_num, crazy_num

def pricing_proxy_client__init_postconfig():
    glob.d.pricing_proxy_client__conn = jsonrpclib.Server(glob.c.pricing_proxy_client__url)

# get pricing information from proxy cache
def pricing_proxy_client__pricing_storage__try_get_price_fn(maker__item_to_sell, taker__payed_by, price_provider):
    
    try:
        maker_price_in_takers = glob.d.pricing_proxy_client__conn.proxy_server__rpc_get_price(maker__item_to_sell, taker__payed_by, price_provider)
    except Exception as err:
        print('**** ERROR >> PROXY >> pricing_proxy_client__pricing_storage__try_get_price_fn >> EXCEPTION >> %s' % err)
        maker_price_in_takers = 0
    
    return maker_price_in_takers
