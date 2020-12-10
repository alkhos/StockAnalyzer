import yfinance
import requests
import json
import datetime
import pandas as pd 

def get_current_price(symbol):
    stock_ticker = yfinance.Ticker(symbol)
    stock_value = stock_ticker.history(period='7d')
    stock_price = 0
    last_date = datetime.date.min
    for index, row in stock_value.iterrows():
        current_date = index.to_pydatetime().date()
        if current_date > last_date:
            last_date = current_date
            stock_price = row.Close

    if stock_price == 0:
        raise ValueError('Stock price is received as 0')
    return round(float(stock_price) , 2)
