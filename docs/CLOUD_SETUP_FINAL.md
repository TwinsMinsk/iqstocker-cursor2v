# ✅ Облачное окружение настроено!

## 🎉 Что уже сделано

### ✅ Supabase PostgreSQL
- **Миграции применены успешно!**
- Все 9 таблиц созданы:
  1. `users` - пользователи
  2. `limits` - лимиты
  3. `csv_analyses` - загруженные CSV
  4. `analytics_reports` - отчеты аналитики
  5. `theme_templates` - шаблоны тем
  6. `theme_requests` - запросы тем
  7. `payments` - платежи
  8. `system_messages` - системные сообщения
  9. `broadcast_messages` - рассылки

### ✅ Railway
- Проект связан: **IQStocker-v2**
- Сервис: **iqstocker-cursor2v**

---

## 📋 Что нужно сделать

### 1️⃣ Получить DATABASE_URL из Supabase

1. Откройте [Supabase Dashboard](https://supabase.com/dashboard/project/zpotpummnbfdlnzibyqb/settings/database)
2. Перейдите в **Settings** → **Database**
3. Найдите раздел **Connection string**
4. Выберите вкладку **URI**
5. Скопируйте connection string
6. **ВАЖНО**: Замените `postgresql://` на `postgresql+asyncpg://`
7. Обновите `.env` файл:
   ```bash
   DATABASE_URL=postgresql+asyncpg://postgres:[PASSWORD]@db.zpotpummnbfdlnzibyqb.supabase.co:5432/postgres
   ```

### 2️⃣ Настроить Railway Redis

Если в Railway есть Redis сервис:
1. Откройте [Railway Dashboard](https://railway.app/project/6cf8b162-724d-4555-83a2-15f25dfedf40)
2. Найдите сервис **Redis**
3. Скопируйте переменные:
   - `REDIS_HOST`
   - `REDIS_PORT`
   - `REDIS_PASSWORD` (если есть)
4. Обновите `.env`:
   ```bash
   REDIS_HOST=[host-from-railway]
   REDIS_PORT=6379
   REDIS_PASSWORD=[password-if-needed]
   REDIS_DB=0
   ```

### 3️⃣ Загрузить темы

После настройки DATABASE_URL:

```bash
python scripts/load_themes.py
```

Это загрузит темы из `Стоки 2(ТЕМЫ ИТОГ).csv` в таблицу `theme_templates`.

### 4️⃣ Проверить подключение

```bash
python scripts/check_cloud_setup.py
```

### 5️⃣ Запустить бота

```bash
python -m src.bot.main
```

---

## 🔧 Использование MCP инструментов

Теперь можно использовать MCP для работы с базой данных:

### Supabase MCP

```python
# Проверить таблицы
mcp_supabase_list_tables(project_id="zpotpummnbfdlnzibyqb")

# Выполнить SQL запрос
mcp_supabase_execute_sql(
    project_id="zpotpummnbfdlnzibyqb",
    query="SELECT COUNT(*) FROM users"
)

# Применить новую миграцию
mcp_supabase_apply_migration(
    project_id="zpotpummnbfdlnzibyqb",
    name="add_new_column",
    query="ALTER TABLE users ADD COLUMN new_field VARCHAR(255)"
)
```

### Railway MCP

```python
# Список сервисов
mcp_Railway_list_services(workspacePath="C:\\Project\\iqstocker-v2")

# Переменные окружения
mcp_Railway_list_variables(workspacePath="C:\\Project\\iqstocker-v2")

# Установить переменные
mcp_Railway_set_variables(
    workspacePath="C:\\Project\\iqstocker-v2",
    variables=["DATABASE_URL=postgresql+asyncpg://..."]
)

# Логи
mcp_Railway_get_logs(
    workspacePath="C:\\Project\\iqstocker-v2",
    logType="deploy"
)
```

---

## 📊 Текущая конфигурация

### Supabase
- **Project ID**: `zpotpummnbfdlnzibyqb`
- **Host**: `db.zpotpummnbfdlnzibyqb.supabase.co`
- **Database**: `postgres`
- **Status**: ✅ Миграции применены

### Railway
- **Project ID**: `6cf8b162-724d-4555-83a2-15f25dfedf40`
- **Project Name**: IQStocker-v2
- **Service**: iqstocker-cursor2v
- **Status**: ✅ Связан

---

## 🚀 Следующие шаги

1. ✅ **Обновите DATABASE_URL** в `.env` файле
2. ✅ **Настройте REDIS** переменные (если нужно)
3. ✅ **Загрузите темы**: `python scripts/load_themes.py`
4. ✅ **Проверьте подключение**: `python scripts/check_cloud_setup.py`
5. ✅ **Запустите бота**: `python -m src.bot.main`

---

## ❓ Вопросы?

Если возникнут проблемы:
1. Проверьте `.env` файл - правильность DATABASE_URL
2. Проверьте подключение: `python scripts/test_db_simple.py`
3. Посмотрите логи Supabase: Dashboard → Logs
4. Проверьте Railway: `railway logs`

---

**Все готово для продолжения работы! 🎉**

