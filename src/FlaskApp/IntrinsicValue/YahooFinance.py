import yfinance
import requests
import json
import datetime
import pandas as pd 

def get_current_price(symbol):
    """Get current price for the stock

    Args:
        symbol (str): Ticker symbol of the stock

    Raises:
        ValueError: If stock price cannot be retrieved, e.g. wrong symbol

    Returns:
        float: Stock pirce
    """
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

def get_price_on_date(symbol, date_str):
    """Provide stock value on the provided date

    Args:
        symbol (str): Stock ticker symbol
        date_str (str): Date in a YYYY-mm-dd format
    """
    date_start = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    date_end = date_start + datetime.timedelta(days=7)
    date_end_str = date_end.strftime('%Y-%m-%d')
    stock_ticker = yfinance.Ticker(symbol)
    stock_value = stock_ticker.history(period='7d', start=date_str, end=date_end_str)

    stock_price = 0
    first_date = datetime.date.max
    for index, row in stock_value.iterrows():
        current_date = index.to_pydatetime().date()
        if current_date < first_date:
            first_date = current_date
            stock_price = row.Close

    if stock_price == 0:
        raise ValueError('Stock price is received as 0')
    return round(float(stock_price) , 2)
    