from datetime import datetime
import IntrinsicValue.FinancialsAlpha as FA
import IntrinsicValue.EdgarLookup as Edgar
from flask import render_template, flash, redirect, url_for, request, jsonify, session
import time
from app import app, db
from app.models import Report, TickerCik
from app.forms import StockInputForm
from IntrinsicValue import IntrinsicValue
import sys
import requests
import urllib.parse
 

sys.path.insert(1, '../IntrinsicValue')

@app.route('/index/<symbol>')
def index(symbol='MSFT'):
    intrinsic_value_calculator = IntrinsicValue.InrinsicValue(symbol)
    growth_rate = request.cookies.get('growth_rate')
    if growth_rate is not None:
        intrinsic_value_calculator.growth_rate = int(growth_rate)
    intrinsic_value_per_share = intrinsic_value_calculator.get_intrinsic_value_per_share()
    stock_ticker = {'symbol': symbol, 'intrinsic_value_per_share': intrinsic_value_per_share}
    return render_template('index.html', title='Home', stock_ticker=stock_ticker)


@app.route('/OldReport', methods=['GET', 'POST'])
def StockReport():
    form = StockInputForm()
    if form.validate_on_submit():
        flash('Stock Report requested for ticker symbol {}'.format(
            form.ticker.data))
        growth_rate = -1
        if form.growth_rate is not None:
            growth_rate = form.growth_rate.data
        response = redirect(url_for('index', symbol = form.ticker.data))
        response.set_cookie('growth_rate', str(growth_rate))
        return response
    return render_template('OldReport.html', title='Submit', form=form)

@app.route('/', methods=['GET', 'POST'])
@app.route("/StockReport")
def main():
    return render_template('StockReport.html', reload = time.time())

@app.route("/StockScreen")
def StockScreen():
    return render_template('StockScreen.html', reload = time.time())

@app.route("/api/info")
def api_info():
    info = {
       "ip" : "127.0.0.1",
       "hostname" : "everest",
       "description" : "Main server",
       "load" : [ 3.21, 7, 14 ]
    }
    return jsonify(info)

@app.route("/api/downloads")
def downloads():
    symbol = str(request.args.get('symbol', type=str))
    intrinsic_value_calculator = IntrinsicValue.InrinsicValue(symbol)
    fill_intrinsic_value_calculator(intrinsic_value_calculator)
    FA.save_as_json(intrinsic_value_calculator.overview, FA.DocumentType.OVERVIEW)
    FA.save_as_json(intrinsic_value_calculator.balance_sheet, FA.DocumentType.BALANCE_SHEET)
    FA.save_as_json(intrinsic_value_calculator.income_statement, FA.DocumentType.INCOME_STATEMENT)
    FA.save_as_json(intrinsic_value_calculator.cash_flow, FA.DocumentType.CASH_FLOW)
    return jsonify({
        'symbol'                    : symbol,
    })

