"""
FastAPI приложение для API endpoints IQStocker v2.0

Health checks, webhooks
"""

from fastapi import FastAPI

from src.api import health, webhooks
from src.config.logging import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="IQStocker API",
    description="API endpoints для IQStocker v2.0",
    version="2.0.0",
)

# Регистрация роутеров
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["Webhooks"])


@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "service": "IQStocker API",
        "version": "2.0.0",
        "status": "running",
    }

