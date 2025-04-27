#!/usr/bin/python3

# pricing proxy client for pricing storage

from utils import getpricing as pricebot

# proxy server cache callback to get pricing information from external source
def pricing_proxy_server__pricing_storage__try_get_price_fn(maker__item_to_sell, taker__payed_by, price_provider):
    
    # ~ print('>>>> Updating external pricing information for maker <{0}> taker <{1}> /{2}'.format(maker__item_to_sell, taker__payed_by, price_provider))
    maker_price_in_takers = pricebot.getpricedata(maker__item_to_sell, taker__payed_by, price_provider)
    
    return maker_price_in_takers