@app.route("/api/intrinsicvalue")
def intrinsicvalue():
    symbol = str(request.args.get('symbol', type=str))
    growth_rate = str(request.args.get('growth_rate', type=str))
    effective_tax_rate = str(request.args.get('effective_tax_rate', type=str))
    interest_rate = str(request.args.get('interest_rate', type=str))
    intrinsic_value_calculator = IntrinsicValue.InrinsicValue(symbol)

    ###########
    fill_intrinsic_value_calculator(intrinsic_value_calculator)

    # set optional values, growth rate
    if growth_rate and growth_rate != 'None':
        # process growth rate if provided
        intrinsic_value_calculator.growth_rate = float(growth_rate)

    # set optional values, tax rate
    if effective_tax_rate and effective_tax_rate != 'None':
        # process growth rate if provided
        intrinsic_value_calculator.business_tax_rate = float(effective_tax_rate)

    # set optional values, interest rate
    if interest_rate and interest_rate != 'None':
        # process growth rate if provided
        intrinsic_value_calculator.interest_rate = int(interest_rate)

    # intrinsic value
    intrinsic_value_per_share = intrinsic_value_calculator.get_intrinsic_value_per_share()
    short_term_debt = FA.get_financial_statement_record(intrinsic_value_calculator.balance_sheet, 'shortTermDebt')
    long_term_debt = FA.get_long_term_debt(intrinsic_value_calculator.balance_sheet)
    total_revenue_plot = intrinsic_value_calculator.plot_revenue()

    # graham
    current_ratio = FA.get_current_ratio(intrinsic_value_calculator.balance_sheet)
    earning_deficits = FA.count_earning_deficits(intrinsic_value_calculator.income_statement)
    earning_deficits_str = 'Annual: ' + str(earning_deficits['annual']) + ' | ' + 'Quarterly: ' + str(earning_deficits['quarterly'])
    earning_growth = FA.get_earning_growth(intrinsic_value_calculator.income_statement)
    earning_growth_str = 'Annual: ' + str(round(earning_growth['annual'],2)) + ' | ' + 'Quarterly: ' + str(round(earning_growth['quarterly'],2))
    d_t_n_c_a_ratio = FA.get_debt_to_net_current_assets_ratio(intrinsic_value_calculator.balance_sheet)
    dividend = FA.get_last_dividend(intrinsic_value_calculator.overview)
    p_t_b_v_ratio = FA.get_price_to_tangible_book_value(intrinsic_value_calculator.balance_sheet, \
        intrinsic_value_calculator.current_price, intrinsic_value_calculator.shares_outstanding)
    r_o_i_c = FA.get_return_on_invested_capital(intrinsic_value_calculator.income_statement, intrinsic_value_calculator.balance_sheet, \
        intrinsic_value_calculator.cash_flow, effective_tax_rate)
    w_a_c_c = intrinsic_value_calculator.get_weighted_average_cost_of_capital()

    # peter lynch
    p_e = FA.get_price_to_earnings_ratio(intrinsic_value_calculator.overview, intrinsic_value_calculator.current_price)
    p_e_g = FA.get_price_to_earnings_over_growth_ratio(intrinsic_value_calculator.overview, intrinsic_value_calculator.current_price)
    d_p_e_g = FA.get_dividend_adjusted_price_to_earnings_over_growth_ratio(intrinsic_value_calculator.overview, intrinsic_value_calculator.current_price)
    n_c_s = FA.get_net_cash_per_share(intrinsic_value_calculator.balance_sheet, intrinsic_value_calculator.shares_outstanding)
    d_e_ratio = FA.get_debt_to_equity_ratio(intrinsic_value_calculator.balance_sheet)
    insider = float(intrinsic_value_calculator.overview['PercentInsiders'])

    # other ratios
    invetory_turnover = FA.get_inventory_turnover_last_year(intrinsic_value_calculator.balance_sheet, intrinsic_value_calculator.income_statement)
    receivables_turnover = FA.get_receivable_turnover_ratio(intrinsic_value_calculator.balance_sheet, intrinsic_value_calculator.income_statement)
    payables_turnover = FA.get_payable_turnover_ratio(intrinsic_value_calculator.balance_sheet, intrinsic_value_calculator.income_statement)
    asset_turnover = FA.get_asset_turnover(intrinsic_value_calculator.balance_sheet, intrinsic_value_calculator.income_statement)
    r_o_e = FA.get_return_on_equity(intrinsic_value_calculator.balance_sheet, intrinsic_value_calculator.income_statement)
    r_o_a = FA.get_return_on_assets(intrinsic_value_calculator.balance_sheet, intrinsic_value_calculator.income_statement)
    profit_margin = FA.get_net_profit_margin(intrinsic_value_calculator.income_statement)
    quality_of_income = FA.get_quality_of_income(intrinsic_value_calculator.income_statement, intrinsic_value_calculator.cash_flow)

    # plots
    eps_plot = intrinsic_value_calculator.plot_eps()
    accounts_payable_plot = intrinsic_value_calculator.plot_accounts_payable()
    accounts_receivable_plot = intrinsic_value_calculator.plot_accounts_receivable()
    inventory_plot = intrinsic_value_calculator.plot_inventory()
    free_cash_flow_plot = intrinsic_value_calculator.plot_free_cash_flow()
    growth_plots_annual = intrinsic_value_calculator.plot_annual_growth_values()
    growth_plots_quarterly = intrinsic_value_calculator.plot_quarterly_growth_values()

    # get stock name
    responses = requests.get('https://www.macrotrends.net/stocks/charts/' + symbol)
    path = urllib.parse.urlparse(responses.url).path
    stock_name = path.split('/')[-2]

    # get annual reports from Edgar
    cik = get_cik(symbol)
    edgar_lookup = Edgar.EdgarLookup(cik)
    ten_k = edgar_lookup.get_reports(form_name='10-K')
    ten_q = edgar_lookup.get_reports(form_name='10-Q')

    return jsonify({
        'symbol'                    : symbol,
        'stock_name'                : stock_name,
        'intrinsic_value'           : intrinsic_value_per_share,
        'stock_price'               : intrinsic_value_calculator.current_price,
        'market_cap'                : round(intrinsic_value_calculator.market_value_of_equity/1e6, 2),
        'shares_outstanding'        : round(intrinsic_value_calculator.shares_outstanding/1e6, 2),
        'short_term_debt'           : round(short_term_debt/1e6, 2),
        'long_term_debt'            : round(long_term_debt/1e6, 2),
        'total_liabilities'         : round(intrinsic_value_calculator.total_liabilities/1e6, 2),
        'cash'                      : round(intrinsic_value_calculator.cash/1e6, 2),
        'beta'                      : round(intrinsic_value_calculator.beta, 2),
        'ttm_free_cash_flow'        : round(intrinsic_value_calculator.free_cashflow_ttm/1e6, 2),
        'gdp_growth_rate'           : round(intrinsic_value_calculator.gdp_growth_rate, 2),
        'marktet_rish_premium'      : intrinsic_value_calculator.market_risk_premium,
        'risk_free_rate'            : intrinsic_value_calculator.risk_free_rate,
        'business_interest_rate'    : intrinsic_value_calculator.interest_rate,
        'income_tax_rate'           : intrinsic_value_calculator.business_tax_rate,
        'business_growth_rate'      : round(intrinsic_value_calculator.growth_rate, 2),
        

        'current_ratio'             : round(current_ratio, 2),
        'd_t_n_c_a_ratio'           : round(d_t_n_c_a_ratio, 2),
        'earning_deficits'          : earning_deficits_str,
        'dividend'                  : round(dividend, 2),
        'earning_growth'            : earning_growth_str,
        'p_t_b_v_ratio'             : round(p_t_b_v_ratio, 2),
        'r_o_i_c'                   : round(r_o_i_c, 2),
        'w_a_c_c'                   : round(100*w_a_c_c, 2),

        'p_e'                       : round(p_e, 2),
        'p_e_g'                     : round(p_e_g, 2),
        'd_p_e_g'                   : round(d_p_e_g, 2),
        'n_c_s'                     : round(n_c_s, 2),
        'd_e_ratio'                 : round(d_e_ratio, 2),
        'insider'                   : round(insider, 2),

        'invetory_turnover'         : round(invetory_turnover, 2),
        'receivables_turnover'      : round(receivables_turnover, 2),
        'payables_turnover'         : round(payables_turnover, 2),
        'asset_turnover'            : round(asset_turnover, 2),
        'r_o_e'                     : round(100*r_o_e, 2),
        'r_o_a'                     : round(100*r_o_a, 2),
        'profit_margin'             : round(100*profit_margin, 2),
        'quality_of_income'         : round(quality_of_income, 2),

        'total_revenue_plot'        : total_revenue_plot,
        'eps_plot'                  : eps_plot,
        'accounts_payable_plot'     : accounts_payable_plot,
        'accounts_receivable_plot'  : accounts_receivable_plot,
        'inventory_plot'            : inventory_plot,
        'free_cash_flow_plot'       : free_cash_flow_plot,
        'growth_plots_annual'       : growth_plots_annual,
        'growth_plots_quarterly'    : growth_plots_quarterly,

        '10-K'                      : ten_k,
        '10-Q'                      : ten_q
    })

