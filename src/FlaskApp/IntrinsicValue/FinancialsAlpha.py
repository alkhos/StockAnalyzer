from numpy.lib.type_check import common_type
import requests
import json
import datetime
import enum
import plotly
import plotly.graph_objects as go

class DocumentType(enum.Enum):
    def __str__(self):
        return str(self.value)

    BALANCE_SHEET = 1
    INCOME_STATEMENT = 2
    CASH_FLOW = 3
    OVERVIEW = 4

def get_financial_statement(symbol, document_type, api_key, use_file=False): 
    """Get the financial statements

    Args:
        symbol (str): Stock ticket symbol
        document_type (enum): Document Type: overview, balance_sheet, income_statement, or cash_flow
        api_key (str): API key
        use_file (bool, optional): Optiona value to read from a file. Defaults to False.

    Returns:
        json: JSON object representing the financial statements
    """
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
    """Save financial statement as JSON

    Args:
        finiancial_statements (json): JSON object representing the financial statements
        document_type (enum): Document Type: overview, balance_sheet, income_statement, or cash_flow
    """
    # write output to a file
    symbol = finiancial_statements['symbol'] if 'symbol' in finiancial_statements else finiancial_statements['Symbol']
    file_name = symbol + '_' + document_type.name  + '.json'
    with open(file_name, 'w') as data_output_file:
        json.dump(finiancial_statements, data_output_file, indent=4, sort_keys=True)

def get_last_four_quarters(finiancial_statements):
    """Get last four quarters of financial data

    Args:
        finiancial_statements (json): JSON object representing the financial statement

    Returns:
        json: A dictionary of last four quarters of the provided financial statement
    """
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
    """Get last four quarters of the given financial statement

    Args:
        finiancial_statements (json): JSON object representing the financial statement

    Returns:
        json: A  trimmed json with the last four quarters' data
    """
    return finiancial_statements['quarterlyReports'][0]

def get_last_annual(finiancial_statements):
    """Get last year of the given financial statement

    Args:
        finiancial_statements (json): JSON object representing the financial statement

    Returns:
        json: A  trimmed json with the last year' data
    """
    return finiancial_statements['annualReports'][0]

def get_last_annual_report_date(finiancial_statements):
    """Get the date of reporting for the last annual report

    Args:
        finiancial_statements (json): JSON object representing the financial statement

    Returns:
        datetime: date of the last annual report
    """
    all_reports = []
    for report in finiancial_statements['annualReports']:
        datetime_object = datetime.datetime.strptime(report['fiscalDateEnding'], '%Y-%m-%d')
        all_reports.append(datetime_object)
    last_report = max(all_reports)
    last_report_str = last_report.strftime('%Y-%m-%d')
    return last_report_str

def get_last_quarterly_report_date(finiancial_statements):
    """Get the date of reporting for the last quarterly report

    Args:
        finiancial_statements (json): JSON object representing the financial statement

    Returns:
        datetime: date of the last quarterly report
    """
    all_reports = []
    for report in finiancial_statements['quarterlyReports']:
        datetime_object = datetime.datetime.strptime(report['fiscalDateEnding'], '%Y-%m-%d')
        all_reports.append(datetime_object)
    last_report = max(all_reports)
    last_report_str = last_report.strftime('%Y-%m-%d')
    return last_report_str

def get_free_cashflow_ttm(cash_flow_statement):
    """Get trailing twelve month value for free cash flow (FCF)

    Args:
        cash_flow_statement (json): Cash flow statement as a json

    Returns:
        int: TTM value of free cash flow
    """
    last_four_quarters = get_last_four_quarters(cash_flow_statement)
    free_cash_flow_ttm = 0
    for quarter in last_four_quarters:
        free_cash_flow = int(quarter['operatingCashflow']) - int(quarter['capitalExpenditures'])
        free_cash_flow_ttm = free_cash_flow_ttm + free_cash_flow
    return free_cash_flow_ttm

def get_financial_statement_record_ttm(finiancial_statement, record_name):
    """Get trailing twelve month value for the requested record from the financial statement

    Args:
        finiancial_statement (json): Financial statement to be used as a json
        record_name (str): Name of the record from finanacial statement 

    Returns:
        int: TTM value of the requested item from the financial statement
    """
    last_four_quarters = get_last_four_quarters(finiancial_statement)
    record_ttm = 0
    for record in last_four_quarters:
        value = 0 if record[record_name] == "None" else int(record[record_name])
        record_ttm = record_ttm + value
    return record_ttm

