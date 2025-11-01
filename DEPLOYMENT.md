# Руководство по деплою IQStocker v2.0

## 🚀 Деплой на Railway.app

### 1. Подготовка

1. Создайте аккаунт на [Railway.app](https://railway.app)
2. Создайте новый проект
3. Добавьте следующие сервисы:
   - PostgreSQL (Database)
   - Redis (Database)
   - Bot Service (Python)
   - Admin Service (Python)
   - Worker Service (Python)

### 2. Настройка PostgreSQL

1. Создайте PostgreSQL сервис в Railway
2. Railway автоматически предоставит `DATABASE_URL`
3. Скопируйте `DATABASE_URL` в переменные окружения других сервисов

### 3. Настройка Redis

1. Создайте Redis сервис в Railway
2. Railway автоматически предоставит `REDIS_URL`
3. Скопируйте `REDIS_URL` в переменные окружения других сервисов

### 4. Настройка Bot Service

**Dockerfile:** `Dockerfile.bot`

**Environment Variables:**
```bash
BOT_TOKEN=your_bot_token
CHANNEL_ID=-1001234567890
ADMIN_IDS=123456,789012
DATABASE_URL=postgresql+asyncpg://...
REDIS_HOST=...
REDIS_PORT=6379
REDIS_DB=0
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secure_password
SECRET_KEY=random_secret_key
TRIBUTE_API_KEY=placeholder  # Заменить на реальный при интеграции
TRIBUTE_WEBHOOK_SECRET=placeholder  # Заменить на реальный при интеграции
ENVIRONMENT=production
LOG_LEVEL=INFO
BASE_URL=https://your-domain.railway.app
```

**Start Command:**
```bash
poetry run alembic upgrade head && python -m src.bot.main
```

### 5. Настройка Admin Service

**Dockerfile:** `Dockerfile.admin`

**Environment Variables:**
```bash
DATABASE_URL=postgresql+asyncpg://...
REDIS_HOST=...
REDIS_PORT=6379
REDIS_DB=0
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secure_password
SECRET_KEY=random_secret_key
ENVIRONMENT=production
LOG_LEVEL=INFO
BASE_URL=https://your-domain.railway.app
```

**Start Command:**
```bash
poetry run alembic upgrade head && poetry run uvicorn src.admin.main:app --host 0.0.0.0 --port $PORT
```

**Public URL:** Включите для доступа к админ-панели

### 6. Настройка Worker Service

**Dockerfile:** `Dockerfile.worker`

**Environment Variables:**
```bash
DATABASE_URL=postgresql+asyncpg://...
REDIS_HOST=...
REDIS_PORT=6379
REDIS_DB=0
ENVIRONMENT=production
LOG_LEVEL=INFO
```

**Start Command:**
```bash
poetry run alembic upgrade head && poetry run arq src.workers.main.WorkerSettings
```

### 7. Применение миграций

Миграции применяются автоматически при старте каждого сервиса через команду:
```bash
poetry run alembic upgrade head
```

Для ручного применения:
```bash
railway run poetry run alembic upgrade head
```

### 8. Загрузка тем из CSV

После применения миграций, загрузите темы из CSV файла:
```bash
railway run poetry run python scripts/load_themes.py
```

### 9. Health Checks

Все сервисы имеют health check endpoints:
- Bot: `/health` (если настроен)
- Admin: `/health`
- API: `/api/health`

### 10. Мониторинг

- Логи доступны в Railway dashboard
- Метрики можно настроить через Railway Metrics
- Alerts можно настроить через Railway Alerts

## 📝 Чеклист перед деплоем

- [ ] Все environment variables настроены
- [ ] TRIBUTE_API_KEY и TRIBUTE_WEBHOOK_SECRET обновлены (если интегрированы)
- [ ] BASE_URL настроен на реальный домен
- [ ] Миграции применены
- [ ] Темы загружены из CSV
- [ ] Health checks работают
- [ ] Логи проверены на ошибки

## 🔧 Troubleshooting

### Проблемы с миграциями
```bash
railway run poetry run alembic current
railway run poetry run alembic history
```

### Проблемы с подключением к БД
Проверьте `DATABASE_URL` в Railway dashboard

### Проблемы с Redis
Проверьте `REDIS_HOST` и `REDIS_PORT` в Railway dashboard

### Логи для отладки
```bash
railway logs --service bot
railway logs --service admin
railway logs --service worker
```

