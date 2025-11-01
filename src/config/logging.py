"""
Настройка логирования для IQStocker v2.0

Использует structlog для структурированного логирования
"""

import logging
import sys

import structlog

from src.config.settings import settings


def configure_logging() -> None:
    """Настроить логирование"""
    
    # Определяем процессоры в зависимости от окружения
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    # Выбираем рендерер в зависимости от окружения
    if settings.app.environment == "development":
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        processors.append(structlog.processors.JSONRenderer())
    
    # Настраиваем structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Настраиваем стандартное логирование
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.app.log_level.upper()),
    )


def get_logger(name: str | None = None) -> structlog.BoundLogger:
    """
    Получить логгер
    
    Args:
        name: Имя логгера (по умолчанию __name__)
        
    Returns:
        Структурированный логгер
    """
    return structlog.get_logger(name)


# Инициализация логирования при импорте модуля
configure_logging()
