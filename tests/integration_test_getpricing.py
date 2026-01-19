#!/usr/bin/env python3

import time
import sys

from utils.getpricing import getmarketprice, getpricedata


# Rate limiting for CoinGecko
class CoinGeckoRateLimiter:
    def __init__(self, calls_per_minute=2):
        self.calls_per_minute = calls_per_minute
        self.min_interval = 60.0 / calls_per_minute 
        self.last_call_time = 0
    
    def wait_if_needed(self):
        current_time = time.time()
        time_since_last = current_time - self.last_call_time
        
        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            if sleep_time > 0:
                print(f"Rate limiting: sleeping {sleep_time:.1f}s for CoinGecko")
                time.sleep(sleep_time)
        
        self.last_call_time = time.time()


# Create rate limiter instance
cg_limiter = CoinGeckoRateLimiter()


def integration_test__getpricing():
    print('>> INFO >> TEST >> integration_test__getpricing')
    
    # Define test data
    test_pairs = [
        ('BTC', 'USDT'),
        ('BTC', 'LTC'),
        ('BTC', 'DOGE'),
    ]
    test_markets = [f"{base}-{quote}" for base, quote in test_pairs]
    
    error_num = 0
    
    ####################################################################
    ## Test getmarketprice with CCXT
    print('\n>> INFO >> TEST >> getmarketprice() with CCXT (Binance)')
    for market in test_markets:
        try:
            price = getmarketprice(market, 'ccxt')
            if price > 0:
                print('>> INFO >> TEST >> CCXT {} = {}'.format(market, price))
            else:
                print('** ERROR >> TEST >> CCXT {} >> invalid price {}'.format(market, price))
                error_num += 1
        except Exception as e:
            print('** ERROR >> TEST >> CCXT {} >> exception: {}'.format(market, e))
            error_num += 1
        time.sleep(1)
    
    ####################################################################
    ## Test getmarketprice with CoinGecko
    print('\n>> INFO >> TEST >> getmarketprice() with CoinGecko (cg)')
    for market in test_markets:
        cg_limiter.wait_if_needed()  # Apply rate limiting
        try:
            price = getmarketprice(market, 'cg')
            if price > 0:
                print('>> INFO >> TEST >> CoinGecko {} = {}'.format(market, price))
            else:
                print('** ERROR >> TEST >> CoinGecko {} >> invalid price {}'.format(market, price))
                error_num += 1
        except Exception as e:
            print('** ERROR >> TEST >> CoinGecko {} >> failed: {}'.format(market, e))
            error_num += 1
    
    ####################################################################
    ## Test getpricedata with CCXT
    print('\n>> INFO >> TEST >> getpricedata() with CCXT (Binance)')
    for maker, taker in test_pairs:
        try:
            price = getpricedata(maker, taker, 'ccxt')
            if price > 0:
                print('>> INFO >> TEST >> CCXT {}/{} = {}'.format(maker, taker, price))
            else:
                print('** ERROR >> TEST >> CCXT {}/{} >> invalid price {}'.format(maker, taker, price))
                error_num += 1
        except Exception as e:
            print('** ERROR >> TEST >> CCXT {}/{} >> exception: {}'.format(maker, taker, e))
            error_num += 1
        time.sleep(1)
    
    ####################################################################
    ## Test getpricedata with CoinGecko
    print('\n>> INFO >> TEST >> getpricedata() with CoinGecko (cg)')
    for maker, taker in test_pairs:
        cg_limiter.wait_if_needed()  # Apply rate limiting
        try:
            price = getpricedata(maker, taker, 'cg')
            if price > 0:
                print('>> INFO >> TEST >> CoinGecko {}/{} = {}'.format(maker, taker, price))
            else:
                print('** ERROR >> TEST >> CoinGecko {}/{} >> invalid price {}'.format(maker, taker, price))
                error_num += 1
        except Exception as e:
            print('** ERROR >> TEST >> CoinGecko {}/{} >> failed: {}'.format(maker, taker, e))
            error_num += 1
    
    ####################################################################
    ## Test market name reversal logic
    print('\n>> INFO >> TEST >> Market Name Reversal Logic')
    base, quote = test_pairs[0]
    market_forward = "{}-{}".format(base, quote)
    market_reverse = "{}-{}".format(quote, base)
    try:
        price1 = getmarketprice(market_forward, 'ccxt')
        time.sleep(1)
        price2 = getmarketprice(market_reverse, 'ccxt')
        
        if price1 > 0 and price2 > 0:
            ratio = price1 * price2
            if abs(ratio - 1.0) < 0.1:
                print('>> INFO >> TEST >> Market reversal {}={}, {}={}, ratio={:.4f}'.format(
                    market_forward, price1, market_reverse, price2, ratio))
            else:
                print('** ERROR >> TEST >> Market reversal >> ratio {:.4f} outside expected range'.format(ratio))
                error_num += 1
        else:
            print('** ERROR >> TEST >> Market reversal >> invalid prices {}, {}'.format(price1, price2))
            error_num += 1
    except Exception as e:
        print('** ERROR >> TEST >> Market reversal >> exception: {}'.format(e))
        error_num += 1
    
    ####################################################################
    ## Test error handling
    print('\n>> INFO >> TEST >> Error Handling')
    try:
        price = getmarketprice('INVALID-INVALID', 'ccxt')
        if price == 0:
            print('>> INFO >> TEST >> Invalid market handled gracefully (returned 0)')
        else:
            print('** ERROR >> TEST >> Invalid market >> returned {} instead of 0'.format(price))
            error_num += 1
    except Exception as e:
        print('** ERROR >> TEST >> Exception handled gracefully: {}'.format(type(e).__name__))
        error_num += 1
    
    ####################################################################
    ## Summary
    print('\n>> INFO >> TEST >> Summary')
    if error_num == 0:
        print('>> INFO >> TEST >> All integration tests passed')
        sys.exit(0)
    else:
        print('** ERROR >> TEST >> {} integration tests failed'.format(error_num))
        sys.exit(1)


if __name__ == '__main__':
    integration_test__getpricing()
