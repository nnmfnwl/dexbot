#!/usr/bin/env python3
"""CCXT Pricing Module Demo - Demonstrating Binance, Kraken, and KuCoin functionality"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ccxt_pricing import CCXTPricing, SymbolNotFoundError
import ccxt


def demo_exchange(exchange_name: str, demo_pairs: list):
    """Demonstrate a specific exchange with standardized calls
    
    Args:
        exchange_name: Name of the exchange to demo
        demo_pairs: List of (base, quote) tuples to test
    """
    print(f'\n{"=" * 60}')
    print(f'Demo: {exchange_name.upper()}')
    print(f'{"=" * 60}')

    ccxt_pricing = CCXTPricing()

    # Demo 1: Load exchange
    print(f'\n1. Load {exchange_name} exchange')
    try:
        exchange = ccxt_pricing.get_exchange(exchange_name)
        print(f'   ✓ Exchange loaded: {exchange.name}')
    except ValueError as e:
        print(f'   ✗ Failed to load exchange: {e}')
        return
    except Exception as e:
        print(f'   ✗ Unexpected error: {e}')
        return

    # Demo 2: Load markets
    print(f'\n2. Load {exchange_name} markets')
    try:
        markets = ccxt_pricing.get_markets(exchange_name)
        print(f'   ✓ Markets loaded: {len(markets)} markets available')
    except ccxt.NetworkError as e:
        print(f'   ✗ Network error loading markets: {e}')
        return
    except ccxt.ExchangeError as e:
        print(f'   ✗ Exchange error loading markets: {e}')
        return
    except Exception as e:
        print(f'   ✗ Unexpected error: {e}')
        return

    # Demo 3: Get individual prices
    print(f'\n3. Get individual prices')
    for base, quote in demo_pairs:
        try:
            price = ccxt_pricing.get_price(base, quote, exchange_name)
            print(f'   ✓ {base}/{quote}: {price}')
        except SymbolNotFoundError as e:
            print(f'   ✗ {base}/{quote}: Symbol not found - {e}')
        except ccxt.NetworkError as e:
            print(f'   ✗ {base}/{quote}: Network error - {e}')
        except ccxt.ExchangeError as e:
            print(f'   ✗ {base}/{quote}: Exchange error - {e}')
        except Exception as e:
            print(f'   ✗ {base}/{quote}: Unexpected error - {e}')

    # Demo 4: Batch fetch prices
    print(f'\n4. Batch fetch prices')
    try:
        batch_prices = ccxt_pricing.get_prices_batch(demo_pairs, exchange_name)
        print(f'   ✓ Batch fetch successful ({len(batch_prices)} pairs)')
        for (base, quote), price in batch_prices.items():
            print(f'      {base}/{quote}: {price}')
    except ValueError as e:
        print(f'   ✗ Batch fetch failed (no valid symbols): {e}')
    except ccxt.NetworkError as e:
        print(f'   ✗ Batch fetch failed (network error): {e}')
    except ccxt.ExchangeError as e:
        print(f'   ✗ Batch fetch failed (exchange error): {e}')
    except Exception as e:
        print(f'   ✗ Unexpected error: {e}')

    # Demo 5: Invalid pair handling
    print(f'\n5. Invalid pair handling (should raise SymbolNotFoundError)')
    try:
        invalid_price = ccxt_pricing.get_price('INVALID', 'COIN', exchange_name)
        print(f'   ✗ Invalid pair returned unexpected value: {invalid_price}')
    except SymbolNotFoundError as e:
        print(f'   ✓ Invalid pair handled correctly: {e}')
    except Exception as e:
        print(f'   ✗ Unexpected error type: {e}')


def demo_all_exchanges():
    """Demonstrate functionality across all exchanges"""
    print('=' * 60)
    print('CCXT PRICING MODULE - DEMONSTRATION')
    print('=' * 60)

    # Define demo pairs for each exchange
    # Using a dictionary to eliminate repetition (DRY principle)
    exchanges_config = {
        'binance': [('BTC', 'USDT'), ('LTC', 'BTC'), ('ETH', 'USDT')],
        'kraken': [('BTC', 'USD'), ('LTC', 'BTC'), ('ETH', 'USD')],
        'kucoin': [('BTC', 'USDT'), ('LTC', 'BTC'), ('ETH', 'USDT')]
    }

    # Demo each exchange
    for exchange_name, demo_pairs in exchanges_config.items():
        demo_exchange(exchange_name, demo_pairs)

    # Demo invalid exchange handling
    print(f'\n{"=" * 60}')
    print('Demo: Invalid Exchange Handling')
    print(f'{"=" * 60}')
    ccxt_pricing = CCXTPricing()
    try:
        invalid_exchange = ccxt_pricing.get_exchange('invalid_exchange_name')
        print('   ✗ Invalid exchange not handled correctly')
    except ValueError as e:
        print(f'   ✓ Invalid exchange handled correctly: {e}')
    except Exception as e:
        print(f'   ✗ Unexpected error: {e}')

    print(f'\n{"=" * 60}')
    print('DEMONSTRATION COMPLETED')
    print(f'{"=" * 60}')


def demo_resilience():
    """Demonstrate resilience features"""
    print(f'\n{"=" * 60}')
    print('Demo: Resilience Features')
    print(f'{"=" * 60}')

    # Demo custom configuration
    print('\n1. Custom timeout and retry configuration')
    ccxt_custom = CCXTPricing(timeout=5000, retries=2, backoff_factor=1.5)
    print(f'   ✓ Created instance with custom config:')
    print(f'      - Timeout: {ccxt_custom.timeout}ms')
    print(f'      - Retries: {ccxt_custom.retries}')
    print(f'      - Backoff factor: {ccxt_custom.backoff_factor}')

    # Demo rate limiting (enabled by default)
    print('\n2. Rate limiting enabled by default')
    try:
        exchange = ccxt_custom.get_exchange('binance')
        print(f'   ✓ Exchange created with rate limiting: {exchange.enableRateLimit}')
    except Exception as e:
        print(f'   ✗ Error: {e}')

    # Demo symbol variants
    print('\n3. Symbol format variants')
    ccxt_pricing = CCXTPricing()
    variants = ccxt_pricing._generate_symbol_variants('BTC', 'USD')
    print(f'   ✓ Generated {len(variants)} symbol variants for BTC/USD:')
    for variant in variants:
        print(f'      - {variant}')


def demo_batch_return_format():
    """Demonstrate batch fetch return format with original pairs"""
    print(f'\n{"=" * 60}')
    print('Demo: Batch Fetch Return Format')
    print(f'{"=" * 60}')

    ccxt_pricing = CCXTPricing()

    print('\n1. Batch fetch returns (base, quote) tuples as keys')
    pairs = [('BTC', 'USDT'), ('ETH', 'USDT')]

    try:
        batch_prices = ccxt_pricing.get_prices_batch(pairs, 'binance')
        print(f'   ✓ Fetched {len(batch_prices)} prices')
        print(f'   ✓ Return type: Dict[Tuple[str, str], float]')
        print('\n   Results:')
        for (base, quote), price in batch_prices.items():
            print(f'      ({base!r}, {quote!r}): {price}')
    except Exception as e:
        print(f'   ✗ Error: {e}')


if __name__ == '__main__':
    # Run main demos
    demo_all_exchanges()

    # Run resilience demo
    demo_resilience()

    # Run batch return format demo
    demo_batch_return_format()
