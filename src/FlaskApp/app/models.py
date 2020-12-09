from app import db
import datetime
from sqlalchemy.dialects.postgresql import JSON
import sqlalchemy

class Report(db.Model):
    symbol = db.Column(db.String(128), primary_key =True)
    overview = db.Column(JSON)
    income_statement = db.Column(JSON)
    balance_sheet = db.Column(JSON)
    cash_flow = db.Column(JSON)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)


    def __repr__(self):
        overview_status = 'NotSet' if self.overview is None else 'Set'
        income_statement_status = 'NotSet' if self.income_statement is None else 'Set'
        balance_sheet_status = 'NotSet' if self.balance_sheet is None else 'Set'
        cash_flow_status = 'NotSet' if self.cash_flow is None else 'Set'
        return '<Symbol {}, create at {}, overview is {}, income statement is {}, balancesheet is {}, cash flow is {}>'\
        .format(self.symbol, self.created_date.strftime('%Y-%m-%d'),overview_status, income_statement_status, balance_sheet_status,cash_flow_status)    
