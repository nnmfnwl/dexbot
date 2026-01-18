#!/usr/bin/env python3
"""CCXT Pricing Module - Handles price fetching from CCXT exchanges"""

import time
from typing import Dict, List, Tuple, Any

import ccxt


class SymbolNotFoundError(Exception):
    """Raised when a trading symbol is not found on an exchange"""
    pass


class CCXTPricing:
    """CCXT pricing handler with connection management and resilience features"""

    def __init__(self, timeout: int = 10000, retries: int = 3, backoff_factor: float = 2.0):
        """Initialize CCXT pricing handler
        
        Args:
            timeout: Request timeout in milliseconds (default: 10000)
            retries: Number of retry attempts for network failures (default: 3)
            backoff_factor: Exponential backoff multiplier (default: 2.0)
        """
        self.exchanges: Dict[str, ccxt.Exchange] = {}
        self.markets: Dict[str, Dict[str, Any]] = {}
        self.timeout = timeout
        self.retries = retries
        self.backoff_factor = backoff_factor

    def _generate_symbol_variants(self, base: str, quote: str) -> List[str]:
        """Generate potential symbol formats for a given pair.
        
        Generates multiple format variants to handle different exchange conventions:
        - Standard: BASE/QUOTE (uppercase) - used by Binance, Kraken, Coinbase
        - Hyphenated: BASE-QUOTE (uppercase) - used by some exchanges
        - Lowercase: base/quote - less common but exists
        
        Args:
            base: Base currency symbol.
            quote: Quote currency symbol.
            
        Returns:
            A list of potential symbol strings, ordered by likelihood.
        """
        base_upper = base.upper()
        quote_upper = quote.upper()
        base_lower = base.lower()
        quote_lower = quote.lower()

        return [
            f"{base_upper}/{quote_upper}",  # Most common: BTC/USDT
            f"{base_upper}-{quote_upper}",  # Hyphenated: BTC-USDT
            f"{base_lower}/{quote_lower}",  # Lowercase: btc/usdt
            f"{base_upper}_{quote_upper}",  # Underscore: BTC_USDT
        ]

    def _fetch_with_retry(self, func, *args, **kwargs) -> Any:
        """Execute a function with retry logic for network failures
        
        Args:
            func: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result from the function call
            
        Raises:
            ccxt.NetworkError: If all retry attempts fail
            ccxt.ExchangeError: For non-network related exchange errors
        """
        last_exception = None

        for attempt in range(self.retries):
            try:
                return func(*args, **kwargs)
            except ccxt.NetworkError as e:
                last_exception = e
                if attempt < self.retries - 1:
                    sleep_time = self.backoff_factor ** attempt
                    print(
                        f"WARNING: Network error on attempt {attempt + 1}/{self.retries}: {e}. "
                        f"Retrying in {sleep_time}s..."
                    )
                    time.sleep(sleep_time)
                else:
                    print(f"ERROR: All {self.retries} retry attempts failed")
            except ccxt.ExchangeError as e:
                # Don't retry exchange-specific errors (invalid symbol, insufficient funds, etc.)
                print(f"ERROR: Exchange error (not retrying): {e}")
                raise

        # If we exhausted all retries, raise the last exception
        raise last_exception

    def get_exchange(self, exchange_name: str) -> ccxt.Exchange:
        """Get or create exchange instance
        
        Args:
            exchange_name: Name of the exchange (e.g., 'binance', 'coinbase')
            
        Returns:
            CCXT exchange instance
            
        Raises:
            ValueError: If exchange name is unknown
            Exception: If exchange creation fails for other reasons
        """
        if exchange_name in self.exchanges:
            return self.exchanges[exchange_name]

        try:
            exchange_class = getattr(ccxt, exchange_name)
            exchange = exchange_class({
                'timeout': self.timeout,
                'enableRateLimit': True,  # Built-in rate limiting protection
            })
            self.exchanges[exchange_name] = exchange
            return exchange
        except AttributeError:
            raise ValueError(f"Unknown exchange: {exchange_name}")
        except Exception as e:
            print(f"ERROR: Failed to create exchange {exchange_name}: {e}")
            raise

    def get_markets(self, exchange_name: str) -> Dict[str, Any]:
        """Get markets for exchange
        
        Args:
            exchange_name: Name of the exchange
            
        Returns:
            Dictionary of markets
            
        Raises:
            ValueError: If exchange is unknown
            Exception: If market loading fails
        """
        if exchange_name in self.markets:
            return self.markets[exchange_name]

        exchange = self.get_exchange(exchange_name)

        try:
            markets = self._fetch_with_retry(exchange.load_markets)
            self.markets[exchange_name] = markets
            return markets
        except Exception as e:
            print(f"ERROR: Failed to load markets for {exchange_name}: {e}")
            raise

    def get_price(self, base: str, quote: str, exchange_name: str) -> float:
        """Get price from exchange
        
        Args:
            base: Base currency symbol (e.g., 'BTC')
            quote: Quote currency symbol (e.g., 'USD')
            exchange_name: Name of the exchange
            
        Returns:
            Current price as float
            
        Raises:
            ValueError: If exchange is unknown
            SymbolNotFoundError: If symbol is not found on the exchange
            ccxt.NetworkError: If network request fails after retries
            ccxt.ExchangeError: For other exchange-specific errors
        """
        exchange = self.get_exchange(exchange_name)
        markets = self.get_markets(exchange_name)

        symbols = self._generate_symbol_variants(base, quote)

        for symbol in symbols:
            if symbol in markets:
                try:
                    ticker = self._fetch_with_retry(exchange.fetch_ticker, symbol)
                    return float(ticker['last'])
                except Exception as e:
                    print(f"ERROR: Failed to fetch ticker for {symbol} on {exchange_name}: {e}")
                    raise

        raise SymbolNotFoundError(f"Symbol {base}/{quote} not found on {exchange_name}")

    def get_prices_batch(
            self,
            pairs: List[Tuple[str, str]],
            exchange_name: str
    ) -> Dict[Tuple[str, str], float]:
        """Batch fetch multiple tickers in one CCXT call
        
        Args:
            pairs: List of (base, quote) currency pairs
            exchange_name: Name of the exchange
            
        Returns:
            Dictionary mapping (base, quote) tuples to prices
            
        Raises:
            ValueError: If exchange is unknown or no valid symbols found
            ccxt.NetworkError: If network request fails after retries
            ccxt.ExchangeError: For other exchange-specific errors
        """
        exchange = self.get_exchange(exchange_name)
        markets = self.get_markets(exchange_name)

        # Map pairs to their valid symbols
        pair_to_symbol = {}
        for base, quote in pairs:
            symbols = self._generate_symbol_variants(base, quote)
            for symbol in symbols:
                if symbol in markets:
                    pair_to_symbol[(base, quote)] = symbol
                    break

        if not pair_to_symbol:
            raise ValueError(f"No valid symbols found for pairs on {exchange_name}")

        try:
            # Batch fetch all tickers in one call
            valid_symbols = list(pair_to_symbol.values())
            tickers = self._fetch_with_retry(exchange.fetch_tickers, valid_symbols)

            # Map results back to original (base, quote) pairs
            result = {}
            for pair, symbol in pair_to_symbol.items():
                if symbol in tickers:
                    result[pair] = float(tickers[symbol]['last'])

            return result
        except Exception as e:
            print(f"ERROR: Failed to fetch tickers batch on {exchange_name}: {e}")
            raise
