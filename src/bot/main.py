"""
Главный файл Telegram бота IQStocker v2.0

Инициализация бота, регистрация handlers, запуск
"""

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from src.bot.handlers import (
    admin,
    analytics,
    calendar,
    channel,
    faq,
    lessons,
    menu,
    payments,
    profile,
    referral,
    start,
    themes,
)
from src.config.logging import get_logger
from src.config.settings import settings

logger = get_logger(__name__)


async def main():
    """Главная функция запуска бота"""
    # Инициализация бота
    bot = Bot(
        token=settings.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    
    # Инициализация диспетчера
    dp = Dispatcher(storage=MemoryStorage())
    
    # Регистрация handlers
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(channel.router)
    dp.include_router(profile.router)
    dp.include_router(analytics.router)
    dp.include_router(themes.router)
    dp.include_router(lessons.router)
    dp.include_router(calendar.router)
    dp.include_router(faq.router)
    dp.include_router(referral.router)
    dp.include_router(payments.router)
    dp.include_router(admin.router)
    
    logger.info("bot_started", bot_token=settings.bot.token[:10] + "...")
    
    # Запуск бота
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error("bot_error", error=str(e), exc_info=True)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

