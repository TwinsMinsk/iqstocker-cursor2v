# IQStocker v2.0 - Quick Start Guide

## Prerequisites
- Python 3.11+
- Poetry
- Docker & Docker Compose
- PostgreSQL (via Docker)
- Redis (via Docker)

## Installation

### 1. Clone & Setup (5 commands)
```bash
cd iqstocker-v2
poetry install
cp .env.example .env
# Edit .env with your credentials
```

### 2. Local Development
```bash
# Start databases
docker compose up -d postgres redis

# Apply migrations
poetry run alembic upgrade head

# Run bot
poetry run python -m src.bot.main
```

### 3. Testing
```bash
poetry run pytest
poetry run mypy src/
poetry run ruff check src/
```

### 4. Deploy to Railway
1. Connect GitHub repository
2. Create PostgreSQL and Redis services
3. Set ENV variables
4. Deploy via Git Push

## Project Structure
- `src/bot/` - Telegram bot handlers
- `src/admin/` - FastAPI admin panel
- `src/database/` - Models & repositories
- `src/services/` - Business logic
- `src/workers/` - Background tasks

## Key Files
- `tid_v2.md` - Technical specification
- `AGENT_PLAN.md` - Implementation plan
- `lexicon_ru.py` - All bot texts

## Useful Commands
```bash
# Development
poetry install
poetry run pytest

# Database
poetry run alembic revision --autogenerate -m "Message"
poetry run alembic upgrade head

# Docker
docker compose up -d
docker compose logs -f bot
docker compose down
```

## Support
Refer to tid_v2.md for detailed documentation.
