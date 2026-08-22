from pydantic import BaseModel
from decimal import Decimal
from typing import Optional

class CandleData(BaseModel):
    ts:str
    open:Decimal
    high:Decimal
    low:Decimal
    close:Decimal
    volume:Decimal
    sma_20:Optional[Decimal]=None
    rsi_14:Optional[Decimal]=None

class AnalyticsResponse(BaseModel):
    symbol:str
    interval:str
    candles:list[CandleData]

