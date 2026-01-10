# REQUIRED
tradingaddress = {}
# ~ tradingaddress['BTC'] = '_address_'
# ~ tradingaddress['SYS'] = '_address_'
# ~ tradingaddress['LTC'] = '_address_'
# ~ tradingaddress['BLOCK'] = '_address_'
# ~ tradingaddress['PIVX'] = '_address_'
# ~ tradingaddress['MUE'] = '_address_'
rpcport = 41414
rpcuser = 'BlockDXBlocknet'
rpcpassword = 'a4c84e11-69fc-4640-a0fe-de27b9537565'
cryptobridgeURL = 'https://api.crypto-bridge.org/api/v1/ticker' # required if using the --usecb flag


# Custom price settings: Required if using the --usecustom flag.
apiendpoint = {}
apiendpoint['BTC'] = '1' # pricing in BTC, endpoint not needed
apiendpoint['SYS'] = 'https://chainz.cryptoid.info/sys/api.dws?q=ticker.btc'
apiendpoint['LTC'] = 'https://api.cryptonator.com/api/full/ltc-btc'
apiendpoint['BLOCK'] = '_url_'
apiendpoint['MUE'] = '_url_'

customrequest1 = ['LTC']
customrequest2 = ['_asset1_', '_asset2_']
customrequest3 = ['_asset3_', '_asset4_']

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