def get_financial_statement_record(finiancial_statement, record_name, find_latest_existing=False):
    """Get any record from the financial statement for the last quarter

    Args:
        finiancial_statement (json): Financial statement to be used as a json
        record_name (str): Name of the record from finanacial statement 
        find_latest_existing (bool, optional): If set to true, and the record not exisiting in the last quarter, we
            will find the latest one that has a number. Defaults to False.

    Returns:
        int : Value of the requested item from the financial statement
    """
    last_quarter = get_last_quarter(finiancial_statement)
    if find_latest_existing:
        for record in finiancial_statement['quarterlyReports']:
            if record[record_name] == "None":
                continue
            return int(record[record_name])
    else:
        value = 0 if last_quarter[record_name] == "None" else int(last_quarter[record_name])
        return value

def get_financial_statement_record_average(finiancial_statement, record_name):
    """Get any record from the financial statement for the last quarter

    Args:
        finiancial_statement (json): Financial statement to be used as a json
        record_name (str): Name of the record from finanacial statement 
        find_latest_existing (bool, optional): If set to true, and the record not exisiting in the last quarter, we
            will find the latest one that has a number. Defaults to False.

    Returns:
        int : Value of the requested item from the financial statement
    """
    last_four_quarters = get_last_four_quarters(finiancial_statement)
    values = []
    for quarter in last_four_quarters:
        if quarter[record_name] == "None":
            continue
        values.append(int(quarter[record_name]))
    return float(sum(values))/len(values) # get the average

def get_long_term_debt(balance_sheet):
    """Get the value of long term debt. Use maximum of long term debt and total long term debt on the statement

    Args:
        balance_sheet (json): Balance sheet as a json

    Returns:
        int: long term debt
    """
    total_long_term_debt = get_financial_statement_record(balance_sheet, 'totalLongTermDebt')
    long_term_debt = get_financial_statement_record(balance_sheet, 'longTermDebt')
    return max(total_long_term_debt, long_term_debt)
    
def get_interest_rate(balance_sheet, income_statemet):
    """Get business interest rate as interest expense over total of long-term and short term debt

    Args:
        balance_sheet (json): Balance sheet as a json
        income_statemet (json): Income statement as a json

    Returns:
        float: business interest rate in %
    """
    interest_expense = get_financial_statement_record_ttm(income_statemet, 'interestExpense')
    principal_balance = get_long_term_debt(balance_sheet) + \
        get_financial_statement_record(balance_sheet, 'shortTermDebt')
    return round(100*interest_expense/principal_balance, 2) if principal_balance != 0 else 0

def get_long_term_interest_rate(balance_sheet, income_statemet):
    """Get long term interest rate for the business as interest expense over total long-term debt

    Args:
        balance_sheet (json): Balance sheet as a json
        income_statemet (json): Income statement as a json

    Returns:
        float: long term interest rate in %
    """
    interest_expense = get_financial_statement_record_ttm(income_statemet, 'interestExpense')
    principal_balance = get_long_term_debt(balance_sheet) 
    return round(100*interest_expense/principal_balance, 2) if principal_balance != 0 else 0

def get_metadata_item(company_overview, record_name):
    """Retriew any numerical record from company overview

    Args:
        company_overview (json): Company overview as a json
        record_name (str): Name of the record to be looked up

    Returns:
        float: Value of the requested record
    """
    # Beta, SharesOutstanding, MarketCapitalization, cash
    if company_overview[record_name] == 'None':
        return 0
    value = float(company_overview[record_name]) if '.' in company_overview[record_name] else int(company_overview[record_name])
    return value

def get_market_value_of_debt(balance_sheet):
    """Get market value of debt as long-term + short-term debt times 1.2

    Args:
        balance_sheet (json): Balance sheet as a json

    Returns:
        float: market value of debt
    """
    long_term_debt = get_long_term_debt(balance_sheet)
    short_term_debt = get_financial_statement_record(balance_sheet,'shortTermDebt')
    market_value_of_debt = (long_term_debt + short_term_debt) * 1.2
    return round(market_value_of_debt)


def get_current_price(symbol, api_key):
    """Get current pirce of the stock

    Args:
        symbol (str): Stock ticket symbol
        api_key (str): API key

    Raises:
        NameError: If stock ticker symbol is invalid

    Returns:
        float: the current stock price
    """
    r = requests.get('https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=' + symbol +'&apikey=' + api_key) 
    res = r.json()
    for record in res:
        if 'Quote' in record:
            for inner_record in res[record]:
                if 'price' in inner_record:
                    return float(res[record][inner_record])
    raise NameError("Cannot find current stock price") 

