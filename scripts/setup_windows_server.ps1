# Скрипт установки для Windows Server 2022

Write-Host "🚀 Установка IQStocker v2.0 на Windows Server 2022" -ForegroundColor Green
Write-Host "=" * 60

# Проверка PostgreSQL
Write-Host "`n📊 Проверка PostgreSQL..." -ForegroundColor Yellow
$postgresService = Get-Service -Name "*postgres*" -ErrorAction SilentlyContinue

if ($postgresService) {
    Write-Host "✅ PostgreSQL найден: $($postgresService.Name)" -ForegroundColor Green
} else {
    Write-Host "❌ PostgreSQL не найден" -ForegroundColor Red
    Write-Host "`n📥 Установка PostgreSQL:" -ForegroundColor Cyan
    Write-Host "1. Скачайте: https://www.postgresql.org/download/windows/"
    Write-Host "2. Или используйте chocolatey: choco install postgresql16"
    Write-Host "3. После установки создайте БД и пользователя:"
    Write-Host "   CREATE DATABASE iqstocker;"
    Write-Host "   CREATE USER iqstocker WITH PASSWORD 'iqstocker';"
    Write-Host "   GRANT ALL PRIVILEGES ON DATABASE iqstocker TO iqstocker;"
}

# Проверка Redis
Write-Host "`n📊 Проверка Redis..." -ForegroundColor Yellow
$redisService = Get-Service -Name "*redis*","*memurai*" -ErrorAction SilentlyContinue

if ($redisService) {
    Write-Host "✅ Redis найден: $($redisService.Name)" -ForegroundColor Green
} else {
    Write-Host "❌ Redis не найден" -ForegroundColor Red
    Write-Host "`n📥 Установка Redis:" -ForegroundColor Cyan
    Write-Host "Вариант 1: Memurai (рекомендуется)"
    Write-Host "  Скачайте: https://www.memurai.com/"
    Write-Host "Вариант 2: Redis для Windows"
    Write-Host "  Скачайте: https://github.com/tporadowski/redis/releases"
    Write-Host "Вариант 3: Облачный Redis (Upstash)"
    Write-Host "  Создайте: https://upstash.com/"
}

# Проверка портов
Write-Host "`n🔌 Проверка портов..." -ForegroundColor Yellow
$pgPort = Test-NetConnection -ComputerName localhost -Port 5432 -InformationLevel Quiet -WarningAction SilentlyContinue
$redisPort = Test-NetConnection -ComputerName localhost -Port 6379 -InformationLevel Quiet -WarningAction SilentlyContinue

Write-Host "PostgreSQL (5432): $(if ($pgPort) { '✅ Доступен' -ForegroundColor Green } else { '❌ Недоступен' -ForegroundColor Red })"
Write-Host "Redis (6379): $(if ($redisPort) { '✅ Доступен' -ForegroundColor Green } else { '❌ Недоступен' -ForegroundColor Red })"

Write-Host "`n✅ Готово! После установки PostgreSQL и Redis запустите:`n" -ForegroundColor Green
Write-Host "  python -m alembic upgrade head"
Write-Host "  python -m src.bot.main"

