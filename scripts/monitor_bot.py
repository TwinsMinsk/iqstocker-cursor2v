"""
Мониторинг бота в реальном времени

Выводит логи бота в консоль
"""

import time
from pathlib import Path

log_file = Path("logs/bot_live.log")

print("🔍 Мониторинг логов бота...")
print("Нажмите Ctrl+C для остановки\n")
print("=" * 60)

if not log_file.exists():
    print(f"❌ Лог файл {log_file} не найден")
    print("Бот может еще не запуститься или пишет в другой файл")
    print("Проверьте, что бот запущен: Get-Process python")
    exit(1)

try:
    with open(log_file, 'r', encoding='utf-8') as f:
        # Читаем последние строки
        lines = f.readlines()
        if lines:
            print("Последние строки лога:")
            print("-" * 60)
            for line in lines[-20:]:
                print(line.rstrip())
            print("-" * 60)
        
        # Мониторим новые строки
        print("\n📊 Ожидание новых логов...\n")
        while True:
            line = f.readline()
            if line:
                print(f"[{time.strftime('%H:%M:%S')}] {line.rstrip()}")
            else:
                time.sleep(0.5)
except KeyboardInterrupt:
    print("\n\n⏹️ Мониторинг остановлен")
except FileNotFoundError:
    print(f"❌ Файл {log_file} не найден")

