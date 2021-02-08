import IntrinsicValue.FinancialsAlpha as FinancialsAlpha
import IntrinsicValue.Investing as Investing
import IntrinsicValue.WorldBank as WorldBank
import IntrinsicValue.YahooFinance as YahooFinance
import plotly.graph_objects as go
import plotly
import datetime
import json

class InrinsicValue:
    """Intrinsic value and other stock data calculator class

    Returns:
        IntrinsicValue: Class object with all the company data
    """
    alpha_api_key = "J579CA8H9XAI3MEY"

    # Initialize from symbol
    def __init__(self, symbol):
        """Constructor
        Args:
            symbol (str): stock ticker symbol
        """
        self.symbol = symbol

    def get_financial_statements_externally(self):
        """Get financial statements from external sources. Free API is limited to 5 calls per minute
        """
        # overview 
        document_type = FinancialsAlpha.DocumentType.OVERVIEW
        self.overview = FinancialsAlpha.get_financial_statement(self.symbol, document_type, self.alpha_api_key, use_file=False)
        # FinancialsAlpha.save_as_json(self.overview, document_type)

        # income statement 
        document_type = FinancialsAlpha.DocumentType.INCOME_STATEMENT
        self.income_statement = FinancialsAlpha.get_financial_statement(self.symbol, document_type, self.alpha_api_key, use_file=False)
        # FinancialsAlpha.save_as_json(self.income_statement, document_type)

        # balance sheet
        document_type = FinancialsAlpha.DocumentType.BALANCE_SHEET
        self.balance_sheet = FinancialsAlpha.get_financial_statement(self.symbol, document_type, self.alpha_api_key, use_file=False)
        # FinancialsAlpha.save_as_json(self.balance_sheet, document_type)

        # cashflow 
        document_type = FinancialsAlpha.DocumentType.CASH_FLOW
        self.cash_flow = FinancialsAlpha.get_financial_statement(self.symbol, document_type, self.alpha_api_key, use_file=False)
        # FinancialsAlpha.save_as_json(self.cash_flow, document_type)

        # get other values
        self.get_constructor_values()

    # initialize from financial statements
    def set_financial_statements(self, overview, income_statement, balance_sheet, cash_flow):
        """Get financial statements from provided data

        Args:
            overview (json): Company overview in JSON form
            income_statement (json): Income statement in JSON form
            balance_sheet (json): Balance Sheet in JSON form
            cash_flow (json): Cash flow in JSON form
        """
        # overview 
        self.overview = overview

        # income statement 
        self.income_statement = income_statement

        # balance sheet
        self.balance_sheet = balance_sheet

        # cashflow 
        self.cash_flow = cash_flow

        # get other values
        self.get_constructor_values()
    
    def get_constructor_values(self):
        """Set the other values that the class needs
        """
        # free cash flow
        self.free_cashflow_ttm = FinancialsAlpha.get_free_cashflow_ttm(self.cash_flow)

        # shares outstanding
        self.shares_outstanding = FinancialsAlpha.get_metadata_item(self.overview, 'SharesOutstanding')

        # current price
        # self.current_price = FinancialsAlpha.get_current_price(symbol, self.alpha_api_key)
        self.current_price = YahooFinance.get_current_price(self.symbol)

        # growth rate
        self.growth_rate = FinancialsAlpha.get_growth_rate(self.symbol, self.overview, self.current_price)

        # Beta
        self.beta = FinancialsAlpha.get_metadata_item(self.overview, 'Beta')

        # risk free rate
        self.risk_free_rate = Investing.get_risk_free_rate()

        # market risk premium 
        self.market_risk_premium = 5.33

        # business tax rate 
        self.business_tax_rate = FinancialsAlpha.get_business_tax_rate(self.income_statement)

        # Interest Rate
        self.interest_rate = FinancialsAlpha.get_interest_rate(self.balance_sheet, self.income_statement)

        # Long-Term Interest Rate
        self.long_term_interest_rate = FinancialsAlpha.get_long_term_interest_rate(self.balance_sheet, self.income_statement)

        # Market Capitalization ( Market Value of Equity)
        self.market_value_of_equity = FinancialsAlpha.get_metadata_item(self.overview, 'MarketCapitalization')

        # Market value of debt
        self.market_value_of_debt = FinancialsAlpha.get_market_value_of_debt(self.balance_sheet)

        # Total Liabilities
        self.total_liabilities = FinancialsAlpha.get_financial_statement_record(self.balance_sheet, 'totalLiabilities')
        
        # Cash and Cash Equivalents
        self.cash = FinancialsAlpha.get_financial_statement_record(self.balance_sheet, 'cash')

        # gdp growth rate
        self.gdp_growth_rate = WorldBank.get_us_gdp_growth_rate()

        # Dicsount Rate 
        self.discount_rate = self.get_weighted_average_cost_of_capital()


    def get_weighted_average_cost_of_capital(self):
        """Compute the weighted average cost of capital

        Returns:
            float: weighted average cost of capital
        """
        r_e = (self.risk_free_rate + self.beta * self.market_risk_premium) / 100
        r_d = (self.interest_rate / 100)* (1 - self.business_tax_rate / 100) 
        wacc = ((self.market_value_of_equity * r_e) +(self.market_value_of_debt * r_d))/ (self.market_value_of_equity + self.market_value_of_debt) 
        return wacc

    def get_discounted_cash_flow(self):
        """Get discounted cash flow

        Returns:
            list: discounted cash flow as a list
        """
        discounted_cash_flow = []
        growth_factor = 1 + self.growth_rate / 100
        projected_free_cash_flow = self.free_cashflow_ttm
        for i in range(1,11):
            projected_free_cash_flow = projected_free_cash_flow * growth_factor
            discount_factor = 1 / pow(1 + self.discount_rate, i)
            discounted_cash_flow.append(projected_free_cash_flow*discount_factor)
        return discounted_cash_flow

    def get_perpetuity_value(self):
        """Get perpetuity value

        Returns:
            float: perpetuity value of the company
        """
        growth_factor = 1 + self.growth_rate / 100
        final_year_projected_free_cash_flow = self.free_cashflow_ttm * pow(growth_factor, 10)
        perpetuity_growth_rate = self.gdp_growth_rate / 100
        perpetuity_growth_factor = 1 + perpetuity_growth_rate
        perpetuity_value = (final_year_projected_free_cash_flow * perpetuity_growth_factor) / (self.discount_rate - perpetuity_growth_rate)
        return perpetuity_value

    def get_terminal_value(self):
        """Get the terminal value for the company based on perpetuity value

        Returns:
            float: terminal value
        """
        discount_factor = 1 / pow(1 + self.discount_rate, 10)
        return self.get_perpetuity_value() * discount_factor

    def get_intrinsic_value_per_share(self):
        """Get intrinsic value per share

        Returns:
            float: Intrinsic value per share
        """
        intrinsic_value = (sum(self.get_discounted_cash_flow()) + self.get_terminal_value() + self.cash - self.total_liabilities) / self.shares_outstanding
        return round(intrinsic_value, 2)

    def set_stock_price_at_annaul_reporting_dates(self):
        """Get the values of stock at annual report dates
        """
        self.annual_stock_prices = {}
        for record in self.balance_sheet['annualReports']:
            date_str = record['fiscalDateEnding']
            stock_price = YahooFinance.get_price_on_date(self.symbol, date_str)
            self.annual_stock_prices[date_str] = stock_price
    
    def set_stock_price_at_quarterly_reporting_dates(self):
        """Get the values of stock at quarterly report dates
        """
        self.quarterlyl_stock_prices = {}
        for record in self.balance_sheet['quarterlyReports']:
            date_str = record['fiscalDateEnding']
            stock_price = YahooFinance.get_price_on_date(self.symbol, date_str)
            self.quarterlyl_stock_prices[date_str] = stock_price
    
    #################### PLOTTERS #################################
    def plot_free_cash_flow(self):
        """Plot Free Cashflow

        Returns:
            json: Free cash flow vs time as a plotly json
        """
        free_cash_flows = {}
        for record in self.cash_flow['annualReports']:
            datetime_object = datetime.datetime.strptime(record['fiscalDateEnding'], '%Y-%m-%d')
            free_cash_flow = int(record['operatingCashflow']) - int(record['capitalExpenditures'])
            free_cash_flows[datetime_object] = free_cash_flow / 1e6

        # add TTM
        datetime_object = datetime.datetime.now()
        free_cash_flow_ttm = FinancialsAlpha.get_free_cashflow_ttm(self.cash_flow)
        free_cash_flows[datetime_object] = free_cash_flow_ttm / 1e6

        # using plotly
        return FinancialsAlpha.produce_plotly_time_series(free_cash_flows, self.symbol, 'Free Cash Flow')

    def get_revenue_values(self):
        """get revenue values

        Returns:
            dict: a time dictionary of revenue values 
        """
        self.revenue_annual_list = {}
        for record in self.income_statement['annualReports']:
            datetime_object = datetime.datetime.strptime(record['fiscalDateEnding'], '%Y-%m-%d')
            total_revenue = int(record['totalRevenue'])
            self.revenue_annual_list[datetime_object] = total_revenue / 1e6

        # add TTM
        datetime_object = datetime.datetime.now()
        total_revenue_ttm = FinancialsAlpha.get_financial_statement_record_ttm(self.income_statement, 'totalRevenue')
        self.revenue_annual_list[datetime_object] = total_revenue_ttm / 1e6

        # quarterly 
        self.revenue_quarterly_list = {}

        for record in self.income_statement['quarterlyReports']:
            datetime_object = datetime.datetime.strptime(record['fiscalDateEnding'], '%Y-%m-%d')
            year = datetime_object.year
            month = datetime_object.month
            total_revenue = int(record['totalRevenue'])
            
            # great year dictionary if needed
            if year not in self.revenue_quarterly_list:
                self.revenue_quarterly_list[year] = {}
            
            quarter = self.get_quarter_from_month(month)
            self.revenue_quarterly_list[year][quarter] = total_revenue

    def plot_revenue(self):
        """Plot Revenue

        Returns:
            json: Revenue vs time as a plotly json
        """
        # set revenue list
        if not hasattr(self, 'revenue_annual_list'):
            self.get_revenue_values()
        
        # using plotly
        return FinancialsAlpha.produce_plotly_time_series(self.revenue_annual_list, self.symbol, 'Total Revenue')

    def plot_days_payable_outstanding(self):
        """Plot days payable outstanding using ending payables

        Returns:
            json: days payable outstanding vs time as a plotly json
        """
        days_payable_outstanding = {}
        for record in self.balance_sheet['annualReports']:
            datetime_object = datetime.datetime.strptime(record['fiscalDateEnding'], '%Y-%m-%d')
            days_payable_outstanding[datetime_object] = FinancialsAlpha.get_numeric_record(record, 'accountsPayable', 'int') 

        for record in self.income_statement['annualReports']:
            datetime_object = datetime.datetime.strptime(record['fiscalDateEnding'], '%Y-%m-%d')
            cost_of_revenue = int(record['costOfRevenue'])
            days_payable_outstanding[datetime_object] = 365* (days_payable_outstanding[datetime_object] / cost_of_revenue)

        # add TTM
        datetime_object = datetime.datetime.now()
        accounts_payable_ttm = FinancialsAlpha.get_financial_statement_record(self.balance_sheet, 'accountsPayable')
        cost_of_revenue_ttm = FinancialsAlpha.get_financial_statement_record_ttm(self.income_statement, 'costOfRevenue')
        if accounts_payable_ttm != 0:
            days_payable_outstanding[datetime_object] = 365* (accounts_payable_ttm / cost_of_revenue_ttm)

        # using plotly
        return FinancialsAlpha.produce_plotly_time_series(days_payable_outstanding, self.symbol, 'Days Payable Outstanding')

    def plot_days_sales_outstanding(self):
        """Plot days sale outstanding

        Returns:
            json: days sale outstanding vs time as a plotly json
        """
        days_sale_outstanding = {}
        for record in self.balance_sheet['annualReports']:
            datetime_object = datetime.datetime.strptime(record['fiscalDateEnding'], '%Y-%m-%d')
            days_sale_outstanding[datetime_object] = FinancialsAlpha.get_numeric_record(record, 'netReceivables', 'int') 

        for record in self.income_statement['annualReports']:
            datetime_object = datetime.datetime.strptime(record['fiscalDateEnding'], '%Y-%m-%d')
            total_revenue = int(record['totalRevenue'])
            days_sale_outstanding[datetime_object] = 365*(days_sale_outstanding[datetime_object] / total_revenue)

        # add TTM
        datetime_object = datetime.datetime.now()
        accounts_receivable_ttm = FinancialsAlpha.get_financial_statement_record(self.balance_sheet, 'netReceivables')
        total_revenue_ttm = FinancialsAlpha.get_financial_statement_record_ttm(self.income_statement, 'totalRevenue')
        if accounts_receivable_ttm != 0:
            days_sale_outstanding[datetime_object] = 365*(accounts_receivable_ttm / total_revenue_ttm)

        # using plotly
        return FinancialsAlpha.produce_plotly_time_series(days_sale_outstanding, self.symbol, 'Days Sale Outstanding')

    def plot_days_sale_of_inventory(self):
        """Plot days sale of inventory

        Returns:
            json: days sale of inventory vs time as a plotly json
        """
        days_sale_of_inventory = {}
        for record in self.balance_sheet['annualReports']:
            datetime_object = datetime.datetime.strptime(record['fiscalDateEnding'], '%Y-%m-%d')
            days_sale_of_inventory[datetime_object] = FinancialsAlpha.get_numeric_record(record, 'inventory', 'int')

        for record in self.income_statement['annualReports']:
            datetime_object = datetime.datetime.strptime(record['fiscalDateEnding'], '%Y-%m-%d')
            cost_of_revenue = FinancialsAlpha.get_numeric_record(record, 'costOfRevenue', 'int')
            days_sale_of_inventory[datetime_object] = 365 * (days_sale_of_inventory[datetime_object] / cost_of_revenue)

        # add TTM
        datetime_object = datetime.datetime.now()
        inventory_ttm = FinancialsAlpha.get_financial_statement_record(self.balance_sheet, 'inventory')
        cost_of_revenue_ttm = FinancialsAlpha.get_financial_statement_record_ttm(self.income_statement, 'costOfRevenue')
        if inventory_ttm != 0:
            days_sale_of_inventory[datetime_object] = 365 * (inventory_ttm / cost_of_revenue_ttm)

        # using plotly
        return FinancialsAlpha.produce_plotly_time_series(days_sale_of_inventory, self.symbol, 'Days Sale of Inventory')

    def get_eps_values(self):
        """get EPS values for each year and each quarter

        Returns:
            dict: a time dictionary of EPS values 
        """
        self.eps_annual_list = {}

        for record in self.income_statement['annualReports']:
            datetime_object = datetime.datetime.strptime(record['fiscalDateEnding'], '%Y-%m-%d')
            total_income = int(record['netIncomeApplicableToCommonShares'])
            self.eps_annual_list[datetime_object] = total_income

        for record in self.balance_sheet['annualReports']:
            datetime_object = datetime.datetime.strptime(record['fiscalDateEnding'], '%Y-%m-%d')
            if datetime_object in self.eps_annual_list:
                total_income = self.eps_annual_list[datetime_object]
                if record['commonStockSharesOutstanding'] == 'None':
                    continue
                total_shares = int(record['commonStockSharesOutstanding'])
                self.eps_annual_list[datetime_object] = total_income / total_shares

        # add TTM
        datetime_object = datetime.datetime.now()
        total_income_ttm = FinancialsAlpha.get_financial_statement_record_ttm(self.income_statement, 'netIncomeApplicableToCommonShares')
        total_shares = FinancialsAlpha.get_financial_statement_record(self.balance_sheet, 'commonStockSharesOutstanding', find_latest_existing=True)
        self.eps_annual_list[datetime_object] = total_income_ttm / total_shares

        # quarterly
        self.eps_quarterly_list = {}
        quarterly_shares = {}
        quarterly_income = {}

        # get income
        for record in self.income_statement['quarterlyReports']:
            datetime_object = datetime.datetime.strptime(record['fiscalDateEnding'], '%Y-%m-%d')
            year = datetime_object.year
            month = datetime_object.month
            total_income = int(record['netIncomeApplicableToCommonShares'])
            
            # great year dictionary if needed
            if year not in quarterly_income:
                quarterly_income[year] = {}
            
            quarter = self.get_quarter_from_month(month)
            quarterly_income[year][quarter] = total_income

        # get number of shares
        for record in self.balance_sheet['quarterlyReports']:
            datetime_object = datetime.datetime.strptime(record['fiscalDateEnding'], '%Y-%m-%d')
            year = datetime_object.year
            month = datetime_object.month
            if record['commonStockSharesOutstanding'] == 'None':
                continue
            total_shares = int(record['commonStockSharesOutstanding'])
            
            # great year dictionary if needed
            if year not in quarterly_shares:
                quarterly_shares[year] = {}
            
            quarter = self.get_quarter_from_month(month)
            quarterly_shares[year][quarter] = total_shares

        # calculate EPS
        for year in quarterly_income:
            if year not in quarterly_shares:
                continue
            if year not in self.eps_quarterly_list:
                self.eps_quarterly_list[year] = {}
            for quarter in quarterly_income[year]:
                if quarter not in quarterly_shares[year]:
                    continue
                self.eps_quarterly_list[year][quarter] = quarterly_income[year][quarter] / quarterly_shares[year][quarter]

    def get_quarter_from_month(self, month):
        if 1 <= month <= 3:
            quarter = 'Q2'
        elif 4 <= month <= 6:
            quarter = 'Q3'
        elif 7 <= month <= 9:
            quarter = 'Q4'
        else:
            quarter = 'Q1'

        return quarter

    def get_date_from_quarter(self, year, quarter):
        if quarter == 'Q2':
            date_object = datetime.datetime(year, 1, 1)
        if quarter == 'Q3':
            date_object = datetime.datetime(year, 4, 1)
        if quarter == 'Q4':
            date_object = datetime.datetime(year, 7, 1)
        else:
            date_object = datetime.datetime(year, 10, 1)

        return date_object

    def plot_eps(self):
        """Plot EPS

        Returns:
            json: EPS vs time as a plotly json
        """
        # set EPS list
        if not hasattr(self, 'eps_annual_list'):
            self.get_eps_values()

        # using plotly
        return FinancialsAlpha.produce_plotly_time_series(self.eps_annual_list, self.symbol, 'Earnings per Share')

    def plot_annual_growth_values(self):
        """Plot % growth for EPS and revenue

        Returns:
            json: EPS and revenue growth as a plotyly json
        """
        revenue_growth = {}
        eps_growth = {}

        # revenue growth
        prev_value = None
        for record in sorted(self.revenue_annual_list.keys()):
            if prev_value is None:
                prev_value = self.revenue_annual_list[record]
                continue
            if self.revenue_annual_list[record] != 0:
                revenue_growth[record] = 100*(self.revenue_annual_list[record] - prev_value)/self.revenue_annual_list[record]
            else:
                revenue_growth[record] = 0
            prev_value = self.revenue_annual_list[record]

        # eps growth
        prev_value = None
        for record in sorted(self.eps_annual_list.keys()):
            if prev_value is None:
                prev_value = self.eps_annual_list[record]
                continue
            if self.eps_annual_list[record] != 0:
                eps_growth[record] = 100*(self.eps_annual_list[record] - prev_value)/self.eps_annual_list[record]
            else:
                eps_growth[record] = 0
            prev_value = self.eps_annual_list[record]
        
        # using plotly
        trace = []
        date_str,growth = zip(*sorted(revenue_growth.items()))
        trace.append(go.Bar(x=date_str, y=growth, name='Revenue Growth (%)', \
            hovertemplate='Year: %{x}: <br>Revenue Growth: %{y}'))
        date_str,growth = zip(*sorted(eps_growth.items()))
        trace.append(go.Bar(x=date_str, y=growth, name='EPS Growth (%)', \
            hovertemplate='Year: %{x}: <br>EPS Growth: %{y}'))

        layout = go.Layout(
            title={'text': 'Revenu and EPS growth in %'},
            xaxis={'title': 'Year'},
            yaxis={'title': 'Growth %'},
            hovermode='closest',
        )

        figure = go.Figure(data=trace, layout=layout)
        graph_json = json.dumps(figure, cls= plotly.utils.PlotlyJSONEncoder)

        return graph_json

    def plot_quarterly_growth_values(self):
        """Plot % growth for EPS and revenue comparing with last year's quarter

        Returns:
            json: EPS and revenue growth as a plotyly json
        """
        revenue_growth = {}
        eps_growth = {}

        # revenue growth
        for year in sorted(self.revenue_quarterly_list.keys()):
            for quarter in self.revenue_quarterly_list[year]:
                current_value = self.revenue_quarterly_list[year][quarter]
                prev_year = year - 1
                if prev_year not in self.revenue_quarterly_list:
                    continue
                if quarter not in self.revenue_quarterly_list[prev_year]:
                    continue
                prev_value = self.revenue_quarterly_list[prev_year][quarter]
                date_object = self.get_date_from_quarter(year, quarter)                   
                if prev_value != 0:
                    revenue_growth[date_object] = 100*(current_value - prev_value)/prev_value
                else:
                    revenue_growth[date_object] = 0

        # eps growth
        for year in sorted(self.eps_quarterly_list.keys()):
            prev_year = year - 1
            if prev_year not in self.eps_quarterly_list:
                continue
            for quarter in self.eps_quarterly_list[year]:
                current_value = self.eps_quarterly_list[year][quarter]
                if quarter not in self.eps_quarterly_list[prev_year]:
                    continue
                prev_value = self.eps_quarterly_list[prev_year][quarter]
                date_object = self.get_date_from_quarter(year, quarter)
                if prev_value != 0:
                    eps_growth[date_object] = 100*(current_value - prev_value)/prev_value
                else:
                    eps_growth[date_object] = 0
        
        # using plotly
        trace = []
        date_str,growth = zip(*sorted(revenue_growth.items()))
        trace.append(go.Bar(x=date_str, y=growth, name='Revenue Growth (%)', \
            hovertemplate='Year: %{x}: <br>Revenue Growth: %{y}'))
        date_str,growth = zip(*sorted(eps_growth.items()))
        trace.append(go.Bar(x=date_str, y=growth, name='EPS Growth (%)', \
            hovertemplate='Year: %{x}: <br>EPS Growth: %{y}'))

        layout = go.Layout(
            title={'text': 'Revenu and EPS growth in %'},
            xaxis={'title': 'Year'},
            yaxis={'title': 'Growth %'},
            hovermode='closest',
        )

        figure = go.Figure(data=trace, layout=layout)
        graph_json = json.dumps(figure, cls= plotly.utils.PlotlyJSONEncoder)

        return graph_json




    

    

            


