# Установка IQStocker v2.0 на Windows Server 2022 (без Docker)

## Проблема
Docker Desktop не работает на Windows Server 2022 из-за требований WSL2.

## Решения

### Вариант 1: Установка PostgreSQL и Redis напрямую (рекомендуется)

#### 1. Установка PostgreSQL

1. Скачайте PostgreSQL 16 для Windows:
   - https://www.postgresql.org/download/windows/
   - Или используйте установщик: https://www.postgresql.org/download/windows/installer/

2. Установите PostgreSQL:
   - Запомните пароль для пользователя `postgres`
   - Порт по умолчанию: `5432`

3. Создайте базу данных:
```sql
CREATE DATABASE iqstocker;
CREATE USER iqstocker WITH PASSWORD 'iqstocker';
GRANT ALL PRIVILEGES ON DATABASE iqstocker TO iqstocker;
```

4. Обновите `.env`:
```bash
DATABASE_URL=postgresql+asyncpg://iqstocker:iqstocker@localhost:5432/iqstocker
```

#### 2. Установка Redis для Windows

**Вариант A: Memurai (официальный Redis для Windows)**
1. Скачайте Memurai: https://www.memurai.com/
2. Установите как Windows Service
3. Порт по умолчанию: `6379`

**Вариант B: Redis для Windows (портативная версия)**
1. Скачайте: https://github.com/tporadowski/redis/releases
2. Распакуйте и запустите `redis-server.exe`

**Вариант C: Облачный Redis (для тестирования)**
- Используйте Redis Cloud: https://redis.com/try-free/
- Или Upstash: https://upstash.com/

Обновите `.env`:
```bash
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

### Вариант 2: Облачные сервисы (быстрое решение)

#### PostgreSQL (Supabase)
1. Создайте проект на https://supabase.com
2. Получите connection string
3. Обновите `.env`:
```bash
DATABASE_URL=postgresql+asyncpg://postgres:[password]@[host]:5432/postgres
```

#### Redis (Upstash)
1. Создайте Redis на https://upstash.com
2. Получите endpoint и password
3. Обновите `.env`:
```bash
REDIS_HOST=[upstash-host]
REDIS_PORT=6379
REDIS_PASSWORD=[password]
```

### Вариант 3: SQLite для тестирования (временно)

Можно изменить на SQLite для быстрого тестирования, но потребуются изменения в коде.

## Шаги после установки

1. Применить миграции:
```bash
python -m alembic upgrade head
```

2. Загрузить темы:
```bash
python scripts/load_themes.py
```

3. Запустить бота:
```bash
python -m src.bot.main
```

## Проверка установки

### PostgreSQL
```bash
psql -U iqstocker -d iqstocker -c "SELECT version();"
```

### Redis
```bash
redis-cli ping
# Должен ответить: PONG
```

## Альтернатива: Использовать готовые решения

- **Railway.app** - автоматически предоставляет PostgreSQL и Redis
- **Render.com** - бесплатный PostgreSQL и Redis
- **Supabase** - бесплатный PostgreSQL

