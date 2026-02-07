from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import (
    market_data_router,
    indicators_router,
    screener_router,
    stats_router,
)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(market_data_router)
app.include_router(indicators_router)
app.include_router(screener_router)
app.include_router(stats_router)


@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration."""
    return {"status": "healthy", "service": "meridian-analytics"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Meridian Analytics Service", "version": "0.1.0"}
