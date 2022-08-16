####################################################################################################################

api_key = ''
secret_key = ''

####################################################################################################################

symbol = "NEARBUSD" # Symbol to trade on
precision = 3       # Precision of the coin to trade 
interval = "15m"     # Time interval to trade in ex; 5m , 15m , 1h ,1d , 1w
quantity = 6        # Amount of the other coin (not USDT)
leverage = 15        # Leverage

####################################################################################################################

short_ema = 9  # Short EMA
long_ema = 20  # Long EMA

####################################################################################################################

tp = 0.003     # Take Profit % ex : 3%, 5%, ... 0.003
sl = 0.004     # Stop Loss % ex : 3%, 5%, ...   0.005   
limit = 150    # how many candles to get in hostorical klines 
