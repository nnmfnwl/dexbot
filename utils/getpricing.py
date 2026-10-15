#!/usr/bin/env python3
__author__ = 'atcsecure'
__copyright__ = 'All rights reserved'
__credits__ = ['atcsecure']
__license__ = 'GPL'
__version__ = '0.0.1'
__maintainer__ = 'atcsecure'
__status__ = 'Alpha'
__update__ = '2026.01.19 nnmfnwl7'
__update__ = '2026.10.18 nnmfnwl7 & Tryou'

import time
import sys
import requests
from utils import coingecko
from utils import custompricing
from utils import dxsettings
from utils.ccxtpricing import CCXTPricing, SymbolNotFoundError, CCXT_EXCHANGE

from features.log import *

my_ccxt = CCXTPricing()

def getmarketprice(marketname, BOTuse):
  # get market price
  markets = []
  markets = marketname.split('-')
  lastprice = 0
  if markets[1] == 'BTC':
    marketname = '{}-{}'.format(markets[1], markets[0])

  if BOTuse == 'custom':
    asset = markets[1]
    LOG_ACTION('>>>> Looking up custom pricing: {}'.format(marketname), '\n')
    # lets get maker price
    try:
        endpoint = dxsettings.apiendpoint[asset]
        lastprice = custompricing.getprice(asset,endpoint)
    except Exception as e:
        LOG_ERROR('ERROR: {}'.format(e))
        LOG_FATAL('program aborted...')
        sys.exit(1)
    LOG_DEBUG(lastprice)
  
  if BOTuse == 'ccxt':
    LOG_ACTION('>>>> Looking up CCXT market: {} on {}'.format(marketname, CCXT_EXCHANGE))
    try:
      lastprice = my_ccxt.get_price(markets[0], markets[1], CCXT_EXCHANGE)
      LOG_INFO('>>>> Found CCXT market: {}, Price: {}'.format(marketname, lastprice))
    except SymbolNotFoundError as e:
      LOG_WARNING('WARNING: Symbol not found on {}: {}'.format(CCXT_EXCHANGE, e))
    except Exception as e:
      LOG_ERROR('ERROR: CCXT pricing failed: {}'.format(e))
  
  if BOTuse == 'cmc':
    LOG_ACTION('>>>> Looking up CMC market: {} on {}'.format(marketname, CCXT_EXCHANGE))
    lastprice = pricing_cmcmod__get_price(markets[0], markets[1])
    
  if BOTuse == 'cg' or lastprice == 0:
    LOG_ACTION('>>>> Looking up CoinGecko pricing: {}'.format(markets[1]), '\n')
    cg = coingecko.CoinGeckoAPI()
    cg_coin_list = cg.get_coins_list()
    # CoinGecko uses IDs, need to lookup ID for market
    for coin in cg_coin_list:
      if coin['symbol'] == markets[1].lower():
        coin_id = coin['id']
        LOG_INFO('Found {} ID: {}'.format(markets[1],coin_id))
        currentprice = cg.get_price(ids=coin_id, vs_currencies=markets[0])
        lastprice = currentprice[coin_id]
        vsmarket = markets[0].lower()
        LOG_INFO('Last price: {}'.format(lastprice[vsmarket]))
        lastprice = lastprice[vsmarket]
        break

  return float(lastprice)


def getpricedata(maker, taker, BOTuse):
  basemarket = ('BTC-{}'.format(maker))
  takermarket = ('BTC-{}'.format(taker))
  
  LOG_DEBUG('>>>> Maker: {}, Taker: {}'.format(maker,taker))
  LOG_DEBUG('>>>> Base market: {}'.format(basemarket))
  
  if maker == 'BTC':
    marketprice = 1/getmarketprice(takermarket, BOTuse)
    return marketprice
  
  makerprice = getmarketprice(basemarket, BOTuse)
  LOG_DEBUG('>>>> Taker market: {}'.format(takermarket))
  if taker == 'BTC':
    marketprice = makerprice
  else:
    takerprice = getmarketprice(takermarket, BOTuse)
    try:
      marketprice = makerprice / takerprice
    except:
      marketprice = 0
      LOG_DEBUG('ERROR: Price set to 0')
  return marketprice


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
