"""
Скрипт для запуска бота с обработкой ошибок

Запускает бота и логирует все ошибки
"""

import asyncio
import sys
from pathlib import Path

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.bot.main import main
from src.config.logging import get_logger

logger = get_logger(__name__)


if __name__ == "__main__":
    try:
        logger.info("bot_starting", script="run_bot.py")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("bot_stopped", reason="keyboard_interrupt")
    except Exception as e:
        logger.error("bot_crash", error=str(e), exc_info=True)
        sys.exit(1)

