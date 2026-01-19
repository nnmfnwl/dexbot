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
    
    # Define sources to test
    sources = ['ccxt', 'cg']
    
    error_num = 0
    
    # Store results for final comparison
    results = {}
    for source in sources:
        results[source] = {}
    
    for source in sources:
        print(f'\n>> INFO >> TEST >> Testing source: {source.upper()}')
        
        ####################################################################
        ## Test getmarketprice
        print(f'\n>> INFO >> TEST >> getmarketprice() with {source.upper()}')
        for market in test_markets:
            # Apply rate limiting for CoinGecko BEFORE the call
            if source == 'cg':
                cg_limiter.wait_if_needed()
            
            try:
                price = getmarketprice(market, source)
                if price > 0:
                    print('>> INFO >> TEST >> {} {} = {}'.format(source.upper(), market, price))
                    results[source][f'getmarketprice_{market}'] = {'price': price, 'status': 'PASS'}
                else:
                    print('** ERROR >> TEST >> {} {} >> invalid price {}'.format(source.upper(), market, price))
                    results[source][f'getmarketprice_{market}'] = {'price': price, 'status': 'FAIL'}
                    error_num += 1
            except Exception as e:
                print('** ERROR >> TEST >> {} {} >> exception: {}'.format(source.upper(), market, e))
                results[source][f'getmarketprice_{market}'] = {'price': None, 'status': 'FAIL', 'error': str(e)}
                error_num += 1
        
        ####################################################################
        ## Test getpricedata
        print(f'\n>> INFO >> TEST >> getpricedata() with {source.upper()}')
        for maker, taker in test_pairs:
            # Apply rate limiting for CoinGecko BEFORE the call
            if source == 'cg':
                cg_limiter.wait_if_needed()
            
            try:
                price = getpricedata(maker, taker, source)
                if price > 0:
                    print('>> INFO >> TEST >> {} {}/{} = {}'.format(source.upper(), maker, taker, price))
                    results[source][f'getpricedata_{maker}_{taker}'] = {'price': price, 'status': 'PASS'}
                else:
                    print('** ERROR >> TEST >> {} {}/{} >> invalid price {}'.format(source.upper(), maker, taker, price))
                    results[source][f'getpricedata_{maker}_{taker}'] = {'price': price, 'status': 'FAIL'}
                    error_num += 1
            except Exception as e:
                print('** ERROR >> TEST >> {} {}/{} >> exception: {}'.format(source.upper(), maker, taker, e))
                results[source][f'getpricedata_{maker}_{taker}'] = {'price': None, 'status': 'FAIL', 'error': str(e)}
                error_num += 1
        
        ####################################################################
        ## Test market name reversal logic
        print(f'\n>> INFO >> TEST >> Market Name Reversal Logic ({source.upper()})')
        base, quote = test_pairs[0]
        market_forward = "{}-{}".format(base, quote)
        market_reverse = "{}-{}".format(quote, base)
        try:
            # Apply rate limiting for CoinGecko BEFORE the first call
            if source == 'cg':
                cg_limiter.wait_if_needed()
            price1 = getmarketprice(market_forward, source)
            
            # Apply rate limiting for CoinGecko BEFORE the second call
            if source == 'cg':
                cg_limiter.wait_if_needed()
            price2 = getmarketprice(market_reverse, source)
            
            if price1 > 0 and price2 > 0:
                ratio = price1 * price2
                if abs(ratio - 1.0) < 0.1:
                    print('>> INFO >> TEST >> Market reversal {}={}, {}={}, ratio={:.4f}'.format(
                        market_forward, price1, market_reverse, price2, ratio))
                    results[source]['market_reversal'] = {'ratio': ratio, 'status': 'PASS'}
                else:
                    print('** ERROR >> TEST >> Market reversal >> ratio {:.4f} outside expected range'.format(ratio))
                    results[source]['market_reversal'] = {'ratio': ratio, 'status': 'FAIL'}
                    error_num += 1
            else:
                print('** ERROR >> TEST >> Market reversal >> invalid prices {}, {}'.format(price1, price2))
                results[source]['market_reversal'] = {'ratio': None, 'status': 'FAIL'}
                error_num += 1
        except Exception as e:
            print('** ERROR >> TEST >> Market reversal >> exception: {}'.format(e))
            results[source]['market_reversal'] = {'ratio': None, 'status': 'FAIL', 'error': str(e)}
            error_num += 1
        
        ####################################################################
        ## Test error handling
        print(f'\n>> INFO >> TEST >> Error Handling ({source.upper()})')
        try:
            # Apply rate limiting for CoinGecko BEFORE the call
            if source == 'cg':
                cg_limiter.wait_if_needed()
            price = getmarketprice('INVALID-INVALID', source)
            if price == 0:
                print('>> INFO >> TEST >> Invalid market handled gracefully (returned 0)')
                results[source]['error_handling'] = {'price': price, 'status': 'PASS'}
            else:
                print('** ERROR >> TEST >> Invalid market >> returned {} instead of 0'.format(price))
                results[source]['error_handling'] = {'price': price, 'status': 'FAIL'}
                error_num += 1
        except Exception as e:
            print('** ERROR >> TEST >> Exception handled gracefully: {}'.format(type(e).__name__))
            results[source]['error_handling'] = {'price': None, 'status': 'PASS', 'error': str(e)}
            error_num += 1
    
    ####################################################################
    ## Final Comparison Table
    print('\n' + '='*80)
    print('FINAL COMPARISON TABLE')
    print('='*80)
    
    # Collect all test names across sources
    all_tests = set()
    for source in sources:
        all_tests.update(results[source].keys())
    
    # Sort tests for consistent ordering
    sorted_tests = sorted(all_tests)
    
    # Print header
    header = f"{'Test':<30} | {'CCXT':<20} | {'CG':<20} | {'Diff':<10} | {'% Diff':<10}"
    print(header)
    print('-'*len(header))
    
    # Print rows
    for test in sorted_tests:
        ccxt_result = results['ccxt'].get(test, {})
        cg_result = results['cg'].get(test, {})
        
        ccxt_price = ccxt_result.get('price') or ccxt_result.get('ratio')
        cg_price = cg_result.get('price') or cg_result.get('ratio')
        
        ccxt_status = ccxt_result.get('status', 'N/A')
        cg_status = cg_result.get('status', 'N/A')
        
        # Calculate differences if both prices are available
        diff = ''
        pct_diff = ''
        if ccxt_price is not None and cg_price is not None and isinstance(ccxt_price, (int, float)) and isinstance(cg_price, (int, float)):
            diff = ccxt_price - cg_price
            if cg_price != 0:
                pct_diff = (diff / cg_price) * 100
                pct_diff = f"{pct_diff:.2f}%"
            else:
                pct_diff = 'N/A'
            diff = f"{diff:.6f}"
        
        # Format CCXT and CG columns with status
        ccxt_col = f"{ccxt_price if ccxt_price is not None else 'N/A'} ({ccxt_status})"
        cg_col = f"{cg_price if cg_price is not None else 'N/A'} ({cg_status})"
        
        print(f"{test:<30} | {ccxt_col:<20} | {cg_col:<20} | {diff:<10} | {pct_diff:<10}")
    
    print('='*80)
    
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
