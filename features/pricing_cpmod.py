#!/usr/bin/python3

# coinpaprika pricing feature

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
def pricing_cpmod__init_preconfig__():
   
   c.pricing_cpmod__apikey = None
   c.pricing_cpmod__url_byslug = 'https://api.coinpaprika.com/v1/price-converter'
   d.pricing_cpmod__headers = None


pricing_cpmod__init_preconfig__()


# define argument parameter
def pricing_cpmod__load_config_define():
   
   feature__main_cfg__add_variable('cpmod_apikey', "", feature__main_cfg__validate_str, None, """Coinpaprika API key. After registration on Coinpaprika you could obtain your own API key at coinpaprika.com/api/panel/"""
    , [['example how key look like','1a12345678910e1ea1f1d1a111e111d1']])


# parse configuration value
def pricing_cpmod__load_config_postparse(args):
   
   c.pricing_cpmod__apikey = str(args.cpmod_apikey)


# verify argument value after load
def pricing_cpmod__load_config_verify():
   
   error_num = 0
   crazy_num = 0
   
   if len(c.pricing_cpmod__apikey) < 0:
      LOG_ERROR('<cpmod_apikey> value <{0}> is invalid. After registration on Coinpaprika you could obtain your own API key at coinpaprika.com/api/panel/'.format(c.pricing_cpmod__apikey))
      error_num += 1
   
   return error_num, crazy_num


# initial postconfig to:
#  set API key
#  register cpmod commands
def pricing_cpmod__init_postconfig(cli__reg_fn):
   
   pricing_cpmod__update_api_key(c.pricing_cpmod__apikey)
   
   cli__reg_fn('cpmod', pricing_cpmod__cli_apikey_help, pricing_cpmod__cli_apikey_cmd, "update Coinpaprika pricing variables, like API key...")


# update API key
def pricing_cpmod__update_api_key(apikey):
   
   if apikey == "" or apikey == None:
      d.pricing_cpmod__headers = {
         'Accept': 'application/json',
      }
   else:
      d.pricing_cpmod__headers = {
         'Accept': 'application/json',
         'X-CoinPaprika-API-Key': apikey,
      }
   
   c.pricing_cpmod__apikey = apikey
   
   pricing_storage__pricing_mod_upt_req_params(d.pricing_cpmod__headers)

# get price main function
def pricing_cpmod__get_price(req):
   
   price = pricing_cpmod__get_price_by_slug(req)
      
   return price


# get price by slug-name
def pricing_cpmod__get_price_by_slug(req):
   
   maker_name = req.get('maker_name', None)
   taker_name = req.get('taker_name', None)
   maker_ticker = req.get('maker_ticker', None)
   taker_ticker = req.get('taker_ticker', None)
   maker_ucid = req.get('maker_ucid', None)
   taker_ucid = req.get('taker_ucid', None)
   
   free_key = req.get('X-CoinPaprika-API-Key', None)
   
   price = 0
   
   if (maker_ticker == "" or maker_ticker == None or
      maker_name == "" or maker_name == None or
      taker_ticker == "" or taker_ticker == None or
      taker_name == "" or taker_name == None):
         LOG_ERROR(f"Request {req} is invalid")
         return price
   
   # prepare parameters for the API request
   parameters = {
      "amount": 1,
      "base_currency_id": f"{maker_ticker}-{maker_name}",
      "quote_currency_id": f"{taker_ticker}-{taker_name}",
   }
   
   response = None
   
   if free_key != None:
      free_headers = {
         'Accept': 'application/json',
         'X-CoinPaprika-API-Key': free_key,
      }
      response = requests.get(c.pricing_cpmod__url_byslug, headers=free_headers, params=parameters)
   
   # if response from custom previous request with custom API key failed or API key not available
   # then we try anyway request, because coinpaprika works also without APi key but limited
   if response == None or response.status_code != 200:
      response = requests.get(c.pricing_cpmod__url_byslug, headers=d.pricing_cpmod__headers, params=parameters)
   
   # Check if the request was successful
   if response.status_code == 200:
      data = response.json()
      
      # get price
      price = data['price']
      
      LOG_DEBUG(f"{maker_name}/{taker_name} {maker_ticker}/{taker_ticker} {maker_ucid}/{taker_ucid} price {price}")
   else:
      LOG_ERROR(f"{maker_name}/{taker_name} {maker_ticker}/{taker_ticker} {maker_ucid}/{taker_ucid} - {response.status_code} - {response.text}")
   
   return price


# console interface api key commands
def pricing_cpmod__cli_apikey_cmd(cmd1, arg2, arg3):
   global c, s, d
   
   LOG_DEBUG("CLI command >> {} {} {}".format(cmd1, arg2, arg3))
   
   # default action is to cancel all orders on configured address
   if arg2 == "apikey" and len(arg3) > 3: 
      pricing_cpmod__update_api_key(arg3)
   else:
      LOG_ERROR("exit arguments >> {} >> {} >> are invalid".format(arg2, arg3))
   
   return


# console interface api key help
def pricing_cpmod__cli_apikey_help(cmd1, arg2):
   
   print("""Command cpmod:
USAGE:

cpmod [arguments]
  - arguments
  
  - apikey - [apikey] [apikeystring] - try to update Coinpaprika users API key. After registration on coinpaprika you could obtain your own API key at coinpaprika.com/api/panel/

""")



# Try by your own by copy pasting into python console
# ~ url="https://api.coinpaprika.com/v1/price-converter"

# ~ api_key=""
# ~ maker_slug="BTC-bitcoin"
# ~ taker_slug="LTC-litecoin"
# ~ headerss = {
   # ~ 'Accepts': 'application/json',
   # ~ 'X-CoinPaprika-API-Key': api_key,
# ~ }

# ~ parameters = {
   # ~ "amount": 1,
   # ~ "base_currency_id": maker_slug,
   # ~ "quote_currency_id": taker_slug,
# ~ }

# ~ response = requests.get(url, headers=headerss, params=parameters)
# ~ print(f"Error: {response.status_code} - {response.text}")
# ~ data = response.json()
# ~ print(f"DATA:{data}")

# ~ price = data['price']

# ~ print(f"{maker_slug}/{taker_slug} is approximately {price}")
