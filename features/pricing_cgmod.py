#!/usr/bin/python3

# coingecko pricing feature

import time
import requests

import features.glob as glob
c = glob.c
s = glob.s
d = glob.d

from features.tmp_cfg import *
from features.main_cfg import *
from features.log import *

from features.pricing_storage import pricing_storage__get_pair_id, pricing_storage__set_price, pricing_storage__pricing_mod_upt_req_params

# preconfiguration initialization
def pricing_cgmod__init_preconfig__():
   
   c.pricing_cgmod__free_apikey = None
   c.pricing_cgmod__pro_apikey = None
   c.pricing_cgmod__url_free_by_slug = 'https://api.coingecko.com/api/v3/simple/price'
   c.pricing_cgmod__url_pro_by_slug = 'https://pro-api.coingecko.com/api/v3/simple/price'
   d.pricing_cgmod__free_headers = None
   d.pricing_cgmod__pro_headers = None


pricing_cgmod__init_preconfig__()


# define argument parameter
def pricing_cgmod__load_config_define():
   
   feature__main_cfg__add_variable('cgmod_free_apikey', "", feature__main_cfg__validate_str, None, """Coingecko API key. After registration on Coingecko you could obtain your own API key at https://www.coingecko.com/en/api/pricing"""
    , [['example how key look like','1a12345678910e1ea1f1d1a111e111d1']])
    
   feature__main_cfg__add_variable('cgmod_pro_apikey', "", feature__main_cfg__validate_str, None, """Coingecko API key. After registration on Coingecko you could obtain your own API key at https://www.coingecko.com/en/api/pricing"""
    , [['example how key look like','1a12345678910e1ea1f1d1a111e111d1']])


# parse configuration value
def pricing_cgmod__load_config_postparse(args):
   
   c.pricing_cgmod__free_apikey = str(args.cgmod_free_apikey)
   c.pricing_cgmod__pro_apikey = str(args.cgmod_pro_apikey)


# verify argument value after load
def pricing_cgmod__load_config_verify():
   
   error_num = 0
   crazy_num = 0
   
   if len(c.pricing_cgmod__free_apikey) < 0:
      LOG_ERROR('<cgmod_free_apikey> value <{0}> is invalid. After registration on Coingecko you could obtain your own API key at https://www.coingecko.com/en/api/pricing'.format(c.pricing_cgmod__free_apikey))
      error_num += 1
      
   if len(c.pricing_cgmod__pro_apikey) < 0:
      LOG_ERROR('<cgmod_pro_apikey> value <{0}> is invalid. After registration on Coingecko you could obtain your own API key at https://www.coingecko.com/en/api/pricing'.format(c.pricing_cgmod__pro_apikey))
      error_num += 1
   
   return error_num, crazy_num


# initial postconfig to:
#  set API key
#  register cgmod commands
def pricing_cgmod__init_postconfig(cli__reg_fn):
   
   pricing_cgmod__update_free_api_key(c.pricing_cgmod__free_apikey)
   pricing_cgmod__update_pro_api_key(c.pricing_cgmod__pro_apikey)
   
   cli__reg_fn('cgmod', pricing_cgmod__cli_apikey_help, pricing_cgmod__cli_apikey_cmd, "update Coingecko pricing variables, like API key...")


# update free API key
def pricing_cgmod__update_free_api_key(apikey):
   
   if apikey == "" or apikey == None:
      d.pricing_cgmod__free_headers = {
         'Accept': 'application/json',
      }
   else:
      d.pricing_cgmod__free_headers = {
         'Accept': 'application/json',
         'x-cg-demo-api-key': apikey,
      }
   
   c.pricing_cgmod__free_apikey = apikey
   
   pricing_storage__pricing_mod_upt_req_params(d.pricing_cgmod__free_headers)

# update pro API key
def pricing_cgmod__update_pro_api_key(apikey):
   
   if apikey == "" or apikey == None:
      d.pricing_cgmod__pro_headers = {
         'Accept': 'application/json',
      }
   else:
      d.pricing_cgmod__pro_headers = {
         'Accept': 'application/json',
         'x-cg-pro-api-key': apikey,
      }
   
   c.pricing_cgmod__pro_apikey = apikey
   
   pricing_storage__pricing_mod_upt_req_params(d.pricing_cgmod__pro_headers)

# get price main function
def pricing_cgmod__get_price(req):
   
   price = pricing_cgmod__get_price_by_slug(req)
      
   return price


