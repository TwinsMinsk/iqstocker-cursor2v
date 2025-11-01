"""
Скрипт для настройки Supabase подключения

Получает connection string и настраивает миграции
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

print("🔧 Настройка Supabase для IQStocker v2.0")
print("=" * 60)

# Загружаем .env
env_path = Path('.env')
if env_path.exists():
    load_dotenv(env_path)

# Supabase данные
SUPABASE_PROJECT_ID = "zpotpummnbfdlnzibyqb"
SUPABASE_HOST = "db.zpotpummnbfdlnzibyqb.supabase.co"
SUPABASE_PORT = 5432
SUPABASE_DB = "postgres"
SUPABASE_USER = "postgres"

print(f"\n✅ Supabase проект:")
print(f"   Project ID: {SUPABASE_PROJECT_ID}")
print(f"   Host: {SUPABASE_HOST}")
print(f"   Database: {SUPABASE_DB}")
print(f"   User: {SUPABASE_USER}")

print("\n📋 Для получения connection string:")
print("   1. Откройте: https://supabase.com/dashboard/project/zpotpummnbfdlnzibyqb/settings/database")
print("   2. Найдите раздел 'Connection string'")
print("   3. Выберите 'URI' формат")
print("   4. Скопируйте строку подключения")
print("   5. Замените 'postgresql://' на 'postgresql+asyncpg://'")
print("   6. Обновите DATABASE_URL в .env")

print("\n📝 Формат DATABASE_URL:")
print(f"   DATABASE_URL=postgresql+asyncpg://postgres:[PASSWORD]@{SUPABASE_HOST}:{SUPABASE_PORT}/{SUPABASE_DB}")

current_db_url = os.getenv("DATABASE_URL", "")
if current_db_url and "supabase" in current_db_url:
    print(f"\n✅ DATABASE_URL уже настроен: {current_db_url[:50]}...")
else:
    print("\n⚠️  DATABASE_URL не настроен для Supabase")
    print("   Обновите .env файл с connection string из Supabase dashboard")

print("\n🔧 Следующие шаги:")
print("   1. Обновите DATABASE_URL в .env файле")
print("   2. Примените миграции: python -m alembic upgrade head")
print("   3. Загрузите темы: python scripts/load_themes.py")

