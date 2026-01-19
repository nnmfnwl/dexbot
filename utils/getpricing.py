#!/usr/bin/env python3
__author__ = 'atcsecure'
__copyright__ = 'All rights reserved'
__credits__ = ['atcsecure']
__license__ = 'GPL'
__version__ = '0.0.1'
__maintainer__ = 'atcsecure'
__status__ = 'Alpha'
__update__ = '2026.01.19 nnmfnwl7'

import time
import sys
import requests
from utils import coingecko
from utils import custompricing
from utils import dxsettings

def getmarketprice(marketname, BOTuse):
  # get market price
  markets = []
  markets = marketname.split('-')
  lastprice = 0
  if markets[1] == 'BTC':
    marketname = '{}-{}'.format(markets[1], markets[0])

  if BOTuse == 'custom':
    print('### custom ####')
    asset = markets[1]
    print('>>>> Looking up custom pricing: {}'.format(marketname))
    # lets get maker price
    try:
        endpoint = dxsettings.apiendpoint[asset]
        lastprice = custompricing.getprice(asset,endpoint)
    except Exception as e:
        print('ERROR: {}'.format(e))
        print('program aborted...')
        sys.exit(1)
    print(lastprice)

  if BOTuse == 'cg' or lastprice == 0:
    print('>>>> Looking up CoinGecko pricing: {}'.format(markets[1]))
    cg = coingecko.CoinGeckoAPI()
    cg_coin_list = cg.get_coins_list()
    # CoinGecko uses IDs, need to lookup ID for market
    for coin in cg_coin_list:
      if coin['symbol'] == markets[1].lower():
        coin_id = coin['id']
        print('Found {} ID: {}'.format(markets[1],coin_id))
        currentprice = cg.get_price(ids=coin_id, vs_currencies=markets[0])
        lastprice = currentprice[coin_id]
        vsmarket = markets[0].lower()
        print('Last price: {}'.format(lastprice[vsmarket]))
        lastprice = lastprice[vsmarket]
        break

  return float(lastprice)


def getpricedata(maker, taker, BOTuse):
  basemarket = ('BTC-{}'.format(maker))
  takermarket = ('BTC-{}'.format(taker))
  print('>>>> Maker: {}, Taker: {}'.format(maker,taker))
  print('>>>> Base market: {}'.format(basemarket))
  if maker == 'BTC':
    marketprice = 1/getmarketprice(takermarket, BOTuse)
    return marketprice
  makerprice = getmarketprice(basemarket, BOTuse)
  print('>>>> Taker market: {}'.format(takermarket))
  if taker == 'BTC':
    marketprice = makerprice
  else:
    takerprice = getmarketprice(takermarket, BOTuse)
    try:
      marketprice = makerprice / takerprice
    except:
      marketprice = 0
      print('ERROR: Price set to 0')
  return marketprice


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
