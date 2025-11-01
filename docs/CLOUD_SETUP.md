# Настройка облачного окружения IQStocker v2.0

## 🎯 Используемые сервисы

### Supabase (PostgreSQL)
- **Project ID**: `zpotpummnbfdlnzibyqb`
- **Project Name**: IQStocke-V2
- **Region**: eu-north-1
- **Host**: `db.zpotpummnbfdlnzibyqb.supabase.co`
- **URL**: `https://zpotpummnbfdlnzibyqb.supabase.co`

### Railway (Redis + Deployment)
- **Project ID**: `6cf8b162-724d-4555-83a2-15f25dfedf40`
- **Project Name**: IQStocker-v2
- **Service**: iqstocker-cursor2v

---

## 📋 Пошаговая настройка

### 1. Получение DATABASE_URL из Supabase

1. Откройте [Supabase Dashboard](https://supabase.com/dashboard/project/zpotpummnbfdlnzibyqb/settings/database)
2. Перейдите в **Settings** → **Database**
3. Найдите раздел **Connection string**
4. Выберите **URI** формат
5. Скопируйте connection string (примерно так: `postgresql://postgres:[PASSWORD]@db.zpotpummnbfdlnzibyqb.supabase.co:5432/postgres`)
6. **Замените** `postgresql://` на `postgresql+asyncpg://`
7. Обновите `.env` файл:
   ```bash
   DATABASE_URL=postgresql+asyncpg://postgres:[PASSWORD]@db.zpotpummnbfdlnzibyqb.supabase.co:5432/postgres
   ```

### 2. Настройка Railway Redis

#### Вариант A: Получение через Railway CLI
```bash
railway variables
# Найдите REDIS_URL или REDIS_HOST, REDIS_PORT, REDIS_PASSWORD
```

#### Вариант B: Получение из Railway Dashboard
1. Откройте [Railway Dashboard](https://railway.app/project/6cf8b162-724d-4555-83a2-15f25dfedf40)
2. Перейдите в сервис **Redis**
3. Найдите переменные окружения:
   - `REDIS_URL` (если есть)
   - Или отдельные: `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`
4. Обновите `.env` файл:
   ```bash
   REDIS_HOST=[host-from-railway]
   REDIS_PORT=6379
   REDIS_PASSWORD=[password-from-railway]
   REDIS_DB=0
   ```

### 3. Применение миграций

После настройки `DATABASE_URL`:

```bash
python -m alembic upgrade head
```

Это создаст все необходимые таблицы в Supabase PostgreSQL:
- `users`
- `limits`
- `csv_analyses`
- `analytics_reports`
- `theme_requests`
- `theme_templates`
- `referrals`
- `payments`
- `system_messages`
- `broadcast_messages`

### 4. Загрузка тем

Загрузите темы из CSV файла:

```bash
python scripts/load_themes.py
```

### 5. Тестирование подключения

```bash
python scripts/test_db_connection.py
```

### 6. Запуск бота

```bash
python -m src.bot.main
```

---

## 🔧 Использование MCP инструментов

### Supabase MCP

```python
# Получить список таблиц
mcp_supabase_list_tables(project_id="zpotpummnbfdlnzibyqb")

# Выполнить SQL запрос
mcp_supabase_execute_sql(
    project_id="zpotpummnbfdlnzibyqb",
    query="SELECT * FROM users LIMIT 10"
)

# Применить миграцию
mcp_supabase_apply_migration(
    project_id="zpotpummnbfdlnzibyqb",
    name="initial_schema",
    query="CREATE TABLE..."
)
```

### Railway MCP

```python
# Получить список сервисов
mcp_Railway_list_services(workspacePath="C:\\Project\\iqstocker-v2")

# Получить переменные окружения
mcp_Railway_list_variables(workspacePath="C:\\Project\\iqstocker-v2")

# Установить переменные
mcp_Railway_set_variables(
    workspacePath="C:\\Project\\iqstocker-v2",
    variables=["KEY=value"]
)
```

---

## 📝 Пример .env файла

```bash
# Bot Configuration
BOT_TOKEN=8292646983:AAGTkZeNlK7nu0VEu6QFAyNkjcminXa_ARA
ADMIN_IDS=811079407
CHANNEL_ID=-1002068980058

# Database (Supabase)
DATABASE_URL=postgresql+asyncpg://postgres:[PASSWORD]@db.zpotpummnbfdlnzibyqb.supabase.co:5432/postgres
DATABASE_ECHO=false

# Redis (Railway)
REDIS_HOST=[host-from-railway]
REDIS_PORT=6379
REDIS_PASSWORD=[password-from-railway]
REDIS_DB=0

# Admin Panel
ADMIN_USERNAME=admin
ADMIN_PASSWORD=Qwerty123
SECRET_KEY=16a6eadb2202a422df6299c3e8e28a38ebd68204f612eb00

# Tribute.tg
TRIBUTE_API_KEY=placeholder
TRIBUTE_WEBHOOK_SECRET=placeholder

# Application
ENVIRONMENT=production
LOG_LEVEL=INFO
BASE_URL=https://your-domain.railway.app
```

---

## ✅ Проверка настройки

1. **Проверка Supabase:**
   ```bash
   python scripts/test_db_simple.py
   ```

2. **Проверка миграций:**
   ```bash
   python -m alembic current
   ```

3. **Проверка таблиц:**
   - Используйте MCP: `mcp_supabase_list_tables(project_id="zpotpummnbfdlnzibyqb")`

4. **Проверка Railway:**
   ```bash
   railway variables
   railway status
   ```

---

## 🚀 Деплой на Railway

После настройки локального окружения можно задеплоить на Railway:

1. **Создать сервисы:**
   - Bot service
   - Admin service (web)
   - Worker service

2. **Настроить переменные окружения** для каждого сервиса

3. **Деплой:**
   ```bash
   railway up
   ```

---

## 📞 Поддержка

При возникновении проблем:
- Проверьте логи: `railway logs`
- Проверьте Supabase dashboard
- Проверьте Railway dashboard

