from datetime import date, datetime
import IntrinsicValue.FinancialsAlpha as FA
from flask import render_template, flash, redirect, url_for, request, jsonify, session
import time
from app import app, db
from app.models import Report
from app.forms import StockInputForm
from IntrinsicValue import IntrinsicValue
import sys
import plotly
import plotly.graph_objects as go
import json
import pandas as pd 
import numpy as np
 

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

    if growth_rate and growth_rate != 'None':
        # process growth rate if provided
        intrinsic_value_calculator.growth_rate = int(growth_rate)

    intrinsic_value_per_share = intrinsic_value_calculator.get_intrinsic_value_per_share()
    total_revenue_plot = FA.plot_revenue(intrinsic_value_calculator.income_statement)
    eps_plot = FA.plot_eps(intrinsic_value_calculator.income_statement, intrinsic_value_calculator.balance_sheet)
    accounts_payable_plot = FA.plot_accounts_payable(intrinsic_value_calculator.balance_sheet)
    accounts_receivable_plot = FA.plot_accounts_receivable(intrinsic_value_calculator.balance_sheet)
    inventory_plot = FA.plot_inventory(intrinsic_value_calculator.balance_sheet)
    free_cash_flow_plot = FA.plot_free_cash_flow(intrinsic_value_calculator.cash_flow)
    growth_plots = FA.plot_growth_values(intrinsic_value_calculator.income_statement, intrinsic_value_calculator.balance_sheet)

    return jsonify({
        'symbol'                    : symbol,
        'intrinsic_value'           : intrinsic_value_per_share,
        'stock_price'               : intrinsic_value_calculator.current_price,
        'beta'                      : intrinsic_value_calculator.beta ,
        'total_revenue_plot'        : total_revenue_plot,
        'eps_plot'                  : eps_plot,
        'accounts_payable_plot'     : accounts_payable_plot,
        'accounts_receivable_plot'  : accounts_receivable_plot,
        'inventory_plot'            : inventory_plot,
        'free_cash_flow_plot'       : free_cash_flow_plot,
        'growth_plots'              : growth_plots
    })

@app.route('/bar', methods=['GET', 'POST'])
def change_features():

    feature = request.args['selected']
    graphJSON= create_plot(feature)

    return graphJSON

@app.route('/showLineChart')
def index1():
    bar = create_plot('Bar')
    return render_template('index1.html', plot=bar)

def create_plot(feature):
    if feature == 'Bar':
        N = 40
        x = np.linspace(0, 1, N)
        y = np.random.randn(N)
        df = pd.DataFrame({'x': x, 'y': y}) # creating a sample dataframe
        data = [
            go.Bar(
                x=df['x'], # assign x as the dataframe column 'x'
                y=df['y']
            )
        ]
    else:
        N = 1000
        random_x = np.random.randn(N)
        random_y = np.random.randn(N)

        # Create a trace
        data = [go.Scatter(
            x = random_x,
            y = random_y,
            mode = 'markers'
        )]


    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON