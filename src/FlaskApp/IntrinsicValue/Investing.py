import investpy
import requests
import json
import datetime


def get_risk_free_rate():
    info = investpy.get_bond_information(bond='U.S. 10Y', as_json=True)
    return float(info['Prev. Close'])