from FinancialsAlpha import plot_free_cash_flow
from IntrinsicValue import InrinsicValue

api_key = "bv2np9n48v6ubfuli2a0"
alpha_api_key = "J579CA8H9XAI3MEY"
symbol = "NVDA"

# # overview 
# document_type = FinancialsAlpha.DocumentType.OVERVIEW
# overview = FinancialsAlpha.get_financial_statement(symbol, document_type, alpha_api_key)
# FinancialsAlpha.save_as_json(overview, document_type)

# # income statement 
# document_type = FinancialsAlpha.DocumentType.INCOME_STATEMENT
# income_statement = FinancialsAlpha.get_financial_statement(symbol, document_type, alpha_api_key)
# FinancialsAlpha.save_as_json(income_statement, document_type)

# # balance sheet
# document_type = FinancialsAlpha.DocumentType.BALANCE_SHEET
# balance_sheet = FinancialsAlpha.get_financial_statement(symbol, document_type, alpha_api_key)
# FinancialsAlpha.save_as_json(balance_sheet, document_type)

# # cashflow 
# document_type = FinancialsAlpha.DocumentType.CASH_FLOW
# cash_flow = FinancialsAlpha.get_financial_statement(symbol, document_type, alpha_api_key)
# FinancialsAlpha.save_as_json(cash_flow, document_type)


intrinsic_value_calculator = InrinsicValue(symbol, use_file=True)
intrinsic_value_calculator.growth_rate = 15
#intrinsic_value_per_share = intrinsic_value_calculator.get_intrinsic_value_per_share()
#print(intrinsic_value_per_share)
plot_free_cash_flow(intrinsic_value_calculator.cash_flow)