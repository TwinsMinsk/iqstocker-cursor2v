# Мониторинг бота в PowerShell

Write-Host "🤖 Мониторинг IQStocker Bot" -ForegroundColor Green
Write-Host "=" * 60

# Проверка процесса
$process = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.WorkingSet64 -gt 100MB } | Select-Object -First 1

if ($process) {
    Write-Host "✅ Бот запущен!" -ForegroundColor Green
    Write-Host "   PID: $($process.Id)"
    Write-Host "   Память: $([math]::Round($process.WorkingSet64/1MB,2)) MB"
    Write-Host "   Время работы: $((Get-Date) - $process.StartTime)"
} else {
    Write-Host "❌ Бот не найден" -ForegroundColor Red
}

Write-Host "`n📊 Для просмотра логов используйте: Get-Content logs/bot_live.log -Wait" -ForegroundColor Yellow
Write-Host "📱 Отправьте /start боту в Telegram для тестирования`n" -ForegroundColor Cyan

# Мониторинг логов если файл существует
$logFile = "logs/bot_live.log"
if (Test-Path $logFile) {
    Write-Host "Последние логи:" -ForegroundColor Yellow
    Get-Content $logFile -Tail 20
} else {
    Write-Host "Лог файл не найден. Бот может писать логи в консоль." -ForegroundColor Yellow
}

