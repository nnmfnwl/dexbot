# Features Guide

**Note**: All parameter references in this guide refer to the [dexbot_v2.py](PARAMETERS.md#dexbot_v2py-main-trading-bot)
section in PARAMETERS.md.

## Order Management Features

### Staggered Orders

**What it does**: Places multiple orders at different price levels to increase fill probability and manage capital
exposure.

**Key Parameters**:

- `--slidestart`, `--slideend`: Price range multipliers
- `--sellstart`, `--sellend`: Order size range
- `--maxopen`: Maximum concurrent orders
- `--slidepump`: Additional pump/dump order spread
- `--sell_type`: Distribution curve type

**Configuration Example**:

```bash
--slidestart 1.01 --slideend 1.03 --sellstart 10 --sellend 20
--maxopen 5 --slidepump 0 --sell_type 0
```

**Order Sequence**:

- Order 1: 10 BLOCK at 1.01x market price
- Order 2: 12.5 BLOCK at 1.015x market price
- Order 3: 15 BLOCK at 1.02x market price
- Order 4: 17.5 BLOCK at 1.025x market price
- Order 5: 20 BLOCK at 1.03x market price

**Distribution Types**:

- `--sell_type 0`: Linear (default) - even size progression
- `--sell_type > 0`: Exponential - larger size progression
- `--sell_type < 0`: Logarithmic - smaller size progression

**Risk Calculation**:
Maximum exposure = `maxopen * sellend` (or `(maxopen + 1) * sellend` if `--slidepump > 0`)

**Use Cases**:

- Stable markets with consistent volume
- Capturing small price movements
- Capital allocation: 50-200% of daily trading volume

**Risk Profile**: Lower risk, steady returns

### Dynamic Slide System

**What it does**: Automatically widens spreads when inventory is imbalanced to encourage rebalancing trades.

**Key Parameters**:

- `--slide_dyn_zero_type`: `relative` or `static` balance tracking
- `--slide_dyn_zero`: Target balance ratio (0-1) or amount
- `--slide_dyn_sell_threshold`: Inventory change threshold
- `--slide_dyn_sell_step`: Spread adjustment per threshold
- `--slide_dyn_sell_max`: Maximum dynamic slide limit

**Configuration Example**:

```bash
# Balance-based dynamic slide configuration
--slide_dyn_zero_type relative --slide_dyn_zero 0.5
--slide_dyn_sell_threshold 0.02 --slide_dyn_sell_step 0.005
--slide_dyn_sell_max 0.1
```

**How it Works**:

1. Starting balance: 50 BLOCK, 50 LTC (50/50 ratio)
2. After selling 20 BLOCK: 30 BLOCK, 70 LTC (37.5/62.5 ratio)
3. Dynamic slide widens spread from 1.01x to 1.03x to slow further selling
4. If imbalance continues, spread widens further (up to `--slide_dyn_sell_max`)

**Ignore Zones**:

- `--slide_dyn_sell_ignore`: Small inventory changes that don't trigger adjustments
- `--slide_dyn_buy_ignore`: Similar for buy-side imbalances

**Use Cases**:

- Maintaining inventory balance in volatile markets
- Preventing over-exposure to single assets
- Capital allocation: 100-300% of target inventory

**Risk Profile**: Medium - prevents over-exposure but may miss short-term opportunities

## Safety Features

### Safety Boundaries

**What it does**: Circuit breakers that stop trading when price moves beyond defined limits to prevent trading in
unfavorable conditions.

**Key Parameters**:

- `--sboundary_asset`: Asset for boundary pricing
- `--sboundary_max`, `--sboundary_min`: Price limits
- `--sboundary_max_cancel`, `--sboundary_min_cancel`: Cancel orders on breach
- `--sboundary_max_exit`, `--sboundary_min_exit`: Exit bot on breach

**Configuration Example**:

```bash
# Protect against pump-and-dump schemes
--sboundary_asset USDT --sboundary_max 1.5 --sboundary_min 0.5
--sboundary_max_cancel True --sboundary_max_exit True
--sboundary_min_cancel True --sboundary_min_exit False
```

**Behavior**:

- If BLOCK/USDT price exceeds $1.50: Cancel all orders and exit bot
- If BLOCK/USDT price drops below $0.50: Cancel all orders but keep bot running

**Advanced Options**:

- `--sboundary_max_track_asset`: Dynamic price tracking for upper boundary
- `--sboundary_min_track_asset`: Dynamic price tracking for lower boundary
- `--sboundary_price_reverse`: Use inverse pricing for boundary calculations

**Use Cases**:

- Essential for live trading protection
- Preventing catastrophic losses during market crashes
- Avoiding pump-and-dump schemes

**Risk Mitigation**: Different exit/cancel combinations allow for flexible recovery strategies

### Takerbot

**What it does**: Scans the DEX order book for matching trades to simulate limit orders, automatically executing
favorable market orders.

**Key Parameters**:

- `--takerbot`: Scan interval in seconds
- `--hidden_orders`: Virtual orders for takerbot matching
- `--partial_orders`: Enable partial fill acceptance

**Configuration Example**:

```bash
# Aggressive takerbot with hidden orders
--takerbot 15 --hidden_orders True --partial_orders True
```

**Matching Criteria**:

- **Price**: Within configured slide range + dynamic slide adjustment
- **Size**: Between `sellstart-sellend` and `sellstartmin-sellendmin` ranges
- **Execution**: Multiple bot orders may be canceled to accept a single market order

**Hidden Orders**:

- `--hidden_orders True`: Creates virtual orders not broadcasted to DEX
- Only exist for takerbot matching, don't consume order slots
- Requires `--takerbot > 0` to function

**Partial Orders**:

- `--partial_orders True`: Accepts partial fills
- Works with hidden orders for comprehensive virtual order management

**Operation**:

- Automatically executes market orders meeting criteria
- Scan interval controlled by `--takerbot` parameter
- Cancelled orders can be reopened based on configuration

### Partial Order Management

**What it does**: Manages XBridge partial fills to prevent "dust" accumulation and optimize order sizing.

**Key Parameters**:

- `--sellstartmin`, `--sellendmin`: Minimum order sizes
- `--partial_orders`: Enable partial fill acceptance

**Dust Prevention Logic**:

- Minimum sizes prevent uneconomical order fragments
- If balance insufficient, orders created at maximum possible size between normal and minimum values
- Example: `--sellstart 100 --sellstartmin 15` with 50 BLOCK available → 50 BLOCK order

**Configuration Example**:

```bash
# Prevent dust with minimum order sizes
--sellstart 100 --sellstartmin 15 --sellend 200 --sellendmin 25
--partial_orders True
```

**Order Sizing Rules**:

- Uses `sellstartmin`/`sellendmin` when balance insufficient for full sizes
- Creates orders at maximum possible size within configured range
- Prevents creation of uneconomical small orders

## Pricing Features

### Pricing System

**What it does**: Centralized price management via proxy server to optimize API usage and provide consistent pricing
data across bot instances.

**Key Parameters**:

- `--pricing_proxy_url`: Proxy server connection URL
- `--price_provider`: Specific provider override
- `--usecg`, `--usecb`, `--usecustom`: Enable pricing sources

**Configuration Example**:

```bash
# Multi-source pricing with proxy
--pricing_proxy_url http://127.0.0.1:22333
--usecg True --usecb True --price_provider coingecko
```

**Pricing Sources**:

- Bittrex, CoinGecko, CryptoBridge, and custom endpoints
- Priorities configurable in pricing configuration
- Price redirection via `price_redirections` in bot config

**Proxy Implementation**:

- Runs as separate process with JSON-RPC interface
- Caches pricing data and refreshes periodically
- Multiple bot instances can connect to single proxy

**Use Cases**:

- Reducing API call overhead
- Consistent pricing across multiple bot instances
- Flexible pricing source selection

### Reset and Reopen Logic

**What it does**: Refreshes orders to maintain relevance to current market conditions through various trigger
mechanisms.

**Key Parameters**:

- `--resetonpricechangepositive`, `--resetonpricechangenegative`: Price-based triggers
- `--resetafterdelay`: Time-based reset interval
- `--reopenfinishednum`, `--reopenfinisheddelay`: Order completion triggers

**Reset Triggers (5 Types)**:

1. **Price increase**: `--resetonpricechangepositive` percentage
2. **Price decrease**: `--resetonpricechangenegative` percentage
3. **Time-based**: `--resetafterdelay` seconds since last reset
4. **Order count**: `--reopenfinishednum` filled orders
5. **Time delay**: `--reopenfinisheddelay` seconds since last fill

**Configuration Example**:

```bash
# Comprehensive reset strategy
--resetonpricechangepositive 2.5 --resetonpricechangenegative 2.5
--resetafterdelay 3600 --reopenfinishednum 10 --reopenfinisheddelay 900
```

**Key Differences**:

- **Reset**: Complete cancellation and recreation of all orders (full refresh)
- **Reopen**: Re-creation of only finished/cleared orders, keeping active orders

**Implementation Details**:

- Multiple systems work in parallel with different triggers
- Takerbot-taken orders count toward reopen triggers
- Reset after finish affects both reset and reopen counting

**Use Cases**:

- Maintaining order relevance in volatile markets
- Balancing between market responsiveness and stability
- Preventing stale orders from sitting too long
