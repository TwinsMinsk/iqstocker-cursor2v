"""
Скрипт для инициализации базы данных

Применение миграций и загрузка начальных данных
"""

import asyncio

from alembic.config import Config
from alembic import command

from src.config.logging import get_logger
from src.config.settings import settings
from src.database.connection import engine

logger = get_logger(__name__)


async def init_database():
    """Инициализация базы данных"""
    try:
        # Применяем миграции
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        
        logger.info("database_initialized")
        
    except Exception as e:
        logger.error("database_init_error", error=str(e), exc_info=True)
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_database())

