#!/bin/bash
set -e

echo "🏗️  Creating IQStocker v2.0 project structure..."

# Create all directories
mkdir -p src/bot/{handlers,keyboards,states,lexicon}
mkdir -p src/database/repositories  
mkdir -p src/services
mkdir -p src/admin/{views,static,templates}
mkdir -p src/api
mkdir -p src/workers
mkdir -p src/core/{analytics,utils}
mkdir -p src/config
mkdir -p alembic/versions
mkdir -p tests/{unit,integration}
mkdir -p logs

# Create __init__.py files
find src/ -type d -exec touch {}/__init__.py \;

# Create .env.example
cat > .env.example << 'EOF'
# Bot Configuration
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=123456,789012
CHANNEL_ID=-1001234567890

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/iqstocker
DATABASE_ECHO=false

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Admin Panel
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password
SECRET_KEY=your_random_secret_key

# Tribute.tg
TRIBUTE_API_KEY=trib_key_xxx
TRIBUTE_WEBHOOK_SECRET=webhook_secret_xxx
TRIBUTE_MERCHANT_ID=merchant_xxx

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
BASE_URL=http://localhost:8000
EOF

# Create .gitignore
cat > .gitignore << 'EOF'
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.env
.venv
venv/
logs/
*.log
.pytest_cache/
.coverage
htmlcov/
.mypy_cache/
.ruff_cache/
*.db
*.sqlite
EOF

echo "✅ Project structure created successfully!"
echo "📝 Next steps:"
echo "   1. poetry install"
echo "   2. cp .env.example .env"
echo "   3. Edit .env with your credentials"
echo "   4. docker compose up -d postgres redis"
echo "   5. poetry run alembic upgrade head"
