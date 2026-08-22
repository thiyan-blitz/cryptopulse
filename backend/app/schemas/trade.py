from pydantic import BaseModel, Field
from decimal import Decimal
import uuid

class TradeRequest(BaseModel):
    symbol:str=Field(...,description="The symbol of the cryptocurrency to trade, e.g., BTC, ETH")
    quantity:Decimal=Field(...,gt=0)

class TradeResponse(BaseModel):
    symbol:str
    quantity:Decimal
    tx_type:str
    price_at_decimal:Decimal
    total_value:Decimal
    new_balance:Decimal

class HoldingResponse(BaseModel):
    symbol:str
    quantity:Decimal
    avg_buy_price:Decimal
    current_price:Decimal
    current_value:Decimal
    pnl:Decimal
    pnl_percent:Decimal

class PortfolioResponse(BaseModel):
    balance_usd:Decimal
    total_holdings_value:Decimal
    total_portfolio_value:Decimal
    holdings:list[HoldingResponse]

