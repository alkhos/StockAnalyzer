from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms import validators
from wtforms.fields.core import IntegerField
from wtforms.validators import DataRequired

class StockInputForm(FlaskForm):
    ticker = StringField('Stock Ticker', validators=[DataRequired()])
    growth_rate = IntegerField('Desired Growth Rate', validators=[validators.Optional(), validators.NumberRange(min=0)])
    submit = SubmitField('Submit')