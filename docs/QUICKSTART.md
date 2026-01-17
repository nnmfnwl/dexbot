# Quick Start Guide

## Prerequisites

Before installing dexbot, ensure you have the following:

- **Blocknet wallet**: Running, synced, and unlocked
- **Asset wallets**: Running, synced, and unlocked for the assets you want to trade
- **Python 3.7+**: Installed and available in your PATH (verify with `python3 --version`)
- **Funds**: Available in legacy addresses with split UTXOs

### UTXO Splitting

**Why UTXO Splitting is Required**: Blocknet xBridge requires separate UTXOs for each order. Each order placed on the
DEX consumes UTXO(s), and insufficient UTXOs will limit your ability to place concurrent orders.

**Important**: Without proper UTXO splitting, you can only place 1-2 orders simultaneously, severely limiting your
trading capacity.

Split your UTXOs using the Blocknet wallet before running dexbot:

```bash
# Split UTXOs (example: split balance of {address} into UTXOs of {amount} {coin} each)
# Warning: BTC transaction fees can be significant - only split what's necessary
# Note: This is a Blocknet wallet command, not a dexbot command
blocknet-cli dxsplitaddress {coin} {amount} {address}
```

For detailed UTXO splitting guidance, refer to the [Blocknet documentation](https://api.blocknet.org/#dxsplitaddress).

## Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/nnmfnwl/dexbot
cd dexbot
```

### Step 2: Install Dependencies

```bash
pip3 install -r requirements.txt
```

**Troubleshooting**: If you encounter dependency issues, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Configuration

### Strategy File Setup

1. **Duplicate the template**:
   ```bash
   cp howto/examples/bot_v2_template.py my_strategy.py
   ```

2. **Configure RPC credentials** in `my_strategy.py`:
   ```python
   rpcuser = "user"
   rpcpassword = "password"
   rpchostname = "127.0.0.1"
   rpcport = 41414
   ```

3. **Define your bot configuration** in `my_strategy.py`:
   ```python
   botconfig = (
       "--maker BLOCK --taker LTC "
       "--makeraddress Bxxx --takeraddress Lxxx "
       "--maxopen 3 "
       "--slidestart 1.01 --slideend 1.03 "
       "--sellstart 10 --sellend 10 "
       "--usecg"
   )
   ```

## Execution

### Step 1: Start Pricing Proxy

The pricing proxy manages price data and prevents rate-limiting. Only one proxy is needed even when running multiple
bots.

```bash
python3 dexbot_v2_proxy_run.py
```

### Step 2: Launch Trading Bot

In a separate terminal, start your trading bot:

```bash
python3 dexbot_v2_run.py --config my_strategy
```

## Verification Checklist

Use this comprehensive checklist to verify your setup is working correctly:

### System Requirements

- [ ] Python 3.7+ installed and available
- [ ] All dependencies installed successfully
- [ ] Blocknet wallet running, synced, and unlocked
- [ ] Asset wallets running, synced, and unlocked
- [ ] Sufficient UTXOs available for trading

### Configuration Verification

- [ ] Strategy file created from template
- [ ] RPC credentials properly configured
- [ ] Bot configuration parameters set correctly
- [ ] Maker and taker addresses specified

### Execution Verification

- [ ] Pricing proxy started successfully
- [ ] Trading bot launched without errors
- [ ] No connection refused errors in logs

### Runtime Indicators

Monitor the terminal output for these success indicators:

- `>>>> Updating balances`: Confirms successful wallet communication
- `>>>> Pricing storage >> ...`: Indicates successful price data fetching
- `>>>> Placing ... Order`: Shows successful order placement on the DEX

### Expected Behavior

- First orders should appear within 1-2 minutes under normal conditions
- Timing may vary based on network conditions and API rate limits
- See [FEATURES.md](FEATURES.md) for order distribution details

## Termination

### Graceful Shutdown

To stop the bot and cancel orders:

1. Press `Ctrl+C` to stop the bot process
2. Cancel active orders (optional):
   ```bash
   python3 dexbot_v2_run.py --config my_strategy --canceladdress
   ```

**Note**: This cancels orders for the specified market pair and addresses.

## Troubleshooting

For common issues and solutions, refer to the dedicated [TROUBLESHOOTING.md](TROUBLESHOOTING.md) guide.
