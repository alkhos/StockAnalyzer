import requests
import json
import datetime
import enum
import io
import base64
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import chart_studio.plotly as plty
import plotly.graph_objects as go
import plotly


class DocumentType(enum.Enum):
    def __str__(self):
        return str(self.value)

    BALANCE_SHEET = 1
    INCOME_STATEMENT = 2
    CASH_FLOW = 3
    OVERVIEW = 4

def get_financial_statement(symbol, document_type, api_key, use_file=False): 
    # Get from REST
    if(use_file):
        file_name = symbol + '_' + document_type.name  + '_alpha.json'
        with open(file_name) as data_input_file:
            return json.loads(data_input_file.read())
    else:
        r = requests.get('https://www.alphavantage.co/query?function=' + document_type.name +'&symbol=' + symbol +'&apikey=' + api_key) 
        res = r.json()
        return res

def save_as_json(finiancial_statements, document_type):
    # write output to a file
    symbol = finiancial_statements['symbol'] if 'symbol' in finiancial_statements else finiancial_statements['Symbol']
    file_name = symbol + '_' + document_type.name  + '_alpha.json'
    with open(file_name, 'w') as data_output_file:
        json.dump(finiancial_statements, data_output_file, indent=4, sort_keys=True)

def get_last_four_quarters(finiancial_statements):
    # last_four_quarters = []
    # all_quarters = []
    # for report in finiancial_statements['quarterlyReports']:
    #     datetime_object = datetime.datetime.strptime(report['fiscalDateEnding'], '%Y-%m-%d')
    #     all_quarters.append(datetime_object)
    # all_quarters.sort(reverse=True)
    # last_four_quarters = all_quarters[0:4]
    # last_four_quarters_str = []
    # for quarter in last_four_quarters:
    #     last_four_quarters_str.append(quarter.strftime('%Y-%m-%d'))
    # return last_four_quarters_str
    return finiancial_statements['quarterlyReports'][0:4]

def get_last_quarter(finiancial_statements):
    return finiancial_statements['quarterlyReports'][0]

def get_last_annual(finiancial_statements):
    return finiancial_statements['annualReports'][0]

def get_last_annual_report_date(finiancial_statements):
    all_reports = []
    for report in finiancial_statements['annualReports']:
        datetime_object = datetime.datetime.strptime(report['fiscalDateEnding'], '%Y-%m-%d')
        all_reports.append(datetime_object)
    last_report = max(all_reports)
    last_report_str = last_report.strftime('%Y-%m-%d')
    return last_report_str

def get_last_quarterly_report_date(finiancial_statements):
    all_reports = []
    for report in finiancial_statements['quarterlyReports']:
        datetime_object = datetime.datetime.strptime(report['fiscalDateEnding'], '%Y-%m-%d')
        all_reports.append(datetime_object)
    last_report = max(all_reports)
    last_report_str = last_report.strftime('%Y-%m-%d')
    return last_report_str

def get_free_cashflow_ttm(cash_flow_statement):
    last_four_quarters = get_last_four_quarters(cash_flow_statement)
    free_cash_flow_ttm = 0
    for quarter in last_four_quarters:
        free_cash_flow = int(quarter['operatingCashflow']) - int(quarter['capitalExpenditures'])
        free_cash_flow_ttm = free_cash_flow_ttm + free_cash_flow
    return free_cash_flow_ttm

def get_financial_statement_record_ttm(finiancial_statement, record_name):
    last_four_quarters = get_last_four_quarters(finiancial_statement)
    record_ttm = 0
    for record in last_four_quarters:
        value = 0 if record[record_name] == "None" else int(record[record_name])
        record_ttm = record_ttm + value
    return record_ttm

def get_financial_statement_record(finiancial_statement, record_name, find_latest_existing=False):
    last_quarter = get_last_quarter(finiancial_statement)
    if find_latest_existing:
        for record in finiancial_statement['quarterlyReports']:
            if record[record_name] == "None":
                continue
            return int(record[record_name])
    else:
        value = 0 if last_quarter[record_name] == "None" else int(last_quarter[record_name])
        return value

def get_interest_rate(balance_sheet, income_statemet):
    interest_expense = get_financial_statement_record_ttm(income_statemet, 'interestExpense')
    principal_balance = get_financial_statement_record(balance_sheet, 'totalLongTermDebt') + \
        get_financial_statement_record(balance_sheet, 'shortTermDebt')
    return round(100*interest_expense/principal_balance, 2)

def get_long_term_interest_rate(balance_sheet, income_statemet):
    interest_expense = get_financial_statement_record_ttm(income_statemet, 'interestExpense')
    principal_balance = get_financial_statement_record(balance_sheet, 'totalLongTermDebt') 
    return round(100*interest_expense/principal_balance, 2)

