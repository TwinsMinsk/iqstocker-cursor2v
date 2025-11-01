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

from src.config.settings import settings
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
    Преобразует direct connection URL в pooler URL для Supabase
    Direct: postgresql+asyncpg://postgres:password@db.project.supabase.co:5432/postgres
    Pooler: postgresql+asyncpg://postgres.project:password@aws-0-region.pooler.supabase.com:6543/postgres
    """
    url = settings.database.url
    
    # Если это direct connection к Supabase, преобразуем в pooler URL
    if "db." in url and ".supabase.co" in url and "pooler" not in url:
        # Парсим текущий URL с помощью регулярного выражения
        # Формат: postgresql+asyncpg://postgres:password@db.PROJECT-ID.supabase.co:PORT/postgres
        match = re.match(r'(postgresql\+asyncpg://)postgres:([^@]+)@db\.([^.]+)\.supabase\.co:(\d+)/(.+)', url)
        if match:
            protocol, password_raw, project_id, port, database = match.groups()
            
            # Декодируем пароль, если он был закодирован, затем кодируем правильно
            password = unquote(password_raw)
            
            # Определяем регион (для проекта zpotpummnbfdlnzibyqb это eu-north-1)
            region_map = {
                "zpotpummnbfdlnzibyqb": "eu-north-1",
            }
            region = region_map.get(project_id, "eu-north-1")  # По умолчанию eu-north-1
            
            # Кодируем пароль для использования в URL (безопасное экранирование)
            password_encoded = quote(password, safe="")
            
            # Создаем pooler URL для transaction mode (порт 6543)
            pooler_url = f"{protocol}postgres.{project_id}:{password_encoded}@aws-0-{region}.pooler.supabase.com:6543/{database}"
            return pooler_url
    
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

