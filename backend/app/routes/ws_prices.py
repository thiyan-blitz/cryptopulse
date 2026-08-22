import asyncio
import logging
from fastapi import APIRouter,WebSocket,WebSocketDisconnect
from app.services.binance_listener import latest_prices

logger=logging.getLogger(__name__)

router=APIRouter()


@router.websocket("/ws/prices")
async def prices_ws(websocket:WebSocket):
    await websocket.accept()
    logger.info("Client connected to /ws/prices")

    try:
        while True:
            await websocket.send_json(latest_prices)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        logger.info("Client disconnected from /we/prices")
    except Exception as e:
        logger.exception(f"Error in /ws/prices: {e}")

