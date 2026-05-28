# Troubleshooting

## Common Issues

### Installation & Setup

**Error: `python3: command not found`**

- **Cause**: Python 3 not installed or not in PATH.
- **Resolution**: Install Python 3 (latest available version) and verify with `python3 --version`.

**Error: `Connection refused`**

- **Cause**: Blocknet wallet not running or RPC credentials mismatch.
- **Resolution**:
    - Verify wallet is running: `blocknet-cli getinfo`.
    - Check `server=1` in `~/.blocknet/blocknet.conf`.
    - Verify credentials match between wallet config and strategy file.

**Error: `Insufficient funds`**

- **Cause**: UTXOs not split or too few available.
- **Resolution**: Split UTXOs as shown in [QUICKSTART](QUICKSTART.md).

### Configuration Verification Failure

Parameters outside standard safety ranges were detected.

- **Resolution**: Review terminal output for `**** WARNING` or `**** ERROR`. If values are intentional, set
  `--imreallysurewhatimdoing` to the count of detected warnings.

### Pricing Unavailable

Market data cannot be fetched.

- **Resolution**:
    - Verify `dexbot_v2_proxy_run.py` is active.
    - Check internet connectivity and pricing source status.
    - Ensure asset tickers are supported by the chosen provider.

### Orders Not Appearing

- **Balances**: Verify `--address_funds_only` settings.
- **UTXOs**: Ensure funds are split into multiple UTXOs.
- **Wallet**: Confirm wallets are synced and unlocked.

### RPC Timeout

**Cause:** Network issues or overloaded wallet.

**Resolution:**

- Check sync: `blocknet-cli getblockchaininfo`
- Increase `--delayinternalerror` for recovery time
- Verify system resources (CPU, memory, disk I/O)
- Consider SSD for wallet storage

## Log Reference

| Message                       | Meaning                                                |
|:------------------------------|:-------------------------------------------------------|
| `>>>> Updating balances`      | Wallet data retrieval.                                 |
| `>>>> Pricing storage >> ...` | Price cache update.                                    |
| `>>>> Placing ... Order`      | Order submission to XBridge.                           |
| `**** WARNING`                | Non-critical configuration anomaly.                    |
| `**** ERROR`                  | Critical failure; check connectivity or configuration. |

## Performance Optimization

- **Rate Limiting**: The Pricing Proxy is required when running multiple bot instances.
- **Dust Prevention**: `sellstartmin` should be set to values exceeding transaction fees.

## Debugging

- Use `--canceladdress` to clear orders if the bot state becomes desynchronized.
- RPC connectivity should be verified using `blocknet-cli` before starting the bot.

## Verification Commands

**Quick connectivity checks:**

```bash
blocknet-cli getinfo                    # Check wallet is running and synced
blocknet-cli dxGetLocalTokens           # Verify XBridge is active
blocknet-cli dxGetTokenBalances         # Check asset balances
blocknet-cli dxGetUtxos {asset}         # Verify UTXO availability
curl http://127.0.0.1:22333             # Check pricing proxy status
```
