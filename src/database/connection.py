"""
Подключение к базе данных IQStocker v2.0

Использует SQLModel с asyncpg для PostgreSQL
"""

import re
from typing import AsyncGenerator
from urllib.parse import quote, unquote

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel
import structlog

from src.config.settings import settings

logger = structlog.get_logger(__name__)
from src.database.models import (
    User,
    Limits,
    CSVAnalysis,
    AnalyticsReport,
    ThemeRequest,
    ThemeTemplate,
    Payment,
    SystemMessage,
    BroadcastMessage,
)

# Создание async engine с настройками для Supabase
# Для Railway используем connection pooling через pooler.supabase.com
# Это решает проблемы с "Network is unreachable"
def get_supabase_url() -> str:
    """
    Возвращает правильный URL для подключения к Supabase
    
    КРИТИЧНО: Для Railway используем ПРЯМОЙ connection string (direct connection),
    так как Railway поддерживает IPv6 и это работает стабильнее чем pooler.
    
    Pooler используется только если прямой connection не работает.
    
    Direct: postgresql+asyncpg://postgres:password@db.project.supabase.co:5432/postgres
    Pooler Session Mode: postgresql+asyncpg://postgres.project:password@aws-0-region.pooler.supabase.com:5432/postgres
    
    ВАЖНО: Для pooler формат username: postgres.PROJECT-REF (с точкой!)
    """
    url = settings.database.url
    
    # Логируем исходный URL (без пароля)
    url_masked = re.sub(r':([^@]+)@', ':***@', url)
    logger.info("database_url_processing", url_masked=url_masked)
    
    # Если уже используется pooler URL, возвращаем как есть
    if "pooler.supabase.com" in url:
        logger.info("database_url_pooler_detected")
        return url
    
    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Используем ПРЯМОЙ connection string для Railway
    # Railway поддерживает IPv6, поэтому прямой connection должен работать
    # Это решает проблему "Tenant or user not found" с pooler
    logger.info("database_url_using_direct", reason="Railway supports IPv6, using direct connection")
    return url

engine = create_async_engine(
    get_supabase_url(),
    echo=settings.database.echo,
    future=True,
    pool_pre_ping=True,  # Проверка соединений перед использованием
    # Для Supabase connection pooling используем минимальный локальный пул
    # так как основной пул управляется Supabase pooler
    pool_size=2,  # Минимальный размер для connection pooling
    max_overflow=5,  # Минимальный overflow для connection pooling
)

# Создание async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения сессии БД
    
    Usage:
        async with get_session() as session:
            user = await user_repo.get_by_telegram_id(session, telegram_id)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Инициализация базы данных (создание таблиц)"""
    async with engine.begin() as conn:
        # SQLModel не поддерживает create_all для async напрямую
        # Используем Alembic для миграций, но можем создать таблицы здесь для разработки
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_db() -> None:
    """Закрытие соединения с БД"""
    await engine.dispose()


# Список всех моделей для Alembic autogenerate
__all__ = [
    "engine",
    "AsyncSessionLocal",
    "get_session",
    "init_db",
    "close_db",
]

