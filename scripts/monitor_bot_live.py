"""
Мониторинг логов бота в реальном времени

Выводит логи бота в консоль для наблюдения во время тестирования
"""

import sys
import time
from pathlib import Path

def monitor_logs(log_dir: Path = Path("logs")):
    """Мониторит логи бота"""
    print("🔍 Мониторинг логов бота...")
    print("=" * 70)
    print("Нажмите Ctrl+C для остановки\n")
    
    log_files = list(log_dir.glob("*.log"))
    
    if not log_files:
        print("ℹ️ Логи не найдены. Бот может выводить логи в консоль.")
        print("Проверьте вывод процесса бота напрямую.")
        return
    
    # Находим последний лог файл
    latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
    print(f"📄 Читаю логи из: {latest_log.name}\n")
    
    # Открываем файл и следим за изменениями
    try:
        with open(latest_log, 'r', encoding='utf-8', errors='ignore') as f:
            # Переходим в конец файла
            f.seek(0, 2)
            
            while True:
                line = f.readline()
                if line:
                    print(line.rstrip())
                    sys.stdout.flush()
                else:
                    time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n\n✅ Мониторинг остановлен")
    except Exception as e:
        print(f"\n❌ Ошибка мониторинга: {e}")

if __name__ == "__main__":
    monitor_logs()

