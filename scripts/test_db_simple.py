"""Простой тест подключения к БД"""
import sys
sys.path.insert(0, '.')
import asyncio
from src.config.settings import settings
from src.database.connection import engine
from sqlalchemy import text

async def test():
    print(f"Проверка подключения к БД...")
    print(f"URL: {settings.database.url[:60]}...")
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("✅ Подключение к БД работает!")
            return True
    except Exception as e:
        print(f"❌ Ошибка БД: {type(e).__name__}")
        print(f"   {str(e)[:150]}")
        print("\n💡 Проверьте:")
        print("   1. Docker Desktop запущен?")
        print("   2. PostgreSQL контейнер запущен? (docker compose ps)")
        print("   3. DATABASE_URL правильный?")
        return False

if __name__ == "__main__":
    asyncio.run(test())

