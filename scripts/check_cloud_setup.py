"""
Проверка облачного окружения

Проверяет настройку Supabase и Railway
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.settings import settings
from src.database.connection import engine
from sqlalchemy import text

async def check_supabase():
    """Проверка подключения к Supabase"""
    print("🔍 Проверка Supabase PostgreSQL...")
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version(), current_database()"))
            row = result.fetchone()
            if row:
                print(f"✅ Подключение успешно!")
                print(f"   PostgreSQL: {row[0][:50]}...")
                print(f"   Database: {row[1]}")
                
                # Проверка таблиц
                result = await conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    ORDER BY table_name
                """))
                tables = [row[0] for row in result.fetchall()]
                print(f"\n📊 Созданные таблицы ({len(tables)}):")
                for table in tables:
                    print(f"   ✅ {table}")
                
                if len(tables) == 0:
                    print("   ⚠️  Таблицы не найдены, нужно применить миграции")
                
                return True
    except Exception as e:
        print(f"❌ Ошибка подключения: {type(e).__name__}: {str(e)[:100]}")
        return False

async def main():
    print("=" * 70)
    print("☁️ Проверка облачного окружения IQStocker v2.0")
    print("=" * 70)
    
    print(f"\n📊 Текущие настройки:")
    print(f"   DATABASE_URL: {settings.database.url[:60]}..." if settings.database.url else "   DATABASE_URL: НЕ НАСТРОЕН")
    print(f"   REDIS_HOST: {settings.redis.host}")
    print(f"   REDIS_PORT: {settings.redis.port}")
    
    print("\n" + "=" * 70)
    
    # Проверка Supabase
    supabase_ok = await check_supabase()
    
    print("\n" + "=" * 70)
    
    if supabase_ok:
        print("✅ Supabase настроен и работает!")
    else:
        print("❌ Supabase требует настройки")
    
    print("\n📋 Следующие шаги:")
    if not supabase_ok:
        print("   1. Обновите DATABASE_URL в .env файле")
        print("   2. Примените миграции: python -m alembic upgrade head")
    else:
        print("   1. Загрузите темы: python scripts/load_themes.py")
        print("   2. Запустите бота: python -m src.bot.main")

if __name__ == "__main__":
    asyncio.run(main())

