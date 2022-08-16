from config import symbol, interval, quantity, short_ema, long_ema, precision, tp, sl, limit
import pandas as pd
from binance.enums import HistoricalKlinesType

def ema(s, n):
    """
    returns an n period exponential moving average for
    the time series s
    s is a list ordered from oldest (index 0) to most
    recent (index -1)
    n is an integer
    returns a numeric array of the exponential
    moving average
    """
    # s = array(s)
    ema = []
    j = 1

    # get n sma first and calculate the next n period ema
    sma = sum(s[:n]) / n
    multiplier = 2 / float(1 + n)
    ema.append(sma)

    # EMA(current) = ( (Price(current) - EMA(prev) ) x Multiplier) + EMA(prev)
    ema.append(((s[n] - sma) * multiplier) + sma)

    # now calculate the rest of the values
    for i in s[n + 1:]:
        tmp = ((i - ema[j]) * multiplier) + ema[j]
        j = j + 1
        ema.append(tmp)
    return ema

def get_quan(client):
    value = client.get_historical_klines(symbol = symbol , interval = interval , limit =limit ,klines_type=HistoricalKlinesType.FUTURES)[-1][4]
    return float(value)

def get_data(client):
    res = client.get_historical_klines(symbol = symbol , interval = interval , limit =limit ,klines_type=HistoricalKlinesType.FUTURES)
    return [float(candle[4]) for candle in res ]

def momentum_indicator(Data, close_pos, momentum_pos, lookback):
    data = pd.DataFrame(Data.values, columns=['data'])
    data['momentum'] = [0] * len(Data)
    data = data.astype({"data": float})
    data = data.astype({"momentum": float})
    for i in range(len(Data)):
        data.iloc[i, momentum_pos] = data.iloc[i, close_pos] / data.iloc[i - lookback, close_pos]
    return data

# def get_close(interval,symbol,limit):
#     res = client.get_klines(symbol=symbol, interval=interval, limit=25)
#     coin = pd.DataFrame(res)
#     coin.columns = ['open_time','open', 'high', 'low', 'close', 'volume','close_time', 'qav','num_trades','taker_base_vol','taker_quote_vol', 'ignore']        
#     coin.index = [datetime.fromtimestamp((x-999)/1000) for x in coin.close_time]
#     return coin


def place_order(typ, client):
    if (typ == "BUY"):
        try:
            client.futures_create_order(symbol=symbol, quantity=quantity, type="MARKET", side="BUY",
                                        positionSide="LONG")

            client.futures_create_order(symbol=symbol, quantity=quantity, type='TAKE_PROFIT_MARKET',
                                        positionSide="LONG", firstTrigger="PLACE_ORDER", timeInForce="GTE_GTC",
                                        stopPrice=round(get_quan(client) * (1+tp), precision), side='SELL',
                                        secondTrigger="CANCEL_ORDER", workingType="MARK_PRICE", priceProtect='true')

            client.futures_create_order(symbol=symbol, quantity=quantity, type='STOP_MARKET', positionSide="LONG",
                                        firstTrigger="PLACE_ORDER", timeInForce="GTE_GTC",
                                        stopPrice=round(get_quan(client) * (1-sl), precision), side='SELL',
                                        secondTrigger="CANCEL_ORDER", workingType="MARK_PRICE", priceProtect='true')

            print("Opened BUY Order")
        except Exception as e:
            print("order opening failed", symbol, str(e))

    elif (typ == "SELL"):
        try:
            client.futures_create_order(symbol=symbol, quantity=quantity, type="MARKET", side="SELL",
                                        positionSide="SHORT")

            client.futures_create_order(symbol=symbol, quantity = quantity, type='TAKE_PROFIT_MARKET',
                                        positionSide="SHORT", firstTrigger="PLACE_ORDER", timeInForce="GTE_GTC",
                                        stopPrice=round(get_quan(client) * 0.997, precision), side='BUY',
                                        secondTrigger="CANCEL_ORDER", workingType="MARK_PRICE", priceProtect='true')

            client.futures_create_order(symbol=symbol, quantity=quantity, type='STOP_MARKET', positionSide="SHORT",
                                        firstTrigger="PLACE_ORDER", timeInForce="GTE_GTC",
                                        stopPrice=round(get_quan(client) * 1.005, precision), side='BUY',
                                        secondTrigger="CANCEL_ORDER", workingType="MARK_PRICE", priceProtect='true')

            print("Opened SELL Order")
        except Exception as e:
            print("order opening fails", symbol, str(e))


def get_cross(client):
    data = get_data(client)
    ema_short = ema(data, short_ema)[-1]
    ema_long = ema(data, long_ema)[-1]
    return round(ema_short,precision+2) , round(ema_long,precision+2), round(data[-1],precision)

