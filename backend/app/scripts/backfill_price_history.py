import asyncio
import uuid
from datetime import datetime,timezone

import httpx
from sqlalchemy import select

from app.database.database import AsyncSessionLocal
from app.models.Coin import Coin
from app.models.PriceHistory import PriceHistory
from app.scripts.coins_seed import COINS_SEED

BINANCE_KLINES_URL = "https://api.binance.com/api/v3/klines"
INTERVAL = "1h"
LIMIT = 500

# Increase timeout and define a reusable client setup
TIMEOUT = httpx.Timeout(30.0, connect=10.0)


async def fetch_klines(
    client: httpx.AsyncClient,
    symbol: str,
    interval: str = INTERVAL,
    limit: int = LIMIT,
    retries: int = 3,
):
    params = {"symbol": symbol, "interval": interval, "limit": limit}

    for attempt in range(1, retries + 1):
        try:
            resp = await client.get(BINANCE_KLINES_URL, params=params)
            resp.raise_for_status()
            return resp.json()
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            if attempt == retries:
                print(f"Failed to fetch {symbol} after {retries} attempts: {e}")
                raise
            await asyncio.sleep(attempt * 1.5)


async def backfill():
    # Pass custom timeout to client instance
    async with (
        httpx.AsyncClient(timeout=TIMEOUT) as client,
        AsyncSessionLocal() as db,
    ):
        for entry in COINS_SEED:
            symbol = entry["symbol"]
            result = await db.execute(select(Coin).where(Coin.symbol == symbol))
            coin = result.scalar_one_or_none()

            if not coin:
                print(f"Skipping {symbol}, not in coins table")
                continue

            print(f"Fetching {symbol}...")
            try:
                klines = await fetch_klines(client, symbol)
            except Exception:
                print(f"Skipping {symbol} due to API error.")
                continue

            for k in klines:
                open_time_ms = k[0]
                ts = datetime.fromtimestamp(open_time_ms / 1000, tz=timezone.utc)

                row = PriceHistory(
                    id=uuid.uuid4(),
                    coin_id=coin.id,
                    interval=INTERVAL,
                    open=k[1],
                    high=k[2],
                    low=k[3],
                    close=k[4],
                    volume=k[5],
                    ts=ts,
                )
                db.add(row)

            print(f"Staged {len(klines)} candles for {symbol}")

            # Small delay prevents rate-limit issues on large coin sets
            await asyncio.sleep(0.2)

        # Single commit at the end for efficiency
        await db.commit()
        print("Backfill completed successfully.")


if __name__ == "__main__":
    asyncio.run(backfill())