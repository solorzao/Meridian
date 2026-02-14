from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.jobs.scheduler import shutdown_scheduler, start_scheduler
from app.middleware.error_handler import global_exception_handler
from app.middleware.rate_limiter import limiter
from app.routers import (
    indicators_router,
    market_data_router,
    screener_router,
    stats_router,
)
from app.routers.agents import router as agents_router
from app.routers.analytics import router as analytics_router
from app.routers.billing import router as billing_router
from app.routers.strategies import router as strategies_router
from app.routers.trades import router as trades_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    shutdown_scheduler()


app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Global exception handler
app.add_exception_handler(Exception, global_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Original analytics routes (kept intact for backwards compatibility)
app.include_router(market_data_router)
app.include_router(indicators_router)
app.include_router(screener_router)
app.include_router(stats_router)

# New consolidated API routes
app.include_router(analytics_router)
app.include_router(trades_router)
app.include_router(strategies_router)
app.include_router(billing_router)
app.include_router(agents_router)


@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration."""
    return {"status": "healthy", "service": "meridian-analytics"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Meridian Analytics Service", "version": "0.2.0"}
