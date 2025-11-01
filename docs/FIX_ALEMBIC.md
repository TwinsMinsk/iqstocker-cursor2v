# 🔧 Решение проблемы с Alembic

## ❌ Проблема

При запуске `alembic upgrade head` или `python -m alembic upgrade head` возникает ошибка:
```
pydantic_core._pydantic_core.ValidationError: 1 validation error for BotSettings
token
  Field required [type=missing, input_value={}, input_type=dict]
```

## ✅ Решение

### Вариант 1: Использовать прямой вызов alembic (рекомендуется)

```bash
alembic upgrade head
```

Но нужно убедиться, что `.env` файл существует и правильно настроен.

### Вариант 2: Использовать Supabase MCP (уже применено)

Миграции уже применены через Supabase MCP! Все 9 таблиц созданы.

Проверка:
```python
mcp_supabase_list_tables(project_id="zpotpummnbfdlnzibyqb")
```

### Вариант 3: Обновить DATABASE_URL и использовать alembic

1. **Получите connection string из Supabase:**
   - Откройте: https://supabase.com/dashboard/project/zpotpummnbfdlnzibyqb/settings/database
   - Скопируйте Connection String (URI формат)
   - Замените `postgresql://` на `postgresql+asyncpg://`
   - Обновите `.env` файл

2. **Проверьте что .env загружается:**
   ```bash
   python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('BOT_TOKEN', 'НЕ НАЙДЕН')[:20])"
   ```

3. **Запустите alembic:**
   ```bash
   alembic upgrade head
   ```

## 📝 Текущий статус

✅ **Миграции уже применены через Supabase MCP!**

Все таблицы созданы:
1. users
2. limits
3. csv_analyses
4. analytics_reports
5. theme_templates
6. theme_requests
7. payments
8. system_messages
9. broadcast_messages

## 🚀 Следующие шаги

Так как миграции уже применены, нужно:

1. **Обновить DATABASE_URL в .env** с Supabase connection string
2. **Загрузить темы:**
   ```bash
   python scripts/load_themes.py
   ```
3. **Запустить бота:**
   ```bash
   python -m src.bot.main
   ```

## ⚠️ Примечание

Если нужно применить новые миграции в будущем:

1. Создайте новую миграцию:
   ```bash
   alembic revision --autogenerate -m "description"
   ```

2. Примените через MCP:
   ```python
   mcp_supabase_apply_migration(
       project_id="zpotpummnbfdlnzibyqb",
       name="migration_name",
       query="SQL код миграции"
   )
   ```

Или обновите DATABASE_URL и используйте:
```bash
alembic upgrade head
```

