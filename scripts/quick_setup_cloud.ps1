# Быстрая настройка с облачными сервисами

Write-Host "☁️ Быстрая настройка с облачными сервисами" -ForegroundColor Green
Write-Host "=" * 60

Write-Host "`n📋 Инструкция:" -ForegroundColor Yellow

Write-Host "`n1️⃣ PostgreSQL (Supabase - бесплатно):" -ForegroundColor Cyan
Write-Host "   • Перейдите: https://supabase.com"
Write-Host "   • Создайте новый проект"
Write-Host "   • В настройках проекта → Database → Connection string"
Write-Host "   • Скопируйте connection string"
Write-Host "   • Замените 'postgresql://' на 'postgresql+asyncpg://'"
Write-Host "   • Обновите DATABASE_URL в .env файле"

Write-Host "`n2️⃣ Redis (Upstash - бесплатно):" -ForegroundColor Cyan
Write-Host "   • Перейдите: https://upstash.com/"
Write-Host "   • Создайте новый Redis database"
Write-Host "   • Скопируйте REST URL и password"
Write-Host "   • Обновите в .env:"
Write-Host "     REDIS_HOST=[host-from-upstash]"
Write-Host "     REDIS_PORT=6379"
Write-Host "     REDIS_PASSWORD=[password-from-upstash]"

Write-Host "`n3️⃣ После настройки:" -ForegroundColor Cyan
Write-Host "   • Примените миграции: python -m alembic upgrade head"
Write-Host "   • Загрузите темы: python scripts/load_themes.py"
Write-Host "   • Запустите бота: python -m src.bot.main"

Write-Host "`n💡 Альтернатива: Railway.app" -ForegroundColor Yellow
Write-Host "   • Создайте проект на https://railway.app"
Write-Host "   • Добавьте PostgreSQL и Redis"
Write-Host "   • Railway автоматически предоставит DATABASE_URL и REDIS_URL"

