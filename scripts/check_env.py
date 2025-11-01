"""
Скрипт для проверки переменных окружения

Проверяет наличие всех необходимых переменных для запуска бота
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем .env файл
env_path = Path('.env')
if env_path.exists():
    load_dotenv(env_path)
    print("✅ .env файл найден и загружен")
else:
    print("❌ .env файл не найден")

# Проверяем обязательные переменные
required_vars = {
    "BOT_TOKEN": os.getenv("BOT_TOKEN"),
    "CHANNEL_ID": os.getenv("CHANNEL_ID"),
    "ADMIN_IDS": os.getenv("ADMIN_IDS"),
    "DATABASE_URL": os.getenv("DATABASE_URL"),
    "ADMIN_USERNAME": os.getenv("ADMIN_USERNAME"),
    "ADMIN_PASSWORD": os.getenv("ADMIN_PASSWORD"),
    "SECRET_KEY": os.getenv("SECRET_KEY"),
}

print("\n📋 Проверка переменных окружения:")
print("=" * 60)

all_present = True
for var_name, var_value in required_vars.items():
    if var_value:
        # Скрываем значения для безопасности
        if "PASSWORD" in var_name or "SECRET" in var_name or "TOKEN" in var_name:
            display_value = var_value[:10] + "..." if len(var_value) > 10 else "***"
        else:
            display_value = var_value[:50] + "..." if len(var_value) > 50 else var_value
        print(f"✅ {var_name}: {display_value}")
    else:
        print(f"❌ {var_name}: НЕ НАЙДЕНА")
        all_present = False

print("=" * 60)

if all_present:
    print("\n✅ Все необходимые переменные найдены!")
    return_code = 0
else:
    print("\n❌ Некоторые переменные отсутствуют!")
    print("Проверьте .env файл и добавьте недостающие переменные.")
    return_code = 1

exit(return_code)