def get_growth_rate(symbol, overview, current_price):
    """Get company growth rate as analyst target price vs current price

    Args:
        symbol (str): Stock ticker symbol
        overview (json): Overview document for the stock as json
        current_price (float): current stock price

    Returns:
        float: growth rate of the stock in %
    """
    target_price = get_metadata_item(overview, 'AnalystTargetPrice')
    growth_rate = 100 * (target_price - current_price) / current_price
    return round(growth_rate, 2)

def get_business_tax_rate(income_statemet):
    """Get the business tax rate as income tax expense divided by income before tax

    Args:
        income_statemet (json): the income statement as a json

    Returns:
        float: income tax rate in %
    """
    income_tax_expenses = get_financial_statement_record_ttm(income_statemet, 'incomeTaxExpense') 
    earnings_before_taxes = get_financial_statement_record_ttm(income_statemet, 'incomeBeforeTax')
    business_tax_rate = 100 * income_tax_expenses / earnings_before_taxes
    return round(business_tax_rate, 2)

def get_current_ratio(balance_sheet):
    """Get current ratio as current assests over current liabilities for last quarter

    Args:
        balance_sheet (json): Balance sheet as a json

    Returns:
        float: current ratio as a decimal
    """
    total_current_assets = get_financial_statement_record(balance_sheet, 'totalCurrentAssets')
    total_current_liabilities = get_financial_statement_record(balance_sheet, 'totalCurrentLiabilities')
    return float(total_current_assets/total_current_liabilities) if total_current_liabilities != 0 else 0

def get_debt_to_net_current_assets_ratio(balance_sheet):
    """Get net current assets over total ( short-term and long-term) debt for the last quarter

    Args:
        balance_sheet (json): Balance sheet as a json

    Returns:
        float: Net current assets over debt as a decimal
    """
    total_current_assets = get_financial_statement_record(balance_sheet, 'totalCurrentAssets')
    total_current_liabilities = get_financial_statement_record(balance_sheet, 'totalCurrentLiabilities')
    net_current_assets = total_current_assets - total_current_liabilities
    short_term_debt = get_financial_statement_record(balance_sheet, 'shortTermDebt')
    long_term_debt = get_financial_statement_record(balance_sheet, 'longTermDebt')
    total_debt = short_term_debt + long_term_debt
    return float(net_current_assets/total_debt) if total_debt != 0 else 0

def get_price_to_tangible_book_value(balance_sheet, stock_price, shares_outstanding):
    """Get price over tangible book value(total assets minus total liabilities minus intangible assets and goodwill)

    Args:
        balance_sheet (json): Balance sheet as a json
        stock_price (float): Current stock price
        shares_outstanding (int): Number of shares outstanding currently

    Returns:
        float: Pirce to tangible book value as a decimal
    """
    total_assets = get_financial_statement_record(balance_sheet, 'totalAssets')
    total_liabilities = get_financial_statement_record(balance_sheet, 'totalLiabilities')
    intangible_assets = get_financial_statement_record(balance_sheet, 'intangibleAssets')
    good_will = get_financial_statement_record(balance_sheet, 'goodwill')
    negative_good_will = get_financial_statement_record(balance_sheet, 'negativeGoodwill')
    tangible_book_value = total_assets - total_liabilities - intangible_assets - good_will + negative_good_will
    return float(stock_price/(tangible_book_value/shares_outstanding))

def get_return_on_invested_capital(income_statement, balance_sheet, cash_flow, tax_rate=''):
    """Get the return on invested capital as nopat over invested capital

    Args:
        income_statement (json): Income statement as a json
        balance_sheet (json): Balance sheet as a json
        cash_flow (json): cash flow statement as a json
        tax_rate (str, optional): Company tax rate %. If not provided, we will get it as tax expense over income before tax. Defaults to ''.

    Returns:
        float: ROIC
    """
    income_before_tax = get_financial_statement_record_ttm(income_statement, 'incomeBeforeTax')
    income_tax_expense = get_financial_statement_record_ttm(income_statement, 'incomeTaxExpense')
    operating_income = get_financial_statement_record_ttm(income_statement, 'operatingIncome')
    if tax_rate == '' or tax_rate == 'None' or tax_rate == None:
        nopat = operating_income*(1 - float(income_tax_expense/income_before_tax))
    else:
        nopat = operating_income*(1 - float(tax_rate)/100)
    # long_term_debt = get_financial_statement_record(balance_sheet, 'longTermDebt')
    # short_term_debt = get_financial_statement_record(balance_sheet, 'shortTermDebt')
    # shareholder_equity = get_financial_statement_record(balance_sheet, 'totalShareholderEquity')
    # capital_lease = get_financial_statement_record(balance_sheet, 'capitalLeaseObligations')
    # invested_capital = long_term_debt + short_term_debt + capital_lease + shareholder_equity
    invested_capital = get_invested_capital(balance_sheet, cash_flow)
    return float(100*nopat/invested_capital)

