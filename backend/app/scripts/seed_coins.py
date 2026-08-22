import asyncio 
from sqlalchemy import select
from app.database.database import AsyncSessionLocal
from app.models.Coin import Coin
from app.scripts.coins_seed import COINS_SEED

async def seed_coin():
    async with AsyncSessionLocal() as db:
        for entry in COINS_SEED:
            result=await db.execute(select(Coin).where(Coin.symbol==entry["symbol"]))
            existing=result.scalar_one_or_none()

            if existing:
                existing.name=entry["name"]
                existing.logo_url=entry["logo_url"]

            else:
                db.add(Coin(
                    symbol=entry["symbol"],
                    name=entry["name"],
                    logo_url=entry["logo_url"],
                ))

        await db.commit()
        print(f"Seeded {len(COINS_SEED)} coins.")

if __name__=="__main__":
    asyncio.run(seed_coin())
