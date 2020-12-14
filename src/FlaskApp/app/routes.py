from datetime import datetime
import IntrinsicValue.FinancialsAlpha as FA
from flask import render_template, flash, redirect, url_for, request, jsonify, session
import time
from app import app, db
from app.models import Report
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


@app.route('/', methods=['GET', 'POST'])
@app.route('/StockReport', methods=['GET', 'POST'])
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
    return render_template('StockReport.html', title='Submit', form=form)

@app.route("/stockreport2")
def main():
    return render_template('stockreport2.html', reload = time.time())

@app.route("/api/info")
def api_info():
    info = {
       "ip" : "127.0.0.1",
       "hostname" : "everest",
       "description" : "Main server",
       "load" : [ 3.21, 7, 14 ]
    }
    return jsonify(info)

@app.route("/api/intrinsicvalue")
def add():
    symbol = str(request.args.get('symbol', type=str))
    growth_rate = str(request.args.get('growth_rate', type=str))
    effective_tax_rate = str(request.args.get('effective_tax_rate', type=str))
    interest_rate = str(request.args.get('interest_rate', type=str))
    intrinsic_value_calculator = IntrinsicValue.InrinsicValue(symbol)

    existing_info = Report.query.filter_by(symbol=symbol).first()
    # retrieve the intrinsic value for session if it exists there and is refreshed in less than a day
    if existing_info is not None and ( datetime.now() - existing_info.created_date).days < 1:
        # get intrinsic value
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
        db_record = Report(symbol=symbol, overview=intrinsic_value_calculator.overview, income_statement=intrinsic_value_calculator.income_statement, \
            balance_sheet=intrinsic_value_calculator.balance_sheet, cash_flow=intrinsic_value_calculator.cash_flow, created_date=datetime.now())
        db.session.add(db_record)
        db.session.commit()

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
    long_term_debt = FA.get_financial_statement_record(intrinsic_value_calculator.balance_sheet, 'totalLongTermDebt') 
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
    r_o_i_c = FA.get_return_on_invested_capital(intrinsic_value_calculator.income_statement, intrinsic_value_calculator.balance_sheet)

    # plots
    eps_plot = intrinsic_value_calculator.plot_eps()
    accounts_payable_plot = intrinsic_value_calculator.plot_accounts_payable()
    accounts_receivable_plot = intrinsic_value_calculator.plot_accounts_receivable()
    inventory_plot = intrinsic_value_calculator.plot_inventory()
    free_cash_flow_plot = intrinsic_value_calculator.plot_free_cash_flow()
    growth_plots = intrinsic_value_calculator.plot_growth_values()

    # get stock name
    responses = requests.get('https://www.macrotrends.net/stocks/charts/' + symbol)
    path = urllib.parse.urlparse(responses.url).path
    stock_name = path.split('/')[-2]

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

        'total_revenue_plot'        : total_revenue_plot,
        'eps_plot'                  : eps_plot,
        'accounts_payable_plot'     : accounts_payable_plot,
        'accounts_receivable_plot'  : accounts_receivable_plot,
        'inventory_plot'            : inventory_plot,
        'free_cash_flow_plot'       : free_cash_flow_plot,
        'growth_plots'              : growth_plots
    })