def get_invested_capital(balance_sheet, cash_flow):
    """Get the value of invested capital as the some of all income from non-operating activities

    Args:
        balance_sheet (json): Balance sheet as a json
        cash_flow (json): cash flow statement as a json

    Returns:
        int: Invested capital value
    """
    # from balance sheet
    long_term_debt = get_financial_statement_record(balance_sheet, 'longTermDebt')
    short_term_debt = get_financial_statement_record(balance_sheet, 'shortTermDebt')
    lease_obligations = get_financial_statement_record(balance_sheet, 'capitalLeaseObligations')
    total_debt_and_leases = short_term_debt + long_term_debt + lease_obligations

    # from income statement
    common_stock = get_financial_statement_record(balance_sheet, 'commonStock')
    retained_earnings = get_financial_statement_record(balance_sheet, 'retainedEarnings')
    total_equity_and_equity_equivalents = common_stock + retained_earnings

    # from cash flow statement
    cash_from_financing = get_financial_statement_record_ttm(cash_flow, 'cashflowFromFinancing')
    cash_from_investing = get_financial_statement_record_ttm(cash_flow, 'cashflowFromInvestment')
    non_operating_cash = cash_from_financing + cash_from_investing

    return total_debt_and_leases + total_equity_and_equity_equivalents + non_operating_cash

def get_return_on_equity(balance_sheet, income_statement):
    shareholder_equity = get_financial_statement_record_average(balance_sheet, 'totalShareholderEquity')
    net_income = get_financial_statement_record_ttm(income_statement, 'netIncome')
    return float(net_income/shareholder_equity)

def get_return_on_assets(balance_sheet, income_statement):
    total_assets = get_financial_statement_record_average(balance_sheet, 'totalAssets')
    net_income = get_financial_statement_record_ttm(income_statement, 'netIncome')
    return float(net_income/total_assets)

def get_net_profit_margin(income_statement):
    net_income = get_financial_statement_record_ttm(income_statement, 'netIncome')
    total_revenue = get_financial_statement_record_ttm(income_statement, 'totalRevenue')
    return float(net_income/total_revenue)

def get_quality_of_income(income_statement, cash_flow):
    cash_from_operating_activities = get_financial_statement_record_ttm(cash_flow, 'operatingCashflow')
    net_income = get_financial_statement_record_ttm(income_statement, 'netIncome')
    return float(cash_from_operating_activities/net_income)

def get_price_to_earnings_ratio(overview, stock_price):
    """Get the diluted TTM P/E ration

    Args:
        overview (json): Company overview passed as json
        stock_price (float): current stock price

    Returns:
        float: P/E
    """ 
    diluted_earnings_per_share = float(overview['DilutedEPSTTM'])
    return float(stock_price/diluted_earnings_per_share)

def get_price_to_earnings_over_growth_ratio(overview, stock_price):
    """Get the PEG ratio

    Args:
        overview (json): Company overview passed as json
        stock_price (float): current stock price

    Returns:
        float: PEG ratio
    """
    diluted_earnings_per_share = float(overview['DilutedEPSTTM'])
    nominal_peg = float(overview['PEGRatio'])
    nominal_pe = float(overview['PERatio'])
    growth = nominal_pe / nominal_peg
    return float(diluted_earnings_per_share/growth)

def get_dividend_adjusted_price_to_earnings_over_growth_ratio(overview, stock_price):
    """Get the dividend adjusted PEG ratio

    Args:
        overview (json): Company overview passed as json
        stock_price (float): current stock price

    Returns:
        float: Dividend adjusted PEG ratio
    """
    diluted_earnings_per_share = float(overview['DilutedEPSTTM'])
    nominal_peg = float(overview['PEGRatio'])
    nominal_pe = float(overview['PERatio'])
    growth = nominal_pe / nominal_peg
    dividend_yield = float(overview['DividendYield']) if overview['DividendYield'] != 'None' else 0
    return float(diluted_earnings_per_share/(growth + dividend_yield))

def get_net_cash_per_share(balance_sheet, shares_outstanding):
    """Get the net cash per share as the total cash and short term investments over shares outstanding

    Args:
        balance_sheet (json): Balance sheet as a json
        shares_outstanding (int): current number of shares outstanding

    Returns:
        float: net cash per share
    """
    net_cash = get_financial_statement_record(balance_sheet, 'cashAndShortTermInvestments')
    return float(net_cash/shares_outstanding)

