import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.Coin import Coin
from app.models.PriceHistory import PriceHistory

async def _get_candles(db:AsyncSession,symbol:str,interval:str,limit:int=100):
    result=await db.execute(select(Coin).where(Coin.symbol==symbol.upper()))

    coin=result.scalar_one_or_none()
    if not coin:
        raise HTTPException (status_code=404,detail=f"Coin {symbol} not found")

    result=await db.execute(
        select(PriceHistory).where(PriceHistory.coin_id==coin.id,PriceHistory.interval==interval)
        .order_by(PriceHistory.ts.asc())
        .limit(limit)
    )
    return result.scalars().all()

def calculate_sma(closes:list[Decimal],period:int)->list[Decimal|None]:
    sma=[]
    for i in range(len(closes)):
        if i <period-1:
            sma.append(None)
        else:
            window=closes[i-period+1:i+1]
            sma.append(sum(window)/period)

    return sma

def calculate_rsi(closes:list[Decimal],period:int=14)->list[Decimal|None]:
    rsi=[None]*len(closes)
    if len(closes)<period+1:
        return rsi

    gains,losses=[],[]
    for i in range(1,len(closes)):
        change=closes[i]-closes[i-1]
        gains.append(max(change,Decimal("0")))
        losses.append(max(-change,Decimal("0")))


    avg_gain=sum(gains[:period])/period
    avg_loss=sum(losses[:period])/period

    for i in range(period,len(closes)):
        if i>period:
            avg_gain=(avg_gain*(period-1)+gains[i-1])/period
            avg_loss=(avg_loss*(period-1)+losses[i-1])/period

        if avg_loss==0:
            rsi[i]=Decimal("100")
        else:
            rs=avg_gain/avg_loss
            rsi[i]=Decimal("100")-(Decimal("100")/(1+rs))

    return rsi

async def get_analytics(db:AsyncSession,symbol:str,interval:str="1h"):
    candles=await _get_candles(db,symbol,interval)
    if not candles:
        raise HTTPException(status_code=404,detail="No price history found")

    closes=[c.close for c in candles]
    sma_20=calculate_sma(closes,20)
    rsi_14=calculate_rsi(closes,14)

    return  {
        "symbol":symbol.upper(),
        "interval":interval,
        "candles":[
            {
                "ts": c.ts.isoformat(),
                "open": c.open,
                "high": c.high,
                "low": c.low,
                "close": c.close,
                "volume": c.volume,
                "sma_20": sma_20[i],
                "rsi_14": rsi_14[i],
            }
            for i,c in enumerate(candles)
        ],
    }