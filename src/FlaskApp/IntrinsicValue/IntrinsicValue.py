import IntrinsicValue.FinancialsAlpha as FinancialsAlpha
import IntrinsicValue.Investing as Investing
import IntrinsicValue.WorldBank as WorldBank
import IntrinsicValue.YahooFinance as YahooFinance

class InrinsicValue:
    alpha_api_key = "J579CA8H9XAI3MEY"

    # Initialize from symbol
    def __init__(self, symbol):
        self.symbol = symbol

    def get_financial_statements_externally(self):
        # overview 
        document_type = FinancialsAlpha.DocumentType.OVERVIEW
        self.overview = FinancialsAlpha.get_financial_statement(self.symbol, document_type, self.alpha_api_key, use_file=False)
        # FinancialsAlpha.save_as_json(overview, document_type)

        # income statement 
        document_type = FinancialsAlpha.DocumentType.INCOME_STATEMENT
        self.income_statement = FinancialsAlpha.get_financial_statement(self.symbol, document_type, self.alpha_api_key, use_file=False)
        # FinancialsAlpha.save_as_json(income_statement, document_type)

        # balance sheet
        document_type = FinancialsAlpha.DocumentType.BALANCE_SHEET
        self.balance_sheet = FinancialsAlpha.get_financial_statement(self.symbol, document_type, self.alpha_api_key, use_file=False)
        # FinancialsAlpha.save_as_json(balance_sheet, document_type)

        # cashflow 
        document_type = FinancialsAlpha.DocumentType.CASH_FLOW
        self.cash_flow = FinancialsAlpha.get_financial_statement(self.symbol, document_type, self.alpha_api_key, use_file=False)
        # FinancialsAlpha.save_as_json(cash_flow, document_type)

        # get other values
        self.get_constructor_values()

    # initialize from financial statements
    def set_financial_statements(self, overview, income_statement, balance_sheet, cash_flow):
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
        r_e = (self.risk_free_rate + self.beta * self.market_risk_premium) / 100
        r_d = (self.interest_rate / 100)* (1 - self.business_tax_rate / 100) 
        wacc = ((self.market_value_of_equity * r_e) +(self.market_value_of_debt * r_d))/ (self.market_value_of_equity + self.market_value_of_debt) 
        return wacc

    def get_discounted_cash_flow(self):
        discounted_cash_flow = []
        growth_factor = 1 + self.growth_rate / 100
        projected_free_cash_flow = self.free_cashflow_ttm
        for i in range(1,11):
            projected_free_cash_flow = projected_free_cash_flow * growth_factor
            discount_factor = 1 / pow(1 + self.discount_rate, i)
            discounted_cash_flow.append(projected_free_cash_flow*discount_factor)
        return discounted_cash_flow

    def get_perpetuity_value(self):
        growth_factor = 1 + self.growth_rate / 100
        final_year_projected_free_cash_flow = self.free_cashflow_ttm * pow(growth_factor, 10)
        perpetuity_growth_rate = self.gdp_growth_rate / 100
        perpetuity_growth_factor = 1 + perpetuity_growth_rate
        perpetuity_value = (final_year_projected_free_cash_flow * perpetuity_growth_factor) / (self.discount_rate - perpetuity_growth_rate)
        return perpetuity_value

    def get_terminal_value(self):
        discount_factor = 1 / pow(1 + self.discount_rate, 10)
        return self.get_perpetuity_value() * discount_factor

    def get_intrinsic_value_per_share(self):
        intrinsic_value = (sum(self.get_discounted_cash_flow()) + self.get_terminal_value() + self.cash - self.total_liabilities) / self.shares_outstanding
        return round(intrinsic_value, 2)

    

    

            


