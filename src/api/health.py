"""
Health check endpoints

Проверка здоровья сервисов
"""

from datetime import datetime

from fastapi import APIRouter

from src.config.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Returns:
        Словарь со статусом сервиса
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "iqstocker-api",
    }


@router.get("/ready")
async def readiness_check():
    """
    Readiness check endpoint
    
    Проверяет готовность сервиса к работе
    
    Returns:
        Словарь со статусом готовности
    """
    # TODO: Проверить подключение к БД и Redis
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
    }

