from fastapi import APIRouter,Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.models.User import User
from app.auth.dependencies import get_current_user
from app.schemas.trade import TradeRequest,TradeResponse,PortfolioResponse
from app.services.trade_service import buy_coin,sell_coin,get_portfolio
from app.services.tx_service import get_transactions_with_filters
from app.schemas.transaction import TransactionFilter
from app.schemas.transaction import TransactionResponse

router=APIRouter(prefix="/trade",tags=["Trade"])

@router.post("/buy",response_model=TradeResponse)
async def buy_trade(body:TradeRequest,db:AsyncSession=Depends(get_db),current_user:User=Depends(get_current_user)):
     return await buy_coin(db,current_user.id,body.symbol,body.quantity)

@router.post("/sell",response_model=TradeResponse)
async def sell_trade(body:TradeRequest,db:AsyncSession=Depends(get_db),current_user:User=Depends(get_current_user)):
    return await sell_coin(db,current_user.id,body.symbol,body.quantity)

@router.get("/portfolio",response_model=PortfolioResponse)
async def get_user_portfolio(db:AsyncSession=Depends(get_db),current_user:User=Depends(get_current_user)):
    return await get_portfolio(db,current_user.id)  

@router.get("/transactions",response_model=list[TransactionResponse])
async def get_user_transactions(db:AsyncSession=Depends(get_db),current_user:User=Depends(get_current_user),filters:TransactionFilter=Depends()):
    return await get_transactions_with_filters(db,current_user.id,filters)