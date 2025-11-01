"""
Тест подключения к базе данных

Проверяет подключение к PostgreSQL перед запуском бота
"""

import asyncio
from src.config.settings import settings
from src.database.connection import engine

async def test_connection():
    """Тест подключения к БД"""
    try:
        print(f"Попытка подключения к: {settings.database.url[:50]}...")
        async with engine.begin() as conn:
            result = await conn.execute("SELECT 1")
            print("✅ Подключение к базе данных успешно!")
            return True
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        print(f"Проверьте, что PostgreSQL запущен и доступен по адресу из DATABASE_URL")
        return False

if __name__ == "__main__":
    asyncio.run(test_connection())