def get_debt_to_equity_ratio(balance_sheet):
    """Get the debt to equity ratio as total liabilities over total shareholder's equity

    Args:
        balance_sheet (json): Balance sheet as a json

    Returns:
        float: D/E ratio
    """
    total_liabilities = get_financial_statement_record(balance_sheet, 'totalLiabilities')
    total_shareholder_equity = get_financial_statement_record(balance_sheet, 'totalShareholderEquity')
    return float(total_liabilities/total_shareholder_equity)

def get_inventory_turnover_last_year(balance_sheet, income_statement):
    """Inventory turnover for last year as cost of goods sold over average inventory

    Args:
        income_statement (json): Income statement as a json
        balance_sheet (json): Balance sheet as a json

    Returns:
        float: inventory turnover
    """
    cogs = get_cost_of_goods_sold(income_statement)
    average_inventory = get_financial_statement_record_average(balance_sheet, 'inventory')
    return float(cogs/average_inventory)

def get_cost_of_goods_sold(income_statement):
    total_reveneue = get_financial_statement_record_ttm(income_statement, 'totalRevenue')
    gross_profit = get_financial_statement_record_ttm(income_statement, 'grossProfit')
    cogs = total_reveneue - gross_profit
    return cogs

def get_receivable_turnover_ratio(balance_sheet, income_statement):
    revenue = get_financial_statement_record_ttm(income_statement, 'totalRevenue')
    average_receivables = get_financial_statement_record_average(balance_sheet, 'netReceivables')
    return float(revenue/average_receivables)

def get_payable_turnover_ratio(balance_sheet, income_statement):
    cogs = get_cost_of_goods_sold(income_statement)
    average_receivables = get_financial_statement_record_average(balance_sheet, 'accountsPayable')
    return float(cogs/average_receivables)

def get_asset_turnover(balance_sheet, income_statement):
    total_reveneue = get_financial_statement_record_ttm(income_statement, 'totalRevenue')
    average_assets = get_financial_statement_record_average(balance_sheet, 'totalAssets')
    return float(total_reveneue/average_assets)

def count_earning_deficits(income_statement):
    """Find number of annual reports and number of quarters reporting earnings deficit

    Args:
        income_statemet (json): the income statement as a json

    Returns:
        dict: A dictionary for number of annual reports and number of quarters reporting earnings deficit
    """
    deficits = {}
    count = 0
    for record in income_statement['annualReports']:
        if record['netIncome'] == 'None':
            continue
        if int(record['netIncome']) < 0:
            count = count + 1
    deficits['annual'] = count

    count = 0
    for record in income_statement['quarterlyReports']:
        if record['netIncome'] == 'None':
            continue
        if int(record['netIncome']) < 0:
            count = count + 1
    deficits['quarterly'] = count
    return deficits

def get_earning_growth(income_statement):
    """Get earnings growth for the last quarter and last annum

    Args:
        income_statemet (json): the income statement as a json

    Returns:
        dict: A dictionary with % growth of earnings in the last quarter and annum
    """
    growth = {}
    current = int(income_statement['annualReports'][0]['netIncome'])
    previous = int(income_statement['annualReports'][1]['netIncome'])
    growth['annual'] = float(100*(current-previous)/previous)

    current = int(income_statement['quarterlyReports'][0]['netIncome'])
    previous = int(income_statement['quarterlyReports'][1]['netIncome'])
    growth['quarterly'] = float(100*(current-previous)/previous)
    return growth

def get_last_dividend(overview):
    """Get the value of last dividend payed by the company

    Args:
        overview (json): Company overview data as a json

    Returns:
        float: Value of dividend payed by the company last time
    """
    return get_metadata_item(overview, 'DividendPerShare')

def produce_plotly_time_series(input_dictionary, symbol, record_name):
    """Plot the given input dictionary as a plotly json

    Args:
        input_dictionary (dict): Dictionary of input values over time
        symbol (str): Ticker symbol for the stock
        record_name (str): The name of the item that is being plotted to be used in the title

    Returns:
        json: A timeseires plotly plot as json
    """
    # using plotly
    x,y = zip(*sorted(input_dictionary.items()))
    data = go.Figure([go.Scatter(x=x, y=y)])

    data.update_layout(
        title= record_name + ' for ' + symbol,
        xaxis_title='Year',
        yaxis_title=record_name + ' (Million of Dollars)')
    graph_json = json.dumps(data, cls= plotly.utils.PlotlyJSONEncoder)
    return graph_json
