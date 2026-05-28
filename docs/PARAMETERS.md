# Parameter Reference

## Table of Contents

- [dexbot_v2.py (Main Trading Bot)](#dexbot_v2py-main-trading-bot)
- [dexbot_v2_run.py (Bot Runner)](#dexbot_v2_runpy-bot-runner)
- [dexbot_v2_proxy.py (Pricing Proxy Server)](#dexbot_v2_proxypy-pricing-proxy-server)
- [dexbot_v2_proxy_run.py (Proxy Runner)](#dexbot_v2_proxy_runpy-proxy-runner)

## dexbot_v2.py (Main Trading Bot)

### All Parameters

| Parameter                          | Data Type | Range                                             | Default                  | Description                                                                                             |
|:-----------------------------------|:----------|:--------------------------------------------------|:-------------------------|:--------------------------------------------------------------------------------------------------------|
| `--config`                         | str       | Any                                               | `None`                   | **Required**: Path to strategy file (excluding `.py`).                                                  |
| `--action`                         | str       | `reset`, `restore`, `none`                        | `none`                   | Startup mode: `reset` (ignore cache), `restore` (use cache), `none`.                                    |
| `--imreallysurewhatimdoing`        | int       | `>= 0`                                            | `0`                      | Bypasses safety checks. Must match the count of detected non-standard values.                           |
| `--maker`                          | str       | Ticker                                            | `BLOCK`                  | Asset being sold.                                                                                       |
| `--taker`                          | str       | Ticker                                            | `LTC`                    | Asset being bought.                                                                                     |
| `--makeraddress`                   | str       | Address                                           | `None`                   | Maker wallet address.                                                                                   |
| `--takeraddress`                   | str       | Address                                           | `None`                   | Taker wallet address.                                                                                   |
| `--address_funds_only`             | bool      | `True`, `False`                                   | `False`                  | Restrict trading to UTXOs from specified addresses.                                                     |
| `--sell_size_asset`                | str       | Ticker                                            | `maker`                  | Asset used to define order sizes.                                                                       |
| `--sellstart`                      | float     | `> 0`                                             | `0.001`                  | Size of the first order.                                                                                |
| `--sellend`                        | float     | `> 0`                                             | `0.001`                  | Size of the last order.                                                                                 |
| `--sellstartmin`                   | float     | `[0, sellstart]`                                  | `0`                      | Minimum acceptable size for the first order.                                                            |
| `--sellendmin`                     | float     | `[0, sellend]`                                    | `0`                      | Minimum acceptable size for the last order.                                                             |
| `--sellrandom`                     | bool      | `True`, `False`                                   | `False`                  | Randomize sizes between `sellstart` and `sellend`.                                                      |
| `--sell_type`                      | float     | `(-1, 1)`                                         | `0`                      | Distribution curve: `-1` (exponential), `0` (linear), `1` (logarithmic).                                |
| `--maxopen`                        | int       | `>= 1`                                            | `5`                      | Maximum concurrent open orders.                                                                         |
| `--partial_orders`                 | bool      | `True`, `False`                                   | `False`                  | Enable XBridge partial fulfillment.                                                                     |
| `--slidestart`                     | float     | `> 0`                                             | `1.01`                   | Price multiplier for the first order (e.g., `1.01` = +1%).                                              |
| `--slideend`                       | float     | `> 0`                                             | `1.021`                  | Price multiplier for the last order.                                                                    |
| `--make_next_on_hit`               | bool      | `True`, `False`                                   | `False`                  | Skip failed orders and attempt the next in sequence.                                                    |
| `--slidepump`                      | float     | `>= 0`                                            | `0`                      | Spread for a special "pump" order outside `slideend`.                                                   |
| `--pumpamount`                     | float     | `>= 0`                                            | `0`                      | Size of the pump order. `0` = `sellend`.                                                                |
| `--pumpamountmin`                  | float     | `>= 0`                                            | `0`                      | Minimum acceptable pump order size, otherwise sellendmin is used.                                       |
| `--balance_save_asset`             | str       | Ticker                                            | `None`                   | Size of balance to save is set in specific asset instead of maker.                                      |
| `--balance_save_asset_track`       | bool      | `True`, `False`                                   | `False`                  | Track balance save asset price updates (e.g., if trading BLOCK/BTC on USD, also track USD/BLOCK price). |
| `--balance_save_number`            | float     | `>= 0`                                            | `0`                      | Min taker balance to save and not use for making orders (specified by number).                          |
| `--balance_save_percent`           | float     | `[0, 1]`                                          | `0.05`                   | Min taker balance to save as percentage of maker+taker balance (0.05 = 5%).                             |
| `--slide_dyn_asset`                | str       | Ticker                                            | `taker`                  | Asset for imbalance tracking.                                                                           |
| `--slide_dyn_asset_track`          | bool      | `True`, `False`                                   | `False`                  | Track price updates for the slide asset.                                                                |
| `--slide_dyn_zero_type`            | str       | `relative`, `static`                              | `relative`               | Determines how --slide_dyn_zero is interpreted (ratio or absolute amount)                               |
| `--slide_dyn_zero`                 | float     | -1, -2, or [0,1] (if relative) or >=0 (if static) | `-2`                     | Balance ratio where dynamic slide is 0%. -1=auto, -2=restore from cache                                 |
| `--slide_dyn_type`                 | str       | `relative`, `static`                              | `relative`               | Threshold unit type. Should match --slide_dyn_zero_type.                                                |
| `--slide_dyn_sell_ignore`          | float     | [0,1] (if relative) or >=0 (if static)            | `0`                      | Inventory amount sold before slide activates.                                                           |
| `--slide_dyn_sell_threshold`       | float     | (0,1] (if relative) or >0 (if static)             | `0.02`                   | Inventory change per slide step. Lower = more sensitive.                                                |
| `--slide_dyn_sell_step`            | float     | Any                                               | `0`                      | Spread increment per threshold. 0.005 = 0.5% per step.                                                  |
| `--slide_dyn_sell_step_multiplier` | float     | `>= 0`                                            | `1`                      | Recursive multiplier for sell steps.                                                                    |
| `--slide_dyn_sell_max`             | float     | Any                                               | `0`                      | Cap for dynamic sell slide.                                                                             |
| `--slide_dyn_buy_ignore`           | float     | [0,1] (if relative) or >=0 (if static)            | `0`                      | Inventory amount bought before slide activates.                                                         |
| `--slide_dyn_buy_threshold`        | float     | (0,1] (if relative) or >0 (if static)             | `0.02`                   | Inventory change per slide step.                                                                        |
| `--slide_dyn_buy_step`             | float     | Any                                               | `0`                      | Spread increment per threshold.                                                                         |
| `--slide_dyn_buy_step_multiplier`  | float     | `>= 0`                                            | `1`                      | Recursive multiplier for buy steps.                                                                     |
| `--slide_dyn_buy_max`              | float     | Any                                               | `0`                      | Cap for dynamic buy slide.                                                                              |
| `--sboundary_asset`                | str       | Ticker                                            | `taker`                  | Asset defining absolute boundaries.                                                                     |
| `--sboundary_max`                  | float     | `>= 0`                                            | `0`                      | Absolute price ceiling.                                                                                 |
| `--sboundary_min`                  | float     | `>= 0`                                            | `0`                      | Absolute price floor.                                                                                   |
| `--sboundary_max_track_asset`      | bool      | `True`, `False`                                   | `False`                  | Track price updates for the boundary asset.                                                             |
| `--sboundary_min_track_asset`      | bool      | `True`, `False`                                   | `False`                  | Track boundary asset price updates for minimum boundary.                                                |
| `--sboundary_price_reverse`        | bool      | `True`, `False`                                   | `False`                  | Use `1/X` pricing for boundaries.                                                                       |
| `--sboundary_max_cancel`           | bool      | `True`, `False`                                   | `True`                   | Cancel orders when ceiling is hit.                                                                      |
| `--sboundary_max_exit`             | bool      | `True`, `False`                                   | `True`                   | Exit bot when ceiling is hit.                                                                           |
| `--sboundary_min_cancel`           | bool      | `True`, `False`                                   | `True`                   | Cancel orders when floor is hit.                                                                        |
| `--sboundary_min_exit`             | bool      | `True`, `False`                                   | `False`                  | Exit bot when floor is hit.                                                                             |
| `--rboundary_asset`                | str       | Ticker                                            | `taker`                  | Asset defining relative boundaries.                                                                     |
| `--rboundary_price_initial`        | float     | `>= 0`                                            | `0`                      | Manual center price. `0` = automatic.                                                                   |
| `--rboundary_max`                  | float     | `>= 0`                                            | `0`                      | Relative multiplier ceiling (e.g., `1.5` = +50%).                                                       |
| `--rboundary_min`                  | float     | `>= 0`                                            | `0`                      | Relative multiplier floor.                                                                              |
| `--rboundary_max_track_asset`      | bool      | `True`, `False`                                   | `False`                  | Track price updates for the boundary asset.                                                             |
| `--rboundary_min_track_asset`      | bool      | `True`, `False`                                   | `False`                  | Track boundary asset price updates for minimum boundary.                                                |
| `--rboundary_price_reverse`        | bool      | `True`, `False`                                   | `False`                  | Use `1/X` pricing for boundaries.                                                                       |
| `--rboundary_max_cancel`           | bool      | `True`, `False`                                   | `True`                   | Cancel orders when ceiling is hit.                                                                      |
| `--rboundary_max_exit`             | bool      | `True`, `False`                                   | `True`                   | Exit bot when ceiling is hit.                                                                           |
| `--rboundary_min_cancel`           | bool      | `True`, `False`                                   | `True`                   | Cancel orders when floor is hit.                                                                        |
| `--rboundary_min_exit`             | bool      | `True`, `False`                                   | `False`                  | Exit bot when floor is hit.                                                                             |
| `--takerbot`                       | int       | `>= 0`                                            | `0`                      | Interval (seconds) to auto-take matching orders.                                                        |
| `--flush_canceled_orders`          | int       | `>= 0`                                            | `0`                      | Interval (seconds) to purge XBridge history.                                                            |
| `--resetonpricechangepositive`     | float     | `>= 0`                                            | `0`                      | Reset orders if price rises by X%.                                                                      |
| `--resetonpricechangenegative`     | float     | `>= 0`                                            | `0`                      | Reset orders if price falls by X%.                                                                      |
| `--resetafterdelay`                | int       | `>= 0`                                            | `0`                      | Periodic full reset interval (seconds).                                                                 |
| `--resetafterorderfinishnumber`    | int       | `>= 0`                                            | `0`                      | Reset after X orders are finished.                                                                      |
| `--resetafterorderfinishdelay`     | int       | `>= 0`                                            | `0`                      | Reset X seconds after an order finishes.                                                                |
| `--reopenfinishednum`              | int       | `[0, maxopen]`                                    | `0`                      | Re-place orders after X fills.                                                                          |
| `--reopenfinisheddelay`            | int       | `>= 0`                                            | `0`                      | Re-place orders after X seconds delay.                                                                  |
| `--maker_price`                    | float     | `0`, `-1`, `-2`                                   | `0`                      | `0` (live), `-1` (one-time), `-2` (static).                                                             |
| `--pricing_proxy_url`              | str       | URL                                               | `http://127.0.0.1:22333` | URL of the pricing proxy server.                                                                        |
| `--price_provider`                 | str       | Any                                               | `""`                     | Specific provider override.                                                                             |
| `--usecg`                          | flag      | N/A                                               | N/A                      | Use CoinGecko.                                                                                          |
| `--usecb`                          | flag      | N/A                                               | N/A                      | Use CryptoBridge.                                                                                       |
| `--usecustom`                      | flag      | N/A                                               | N/A                      | Use `dxsettings.py` custom endpoints.                                                                   |
| `--delayinternal`                  | float     | `>= 1`                                            | `2.3`                    | Pause between API calls.                                                                                |
| `--delayinternalcycle`             | float     | `>= 1`                                            | `8`                      | Main loop cycle time.                                                                                   |
| `--delaycheckprice`                | float     | `>= 1`                                            | `180`                    | Price refresh interval.                                                                                 |
| `--delayinternalerror`             | float     | `>= 1`                                            | `10`                     | Pause after errors.                                                                                     |
| `--cancelall`                      | flag      | N/A                                               | N/A                      | Cancel all open orders (flag, no argument).                                                             |
| `--cancelmarket`                   | flag      | N/A                                               | N/A                      | Cancel all market orders (flag, no argument).                                                           |
| `--canceladdress`                  | flag      | N/A                                               | N/A                      | Cancel all orders for the market pair and addresses specified in the config file (flag, no argument).   |
| `--hidden_orders`                  | bool      | `True`, `False`                                   | `False`                  | Hide orders from the public order book.                                                                 |

**Relationship Note**: `--slide_dyn_zero_type` and `--slide_dyn_zero` must use compatible units:

- If `zero_type=relative`, `zero` must be in [0,1] or -1/-2
- If `zero_type=static`, `zero` must be >=0 or -1/-2

**Example**: `--slide_dyn_zero_type relative --slide_dyn_zero 0.5` means dynamic slide is 0% when maker/taker balance
ratio is 50/50.

**Relationship Note**: `*_cancel` and `*_exit` work together:

- `cancel=True, exit=False`: Orders canceled, bot continues.
- `cancel=True, exit=True`: Orders canceled, bot stops.
- `cancel=False, exit=False`: No action (not recommended).

**Recommendation**: Use `--sboundary_max_cancel True --sboundary_max_exit True` for protection against pumps.

## dexbot_v2_run.py (Bot Runner)

### All Parameters

| Parameter         | Data Type | Range                      | Default | Description                                                                                           |
|:------------------|:----------|:---------------------------|:--------|:------------------------------------------------------------------------------------------------------|
| `--config`        | str       | Any                        | `None`  | **Required**: Path to strategy file (excluding `.py`).                                                |
| `--action`        | str       | `reset`, `restore`, `none` | `none`  | Startup mode: `reset` (ignore cache), `restore` (use cache), `none`.                                  |
| `--exitonerror`   | int       | `>= 0`                     | `0`     | Max consecutive crashes before stopping. `0` = unlimited.                                             |
| `--cancelall`     | flag      | N/A                        | N/A     | Cancel all open orders.                                                                               |
| `--cancelmarket`  | flag      | N/A                        | N/A     | Cancel all market orders.                                                                             |
| `--canceladdress` | flag      | N/A                        | N/A     | Cancel all orders for the market pair and addresses specified in the config file (flag, no argument). |

## dexbot_v2_proxy.py (Pricing Proxy Server)

### All Parameters

| Parameter                   | Data Type | Range           | Default     | Description                                                                   |
|:----------------------------|:----------|:----------------|:------------|:------------------------------------------------------------------------------|
| `--proxy_server_addr`       | str       | Any             | `127.0.0.1` | Proxy server bind address.                                                    |
| `--proxy_server_port`       | int       | `> 0`           | `22333`     | Proxy server port.                                                            |
| `--restore`                 | bool      | `True`, `False` | `False`     | Restore cached data on startup.                                               |
| `--imreallysurewhatimdoing` | int       | `>= 0`          | `0`         | Bypasses safety checks. Must match the count of detected non-standard values. |

## dexbot_v2_proxy_run.py (Proxy Runner)

### All Parameters

| Parameter   | Data Type | Range           | Default | Description                     |
|:------------|:----------|:----------------|:--------|:--------------------------------|
| `--restore` | bool      | `True`, `False` | `False` | Restore cached data on startup. |