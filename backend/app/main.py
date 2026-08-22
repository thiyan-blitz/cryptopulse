from fastapi import FastAPI
from app.routes.router import router
import logging
from contextlib import asynccontextmanager
from app.services.binance_listener import start_listener,stop_listener
from app.routes.ws_prices import router as ws_prices_router
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

@asynccontextmanager
async def lifespan(app:FastAPI):
    await start_listener()
    yield
    await stop_listener()

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
app.include_router(ws_prices_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}