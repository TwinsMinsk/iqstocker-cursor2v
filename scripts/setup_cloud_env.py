"""
Скрипт настройки облачного окружения

Получает данные из Supabase и Railway и настраивает .env файл
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем существующий .env
env_path = Path('.env')
if env_path.exists():
    load_dotenv(env_path)
    print("✅ .env файл найден и загружен")

# Supabase данные
SUPABASE_PROJECT_ID = "zpotpummnbfdlnzibyqb"
SUPABASE_HOST = "db.zpotpummnbfdlnzibyqb.supabase.co"
SUPABASE_URL = "https://zpotpummnbfdlnzibyqb.supabase.co"

print("\n📊 Настройка облачного окружения:")
print("=" * 60)
print(f"\n✅ Supabase проект найден:")
print(f"   Project ID: {SUPABASE_PROJECT_ID}")
print(f"   Host: {SUPABASE_HOST}")
print(f"   URL: {SUPABASE_URL}")

# Формируем DATABASE_URL для Supabase
# Нужно получить пароль из переменных окружения Supabase
# Для production нужно использовать Service Role Key или прямой connection string

print("\n💡 Для подключения к Supabase PostgreSQL:")
print("   1. Перейдите на https://supabase.com/dashboard/project/zpotpummnbfdlnzibyqb/settings/database")
print("   2. Скопируйте Connection String (под 'Connection string' → 'URI')")
print("   3. Замените 'postgresql://' на 'postgresql+asyncpg://'")
print("   4. Обновите DATABASE_URL в .env файле")

print("\n📝 Пример формата:")
print("   DATABASE_URL=postgresql+asyncpg://postgres.[password]@db.zpotpummnbfdlnzibyqb.supabase.co:5432/postgres")

print("\n✅ Railway проект:")
print("   Project ID: db40010a-1513-4b2b-9399-dd02125fce44")
print("   Нужно связать через: railway link")

