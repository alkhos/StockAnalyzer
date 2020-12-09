import yfinance
import requests
import json
import datetime
import pandas as pd 

def get_current_price(symbol):
    stock_ticker = yfinance.Ticker(symbol)
    today = datetime.datetime.now()
    weekday = today.weekday()

    # handle weekends
    if weekday >= 5:
        offset = weekday-4
        today = today - datetime.timedelta(days=offset)
    today_str = today.strftime('%Y-%m-%d')

    # handle double numbers
    try:
        stock_value = stock_ticker.history(period='1d').loc[today_str,'Close'][0]
    except:
        stock_value = stock_ticker.history(period='1d').loc[today_str,'Close']
    return round(float(stock_value) , 2)
