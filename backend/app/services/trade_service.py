import uuid
from decimal import Decimal
from datetime import datetime,timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException,status

from app.models.Coin import Coin
from app.models.Wallet import Wallet
from app.models.Holding import Holding
from app.models.Transaction import Transaction as transaction
from app.services.binance_listener import latest_prices

def _get_current_price(symbol:str,)->Decimal:
    ticker=latest_prices.get(symbol.upper())
    if not ticker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Current price for {symbol} not found"
        )
    return Decimal(ticker['price'])

async def _get_coin(db:AsyncSession,symbol:str)->Coin:
    query=select(Coin).where(Coin.symbol==symbol.upper())
    coin=(await db.execute(query)).scalar_one_or_none()
    if not coin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Coin with symbol {symbol} not found"
        )
    return coin

async def buy_coin(db:AsyncSession,user_id:uuid.UUID,symbol:str,quantity:Decimal)->dict:
    coin=await _get_coin(db,symbol)
    current_price=_get_current_price(symbol)
    total_cost=quantity*current_price

    query=select(Wallet).where(Wallet.user_id==user_id)
    wallet=(await db.execute(query)).scalar_one_or_none()
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found for the user"
        )
    
    if wallet.balance_usd<total_cost:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient balance to complete the purchase"
        )
    
    wallet.balance_usd-=total_cost
    await db.flush()

    query=select(Holding).where((Holding.user_id==user_id)&(Holding.coin_id==coin.id))
    holding=(await db.execute(query)).scalar_one_or_none()
    if holding:
        total_quantity=holding.quantity+quantity
        total_invested=holding.avg_buy_price*holding.quantity+total_cost
        holding.avg_buy_price=total_invested/total_quantity
        holding.quantity=total_quantity
        holding.updated_at=datetime.now(timezone.utc)
    else:
        new_holding=Holding(
            id=uuid.uuid4(),
            user_id=user_id,
            coin_id=coin.id,
            quantity=quantity,
            avg_buy_price=current_price,
            updated_at=datetime.now(timezone.utc)
        )
        db.add(new_holding)
    
    new_transaction=transaction(
        id=uuid.uuid4(),
        user_id=user_id,
        coin_id=coin.id,
        tx_type="buy",
        quantity=quantity,
        price_at_trade=current_price,
        total_value=total_cost,
        created_at=datetime.now(timezone.utc)
    )
    db.add(new_transaction)

    await db.commit()
    
    return {
        "symbol":symbol.upper(),
        "quantity":quantity,
        "tx_type":"buy",
        "price_at_decimal":current_price,
        "total_value":total_cost,
        "new_balance":wallet.balance_usd
    }

async def sell_coin(db:AsyncSession,user_id:uuid.UUID,symbol:str,quantity:Decimal):
    price=_get_current_price(symbol)
    coin=await _get_coin(db,symbol)
    total_cost=price*quantity

    query=select(Holding).where(Holding.user_id==user_id,Holding.coin_id==coin.id)
    holding=(await db.execute(query)).scalar_one_or_none()

    if not holding or holding.quantity<quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient holdings"
        )

    query=select(Wallet).where(Wallet.user_id==user_id)
    wallet=(await db.execute(query)).scalar_one_or_none()

    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )

    holding.quantity-=quantity
    holding.updated_at=datetime.now(timezone.utc)

    if holding.quantity==0:
        await db.delete(holding)

    wallet.balance_usd+=total_cost
    wallet.updated_at=datetime.now(timezone.utc)

    tx=transaction(
        id=uuid.uuid4(),
        user_id=user_id,
        coin_id=coin.id,    
        tx_type="sell",
        quantity=quantity,
        price_at_trade=price,
        total_value=total_cost,
        created_at=datetime.now(timezone.utc)
    )
    db.add(tx)
    await db.commit()
    
    return {"symbol":symbol.upper(),
            "quantity":quantity,
            "tx_type":"sell",
            "price_at_decimal":price,
            "total_value":total_cost,
            "new_balance":wallet.balance_usd

        }

async def get_portfolio(db:AsyncSession,user_id:uuid.UUID)->dict:
    query=select(Wallet).where(Wallet.user_id==user_id)
    wallet=(await db.execute(query)).scalar_one_or_none()

    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )

    query=select(Holding).where(Holding.user_id==user_id)
    holdings=(await db.execute(query)).scalars().all()

    total_holdings_value=Decimal(0)
    holding_responses=[]
    for holding in holdings:
        res=await db.execute(select(Coin).where(Coin.id==holding.coin_id))
        coin=res.scalar_one_or_none()
        if not coin:
            continue

        current_price=_get_current_price(coin.symbol)
        current_value=current_price*holding.quantity
        cost_basis=holding.avg_buy_price*holding.quantity
        pnl=current_value-cost_basis
        pnl_percent=(pnl/(cost_basis))*100 if cost_basis>0 else Decimal(0)

        total_holdings_value+=current_value

        holding_responses.append({
            "symbol":coin.symbol,
            "quantity":holding.quantity,
            "avg_buy_price":holding.avg_buy_price,
            "current_price":current_price,
            "current_value":current_value,
            "pnl":pnl,
            "pnl_percent":pnl_percent
        })

    total_portfolio_value=wallet.balance_usd+total_holdings_value

    return {
        "balance_usd":wallet.balance_usd,
        "total_holdings_value":total_holdings_value,
        "total_portfolio_value":total_portfolio_value,
        "holdings":holding_responses
    }