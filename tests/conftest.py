"""
Pytest конфигурация для IQStocker v2.0

Фикстуры для тестирования
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.database.connection import get_session
from src.database.models import SQLModel

# Тестовая база данных
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/test_iqstocker"


@pytest.fixture
async def test_engine():
    """Создает тестовый engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )
    
    # Создаем все таблицы
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    yield engine
    
    # Удаляем все таблицы после тестов
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine):
    """Создает тестовую сессию"""
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def db_session(test_session):
    """Фикстура для dependency injection"""
    yield test_session

