from typing import Optional
from pydantic import BaseModel,ConfigDict
import uuid
from datetime import datetime

class TransactionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    coin_id: uuid.UUID
    symbol:str
    tx_type: str
    quantity: float
    price_at_trade: float
    total_value: float
    created_at:datetime

class TransactionFilter(BaseModel):
    coin_id:Optional[uuid.UUID]=None
    tx_type:Optional[str]=None
    time_range:Optional[str]=None
    sort_by:Optional[str]='created_at'
    sort_order:Optional[str]='desc'