# get price by slug-name
def pricing_cgmod__get_price_by_slug(req):
   
   maker_name = req.get('maker_name', None)
   taker_name = req.get('taker_name', None)
   maker_ticker = req.get('maker_ticker', None)
   taker_ticker = req.get('taker_ticker', None)
   maker_ucid = req.get('maker_ucid', None)
   taker_ucid = req.get('taker_ucid', None)
   
   pro_key = req.get('x-cg-pro-api-key', None)
   free_key = req.get('x-cg-demo-api-key', None)
   
   price = 0
   
   if (maker_name == "" or maker_name == None or
      taker_name == "" or taker_name == None):
         LOG_ERROR(f"Request {req} is invalid")
         return price
   
   # prepare parameters for the API request
   parameters = {
      "ids": f"{maker_name},{taker_name}",
      "vs_currencies": "usd"
   }
   
   response = None
   
   if pro_key != None:
      pro_headers = {
         'Accept': 'application/json',
         'x-cg-pro-api-key': pro_key,
      }
      response = requests.get(c.pricing_cgmod__url_pro_by_slug, headers=pro_headers, params=parameters)
   
   if c.pricing_cgmod__pro_apikey != "" and (response == None or response.status_code != 200):
      response = requests.get(c.pricing_cgmod__url_pro_by_slug, headers=d.pricing_cgmod__pro_headers, params=parameters)
   
   if free_key != None and (response == None or response.status_code != 200):
      free_headers = {
         'Accept': 'application/json',
         'x-cg-demo-api-key': free_key,
      }
      response = requests.get(c.pricing_cgmod__url_free_by_slug, headers=free_headers, params=parameters)
   
   if response == None or response.status_code != 200:
      response = requests.get(c.pricing_cgmod__url_free_by_slug, headers=d.pricing_cgmod__free_headers, params=parameters)
      
   # Check if the request was successful
   if response.status_code == 200:
      data = response.json()
      
      LOG_DEBUG(data)
      
      # get price
      maker_price = data.get(maker_name, {}).get("usd", None)
      taker_price = data.get(taker_name, {}).get("usd", None)
      
      if maker_price != None and taker_price != None:
         price = maker_price / taker_price
         
         pair = pricing_storage__get_pair_id(maker_ticker, "USD", "cg")
         pricing_storage__set_price(pair, maker_price)
         
         pair = pricing_storage__get_pair_id(taker_ticker, "USD", "cg")
         pricing_storage__set_price(pair, taker_price)
      
   
   if price != 0:
      LOG_DEBUG(f"{maker_name}/{taker_name} {maker_ticker}/{taker_ticker} {maker_ucid}/{taker_ucid} price {price}")
   else:
      LOG_ERROR(f"{maker_name}/{taker_name} {maker_ticker}/{taker_ticker} {maker_ucid}/{taker_ucid} - {response.status_code} - {response.text}")
   
   return price


# console interface api key commands
def pricing_cgmod__cli_apikey_cmd(cmd1, arg2, arg3):
   global c, s, d
   
   LOG_DEBUG("CLI command >> {} {} {}".format(cmd1, arg2, arg3))
   
   # default action is to cancel all orders on configured address
   if arg2 == "freeapikey" and len(arg3) > 0: 
      pricing_cgmod__update_free_api_key(arg3)
   elif arg2 == "proapikey" and len(arg3) > 0: 
      pricing_cgmod__update_pro_api_key(arg3)
   else:
      LOG_ERROR("exit arguments >> {} >> {} >> are invalid".format(arg2, arg3))
   
   return


# console interface api key help
def pricing_cgmod__cli_apikey_help(cmd1, arg2):
   
   print("""Command cgmod:
USAGE:

cgmod [arguments]
  - arguments
  
  - freeapikey - [apikey] [apikeystring] - try to update Coingecko users API key. After registration on Coingecko you could obtain your own API key at https://www.coingecko.com/en/api/pricing
  - proapikey - [apikey] [apikeystring] - try to update Coingecko users API key. After registration on Coingecko you could obtain your own API key at https://www.coingecko.com/en/api/pricing

""")



# ~ # Try by your own by copy pasting into python console
# ~ url="https://api.coingecko.com/api/v3/simple/price" # Use pro-api.coingecko.com for Pro

# ~ api_key=""
# ~ maker_slug="bitcoin"
# ~ taker_slug="litecoin"
# ~ headerss = {
   # ~ 'Accepts': 'application/json',
   # ~ "x-cg-pro-api-key": api_key, # Use "x-cg-pro-api-key" if using Pro
# ~ }

# ~ parameters = {
   # ~ "ids": f"{maker_slug},{taker_slug}",
   # ~ "vs_currencies": "usd"
# ~ }

# ~ response = requests.get(url, headers=headerss, params=parameters)
# ~ print(f"Error: {response.status_code} - {response.text}")
# ~ data = response.json()
# ~ print(f"DATA:{data}")


# ~ maker_price = data[maker_slug]["usd"]
# ~ taker_price = data[taker_slug]["usd"]

# ~ price = maker_price / taker_price

# ~ print(f"{maker_slug}/{taker_slug} is approximately {price}")
