from fastapi import APIRouter
from app.routes.auth import router as auth_router
#from app.routes.ws_prices import router as ws_prices_router
from app.routes.trade import router as trade_router
from app.routes.analytics import router as analytics_router
router = APIRouter(prefix="/routes")
router.include_router(auth_router)
router.include_router(trade_router)
router.include_router(analytics_router)