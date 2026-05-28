# Configuration Examples

**Note**: Requires UTXO splitting for proper order distribution.

## Basic Market Making

**Use case**: Stable markets (e.g., BLOCK/LTC).
**Risk level**: Low.

```python
botconfig = (
    "--maker BLOCK --taker LTC "
    "--maxopen 3 "
    "--slidestart 1.01 --slideend 1.03 "
    "--sellstart 10 --sellend 10 "
    "--sell_type 0 "
    "--usecg"
)
```

**Why these values?**

- `maxopen 3`: Limits to 3 maximum concurrent orders
- `slidestart 1.01`: 1% spread for tight competition.
- `sellstart 10`: Minimum order size.
- `--usecg`: Uses CoinGecko for reliable price data.
- `--sell_type 0`: Linear distribution (equal order sizes).

## Volatility Capture

**Use case**: Volatile markets (e.g., BLOCK/BTC during altseason).
**Risk level**: Medium-High.

```python
botconfig = (
    "--maker BLOCK --taker BTC "
    "--maxopen 8 "
    "--slidestart 1.02 --slideend 1.15 "
    "--sellstart 5 --sellend 50 "
    "--sell_type 0.8 "
    "--usecg"
)
```

**Why these values?**

- `maxopen 8`: More orders to capture wider price movements.
- `slideend 1.15`: 15% spread for high volatility.
- `sell_type 0.8`: Logarithmic distribution (larger orders further from price).
- `sellend 50`: Larger orders at wider spreads for bigger moves.

**Warning**: Requires significant capital. During low volatility, orders may not fill.

## Inventory Balancing

**Use case**: Maintains a 50/50 ratio between two assets.
**Risk level**: Medium.

```python
botconfig = (
    "--maker LTC --taker BLOCK "
    "--maxopen 5 "
    "--slidestart 1.01 --slideend 1.05 "
    "--slide_dyn_zero_type relative --slide_dyn_zero -2 "
    "--slide_dyn_sell_threshold 0.02 --slide_dyn_sell_step 0.005 "
    "--slide_dyn_buy_threshold 0.02 --slide_dyn_buy_step 0.005 "
    "--usecg"
)
```

**Note**: The `--sell_type` parameter controls order size distribution:

- `0`: Linear distribution (equal order sizes)
- `>0 to <1`: Logarithmic distribution (larger orders further from price)
- `<0 to >-1`: Reverse logarithmic distribution

**Why these values?**

- `slide_dyn_zero -2`: Automatically set the balanced point based on current inventory.
- `slide_dyn_sell_threshold 0.02`: Widen spread 2% per 2% inventory change.
- `slide_dyn_sell_step 0.005`: Add 0.5% to spread each step.
- `maxopen 5`: Moderate order count for balance management.

**Note**: This strategy actively manages inventory. Monitor closely during high volatility.

## Safety Boundaries

**Use case**: Stops trading if the price exceeds absolute limits.

```python
botconfig = (
    "--maker BLOCK --taker USDT "
    "--sboundary_asset USDT "
    "--sboundary_max 1.5 --sboundary_min 0.5 "
    "--sboundary_max_exit --sboundary_min_exit "
    "--usecg"
)
```

**Why these values?**

- `sboundary_max 1.5`: 50% above initial price triggers boundary
- `sboundary_min 0.5`: 50% below initial price triggers boundary
- `--sboundary_max_exit`: Exit trading when upper boundary is reached
- `--sboundary_min_exit`: Exit trading when lower boundary is reached

## Bidirectional Trading

Requires two separate strategy files and bot instances.

**Instance A (`BLOCK_LTC`):**

```python
botconfig = "--maker BLOCK --taker LTC --slidestart 1.02 --sellstart 10 --sell_type 0 --usecg"
```

**Instance B (`LTC_BLOCK`):**

```python
botconfig = "--maker LTC --taker BLOCK --slidestart 1.02 --sellstart 0.5 --sell_type 0 --usecg"
```

## Price Redirections

Used for assets without reliable external price feeds.

```python
# In strategy config file (e.g., my_strategy.py):
price_redirections = {
    "TOKEN": {"asset": "USDT", "price": 0.50}
}

# Bot configuration:
botconfig = "--maker TOKEN --taker LTC --sellstart 100 --usecg"
```

For detailed parameter explanations, see [PARAMETERS.md](PARAMETERS.md).