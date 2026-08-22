import asyncio
import json
import logging
from typing import Optional
import websockets
from websockets.exceptions import ConnectionClosed

logger=logging.getLogger(__name__)

from app.scripts.coins_seed import COINS_SEED

def _build_stream_url() -> str:
    streams = "/".join(f"{c['symbol'].lower()}@ticker" for c in COINS_SEED)
    return f"wss://stream.binance.com:9443/stream?streams={streams}"

BINANCE_WS_URL = _build_stream_url()

latest_prices:dict[str,dict]={}

_task:Optional[asyncio.Task]=None

_stop_event:Optional[asyncio.Event]=None

async def _listen():
    global _stop_event
    while _stop_event and not _stop_event.is_set():
        try:
            async with websockets.connect(BINANCE_WS_URL, ping_interval=20, ping_timeout=20) as ws:
                logger.info("Connected to binance Websocket")
                async for message in ws:
                    if _stop_event.is_set():
                        break
                    payload = json.loads(message)
                    ticker = payload.get("data", payload)

                    if isinstance(ticker, dict) and "s" in ticker:
                        symbol = ticker["s"]
                        latest_prices[symbol] = {
                            "price": ticker["c"],
                            "change_pct": ticker["P"],
                            "high": ticker["h"],
                            "low": ticker["l"],
                            "volume": ticker["v"],
                        }
        except (ConnectionClosed, OSError) as e:
            logger.warning(f"Binance WS disconnected: {e}. Reconnecting in 5s...")
            await asyncio.sleep(5)
        except Exception as e:
            logger.exception(f"Unexpected error in Binance listener:{e}")
            await asyncio.sleep(5)

async def start_listener():
    global _task,_stop_event
    if _stop_event is None:
        _stop_event=asyncio.Event()
    
    _stop_event.clear()
    if _task is None or _task.done():
        _task=asyncio.create_task(_listen())
        logger.info("Binance listener task started")

async def stop_listener():
    global _task,_stop_event
    if _stop_event:
        _stop_event.set()
    if _task:
        _task.cancel()
        try:
            await _task
        except asyncio.CancelledError:
            pass
    logger.info("Binance listener task stopped")

