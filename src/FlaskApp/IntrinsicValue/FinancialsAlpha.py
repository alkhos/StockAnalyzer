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

def get_financial_statement_record(finiancial_statement, record_name):
    last_quarter = get_last_quarter(finiancial_statement)
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
    else:
        # using plotly
        x,y = zip(*sorted(free_cash_flows.items()))
        # trace = go.Scatter(x=x, y=y)
        # data = [trace]
        symbol = cash_flow_statement['symbol']
        data = go.Figure([go.Scatter(x=x, y=y)])

        data.update_layout(
            title="Free Cash Flow for " + symbol,
            xaxis_title="Year",
            yaxis_title="Free Cash Flow (Million of Dollars)")
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
