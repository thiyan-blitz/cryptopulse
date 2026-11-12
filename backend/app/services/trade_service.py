import uuid
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.Coin import Coin
from app.models.Holding import Holding
from app.models.Transaction import Transaction as transaction
from app.models.Wallet import Wallet
from app.services.binance_listener import latest_prices


def _get_current_price(symbol: str) -> Decimal:
    ticker = latest_prices.get(symbol.upper())
    if not ticker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Current price for {symbol} not found",
        )

    try:
        price = Decimal(str(ticker["price"]))
    except (KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Invalid market price for {symbol}",
        )

    if price <= 0:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Invalid market price for {symbol}",
        )

    return price


async def _get_coin(db: AsyncSession, symbol: str) -> Coin:
    query = select(Coin).where(Coin.symbol == symbol.upper())
    coin = (await db.execute(query)).scalar_one_or_none()

    if not coin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Coin with symbol {symbol} not found",
        )

    return coin


async def _get_locked_wallet(db: AsyncSession, user_id: uuid.UUID) -> Wallet:
    query = select(Wallet).where(Wallet.user_id == user_id).with_for_update()
    wallet = (await db.execute(query)).scalar_one_or_none()

    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found for the user",
        )

    return wallet


async def buy_coin(
    db: AsyncSession,
    user_id: uuid.UUID,
    symbol: str,
    quantity: Decimal,
) -> dict:
    if quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be greater than zero",
        )

    coin = await _get_coin(db, symbol)

    # Lock the wallet first. This serializes balance-changing operations
    # for the same user and prevents concurrent buys from overspending.
    wallet = await _get_locked_wallet(db, user_id)

    current_price = _get_current_price(symbol)
    total_cost = quantity * current_price

    if wallet.balance_usd < total_cost:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient balance to complete the purchase",
        )

    # The wallet lock above serializes creation/update of this user's holdings.
    holding_query = (
        select(Holding)
        .where(Holding.user_id == user_id, Holding.coin_id == coin.id)
        .with_for_update()
    )
    holding = (await db.execute(holding_query)).scalar_one_or_none()

    wallet.balance_usd -= total_cost
    wallet.updated_at = datetime.now(timezone.utc)

    if holding:
        total_quantity = holding.quantity + quantity
        total_invested = holding.avg_buy_price * holding.quantity + total_cost
        holding.avg_buy_price = total_invested / total_quantity
        holding.quantity = total_quantity
        holding.updated_at = datetime.now(timezone.utc)
    else:
        db.add(
            Holding(
                id=uuid.uuid4(),
                user_id=user_id,
                coin_id=coin.id,
                quantity=quantity,
                avg_buy_price=current_price,
                updated_at=datetime.now(timezone.utc),
            )
        )

    db.add(
        transaction(
            id=uuid.uuid4(),
            user_id=user_id,
            coin_id=coin.id,
            tx_type="buy",
            quantity=quantity,
            price_at_trade=current_price,
            total_value=total_cost,
            created_at=datetime.now(timezone.utc),
        )
    )

    await db.commit()

    return {
        "symbol": symbol.upper(),
        "quantity": quantity,
        "tx_type": "buy",
        "price_at_decimal": current_price,
        "total_value": total_cost,
        "new_balance": wallet.balance_usd,
    }


async def sell_coin(
    db: AsyncSession,
    user_id: uuid.UUID,
    symbol: str,
    quantity: Decimal,
) -> dict:
    if quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be greater than zero",
        )

    coin = await _get_coin(db, symbol)

    # Lock the wallet before reading/updating the holding. This makes
    # concurrent buy/sell operations for one user serialize consistently.
    wallet = await _get_locked_wallet(db, user_id)

    price = _get_current_price(symbol)
    total_value = price * quantity

    holding_query = (
        select(Holding)
        .where(Holding.user_id == user_id, Holding.coin_id == coin.id)
        .with_for_update()
    )
    holding = (await db.execute(holding_query)).scalar_one_or_none()

    if not holding or holding.quantity < quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient holdings",
        )

    holding.quantity -= quantity
    holding.updated_at = datetime.now(timezone.utc)

    if holding.quantity == 0:
        await db.delete(holding)

    wallet.balance_usd += total_value
    wallet.updated_at = datetime.now(timezone.utc)

    db.add(
        transaction(
            id=uuid.uuid4(),
            user_id=user_id,
            coin_id=coin.id,
            tx_type="sell",
            quantity=quantity,
            price_at_trade=price,
            total_value=total_value,
            created_at=datetime.now(timezone.utc),
        )
    )

    await db.commit()

    return {
        "symbol": symbol.upper(),
        "quantity": quantity,
        "tx_type": "sell",
        "price_at_decimal": price,
        "total_value": total_value,
        "new_balance": wallet.balance_usd,
    }


async def get_portfolio(db: AsyncSession, user_id: uuid.UUID) -> dict:
    wallet_query = select(Wallet).where(Wallet.user_id == user_id)
    wallet = (await db.execute(wallet_query)).scalar_one_or_none()

    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )

    holdings_query = (
        select(Holding, Coin)
        .join(Coin, Coin.id == Holding.coin_id)
        .where(Holding.user_id == user_id)
    )
    holdings = (await db.execute(holdings_query)).all()

    total_holdings_value = Decimal("0")
    holding_responses = []

    for holding, coin in holdings:
        current_price = _get_current_price(coin.symbol)
        current_value = current_price * holding.quantity
        cost_basis = holding.avg_buy_price * holding.quantity
        pnl = current_value - cost_basis
        pnl_percent = (pnl / cost_basis) * 100 if cost_basis > 0 else Decimal("0")

        total_holdings_value += current_value

        holding_responses.append(
            {
                "symbol": coin.symbol,
                "quantity": holding.quantity,
                "avg_buy_price": holding.avg_buy_price,
                "current_price": current_price,
                "current_value": current_value,
                "pnl": pnl,
                "pnl_percent": pnl_percent,
            }
        )

    total_portfolio_value = wallet.balance_usd + total_holdings_value

    return {
        "balance_usd": wallet.balance_usd,
        "total_holdings_value": total_holdings_value,
        "total_portfolio_value": total_portfolio_value,
        "holdings": holding_responses,
    }
