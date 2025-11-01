"""
Простой тест подключения к Supabase

Проверяет подключение к базе данных через SQLAlchemy
"""

import asyncio
from sqlalchemy import text
from src.database.connection import engine


async def test_connection():
    """Тест подключения к базе данных"""
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text('SELECT 1 as test'))
            test_value = result.scalar()
            print(f'✅ Подключение к Supabase работает!')
            print(f'   Тест: {test_value}')
            
            # Проверяем таблицу users
            result = await conn.execute(text('SELECT COUNT(*) FROM users'))
            user_count = result.scalar()
            print(f'   Пользователей в БД: {user_count}')
            
    except Exception as e:
        print(f'❌ Ошибка подключения: {e}')
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_connection())

