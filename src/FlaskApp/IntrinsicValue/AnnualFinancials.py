import finnhub
import requests
import json
import datetime

def get_annuals(symbol, api_key): 
    # REST
    # Register new webhook for earnings
    r = requests.get('https://finnhub.io/api/v1/stock/financials-reported?token=' + api_key + '&freq=annual' +'&symbol=' + symbol) 
    res = r.json()

    # get the json 
    return res

def get_eps_vlues(finiancial_statements):
    # EPS dump
    eps_values = {}

    # this year
    this_year = datetime.datetime.today().year

    for record in finiancial_statements['data']:
        if(record['year'] >= this_year - 2):
            for inner_record in record['report']['ic']:
                if(inner_record['concept'] == 'EarningsPerShareDiluted'):
                    eps_values[record['year']] = inner_record['value']

    return eps_values

def save_as_json(finiancial_statements):
    # write output to a file
    symbol = finiancial_statements['symbol']
    with open('annual_financial_' + symbol + '.json', 'w') as data_output_file:
        json.dump(finiancial_statements, data_output_file, indent=4, sort_keys=True)

