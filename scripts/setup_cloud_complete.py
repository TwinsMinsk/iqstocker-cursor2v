"""
Полная настройка облачного окружения

Настраивает Supabase PostgreSQL и Railway Redis
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

print("☁️ Полная настройка облачного окружения IQStocker v2.0")
print("=" * 70)

# Загружаем .env
env_path = Path('.env')
if env_path.exists():
    load_dotenv(env_path)
    print("✅ .env файл загружен")

# Supabase данные
SUPABASE_PROJECT_ID = "zpotpummnbfdlnzibyqb"
SUPABASE_HOST = "db.zpotpummnbfdlnzibyqb.supabase.co"
SUPABASE_URL = "https://zpotpummnbfdlnzibyqb.supabase.co"

print(f"\n📊 Текущая конфигурация:")
print("=" * 70)

print(f"\n✅ Supabase (PostgreSQL):")
print(f"   Project ID: {SUPABASE_PROJECT_ID}")
print(f"   Host: {SUPABASE_HOST}")
print(f"   URL: {SUPABASE_URL}")
print(f"   Database: postgres")
print(f"   User: postgres")

print(f"\n✅ Railway (Redis + Services):")
print(f"   Project: IQStocker-v2")
print(f"   Service: iqstocker-cursor2v")

print(f"\n📋 Следующие шаги:")
print("=" * 70)

print("\n1️⃣  Настроить Supabase DATABASE_URL:")
print("   • Откройте: https://supabase.com/dashboard/project/zpotpummnbfdlnzibyqb/settings/database")
print("   • Найдите раздел 'Connection string'")
print("   • Выберите 'URI' формат")
print("   • Скопируйте строку подключения")
print("   • Замените 'postgresql://' на 'postgresql+asyncpg://'")
print("   • Обновите DATABASE_URL в .env")

print("\n2️⃣  Настроить Railway Redis:")
print("   • Используем Railway MCP для получения переменных")
print("   • Или получите REDIS_URL из Railway dashboard")

print("\n3️⃣  Применить миграции:")
print("   • python -m alembic upgrade head")

print("\n4️⃣  Загрузить темы:")
print("   • python scripts/load_themes.py")

print("\n5️⃣  Запустить бота:")
print("   • python -m src.bot.main")

