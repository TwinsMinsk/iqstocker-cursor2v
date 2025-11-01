"""
Handler для команды /start

Регистрация пользователя, обработка реферальных ссылок
"""

import re
from typing import Optional

from aiogram import Bot, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from src.bot.keyboards.factories import get_main_menu_keyboard
from src.bot.lexicon.lexicon_ru import LEXICON_RU
from src.config.logging import get_logger
from src.config.settings import settings
from src.core.exceptions import UserNotFoundException
from src.database.connection import get_session
from src.database.repositories.limits_repo import LimitsRepository
from src.database.repositories.user_repo import UserRepository
from src.services.referral_service import ReferralService
from src.services.user_service import UserService

logger = get_logger(__name__)
router = Router(name=__name__)


def parse_referral_code(text: str) -> Optional[int]:
    """Парсит реферальный код из команды /start"""
    match = re.search(r'ref_(\d+)', text)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None
    return None


async def check_channel_subscription(bot: Bot, user_id: int) -> bool:
    """Проверяет подписку на канал"""
    try:
        channel_id = int(settings.bot.channel_id)
        member = await bot.get_chat_member(channel_id, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.warning("channel_check_error", user_id=user_id, error=str(e))
        return False


@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    """Обработчик команды /start"""
    async for session in get_session():
        try:
            # Парсим реферальный код
            referrer_id = parse_referral_code(message.text or "")
            
            # Проверка подписки на канал отключена для упрощения тестирования
            # TODO: Включить проверку подписки в production
            
            # Создаем сервисы
            user_repo = UserRepository()
            limits_repo = LimitsRepository()
            user_service = UserService(user_repo, limits_repo)
            
            # Создаем или получаем пользователя
            user = await user_service.get_or_create(
                session,
                message.from_user.id,
                message.from_user.username,
                referrer_id,
            )
            
            # Получаем лимиты
            limits = await limits_repo.get_by_user_id(session, user.id)
            if not limits:
                # Создаем дефолтные лимиты если нет
                limits = await limits_repo.create_default(
                    session,
                    user.id,
                    user.subscription_tier,
                )
            
            # Проверяем новый ли пользователь
            is_new_user = user.created_at == user.updated_at
            
            if is_new_user:
                # Новый пользователь
                await message.answer(
                    LEXICON_RU["start"].format(
                        username=message.from_user.username or "Пользователь"
                    ),
                    reply_markup=get_main_menu_keyboard(),
                )
            else:
                # Возвращающийся пользователь
                analytics_left = (
                    limits.analytics_limit - limits.analytics_used
                    if limits.analytics_limit != -1
                    else "∞"
                )
                analytics_limit = limits.analytics_limit if limits.analytics_limit != -1 else "∞"
                
                themes_left = (
                    limits.themes_limit - limits.themes_used
                    if limits.themes_limit != -1
                    else "∞"
                )
                themes_limit = limits.themes_limit if limits.themes_limit != -1 else "∞"
                
                await message.answer(
                    LEXICON_RU["start_registered"].format(
                        username=message.from_user.username or "Пользователь",
                        subscription=user.subscription_tier.value.upper(),
                        analytics_left=analytics_left,
                        analytics_limit=analytics_limit,
                        themes_left=themes_left,
                        themes_limit=themes_limit,
                    ),
                    reply_markup=get_main_menu_keyboard(),
                )
            
            logger.info(
                "user_started",
                user_id=user.id,
                telegram_id=user.telegram_id,
                is_new=is_new_user,
            )
        
        except Exception as e:
            logger.error(
                "start_handler_error",
                telegram_id=message.from_user.id,
                error=str(e),
                exc_info=True,
            )
            await message.answer(LEXICON_RU["error_generic"].format(error_code="START_001"))
        finally:
            break

