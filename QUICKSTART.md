# Quick Start Guide - IQStocker v2.0

## 🚀 Быстрый старт

### Предварительные требования

- Python 3.11+
- Poetry
- Docker и Docker Compose
- PostgreSQL 16
- Redis 7.2

### 1. Клонирование проекта

```bash
git clone <repository-url>
cd iqstocker-v2
```

### 2. Установка зависимостей

```bash
poetry install
```

### 3. Настройка окружения

Скопируйте `.env.example` в `.env` и заполните значения:

```bash
cp .env.example .env
```

Обязательные переменные:
- `BOT_TOKEN` - токен Telegram бота
- `CHANNEL_ID` - ID канала для подписки
- `ADMIN_IDS` - список ID администраторов (через запятую)
- `DATABASE_URL` - URL подключения к PostgreSQL
- `ADMIN_USERNAME` - логин для админ-панели
- `ADMIN_PASSWORD` - пароль для админ-панели
- `SECRET_KEY` - секретный ключ (сгенерируйте: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)

### 4. Запуск с Docker Compose

```bash
docker compose up -d
```

Это запустит:
- PostgreSQL (порт 5432)
- Redis (порт 6379)
- Bot service
- Admin service (порт 8000)
- Worker service

### 5. Применение миграций

```bash
poetry run alembic upgrade head
```

Или через Docker:
```bash
docker compose exec bot poetry run alembic upgrade head
```

### 6. Загрузка тем из CSV

```bash
poetry run python scripts/load_themes.py
```

### 7. Проверка работы

- Bot: Проверьте логи `docker compose logs bot`
- Admin: Откройте http://localhost:8000
- Worker: Проверьте логи `docker compose logs worker`

## 🔧 Разработка

### Запуск бота локально

```bash
poetry run python -m src.bot.main
```

### Запуск админ-панели локально

```bash
poetry run uvicorn src.admin.main:app --reload
```

### Запуск worker локально

```bash
poetry run arq src.workers.main.WorkerSettings
```

### Тестирование

```bash
poetry run pytest
```

### Линтинг

```bash
poetry run ruff check src/
poetry run ruff format src/
```

### Проверка типов

```bash
poetry run mypy src/
```

## 📝 Миграции

### Создание миграции

```bash
poetry run alembic revision --autogenerate -m "Описание изменений"
```

### Применение миграций

```bash
poetry run alembic upgrade head
```

### Откат миграции

```bash
poetry run alembic downgrade -1
```

## 🐳 Docker команды

### Запуск всех сервисов

```bash
docker compose up -d
```

### Просмотр логов

```bash
docker compose logs -f bot
docker compose logs -f admin
docker compose logs -f worker
```

### Остановка

```bash
docker compose down
```

### Пересборка

```bash
docker compose up -d --build
```

### Выполнение команд в контейнере

```bash
docker compose exec bot poetry run alembic upgrade head
docker compose exec admin poetry run python scripts/load_themes.py
```

## 📊 Проверка статуса

### Health checks

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/health
```

### Подключение к PostgreSQL

```bash
docker compose exec postgres psql -U iqstocker -d iqstocker
```

### Подключение к Redis

```bash
docker compose exec redis redis-cli
```

## 🆘 Troubleshooting

### Проблемы с зависимостями

```bash
poetry install --no-dev
```

### Проблемы с миграциями

```bash
poetry run alembic current
poetry run alembic history
```

### Очистка базы данных

```bash
docker compose exec postgres psql -U iqstocker -d iqstocker -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
poetry run alembic upgrade head
```

### Очистка Docker volumes

```bash
docker compose down -v
```