def plot_free_cash_flow(cash_flow_statement, using_matplotlib=False):
    free_cash_flows = {}
    for record in cash_flow_statement['annualReports']:
        datetime_object = datetime.datetime.strptime(record['fiscalDateEnding'], '%Y-%m-%d')
        free_cash_flow = int(record['operatingCashflow']) - int(record['capitalExpenditures'])
        free_cash_flows[datetime_object] = free_cash_flow / 1e6

    # add TTM
    datetime_object = datetime.datetime.now()
    free_cash_flow_ttm = get_free_cashflow_ttm(cash_flow_statement)
    free_cash_flows[datetime_object] = free_cash_flow_ttm / 1e6
    
    if using_matplotlib:
        # using matplotlib
        fig = plt.figure()
        ax = plt.subplot(111)
        x,y = zip(*sorted(free_cash_flows.items()))
        plt.plot(x,y)
        date_formatter = mdates.DateFormatter('%Y')
        plt.xlabel('Year')
        plt.ylabel('Free Cash Flow (millions of dollars)')
        plt.title('Free Cash Flow for ' + cash_flow_statement['symbol'])  
        plt.gca().xaxis.set_major_formatter(date_formatter)
        figure_to_send = io.BytesIO()
        plt.savefig(figure_to_send, format='png', facecolor=(0.95, 0.95, 0.95))
        encoded_img = base64.b64encode(figure_to_send.getvalue()).decode('utf-8').replace('\n', '')
        figure_to_send.close()
        return encoded_img
    else:
        # get the symbol
        symbol = cash_flow_statement['symbol']

        # using plotly
        return produce_plotly_time_series(free_cash_flows, symbol, 'Free Cash Flow')

def get_revenue_values(income_statemenet):
    total_revenues = {}
    for record in income_statemenet['annualReports']:
        datetime_object = datetime.datetime.strptime(record['fiscalDateEnding'], '%Y-%m-%d')
        total_revenue = int(record['totalRevenue'])
        total_revenues[datetime_object] = total_revenue / 1e6

    # add TTM
    datetime_object = datetime.datetime.now()
    total_revenue_ttm = get_financial_statement_record_ttm(income_statemenet, 'totalRevenue')
    total_revenues[datetime_object] = total_revenue_ttm / 1e6
    return total_revenues

def plot_revenue(income_statemenet):
    # get revenue list
    total_revenues = get_revenue_values(income_statemenet)

    # get the symbol
    symbol = income_statemenet['symbol']

    # using plotly
    return produce_plotly_time_series(total_revenues, symbol, 'Total Revenue')

def plot_accounts_payable(balance_sheet):
    accounts_payables = {}
    for record in balance_sheet['annualReports']:
        datetime_object = datetime.datetime.strptime(record['fiscalDateEnding'], '%Y-%m-%d')
        accounts_payable = int(record['accountsPayable'])
        accounts_payables[datetime_object] = accounts_payable / 1e6

    # add TTM
    datetime_object = datetime.datetime.now()
    accounts_payable_ttm = get_financial_statement_record(balance_sheet, 'accountsPayable')
    if accounts_payable_ttm != 0:
        accounts_payables[datetime_object] = accounts_payable_ttm / 1e6

    # get the symbol
    symbol = balance_sheet['symbol']

    # using plotly
    return produce_plotly_time_series(accounts_payables, symbol, 'Accounts Payable')

def plot_accounts_receivable(balance_sheet):
    accounts_receivables = {}
    for record in balance_sheet['annualReports']:
        datetime_object = datetime.datetime.strptime(record['fiscalDateEnding'], '%Y-%m-%d')
        accounts_receivable = int(record['netReceivables'])
        accounts_receivables[datetime_object] = accounts_receivable / 1e6

    # add TTM
    datetime_object = datetime.datetime.now()
    accounts_receivable_ttm = get_financial_statement_record(balance_sheet, 'netReceivables')
    if accounts_receivable_ttm != 0:
        accounts_receivables[datetime_object] = accounts_receivable_ttm / 1e6

    # get the symbol
    symbol = balance_sheet['symbol']

    # using plotly
    return produce_plotly_time_series(accounts_receivables, symbol, 'Accounts Receivable')

def plot_inventory(balance_sheet):
    inventories = {}
    for record in balance_sheet['annualReports']:
        datetime_object = datetime.datetime.strptime(record['fiscalDateEnding'], '%Y-%m-%d')
        inventory = int(record['inventory'])
        inventories[datetime_object] = inventory / 1e6

    # add TTM
    datetime_object = datetime.datetime.now()
    inventory_ttm = get_financial_statement_record(balance_sheet, 'inventory')
    if inventory_ttm != 0:
        inventories[datetime_object] = inventory_ttm / 1e6

    # get the symbol
    symbol = balance_sheet['symbol']

    # using plotly
    return produce_plotly_time_series(inventories, symbol, 'Accounts Receivable')