def fill_intrinsic_value_calculator(intrinsic_value_calculator):
    existing_info = Report.query.filter_by(symbol=intrinsic_value_calculator.symbol).first()
    # retrieve the intrinsic value for session if it exists there and is refreshed in less than a day
    if existing_info is not None and ( datetime.now() - existing_info.created_date).days < 1:
        # get intrinsic value
        # overview = FA.get_financial_statement(symbol, FA.DocumentType.OVERVIEW, intrinsic_value_calculator.alpha_api_key)
        intrinsic_value_calculator.set_financial_statements(existing_info.overview, existing_info.income_statement, 
        existing_info.balance_sheet, existing_info.cash_flow)

        # retreive the calculatr from financial statements
    else:
        # remove existing record if any
        if existing_info is not None:
            db.session.delete(existing_info)
            db.session.commit()

        # get finanacial statements from API
        intrinsic_value_calculator.get_financial_statements_externally()
        
        # add to database 
        db_record = Report(symbol=intrinsic_value_calculator.symbol, overview=intrinsic_value_calculator.overview, income_statement=intrinsic_value_calculator.income_statement, \
            balance_sheet=intrinsic_value_calculator.balance_sheet, cash_flow=intrinsic_value_calculator.cash_flow, created_date=datetime.now())
        db.session.add(db_record)
        db.session.commit()

def get_cik(symbol):
    """Get the CIK value for Edgar lookup. From database first and otherwise from Edgar

    Args:
        symbol (string): Stock ticker symbol

    Returns:
        string: Stock CIK
    """
    db_symbol = symbol + '_ciklookup'
    existing_info = TickerCik.query.filter_by(symbol=db_symbol).first()
    # retrieve the intrinsic value for session if it exists there and is refreshed in less than a day
    if existing_info is not None and ( datetime.now() - existing_info.created_date).days < 30:
        return existing_info.cik
    else:
        # remove existing record if any
        if existing_info is not None:
            db.session.delete(existing_info)
            db.session.commit()

        # get finanacial statements from API
        all_ticker_to_cik = Edgar.EdgarLookup.get_all_ticker_to_cik()
        for item in all_ticker_to_cik:
            if item[0] == symbol.lower():
                # add to database 
                db_record = TickerCik(symbol=db_symbol, cik=item[1], created_date=datetime.now())
                db.session.add(db_record)
                db.session.commit()   
                return item[1]

        return ''