"""
Временное решение: модификация для использования SQLite вместо PostgreSQL

ВНИМАНИЕ: Это временное решение только для тестирования!
Для production обязательно используйте PostgreSQL!
"""

import sys
from pathlib import Path

# Это временный скрипт для быстрого тестирования
# НЕ используйте SQLite в production!

print("⚠️  ВНИМАНИЕ: SQLite - только для тестирования!")
print("Для production используйте PostgreSQL!\n")

print("Для использования SQLite:")
print("1. Установите: pip install aiosqlite")
print("2. Измените DATABASE_URL в .env на:")
print("   DATABASE_URL=sqlite+aiosqlite:///./iqstocker.db")
print("3. Примените миграции: python -m alembic upgrade head")

