# Скрипт для исправления .env файла
# Добавляет отсутствующий BOT_TOKEN

$envFile = ".env"
$botToken = "BOT_TOKEN=8292646983:AAGTkZeNlK7nu0VEu6QFAyNkjcminXa_ARA"

Write-Host "🔧 Исправление .env файла..." -ForegroundColor Yellow

if (-not (Test-Path $envFile)) {
    Write-Host "❌ .env файл не найден!" -ForegroundColor Red
    exit 1
}

$content = Get-Content $envFile -Raw

# Проверяем наличие BOT_TOKEN
if ($content -match "BOT_TOKEN\s*=") {
    Write-Host "✅ BOT_TOKEN уже есть в .env" -ForegroundColor Green
    exit 0
}

# Находим строку после "# Bot Configuration"
if ($content -match "(# Bot Configuration\s*\n)") {
    # Вставляем BOT_TOKEN после комментария
    $newContent = $content -replace "(# Bot Configuration\s*\n)", "`$1$botToken`n"
    Set-Content -Path $envFile -Value $newContent -Encoding UTF8
    Write-Host "✅ BOT_TOKEN добавлен в .env файл!" -ForegroundColor Green
} else {
    # Добавляем в начало файла
    $newContent = "# Bot Configuration`n$botToken`n`n$content"
    Set-Content -Path $envFile -Value $newContent -Encoding UTF8
    Write-Host "✅ BOT_TOKEN добавлен в начало .env файла!" -ForegroundColor Green
}

Write-Host "`n✅ .env файл исправлен!" -ForegroundColor Green
Write-Host "Теперь можно запускать бота: python -m src.bot.main" -ForegroundColor Cyan

