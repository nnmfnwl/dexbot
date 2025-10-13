### Dex Maker/Trading Bot
   * This project is fork of Blocknet's dxmakerbot market making/trading bot for Blocknet's decentralized exchange protocol, built with the [XBridge API](https://api.blocknet.org).

### Content
* [Web Links](#weblinks)
* [Complete Setup with DEXSETUP](#complete-setup)
* [Prerequisites](#prerequisites)
* [Installation](#installation)
   * [Linux](#linux)
   * [MacOS](#macos)
   * [Windows](#windows)
* [Creating Trading Strategy](#creating-trading-strategy)
* [Running the Bot](#running-the-bot)
* [Maker Bot](#maker-bot-usage)

### Web Links
   * [Main Blocknet Website](https://blocknet.org)
   * [Blocknet API](https://api.blocknet.org)
   * [Blocknet Docs](https://docs.blocknet.org)
   * [Discord](https://discord.gg/2e6s7H8)

### Complete Setup
   * You can completely skip going over this readme/installation process and use one of below options to setup complete DEXBOT and BlockDX environment even from scratch on Debian compatible operating systems:
     - Interactive/automatic command line Dexsetup framework installer: [Dexsetup.installer](https://github.com/nnmfnwl/dexsetup.cli.installer)
     - Dexsetup framework: [Dexsetup](https://github.com/nnmfnwl/dexsetup/tree/merge.2025.02.06)


### Prerequisites
1. [Latest Blocknet wallet installed](https://github.com/blocknetdx/blocknet/releases/latest).
1. The wallet of any assets you will be trading. See list of [compatible assets](https://docs.blocknet.org/protocol/xbridge/compatibility/#supported-digital-assets).
1. The Blocknet wallet and any other wallet you're trading out of must be fully synced and fully unlocked.
1. The wallets used for trading must be configured. For simple setup, use [Block DX's automated configuration setup wizard](https://docs.blocknet.org/blockdx/configuration/). Having Block DX installed and opened is also useful to visually monitor the market and your open orders.
1. Make sure funds are split into multiple UTXOs. If you have an order for 1 LTC and you only have a single 10 LTC input, all 10 LTC will be locked in this order. Having multiple, preferably smaller, UTXOs will allow a better distribution of funds across orders.
1. Make sure funds are in legacy addresses (Eg. LTC funds should be in a "L" address).

### Installation

#### Linux
1. Open the command line terminal to enter the following commands
1. Install Python 3: ```apt-get install python3```
   * Or upgrade Python 3: ```apt-get upgrade python3```
1. Install pip (Python's package manager): ```apt-get install python3-pip```
   * Or upgrade pip: ```apt-get upgrade python3-pip```
1. Download DX Maker Bot
   * Download via Git: 
      1. Navigate to your project directory
         * Example: ```cd ~/Downloads/ccwallets/```
            1. Download DX Maker Bot: ```git clone https://github.com/nnmfnwl/dexbot```
         * Download via Github:
            1. Navigate to [https://github.com/nnmfnwl/dexbot](https://github.com/nnmfnwl/dexbot)
            1. Click the green *Clone or download* button and select *Download ZIP* from the dropdown
            1. Save the file and (if necessary) extract the contents to a folder
1. Navigate into the *dexbot* folder
   * Example: ```cd ~/Downloads/ccwallets/dexbot```
1. Install the required DX Maket Bot packages: ```pip3 install -r requirements.txt```
   * If that command does not work: ```pip install -r requirements.txt```

#### MacOS
1. Open Terminal to enter the following commands
1. Install XCode: ```xcode-select --install```
1. Install Homebrew (MacOS package manager): ```/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"```
1. Install Python 3: ```brew install python3```
1. Upgrade pip (Python's package manager): ```pip3 install -U pip```
1. Download DX Maker Bot
   * Download via Git: 
      1. Navigate to your project directory
         * Example: ```cd ~/Documents/ccwallets/```
      1. Download DX Maker Bot: ```git clone https://github.com/nnmfnwl/dexbot```
   * Download via Github:
      1. Navigate to [https://github.com/nnmfnwl/dexbot](https://github.com/nnmfnwl/dexbot)
      1. Click the green *Clone or download* button and select *Download ZIP* from the dropdown
      1. Save the file and (if necessary) extract the contents to a folder
1. Navigate into the *dexbot* folder
   * Example: ```cd ~/Documents/ccwallets/dexbot```
1. Install the required DX Maket Bot packages: ```pip3 install -r requirements.txt```

#### Windows
1. Install Python 3:
   1. Navigate to [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/) and select *Download Python 3.7.x*
   1. Run the installer
   1. Check off *Add Python 3.7 to PATH*
   1. Click *Install Now*
1. Right-click the taskbar *Start* menu and select *Command Prompt (Admin)*
1. Upgrade pip (Python's package manager): ```py -m pip install --upgrade pip```
1. Download DX Maker Bot
   * Download via Git: 
      1. Navigate to your project directory
         * Example: ```C:\Users\%USERNAME%\Downloads\ccwallets/dexbot```
      1. Download DX Maker Bot: ```git clone https://github.com/nnmfnwl/dexbot```
   * Download via Github:
         1. Navigate to [https://github.com/nnmfnwl/dexbot](https://github.com/nnmfnwl/dexbot)
         1. Click the green *Clone or download* button and select *Download ZIP* from the dropdown
         1. Save the file and (if necessary) extract the contents to a folder
1. Navigate into the *dexbot* folder
   * Example: ```cd C:\Users\%USERNAME%\Downloads\ccwallets/dexbot```
1. Install the required DX Maket Bot packages: ```pip3 install -r requirements.txt```
   * If that command does not work: ```pip install -r requirements.txt```

### Creating Trading Strategy
1. make copy of [howto/examples/bot_v2_template.py](./howto/examples/bot_v2_template.py) strategy template into main dexbot directory and rename by strategy you wish to make
1. open strategy template file by text editor and edit one by one `{}` items according inline documentation,
 like Edit RPC setings, edit the trading addresses to match the wallet addresses containing funds split into multiple UTXOs,
1. Make sure funds are in legacy addresses (Eg. LTC funds should be in a "L" address).
1. Every strategy file represents just one way trading. So if you want provide liquidity for BLOC->LTC and also LTC->BLOCK, than you will need two strategy files.
1. Save and close the file. 

### Running the Bot
1. Run the wallets of any assets being traded (fully synced, unlocked).
1. Run the Blocknet wallet (fully synced, unlocked).
1. *Optional*: Run [Block DX](https://docs.blocknet.org/blockdx/setup) for visual reference that the bot is working.
   * At this stage it would be a good idea to test making/taking an order without using the bot to ensure everything is setup properly.
1. Navigate to the *dexbot* directory in the terminal.

### Maker Bot Usage
   * To prevent multiple bot strategies pulling same data from external sources there is dexbot proxy process
   * So at first there must be running bot pricing proxy instance:
```
python3 dexbot_v2_proxy_run.py
```
   * dexbot strategy config file represents one way market, for bidirectional trading there are always two strategies needed to run.
   * For example to start specific previously created bidirectional dexbot strategy, where files are named strategy_BLOCK_LTC_liquidity.py and strategy_BLOCK_LTC_liquidity.py, need to run two commands in two terminal tabs:
```
python3 dexbot_v2_run.py --config strategy_BLOCK_LTC_strategy1
```
   * and 
```
python3 dexbot_v2_run.py --config strategy_LTC_BLOCK_strategy1
```
   * To cancel all orders in market pair and address specified by --config file
```
python3 dexbot_v2_run.py --config strategy_LTC_BLOCK_strategy1 --canceladdress
```
   * To cancel all orders in market pair specified by --config file
```
python3 dexbot_v2_run.py --config strategy_LTC_BLOCK_strategy1 --cancelmarket
```
   * To cancel all orders
```
python3 dexbot_v2_run.py --config strategy_LTC_BLOCK_strategy1 --cancelall
```

### Donations
* Many options to support [Dexbot](https://github.com/nnmfnwl/dexbot/tree/merge.2025.03.26), [Dexsetup](https://github.com/nnmfnwl/dexsetup/tree/merge.2025.02.06), [Dexsetup.installer](https://github.com/nnmfnwl/dexsetup.cli.installer) and [Dexsetup.videos](https://github.com/nnmfnwl/dexsetup.videos) continuous development, testing, liquidity providing and making video tutorials could be found [here](https://github.com/nnmfnwl/dexsetup.cli.installer#9-donations)

