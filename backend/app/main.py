from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routes.router import router
from app.routes.ws_prices import router as ws_prices_router
from app.services.binance_listener import start_listener, stop_listener


logging.basicConfig(level=logging.INFO)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await start_listener()
    yield
    await stop_listener()


app = FastAPI(
    title="CryptoPulse API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(router)
app.include_router(ws_prices_router)


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok"}
