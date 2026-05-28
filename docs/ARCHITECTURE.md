# System Architecture

This document details the modular design and execution flow of the DexBot V2 codebase. It focuses on the structural
relationships between components and data flow.

## Core Execution Components

The bot operates through primary entry points.

- **Main Bot** (`dexbot_v2.py`): Primary event loop, order management, and feature orchestration.
- **Bot Runner** (`dexbot_v2_run.py`): Persistence layer handling automated restarts and crash recovery.
- **Pricing Proxy** (`dexbot_v2_proxy.py`): JSON-RPC server providing centralized price caching to prevent
  rate-limiting.
- **Proxy Runner** (`dexbot_v2_proxy_run.py`): Manages the pricing proxy process lifecycle with automated recovery.

## Feature Modules

Features are isolated in the `features/` directory. Each feature implements lifecycle methods independently like
`init_preconfig`, `load_config_define`, `load_config_postparse`, `load_config_verify`, and `init_postconfig`.

| Module                   | File                                             | Responsibility                                                                                                |
|:-------------------------|:-------------------------------------------------|:--------------------------------------------------------------------------------------------------------------|
| **Global State**         | `features/glob.py`                               | Centralized storage for configuration (`c`), static data (`s`), dynamic runtime state (`d`), and tools (`t`). |
| **Pricing Storage**      | `features/pricing_storage.py`                    | Caches and manages price data from external sources.                                                          |
| **Dynamic Slide**        | `features/slide_dyn.py`                          | Adjusts order spreads based on inventory imbalance.                                                           |
| **Boundaries**           | `features/sboundary.py`, `features/rboundary.py` | Safety circuit breakers (static and relative price limits).                                                   |
| **State Persistence**    | `features/tmp_cfg.py`                            | Saves and restores runtime state across restarts.                                                             |
| **Order Events**         | `features/reset_afot.py`, `features/flush_co.py` | Manages order resets based on fill counts or timers.                                                          |
| **Pricing Proxy Client** | `features/pricing_proxy_client.py`               | Manages communication with pricing proxy server.                                                              |
| **Pricing Proxy Server** | `features/pricing_proxy_server.py`               | Handles price requests from multiple bot instances.                                                           |

## Utility Layer

Low-level helpers located in `utils/`.

| Module             | File                                        | Responsibility                                                    |
|:-------------------|:--------------------------------------------|:------------------------------------------------------------------|
| **RPC Tools**      | `utils/dxbottools.py`                       | Wrappers for Blocknet XBridge RPC calls.                          |
| **RPC Client**     | `utils/authproxy.py`                        | Low-level JSON-RPC communication handler.                         |
| **Pricing APIs**   | `utils/getpricing.py`, `utils/coingecko.py` | Integrations for external price feeds (Bittrex, CoinGecko, etc.). |
| **Custom Pricing** | `utils/custompricing.py`                    | Custom pricing integrations with configurable JSON targeting.     |
| **Settings**       | `utils/dxsettings.py`                       | Default RPC credentials and API endpoints.                        |

## Execution Flow

### 1. Initialization

Configuration is loaded from the strategy file and command-line arguments. Global state is initialized in `glob.py`. The
bot connects to the Blocknet wallet via `dxbottools.init_postconfig`.

### 2. Pricing Proxy (External)

The pricing proxy (`dexbot_v2_proxy.py`) runs independently. It aggregates price requests from multiple bot instances
and caches results to respect API rate limits. The main bot communicates with this proxy via
`features/pricing_proxy_client.py`.

### 3. Main Event Loop (`dexbot_v2.py`)

The bot operates using two nested loops with specific function calls:

1. **Primary Loop**: Handles session lifecycle (clearing old orders, preparing state) via `virtual_orders__clear_all()`
   and `virtual_orders__prepare_once()`.
2. **Secondary Loop**: The continuous trading cycle with detailed steps:
    - **Update**: Balances refreshed via `update_balances()`, prices via `feature__maker_price__pricing_update()`.
    - **Evaluate**: Exit conditions via `events_exit_bot()`, reset conditions via `events_reset_orders()`.
    - **Execute**: Takerbot scans via `feature__takerbot__run()` if active, matching orders based on size/price
      requirements.
    - **Manage**: Virtual orders handled via `virtual_orders__handle()` with staggered order creation and pump/dump
      logic.

### 4. State Management

The **Virtual Order System** tracks trade lifecycles. Virtual orders are tightly coupled with XBridge status updates,
with state persistence handled by `features/tmp_cfg.py`, allowing the bot to resume operations after a restart using the
`--action restore` flag.

**Taker Logic**: The takerbot functionality (`feature__takerbot__run()`) scans order books and executes matching orders
by canceling existing virtual orders and accepting market orders that meet size and price requirements. This implements
a higher-layer limit order feature on top of atomic swaps.

## Related Documentation

- [PARAMETERS](PARAMETERS.md)
- [QUICKSTART](QUICKSTART.md)
- [TROUBLESHOOTING](TROUBLESHOOTING.md)