def get_eps_values(income_statemenet, balance_sheet):
    eps_list = {}

    for record in income_statemenet['annualReports']:
        datetime_object = datetime.datetime.strptime(record['fiscalDateEnding'], '%Y-%m-%d')
        total_income = int(record['netIncomeApplicableToCommonShares'])
        eps_list[datetime_object] = total_income

    for record in balance_sheet['annualReports']:
        datetime_object = datetime.datetime.strptime(record['fiscalDateEnding'], '%Y-%m-%d')
        if datetime_object in eps_list:
            total_income = eps_list[datetime_object]
            total_shares = int(record['commonStockSharesOutstanding'])
            eps_list[datetime_object] = total_income / total_shares

    # add TTM
    datetime_object = datetime.datetime.now()
    total_income_ttm = get_financial_statement_record_ttm(income_statemenet, 'netIncomeApplicableToCommonShares')
    total_shares = get_financial_statement_record(balance_sheet, 'commonStockSharesOutstanding', find_latest_existing=True)
    eps_list[datetime_object] = total_income_ttm / total_shares
    return eps_list

def plot_eps(income_statemenet, balance_sheet):
    # get EPS list
    eps_list = get_eps_values(income_statemenet, balance_sheet)

    # get the symbol
    symbol = income_statemenet['symbol']

    # using plotly
    return produce_plotly_time_series(eps_list, symbol, 'Earnings per Share')

def plot_growth_values(income_statemenet, balance_sheet):
    revenue_growth = {}
    eps_growth = {}

    # get current values 
    revenue_list = get_revenue_values(income_statemenet)
    eps_list = get_eps_values(income_statemenet, balance_sheet)

    # revenue growth
    prev_value = None
    for record in sorted(revenue_list.keys()):
        if prev_value is None:
            prev_value = revenue_list[record]
            continue
        if revenue_list[record] != 0:
            revenue_growth[record] = 100*(revenue_list[record] - prev_value)/revenue_list[record]
        else:
            revenue_growth[record] = 0
        prev_value = revenue_list[record]

    # eps growth
    prev_value = None
    for record in sorted(eps_list.keys()):
        if prev_value is None:
            prev_value = eps_list[record]
            continue
        if eps_list[record] != 0:
            eps_growth[record] = 100*(eps_list[record] - prev_value)/eps_list[record]
        else:
            eps_growth[record] = 0
        prev_value = eps_list[record]
    
    # using plotly
    x,y = zip(*sorted(revenue_growth.items()))
    data = go.Figure([go.Scatter(x=x, y=y, name='Revenue Growth (%)', )])
    x,y = zip(*sorted(eps_growth.items()))
    data.add_trace(go.Scatter(x=x, y=y, name='EPS Growth (%)'))

    data.update_layout(
        title= 'Revenue and EPS Growth in %',
        xaxis_title='Year',
        yaxis_title= 'Growth %')
    graph_json = json.dumps(data, cls= plotly.utils.PlotlyJSONEncoder)
    return graph_json

def produce_plotly_time_series(input_dictionary, symbol, record_name):
    # using plotly
    x,y = zip(*sorted(input_dictionary.items()))
    data = go.Figure([go.Scatter(x=x, y=y)])

    data.update_layout(
        title= record_name + ' for ' + symbol,
        xaxis_title='Year',
        yaxis_title=record_name + ' (Million of Dollars)')
    graph_json = json.dumps(data, cls= plotly.utils.PlotlyJSONEncoder)
    return graph_json

def get_metadata_item(company_overview, record_name):
    # Beta, SharesOutstanding, MarketCapitalization, cash
    value = float(company_overview[record_name]) if '.' in company_overview[record_name] else int(company_overview[record_name])
    return value

def get_market_value_of_debt(balance_sheet):
    long_term_debt = get_financial_statement_record(balance_sheet,'totalLongTermDebt')
    short_term_debt = get_financial_statement_record(balance_sheet,'shortTermDebt')
    market_value_of_debt = (long_term_debt + short_term_debt) * 1.2
    return round(market_value_of_debt)


def get_current_price(symbol, api_key):
    r = requests.get('https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=' + symbol +'&apikey=' + api_key) 
    res = r.json()
    for record in res:
        if 'Quote' in record:
            for inner_record in res[record]:
                if 'price' in inner_record:
                    return float(res[record][inner_record])
    raise NameError("Cannot find current stock price") 

def get_growth_rate(symbol, overview, current_price):
    target_price = get_metadata_item(overview, 'AnalystTargetPrice')
    growth_rate = 100 * (target_price - current_price) / current_price
    return round(growth_rate, 2)

def get_business_tax_rate(income_statemet):
    income_tax_expenses = get_financial_statement_record_ttm(income_statemet, 'incomeTaxExpense') 
    earnings_before_taxes = get_financial_statement_record_ttm(income_statemet, 'incomeBeforeTax')
    business_tax_rate = 100 * income_tax_expenses / earnings_before_taxes
    return round(business_tax_rate, 2)
