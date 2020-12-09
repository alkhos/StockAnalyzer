import requests
import json
import datetime

def get_us_gdp_growth_data_json(): 
    # REST
    # Register new webhook for earnings
    r = requests.get('http://api.worldbank.org/v2/country/us/indicator/NY.GDP.MKTP.KD.ZG?format=json') 
    res = r.json()
    return res

def get_us_gdp_growth_rate():
    us_gdp_growth_data_json = get_us_gdp_growth_data_json()
    for record in us_gdp_growth_data_json:
        if not isinstance(record, list):
            continue
        for inner_record in record:
            if inner_record['value'] is None:
                continue
            return inner_record['value']