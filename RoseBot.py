import time
from binance.client import Client
from config import api_key, secret_key, symbol, interval, leverage, limit
from datetime import datetime
import numpy as np 
import pandas as pd 
from Utilities import get_cross, get_quan, get_data, place_order, momentum_indicator

client = Client(api_key, secret_key)

def main():
    last_ema_short = None
    last_ema_long = None
    #opened_position = [False, "nan"] 
    take_profit = 0
    stop_loss = 0
    try:
      client.futures_change_leverage(symbol=symbol, leverage=leverage)
    except: pass
    print("Script Running...")
    print("Looking for new Trades....")
    print("Watching ", symbol)
    print("\n__________________________________________________________\n")

    while True:
        try:
            current_time = datetime.now().strftime("%H:%M:%S")
            ema_short, ema_long , current_price = get_cross(client)
    
            print(f"\n------------ Current Time : {current_time} ------------\n")
            print(f"------------ Current price = {current_price}-------------- ")
            print(f"------ ema_short = {ema_short} , ema_long = {ema_long} ----")
            print(f"last ema_short = {last_ema_short} , last ema_long = {last_ema_long}")
            print("\n__________________________________________________________\n")
  
        except: pass
      
        # if opened_position[1] == "Long":
        #     if (get_quan(client) > take_profit) or (get_quan(client) < stop_loss):
        #         opened_position = [False, "nan"]
        # elif opened_position[1] == "Short":
        #     if (get_quan(client) < take_profit) or (get_quan(client) > stop_loss):
        #         opened_position = [False, "nan"]

        if (ema_short > ema_long and last_ema_short ) and (last_ema_short < last_ema_long): #and not opened_position[0]
            print('Cross happened (BUY)')
            period = 1

            while True:
                print("Waiting for confirmation candlestick")
                print(f"We are in period #{period}")
                current_time = datetime.now()
                d = int(current_time.strftime("%M")) % 15
                time.sleep(d*60)
                print('rest: ',d)

                data = get_data(client)
                momentum = momentum_indicator(pd.DataFrame(data), 0, 1, period)
                #momentum = momentum_indicator(get_close(interval,symbol,limit).close, 0, 1, period)
                print(f"Momentum tendance {np.sign(float(momentum.momentum.values[-1])- float(momentum.momentum.values[-2]))} ")
                print(f"Momentum value {float(momentum.momentum.values[-1])} ")                    
                ema_short, ema_long ,current_price= get_cross(client)
                if (ema_short < ema_long):
                    print("False signal (Out of Cross)")
                    break
                
                elif (float(momentum.momentum.values[-1])- float(momentum.momentum.values[-2]) > 0): # (float(momentum.momentum.values[-1]) > 1)
                    print("Buy Order")
                    #opened_position = [True, "Long"]
                    place_order("BUY", client) 
                    break  


                else: 
                    print("Waiting for confirmation candlestick (BUY), Period + 1 ")
                    #current_time = datetime.now()
                    #d = int(current_time.strftime("%M")) % 15
                    #time.sleep(60)
                    period+=1

        if (ema_short < ema_long and last_ema_short) and (last_ema_short > last_ema_long): #and not opened_position[0]
            period = 1
            print("Cross happened SELL")

            while True:
                print("Waiting for confirmation candlestick")
                print(f"We are in period #{period}")
                current_time = datetime.now()
                d = int(current_time.strftime("%M")) % 15
                time.sleep(d*60)
                print('rest: ',d)

                data = get_data(client)
                momentum = momentum_indicator(pd.DataFrame(data), 0, 1, period)
                print(f"Momentum tendance {np.sign(float(momentum.momentum.values[-1])- float(momentum.momentum.values[-2]))} ")
                print(f"Momentum value {float(momentum.momentum.values[-1])} ")                    

                ema_short, ema_long, current_price= get_cross(client)
                if (ema_short > ema_long):
                    print("False signal, out of cross")
                    break
                    
                elif (float(momentum.momentum.values[-1])- float(momentum.momentum.values[-2]) < 0): #(float(momentum.momentum.values[-1]) < 1)
                    print("Sell Order")
                    #opened_position = [True, "Short"]
                    place_order("SELL", client)
                    break


                else: 
                    print("Waiting for confirmation candlestick (SELL), Period + 1 ")
                    period+=1    

        last_ema_short = ema_short
        last_ema_long = ema_long
        time.sleep(1)

if __name__ == "__main__":
    main()
