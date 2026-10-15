#!/usr/bin/python3

# pricing proxy client for pricing storage
 
import features.glob as glob
from features.log import *
from features.main_cfg import *

from features.pricing_storage import pricing_storage__pricing_mod_upt_req_params

import jsonrpclib

# preconfiguration initialization
def pricing_proxymod__init_preconfig__():
    glob.d.pricing_proxymod__conn = None
    glob.c.pricing_proxymod__default_url = "http://127.0.0.1:22333"
    glob.c.pricing_proxymod__default_provider = "cp"
    glob.c.pricing_proxymod__default_autotry = "on"
    glob.c.pricing_proxymod__url = ""


pricing_proxymod__init_preconfig__()


# define configuration variables
def pricing_proxymod__load_config_define():
    
    feature__main_cfg__add_variable("proxymod_url", glob.c.pricing_proxymod__default_url, feature__main_cfg__validate_str, None, """pricing proxy url address (default='"""+glob.c.pricing_proxymod__default_url+"""')""", None)
    
    feature__main_cfg__add_variable("proxymod_provider", glob.c.pricing_proxymod__default_provider, feature__main_cfg__validate_str, None, """pricing proxy provider (default='"""+glob.c.pricing_proxymod__default_provider+"""')""", None)
    
    feature__main_cfg__add_variable("proxymod_autotry", glob.c.pricing_proxymod__default_autotry, feature__main_cfg__validate_str, None, """pricing proxy automatically try other providers (default='"""+glob.c.pricing_proxymod__default_url+"""')""", None)


# parse configuration variables after loading configuration
def pricing_proxymod__load_config_postparse(args):
    
    glob.c.pricing_proxymod__url = str(args.proxymod_url)
    glob.c.pricing_proxymod__provider = str(args.proxymod_provider)
    glob.c.pricing_proxymod__autotry = str(args.proxymod_autotry)


# configuration variables verification
def pricing_proxymod__load_config_verify():
    
    error_num = 0
    crazy_num = 0
    
    if glob.c.pricing_proxymod__url == "":
        LOG_ERROR('<proxymod_url> value <{0}> is invalid'.format(glob.c.pricing_proxymod__url))
        error_num += 1
    
    if glob.c.pricing_proxymod__autotry != "off" and glob.c.pricing_proxymod__autotry != "on":
        LOG_ERROR('<proxymod_autotry> value <{0}> is invalid'.format(glob.c.pricing_proxymod__autotry))
        error_num += 1
    
    return error_num, crazy_num


# post-configuration related to making connection to server and updating command line interface
def pricing_proxymod__init_postconfig(cli__reg_fn):
    
    glob.d.pricing_proxymod__conn = jsonrpclib.Server(glob.c.pricing_proxymod__url)
    
    cli__reg_fn('proxymod', pricing_proxymod__cli_provider_help, pricing_proxymod__cli_provider_cmd, "update proxy module client url|provider|auto parameters")


# get pricing information from proxy cache
def pricing_proxymod__try_get_price(req):
    
    # proxy module supposed to update this request parameters to custom proxy module parameters before sending request to proxy server
    req["price_provider"] = glob.c.pricing_proxymod__provider
    req["price_providers_autotry"] = glob.c.pricing_proxymod__autotry
    
    try:
        maker_price_in_takers = glob.d.pricing_proxymod__conn.proxy_server__rpc_get_price(req)
    except Exception as err:
        LOG_ERROR('EXCEPTION >> %s' % err)
        maker_price_in_takers = 0
    
    return maker_price_in_takers


# console interface proxymod commands
def pricing_proxymod__cli_provider_cmd(cmd1, arg2, arg3):
   
    LOG_DEBUG("CLI command >> {} {} {}".format(cmd1, arg2, arg3))
   
    # default action is to cancel all orders on configured address
    if arg2 == "url" and len(arg3) >= 0:
        glob.c.pricing_proxymod__url = arg3
        glob.d.pricing_proxymod__conn = jsonrpclib.Server(glob.c.pricing_proxymod__url)
    elif arg2 == "provider" and len(arg3) >= 0: 
        glob.c.pricing_proxymod__provider = arg3
    elif arg2 == "autotry" and len(arg3) >= 0: 
        glob.c.pricing_proxymod__autotry = arg3
    else:
        LOG_ERROR("exit arguments >> {} >> {} >> are invalid".format(arg2, arg3))
   
    return


# console interface api key help
def pricing_proxymod__cli_provider_help(cmd1, arg2):
   
   print("""Command proxymod:
USAGE:

proxymod [arguments]
  - arguments
  
  - url - [url] <urlstring> - try to update client proxy module url.
  - provider - [provider] <"",cmc,cg,cp> - try to update client proxy module provider.

""")
